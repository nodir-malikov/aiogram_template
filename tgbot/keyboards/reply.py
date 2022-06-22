from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.misc.utils import Map


async def phone_number(texts: Map):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.user.kb.reply.phone,
                            request_contact=True)],
            [KeyboardButton(text=texts.user.kb.reply.close)],
        ],
        resize_keyboard=True,
    )
    return keyboard
