from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.models.users import User


async def user_start(m: Message):
    await m.reply(f"Hello, {m.from_user.get_mention()}!")


async def user_me(m: Message, db_user: User):
    text = "<b>Your data in DB:</b>\n"\
        f"Telegram ID: <code>{db_user.telegram_id}</code>\n"\
        f"First name: <code>{db_user.firstname}</code>\n"\
        f"Last name: <code>{db_user.lastname}</code>\n"\
        f"Username: <code>{db_user.username}</code>\n"\
        f"Phone: <code>{db_user.phone}</code>\n"\
        f"Language code: <code>{db_user.lang_code}</code>\n"
    await m.reply(text)


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
