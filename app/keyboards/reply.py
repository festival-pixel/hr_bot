from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from app.services.i18n import t


def phone_request_kb(lang: str) -> ReplyKeyboardMarkup:
    """Reply-клавиатура запроса номера телефона (Request Contact)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_request_kb(lang: str) -> ReplyKeyboardMarkup:
    """Reply-клавиатура запроса геолокации (Request Location)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_share_location"), request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
