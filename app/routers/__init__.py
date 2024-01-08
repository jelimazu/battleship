from aiogram import Dispatcher, F
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.user import user_handlers
from app.admin import admin_handlers
from data.config import admin_id


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in admin_id:
            return True
        else:
            return False




def register_all_routers(dp: Dispatcher):
    admin_handlers.router.message.filter(F.chat.type == "private", IsAdmin())
    user_handlers.router.message.filter(F.chat.type == "private")
    dp.include_router(admin_handlers.router)  # Админ роутер
    dp.include_router(user_handlers.router)  # Юзер роутер

