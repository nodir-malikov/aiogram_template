from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import ctx_data

from loguru import logger

from tgbot.config import load_config
from tgbot.models.user import TGUser
from tgbot.services.database import AsyncSession
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.keyboards.inline import choose_language, cd_choose_lang
from tgbot.keyboards.reply import phone_number
from tgbot.misc.utils import Map, find_button_text

config = load_config("bot.ini")


async def user_start(m: Message, texts: Map):
    """User start command handler"""
    logger.info(f"User {m.from_user.id} started the bot")
    await m.reply(texts.user.hi.format(mention=m.from_user.get_mention()))


async def user_reset_state(m: Message, texts: Map, state: FSMContext):
    """User reset state command handler"""
    logger.info(f"User {m.from_user.id} reseted state")
    await state.reset_state(with_data=False)
    await m.reply(texts.user.reset_state)


async def user_me(m: Message, db_user: TGUser, texts: Map):
    """User me command handler"""
    logger.info(f"User {m.from_user.id} requested his info")
    await m.reply(
        texts.user.me.format(
            telegram_id=db_user.telegram_id,
            firstname=db_user.firstname,
            lastname=db_user.lastname,
            username=db_user.username,
            phone=db_user.phone,
            lang_code=db_user.lang_code,
        )
    )


async def user_close_reply_keyboard(m: Message, texts: Map):
    """User close reply keyboard button handler"""
    logger.info(f"User {m.from_user.id} closed reply keyboard")
    await m.reply(
        texts.user.close_reply_keyboard, reply_markup=ReplyKeyboardRemove()
    )


async def user_phone(m: Message, texts: Map):
    """User phone command handler"""
    logger.info(f"User {m.from_user.id} requested phone number")
    await m.reply(texts.user.phone, reply_markup=await phone_number(texts))


async def user_phone_sent(
    m: Message, texts: Map, db_user: TGUser, db_session: AsyncSession
):
    """User contact phone receiver handler"""
    logger.info(f"User {m.from_user.id} sent phone number")

    number = m.contact.phone_number

    # if number not start with +, add +
    if not number.startswith("+"):
        number = "+" + number

    # updating user's phone number
    await TGUser.update_user(
        db_session,
        telegram_id=db_user.telegram_id,
        updated_fields={"phone": number},
    )
    await m.reply(texts.user.phone_saved, reply_markup=ReplyKeyboardRemove())


async def user_lang(m: Message, texts: Map):
    """User lang command handler"""
    logger.info(f"User {m.from_user.id} requested language")
    await m.reply(texts.user.lang, reply_markup=await choose_language(texts))


async def user_lang_choosen(
    cb: CallbackQuery,
    callback_data: dict,
    texts: Map,
    db_user: TGUser,
    db_session: AsyncSession,
):
    """User lang choosen handler"""
    code = callback_data.get("lang_code")
    logger.info(f"User {cb.from_user.id} choosed language: {code}")
    await TGUser.update_user(
        db_session,
        telegram_id=db_user.telegram_id,
        updated_fields={"lang_code": code},
    )

    # manually load translation for user with new lang_code
    texts = await TranslationMiddleware().reload_translations(
        cb, ctx_data.get(), code
    )
    btn_text = await find_button_text(
        cb.message.reply_markup.inline_keyboard, cb.data
    )
    await cb.message.edit_text(
        texts.user.lang_choosen.format(lang=btn_text), reply_markup=""
    )
    await cb.answer()


async def user_global_timeout_trigger(
    m: Message, texts: Map, state: FSMContext
):
    """User global timeout trigger handler"""
    logger.info(f"User {m.from_user.id} triggered global timeout")
    await m.reply(
        texts.user.global_timeout_trigger.format(
            timeout=config.tg_bot.global_timeout
        )
    )
    await state.update_data(global_timeout=str(datetime.now()))


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start, commands=["start"], state="*", chat_type="private"
    )
    dp.register_message_handler(
        user_reset_state,
        commands=["res"],
        state="*",
        chat_type="private",
    )
    dp.register_message_handler(
        user_me, commands=["me"], state="*", chat_type="private"
    )
    dp.register_message_handler(
        user_phone, commands=["phone"], state="*", chat_type="private"
    )
    dp.register_message_handler(
        user_lang, commands=["lang"], state="*", chat_type="private"
    )
    dp.register_message_handler(
        user_close_reply_keyboard,
        is_close_btn=True,
        state="*",
        chat_type="private",
    )
    dp.register_message_handler(
        user_phone_sent,
        content_types=["contact"],
        state="*",
        chat_type="private",
    )
    dp.register_callback_query_handler(
        user_lang_choosen,
        cd_choose_lang.filter(),
        state="*",
        chat_type="private",
    )
    dp.register_message_handler(
        user_global_timeout_trigger,
        commands=["global_timeout"],
        state="*",
        chat_type="private",
    )
