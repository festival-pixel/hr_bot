from aiogram import Router

from app.handlers import application, start
from app.handlers.admin import router as admin_router

router = Router()

# Админ-роутер первым: его хендлеры защищены фильтром IsAdmin,
# неподходящие апдейты уходят дальше в пользовательские роутеры.
router.include_router(admin_router)
router.include_router(start.router)
router.include_router(application.router)
