from typing import Union

from loguru import logger

from aiogram import md
from aiogram.types import Message
from aiogram_broadcaster import MessageBroadcaster, TextBroadcaster

from tgbot.misc.utils import ForwardMessageBroadcaster


async def get_mention(chat_id, full_name):
    """Get mention for user"""
    return md.hlink(full_name, f"tg://user?id={chat_id}")


async def broadcast(
    message: Union[str, Message], users: list, is_forward: bool = False
):
    """Broadcast message to users

    message: dict of aiogram.types.Message object which converted to dict via `to_python()` method
    users: list of tgbot.models.users.User object
    """
    logger.success(f"{len(users)} users found for broadcast")
    user_data_list = []
    for user in users:
        user_data = {"chat_id": user.telegram_id}
        if not is_forward:
            user_data["mention"] = await get_mention(
                user.telegram_id,
                f"{user.firstname} {user.lastname if user.lastname else ''}",
            )
        user_data_list.append(user_data)

    try:
        await _start_broadcast(message, user_data_list, is_forward)
    except Exception as e:
        logger.error(f"Error while broadcasting: {e}")
        logger.exception(e)


async def _start_broadcast(
    message: Union[str, Message], users: list, is_forward: bool = False
) -> None:
    """Private method for starting broadcast

    The API will not allow bulk notifications to more than ~30 users per second,
    if you go over that, you'll start getting 429 errors.
    Therefore we need timeout 0.034 seconds below.
    1 sec / 0.034 sec = 29,4 users per second
    https://core.telegram.org/bots/faq#broadcasting-to-users
    """
    if isinstance(message, Message):
        if is_forward:
            await ForwardMessageBroadcaster(
                chats=users,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                timeout=0.034,
            ).run()
            return

        await MessageBroadcaster(
            chats=users, message=message, timeout=0.034
        ).run()
        return

    if isinstance(message, str):
        await TextBroadcaster(chats=users, text=message, timeout=0.034).run()
        return
