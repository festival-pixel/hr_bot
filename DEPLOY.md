# Деплой HR-бота на сервер (Kamatera)

Бот работает через **polling** — публичный домен, белый IP и SSL не нужны.
Нужны только исходящие соединения к Telegram. Всё поднимается в Docker одной командой.

---

## 1. Создать сервер в Kamatera

Панель Kamatera → **Create New Server**:

| Параметр | Значение |
|---|---|
| Zone / Datacenter | **Amsterdam (Europe)** — ближе всего к серверам Telegram |
| Type | **Type B — General Purpose** |
| CPU | 1–2 vCPU |
| RAM | **2 GB** |
| Disk | 30 GB SSD |
| Image | **Ubuntu Server 24.04 LTS 64-bit** |
| Networking | публичный IP (по умолчанию) |
| Password/SSH | задать root-пароль или добавить SSH-ключ |

После создания получишь **IP-адрес** и **root-доступ**.

---

## 2. Подключиться по SSH

```bash
ssh root@SERVER_IP
```

## 3. Установить Docker

```bash
apt update && apt -y upgrade
curl -fsSL https://get.docker.com | sh
docker --version && docker compose version
```

## 4. Загрузить проект на сервер

**Вариант A — готовый архив (рекомендуется, git не нужен).**
Архив уже собран: `D:\pythonProject\hr_bot_deploy.tar.gz` (без `venv`, с `.env` внутри).

На локальном компе (PowerShell) залей его на сервер:
```powershell
scp D:\pythonProject\hr_bot_deploy.tar.gz root@SERVER_IP:/root/
```
На сервере распакуй:
```bash
mkdir -p /root/hr_bot_project && tar -xzf /root/hr_bot_deploy.tar.gz -C /root/hr_bot_project
cd /root/hr_bot_project
```

**Вариант B — через Git** (удобно обновлять через `git pull`):
```bash
git clone https://github.com/festival-pixel/hr_bot.git hr_bot_project && cd hr_bot_project
cp .env.example .env   # затем заполнить .env (см. шаг 5)
```
> Репозиторий приватный → при `git clone` введи логин GitHub и Personal Access
> Token вместо пароля (github.com → Settings → Developer settings → Tokens).

## 5. Проверить/поправить `.env` на сервере

В архиве `.env` **уже есть** (`BOT_TOKEN`, `ADMIN_ID=241055026,779932515`).
Открой и **обязательно смени пароль БД** на сильный:
```bash
nano .env
```
```
DB_PASSWORD=СЛОЖНЫЙ_ПАРОЛЬ    # НЕ оставляй "postgres" на проде!
DEBUG=False
```
Сохранить: Ctrl+O, Enter, Ctrl+X.
> `DB_HOST`/`DB_PORT` в `.env` — для локального запуска; в Docker сервис `bot`
> сам переопределяет их на `postgres:5432`. Менять не нужно.

## 6. Запустить

```bash
docker compose up -d --build
```
Поднимутся **postgres** и **bot**, база создаст таблицы, бот начнёт polling.

## 7. Проверить логи

```bash
docker compose logs -f bot
```
Должно быть:
```
aiogram.dispatcher | Run polling for bot @vsedlyadoma_hr_bot ...
```
Если видишь `TelegramConflictError: terminated by other getUpdates` — значит
где-то ещё запущен тот же бот (например, локальный `python main.py`).
**Один токен = один запущенный экземпляр.** Останови остальные.

Выйти из просмотра логов — `Ctrl+C` (бот продолжит работать в фоне).

---

## Управление

```bash
docker compose ps                 # статус контейнеров
docker compose logs -f bot        # логи бота
docker compose restart bot        # перезапустить бота
docker compose down               # остановить всё
docker compose up -d              # запустить снова
```

**Обновить код (при Git):**
```bash
git pull
docker compose up -d --build
```

**Бэкап базы:**
```bash
docker exec hr_bot_postgres pg_dump -U postgres hr_bot_db > backup_$(date +%F).sql
```

**Автозапуск после перезагрузки сервера** — уже настроен: у обоих сервисов
`restart: always`, Docker сам поднимет их при старте системы.

---

## Безопасность (коротко)
- Порт БД проброшен только на `127.0.0.1` — снаружи Postgres недоступен. ✅
- Смени `DB_PASSWORD` на сильный, не используй дефолтный.
- Опционально включи firewall (бот работает и без открытых входящих портов):
  ```bash
  ufw allow OpenSSH && ufw --force enable
  ```
