from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.services.database import AsyncSession
from tgbot.models.users import User
from tgbot.misc.utils import Map


async def admin_start(m: Message, texts: Map):
    await m.reply(texts.admin.hi)


async def admin_stats(m: Message, db_session: AsyncSession, texts: Map):
    count = await User.users_count(db_session)
    await m.reply(texts.admin.total_users.format(count=count))


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
