from aiogram import Dispatcher
from aiogram.types import Message
from loguru import logger

from tgbot.services.database import AsyncSession
from tgbot.models.users import User
from tgbot.misc.broadcast import broadcast
from tgbot.misc.utils import Map


async def admin_start(m: Message, texts: Map):
    await m.reply(texts.admin.hi)


async def admin_stats(m: Message, db_session: AsyncSession, texts: Map):
    count = await User.users_count(db_session)
    await m.reply(texts.admin.total_users.format(count=count))


async def admin_broadcast(m: Message, db_session: AsyncSession, texts: Map):
    broadcast_text = m.text.replace("/broadcast", "")
    if not broadcast_text:
        await m.reply(texts.admin.no_broadcast_text)
        return
    users = await User.get_all_users(db_session)
    try:
        await broadcast(broadcast_text, users)
        await m.reply(texts.admin.broadcast_success)
    except Exception as e:
        await m.reply(texts.admin.broadcast_error.format(err=e))
        logger.error(f"Error while broadcasting!")
        raise e


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
    dp.register_message_handler(
        admin_broadcast,
        commands=["broadcast"],
        state="*",
        is_admin=True
    )
