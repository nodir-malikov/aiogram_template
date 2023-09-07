import asyncio

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, ContentTypes
from aiogram.dispatcher import FSMContext

from loguru import logger

from tgbot.services.database import AsyncSession
from tgbot.models.user import TGUser
from tgbot.keyboards import inline
from tgbot.misc.states import AdminBroadcast
from tgbot.misc.broadcast import broadcast
from tgbot.misc.utils import (
    Map,
    clear_state_data_startswith,
    humanize_time,
    check_buttons_texts,
    check_buttons_links,
)


async def admin_start(m: Message, texts: Map):
    """Admin start command handler"""
    logger.info(f"Admin {m.from_user.id} sent admin command")
    await m.reply(texts.admin.hi)


async def admin_stats(m: Message, db_session: AsyncSession, texts: Map):
    """Admin stats command handler"""
    logger.info(f"Admin {m.from_user.id} requested stats")
    count = await TGUser.users_count(db_session)
    await m.reply(texts.admin.total_users.format(count=count))


async def admin_broadcast(m: Message, texts: Map, state: FSMContext):
    """Admin broadcast command handler"""
    logger.info(f"Admin {m.from_user.id} sent broadcast command")
    await state.reset_state(with_data=False)
    # clear all states data which starts with "broadcast"
    await clear_state_data_startswith(state, "broadcast")

    await m.reply(
        texts.admin.broadcast_choose_language,
        reply_markup=await inline.admin_broadcast_choose_lang(texts),
    )


async def admin_broadcast_lang_choosen(
    cb: CallbackQuery, callback_data: dict, texts: Map, state: FSMContext
):
    """Admin broadcast language choosen"""
    await state.reset_state(with_data=False)
    await clear_state_data_startswith(state, "broadcast")

    code = callback_data.get("lang_code")
    await state.update_data(broadcast_lang_code=code)
    logger.info(
        f"Admin {cb.from_user.id} choosed language for broadcast: {code}"
    )
    await cb.message.edit_text(
        texts.admin.broadcast_send_message.format(lang=str(code).title()),
        reply_markup=await inline.admin_broadcast_cancel_keyboard(texts),
    )
    await cb.answer()
    await AdminBroadcast.wait_message.set()


async def admin_broadcast_message_received(
    m: Message, db_session: AsyncSession, texts: Map, state: FSMContext
):
    """Admin broadcast message received

    Single forwarded message, text, photo, video, audio, or photo/video/audio with caption is allowed.
    Media group is not allowed.
    All other types of messages are not allowed.

    Formatting of message is saved.
    """
    logger.info(f"Admin {m.from_user.id} sent message for broadcast")
    if (
        not m.content_type
        in [
            "text",
            "photo",
            "video",
        ]
        or m.media_group_id
    ):
        logger.info(
            f"Admin {m.from_user.id} sent invalid message for broadcast. "
            f"Type: {m.content_type}, Media group: {m.media_group_id}"
        )
        await m.reply(texts.admin.broadcast_not_allowed)
        return

    await state.update_data(broadcast_message=m.to_python())
    if m.is_forward():
        logger.info(f"Admin {m.from_user.id} forwarded message for broadcast")

        data = await state.get_data()
        receivers = await TGUser.get_users_count_by_lang_code(
            db_session, data.get("broadcast_lang_code")
        )
        await m.reply(
            text=texts.admin.broadcast_confirm.format(
                count=receivers,
                lang=str(data.get("broadcast_lang_code")).title(),
                time=await humanize_time(receivers * 0.034, texts),
            ),
            reply_markup=await inline.admin_broadcast_confirm_keyboard(texts),
        )
        await AdminBroadcast.wait_confirm.set()
        return

    else:
        logger.info(
            f"Admin {m.from_user.id} sent message for broadcast yourself"
        )
        await m.reply(
            text=texts.admin.broadcast_want_button,
            reply_markup=await inline.admin_broadcast_button_keyboard(texts),
        )

    await AdminBroadcast.wait_buttons.set()


