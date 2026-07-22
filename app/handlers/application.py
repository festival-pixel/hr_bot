from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import DEFAULT_SCHEDULE, SCHEDULE_CHOICE_VACANCIES
from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import (
    confirm_kb,
    schedule_kb,
    skip_location_kb,
    skip_resume_kb,
    yes_no_kb,
)
from app.keyboards.reply import (
    location_request_kb,
    phone_request_kb,
    remove_kb,
)
from app.services.i18n import t
from app.states.application import ApplicationState
from app.utils.formatters import format_confirmation
from app.utils.notify import notify_new_application
from app.utils.validators import parse_age

router = Router()


# ─── Старт анкеты: выбор вакансии ───

@router.callback_query(F.data.startswith("vac:"))
async def choose_vacancy(callback: CallbackQuery, state: FSMContext, lang: str):
    vacancy = callback.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(vacancy=vacancy)
    await state.set_state(ApplicationState.fullname)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "ask_fullname"))
    await callback.answer()


# ─── ФИО ───

@router.message(ApplicationState.fullname, F.text)
async def get_fullname(message: Message, state: FSMContext, lang: str):
    await state.update_data(fullname=message.text.strip())
    await state.set_state(ApplicationState.age)
    await message.answer(t(lang, "ask_age"))


# ─── Возраст ───

@router.message(ApplicationState.age, F.text)
async def get_age(message: Message, state: FSMContext, lang: str):
    age = parse_age(message.text)
    if age is None:
        await message.answer(t(lang, "error_age"))
        return
    await state.update_data(age=age)
    await state.set_state(ApplicationState.phone)
    await message.answer(t(lang, "ask_phone"), reply_markup=phone_request_kb(lang))


# ─── Телефон (контакт или текст) ───

@router.message(ApplicationState.phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext, lang: str):
    await _save_phone(message, state, lang, message.contact.phone_number)


@router.message(ApplicationState.phone, F.text)
async def get_phone_text(message: Message, state: FSMContext, lang: str):
    await _save_phone(message, state, lang, message.text.strip())


async def _save_phone(message: Message, state: FSMContext, lang: str, phone: str):
    await state.update_data(phone=phone)
    await state.set_state(ApplicationState.student)
    await message.answer(t(lang, "phone_saved"), reply_markup=remove_kb())
    await message.answer(
        t(lang, "ask_student"), reply_markup=yes_no_kb(lang, "student")
    )


# ─── Студент ───

@router.callback_query(ApplicationState.student, F.data.startswith("student:"))
async def get_student(callback: CallbackQuery, state: FSMContext, lang: str):
    is_student = callback.data.split(":", 1)[1] == "yes"
    await state.update_data(student=is_student)
    await state.set_state(ApplicationState.address)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "ask_address"))
    await callback.answer()


# ─── Адрес ───

@router.message(ApplicationState.address, F.text)
async def get_address(message: Message, state: FSMContext, lang: str):
    await state.update_data(address=message.text.strip())
    await state.set_state(ApplicationState.location)
    await message.answer(
        t(lang, "ask_location"), reply_markup=location_request_kb(lang)
    )
    sent = await message.answer(
        t(lang, "or_skip"), reply_markup=skip_location_kb(lang)
    )
    await state.update_data(skip_msg_id=sent.message_id)


# ─── Геолокация (или пропуск) ───

@router.message(ApplicationState.location, F.location)
async def get_location(message: Message, state: FSMContext, lang: str, bot: Bot):
    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )
    await _clear_skip_button(message, state, bot)
    await _ask_languages(message, state, lang)


@router.callback_query(ApplicationState.location, F.data == "loc:skip")
async def skip_location(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.update_data(latitude=None, longitude=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _ask_languages(callback.message, state, lang)
    await callback.answer()


async def _clear_skip_button(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    skip_id = data.get("skip_msg_id")
    if skip_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id, message_id=skip_id, reply_markup=None
            )
        except Exception:
            pass


async def _ask_languages(message: Message, state: FSMContext, lang: str):
    await state.set_state(ApplicationState.languages)
    await message.answer(t(lang, "ask_languages"), reply_markup=remove_kb())


# ─── Языки ───

@router.message(ApplicationState.languages, F.text)
async def get_languages(message: Message, state: FSMContext, lang: str):
    await state.update_data(languages=message.text.strip())
    data = await state.get_data()

    if data["vacancy"] in SCHEDULE_CHOICE_VACANCIES:
        await state.set_state(ApplicationState.schedule)
        await message.answer(t(lang, "ask_schedule"), reply_markup=schedule_kb(lang))
    else:
        await state.update_data(schedule=DEFAULT_SCHEDULE)
        await state.set_state(ApplicationState.motivation)
        await message.answer(t(lang, "ask_motivation"))


# ─── График (только кассир/консультант) ───

@router.callback_query(ApplicationState.schedule, F.data.startswith("sch:"))
async def get_schedule(callback: CallbackQuery, state: FSMContext, lang: str):
    schedule = callback.data.split(":", 1)[1]
    await state.update_data(schedule=schedule)
    await state.set_state(ApplicationState.motivation)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "ask_motivation"))
    await callback.answer()


# ─── Мотивация ───

@router.message(ApplicationState.motivation, F.text)
async def get_motivation(message: Message, state: FSMContext, lang: str):
    await state.update_data(motivation=message.text.strip())
    await state.set_state(ApplicationState.resume)
    sent = await message.answer(
        t(lang, "ask_resume"), reply_markup=skip_resume_kb(lang)
    )
    await state.update_data(resume_msg_id=sent.message_id)


# ─── Резюме (документ или пропуск) ───

@router.message(ApplicationState.resume, F.document)
async def get_resume(message: Message, state: FSMContext, lang: str, bot: Bot):
    await state.update_data(resume_file_id=message.document.file_id)
    data = await state.get_data()
    resume_id = data.get("resume_msg_id")
    if resume_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id, message_id=resume_id, reply_markup=None
            )
        except Exception:
            pass
    await _show_confirm(message, state, lang)


@router.callback_query(ApplicationState.resume, F.data == "resume:skip")
async def skip_resume(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.update_data(resume_file_id=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_confirm(callback.message, state, lang)
    await callback.answer()


async def _show_confirm(message: Message, state: FSMContext, lang: str):
    await state.set_state(ApplicationState.confirm)
    data = await state.get_data()
    await message.answer(
        format_confirmation(data, lang), reply_markup=confirm_kb(lang)
    )


# ─── Подтверждение / отправка ───

@router.callback_query(ApplicationState.confirm, F.data == "app:send")
async def send_application(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    lang: str,
    bot: Bot,
):
    data = await state.get_data()
    candidate = await CandidateRepository(session).create(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        language=lang,
        vacancy=data["vacancy"],
        schedule=data["schedule"],
        fullname=data["fullname"],
        age=data["age"],
        phone=data["phone"],
        student=data["student"],
        address=data["address"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        languages=data["languages"],
        motivation=data["motivation"],
        resume_file_id=data.get("resume_file_id"),
    )
    await state.clear()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        t(lang, "success", number=candidate.application_number)
    )
    await callback.answer()

    await notify_new_application(bot, candidate)


@router.callback_query(ApplicationState.confirm, F.data == "app:restart")
async def restart_application(callback: CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    vacancy = data.get("vacancy")
    await state.clear()
    await state.update_data(vacancy=vacancy)
    await state.set_state(ApplicationState.fullname)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "ask_fullname"))
    await callback.answer()
