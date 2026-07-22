# HR-бот «Всё для дома»

Telegram-бот для подбора персонала: кандидат заполняет анкету (RU/UZ),
HR получает заявку и управляет ей (список, фильтры, поиск, статусы, Excel).

## Стек
aiogram 3 · SQLAlchemy 2 (async) · PostgreSQL · pydantic-settings · openpyxl · Docker

## Возможности
**Кандидат:** выбор языка → вакансии → анкета (ФИО, возраст, телефон, студент,
адрес, геолокация, языки, график, мотивация, резюме) → подтверждение → номер заявки.

**HR (несколько админов):** уведомление о заявке + файл резюме, список с фильтрами
по статусу/вакансии, пагинация, поиск по ФИО/телефону, смена статуса
(Новая/Приглашён/Отказ/Архив), полная карточка, экспорт в Excel, статистика.

## Архитектура
```
main.py                  — точка входа
app/
├── config.py            — типизированный конфиг (pydantic-settings)
├── loader.py            — bot, dispatcher
├── middlewares/         — DI: сессия БД + пользователь/язык
├── filters/             — IsAdmin
├── handlers/            — start, application (FSM), admin/*
├── keyboards/           — inline (всё), reply (контакт/геолокация)
├── states/              — FSM состояния
├── database/            — models, session, repositories
├── services/            — i18n, excel
├── utils/               — validators, formatters, notify
└── locales/             — ru.json, uz.json
```

## Локальный запуск
```bash
docker compose up -d postgres          # база в Docker
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env                 # заполнить BOT_TOKEN, ADMIN_ID
python main.py
```

## Запуск целиком в Docker
```bash
cp .env.example .env                   # заполнить значения
docker compose up -d --build
docker compose logs -f bot
```

## Деплой на сервер
См. **[DEPLOY.md](DEPLOY.md)** — пошаговая инструкция (Kamatera / любой VPS).

> ⚠️ Один токен бота = один запущенный экземпляр (иначе `TelegramConflictError`).
