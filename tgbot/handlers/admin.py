from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.services.database import AsyncSession
from tgbot.models.users import User


async def admin_start(m: Message):
    await m.reply("Hello, admin!")


async def admin_stats(m: Message, db_session: AsyncSession):
    count = await User.users_count(db_session)
    await m.reply(f"Total users: {count}")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands=["admin"],
        state="*",
        is_admin=True
    )
    dp.register_message_handler(
        admin_stats,
        commands=["stats"],
        state="*",
        is_admin=True
    )