async def admin_broadcast_want_buttons(
    cb: CallbackQuery, texts: Map, state: FSMContext
):
    """Admin broadcast want buttons"""
    logger.info(f"Admin {cb.from_user.id} want buttons for broadcast")
    await state.update_data(broadcast_want_buttons=True)
    await cb.message.edit_text(
        text=texts.admin.broadcast_send_buttons_texts,
        reply_markup=await inline.admin_broadcast_cancel_keyboard(texts),
    )
    await AdminBroadcast.wait_buttons_texts.set()
    await cb.answer()


async def admin_broadcast_not_want_buttons(
    m: CallbackQuery, db_session: AsyncSession, texts: Map, state: FSMContext
):
    """Admin broadcast do not want buttons"""
    logger.info(f"Admin {m.from_user.id} don't want buttons for broadcast")

    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")
    if isinstance(broadcast_message, dict):
        broadcast_message = Message.to_object(broadcast_message)

    preview = await broadcast_message.send_copy(m.from_user.id)

    await m.bot.send_message(
        chat_id=m.from_user.id,
        text=texts.admin.broadcast_preview,
        reply_to_message_id=preview.message_id,
    )
    await asyncio.sleep(2)

    receivers = await TGUser.get_users_count_by_lang_code(
        db_session, data.get("broadcast_lang_code")
    )
    await m.message.answer(
        text=texts.admin.broadcast_confirm.format(
            count=receivers,
            lang=str(data.get("broadcast_lang_code")).title(),
            time=await humanize_time(receivers * 0.034, texts),
        ),
        reply_markup=await inline.admin_broadcast_confirm_keyboard(texts),
    )
    await AdminBroadcast.wait_confirm.set()


async def admin_broadcast_sent_buttons_texts(
    m: Message, texts: Map, state: FSMContext
):
    """Admin broadcast sent buttons texts"""
    logger.info(f"Admin {m.from_user.id} sent buttons texts for broadcast")
    if not await check_buttons_texts(m.text) or len(m.text.split("\n")) > 10:
        logger.info(f"Admin {m.from_user.id} sent invalid buttons texts")
        await m.reply(texts.admin.broadcast_buttons_texts_invalid)
        return

    await state.update_data(broadcast_buttons_texts=m.text)
    await m.reply(
        text=texts.admin.broadcast_send_buttons_links,
        reply_markup=await inline.admin_broadcast_cancel_keyboard(texts),
    )
    await AdminBroadcast.wait_buttons_links.set()


async def admin_broadcast_sent_buttons_links(
    m: Message, db_session: AsyncSession, texts: Map, state: FSMContext
):
    """Admin broadcast sent buttons links"""
    logger.info(f"Admin {m.from_user.id} sent buttons links for broadcast")
    data = await state.get_data()
    if not await check_buttons_links(
        m.text, data.get("broadcast_buttons_texts")
    ):
        logger.info(f"Admin {m.from_user.id} sent invalid buttons links")
        await m.reply(texts.admin.broadcast_buttons_links_invalid)
        return

    await state.update_data(broadcast_buttons_links=m.text)

    data = await state.get_data()  # get updated data
    broadcast_message = data.get("broadcast_message")
    if isinstance(broadcast_message, dict):
        broadcast_message = Message.to_object(broadcast_message)

    btns = await inline.generate_broadcast_buttons(data)
    await state.update_data(broadcast_buttons_json=btns.to_python())

    preview = await broadcast_message.send_copy(
        m.from_user.id, reply_markup=btns
    )

    await m.bot.send_message(
        chat_id=m.from_user.id,
        text=texts.admin.broadcast_preview,
        reply_to_message_id=preview.message_id,
    )
    await asyncio.sleep(2)

    receivers = await TGUser.get_users_count_by_lang_code(
        db_session, data.get("broadcast_lang_code")
    )
    await m.answer(
        text=texts.admin.broadcast_confirm.format(
            count=receivers,
            lang=str(data.get("broadcast_lang_code")).title(),
            time=await humanize_time(receivers * 0.034, texts),
        ),
        reply_markup=await inline.admin_broadcast_confirm_keyboard(texts),
    )
    await AdminBroadcast.wait_confirm.set()


