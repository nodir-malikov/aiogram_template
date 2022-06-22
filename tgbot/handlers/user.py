from aiogram import Dispatcher
from aiogram.types import Message

from loguru import logger

from tgbot.models.users import User
from tgbot.misc.utils import Map


async def user_start(m: Message, texts: Map):
    await m.reply(texts.user.hi.format(mention=m.from_user.get_mention()))


async def user_me(m: Message, db_user: User, texts: Map):
    await m.reply(texts.user.me.format(
        telegram_id=db_user.telegram_id,
        firstname=db_user.firstname,
        lastname=db_user.lastname,
        username=db_user.username,
        phone=db_user.phone,
        lang_code=db_user.lang_code))


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start,
        commands=["start"],
        state="*"
    )
    dp.register_message_handler(
        user_me,
        commands=["me"],
        state="*"
    )
