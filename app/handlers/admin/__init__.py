from aiogram import Router

from app.filters.admin import IsAdmin
from app.handlers.admin import card, list, menu, search

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

router.include_router(menu.router)
router.include_router(list.router)
router.include_router(search.router)
router.include_router(card.router)
