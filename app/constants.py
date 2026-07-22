from enum import Enum


class Language(str, Enum):
    RU = "ru"
    UZ = "uz"


class Vacancy(str, Enum):
    CLEANER = "cleaner"
    CASHIER = "cashier"
    CONSULTANT = "consultant"
    KITCHEN = "kitchen"
    SALAD = "salad"


class Schedule(str, Enum):
    DAY = "08:00-20:00"
    EVENING = "12:00-00:00"


class Status(str, Enum):
    NEW = "new"
    INVITED = "invited"
    REJECTED = "rejected"
    ARCHIVED = "archived"


# Порядок вакансий в меню
VACANCY_ORDER = [
    Vacancy.CLEANER.value,
    Vacancy.CASHIER.value,
    Vacancy.CONSULTANT.value,
    Vacancy.KITCHEN.value,
    Vacancy.SALAD.value,
]

# Вакансии, где кандидат выбирает график. Остальные — фикс. график ниже.
SCHEDULE_CHOICE_VACANCIES = {Vacancy.CASHIER.value, Vacancy.CONSULTANT.value}
DEFAULT_SCHEDULE = Schedule.DAY.value

# Фиксированные графики для вакансий без выбора
FIXED_SCHEDULES = {
    Vacancy.CLEANER.value: "08:00-20:00",
    Vacancy.KITCHEN.value: "08:00-20:00",
    Vacancy.SALAD.value: "08:00-18:00",
}

# Локализованные названия вакансий
VACANCY_NAMES = {
    "ru": {
        "cleaner": "🧹 Уборщица",
        "cashier": "💰 Кассир",
        "consultant": "🛍 Продавец-консультант",
        "kitchen": "👨‍🍳 Работник кухни",
        "salad": "🥗 Салатница",
    },
    "uz": {
        "cleaner": "🧹 Farrosh",
        "cashier": "💰 Kassir",
        "consultant": "🛍 Sotuvchi-konsultant",
        "kitchen": "👨‍🍳 Oshpaz",
        "salad": "🥗 Salatchi",
    },
}

# Статусы (для админ-панели, RU)
STATUS_NAMES = {
    "new": "🆕 Новая",
    "invited": "✅ Приглашён",
    "rejected": "❌ Отказ",
    "archived": "📦 Архив",
}

STATUS_EMOJI = {
    "new": "🆕",
    "invited": "✅",
    "rejected": "❌",
    "archived": "📦",
}

VACANCY_EMOJI = {
    "cleaner": "🧹",
    "cashier": "💰",
    "consultant": "🛍",
    "kitchen": "👨‍🍳",
    "salad": "🥗",
}