async def admin_broadcast_confirm(
    cb: CallbackQuery, db_session: AsyncSession, texts: Map, state: FSMContext
):
    """Admin broadcast confirm"""
    logger.info(f"Admin {cb.from_user.id} confirmed broadcast")

    await state.reset_state(with_data=False)
    await cb.message.edit_text(texts.admin.broadcast_started, reply_markup="")

    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")
    receivers = await TGUser.get_users_by_lang_code(
        db_session, data.get("broadcast_lang_code")
    )
    if isinstance(broadcast_message, dict):
        broadcast_message = Message.to_object(broadcast_message)

    if not broadcast_message.is_forward():
        if data.get("broadcast_want_buttons"):
            broadcast_message.reply_markup = (
                inline.InlineKeyboardMarkup().to_object(
                    data.get("broadcast_buttons_json")
                )
            )

    logger.info(
        f"Admin {cb.from_user.id} started broadcast:\nMessage: {broadcast_message.to_python()}"
    )
    await broadcast(
        broadcast_message,
        receivers,
        is_forward=bool(broadcast_message.is_forward()),
    )

    await clear_state_data_startswith(state, "broadcast")

    await cb.answer()


async def admin_broadcast_cancel(
    cb: CallbackQuery, texts: Map, state: FSMContext
):
    """Admin broadcast cancel"""
    logger.info(f"Admin {cb.from_user.id} canceled broadcast")
    if await state.get_state() not in AdminBroadcast.states_names:
        logger.info(f"Admin {cb.from_user.id} not in broadcast state")
        await cb.answer(text=texts.admin.not_in_broadcast)
        return

    await state.reset_state(with_data=False)
    await clear_state_data_startswith(state, "broadcast")
    await cb.message.edit_text(texts.admin.broadcast_canceled, reply_markup="")
    await cb.answer()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands=["admin"],
        state="*",
        is_admin=True,
        chat_type="private",
    )
    dp.register_message_handler(
        admin_stats,
        commands=["stats"],
        state="*",
        is_admin=True,
        chat_type="private",
    )
    dp.register_message_handler(
        admin_broadcast,
        commands=["broadcast"],
        state="*",
        is_admin=True,
        chat_type="private",
    )
    dp.register_callback_query_handler(
        admin_broadcast_lang_choosen,
        inline.cd_choose_lang_broadcast.filter(),
        state="*",
        is_admin=True,
        chat_type="private",
    )
    dp.register_message_handler(
        admin_broadcast_message_received,
        state=AdminBroadcast.wait_message,
        is_admin=True,
        chat_type="private",
        content_types=ContentTypes.ANY,
    )
    dp.register_callback_query_handler(
        admin_broadcast_want_buttons,
        text="broadcast_button_yes",
        state=AdminBroadcast.wait_buttons,
        is_admin=True,
        chat_type="private",
    )
    dp.register_callback_query_handler(
        admin_broadcast_not_want_buttons,
        text="broadcast_button_no",
        state=AdminBroadcast.wait_buttons,
        is_admin=True,
        chat_type="private",
    )
    dp.register_message_handler(
        admin_broadcast_sent_buttons_texts,
        state=AdminBroadcast.wait_buttons_texts,
        is_admin=True,
        chat_type="private",
        content_types=ContentTypes.TEXT,
    )
    dp.register_message_handler(
        admin_broadcast_sent_buttons_links,
        state=AdminBroadcast.wait_buttons_links,
        is_admin=True,
        chat_type="private",
        content_types=ContentTypes.TEXT,
    )
    dp.register_callback_query_handler(
        admin_broadcast_confirm,
        state=AdminBroadcast.wait_confirm,
        text="broadcast_confirm",
        is_admin=True,
        chat_type="private",
    )
    dp.register_callback_query_handler(
        admin_broadcast_cancel,
        text="broadcast_cancel",
        state="*",
        is_admin=True,
        chat_type="private",
    )
