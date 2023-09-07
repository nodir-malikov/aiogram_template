from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.utils import Map

cd_choose_lang = CallbackData("choosen_language", "lang_code")
cd_choose_lang_broadcast = CallbackData("choose_lang_broadcast", "lang_code")


async def choose_language(texts: Map):
    """Choose language inline keyboard"""
    # get languages from translation texts
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(
            InlineKeyboardButton(
                v.text, callback_data=cd_choose_lang.new(lang_code=k)
            )
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )


async def admin_broadcast_choose_lang(texts: Map):
    """Choose language inline keyboard"""
    # get languages from translation texts
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(
            InlineKeyboardButton(
                v.text, callback_data=cd_choose_lang_broadcast.new(lang_code=k)
            )
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )


async def admin_broadcast_button_keyboard(texts: Map):
    """
    Ask admin to choose whether to add button to broadcasting message or not
    """
    keyboard = [
        InlineKeyboardButton(
            texts.admin.kb.inline.broadcast_button_yes,
            callback_data="broadcast_button_yes",
        ),
        InlineKeyboardButton(
            texts.admin.kb.inline.broadcast_button_no,
            callback_data="broadcast_button_no",
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])


async def admin_broadcast_confirm_keyboard(texts: Map):
    """
    Ask admin to confirm broadcasting message
    """
    keyboard = [
        InlineKeyboardButton(
            texts.admin.kb.inline.broadcast_confirm,
            callback_data="broadcast_confirm",
        ),
        InlineKeyboardButton(
            texts.admin.kb.inline.broadcast_cancel,
            callback_data="broadcast_cancel",
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])


async def admin_broadcast_cancel_keyboard(texts: Map):
    """
    Cancel broadcast before sending
    """
    keyboard = [
        InlineKeyboardButton(
            texts.admin.kb.inline.broadcast_cancel,
            callback_data="broadcast_cancel",
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])


async def generate_broadcast_buttons(data):
    """Generate broadcast buttons"""
    buttons = []
    broadcast_want_buttons = data.get("broadcast_want_buttons")
    if broadcast_want_buttons:
        buttons_texts = data.get("broadcast_buttons_texts")
        buttons_links = data.get("broadcast_buttons_links")
        if buttons_texts and buttons_links:
            buttons_texts = buttons_texts.split("\n")
            buttons_links = buttons_links.split("\n")
            if len(buttons_texts) == len(buttons_links):
                for i, item in enumerate(buttons_texts):
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                item, url=buttons_links[i]
                            )
                        ]
                    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
