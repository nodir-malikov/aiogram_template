from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.utils import Map

cd_choose_lang = CallbackData("choosen_language", "lang_code")


async def choose_language(texts: Map):
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(InlineKeyboardButton(
            v.text, callback_data=cd_choose_lang.new(lang_code=k)))
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )
