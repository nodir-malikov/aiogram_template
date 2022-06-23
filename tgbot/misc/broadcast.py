from typing import Union

from loguru import logger

from aiogram import md
from aiogram.types import Message
from aiogram_broadcaster import MessageBroadcaster, TextBroadcaster


async def get_mention(chat_id, full_name):
    """Get mention for user"""
    return md.hlink(full_name, f'tg://user?id={chat_id}')


async def broadcast(message: Union[str, Message], users: list):
    """Broadcast message to users

    message: dict of aiogram.types.Message object which converted to dict via `to_python()` method
    users: list of tgbot.models.users.User object
    """
    logger.success(f'{len(users)} users found for broadcast')
    users = [
        {
            'chat_id': user.telegram_id,
            'mention': await get_mention(
                user.telegram_id,
                f"{user.firstname} {user.lastname if user.lastname else ''}")
        } for user in users
    ]
    try:
        await _start_broadcast(message, users)
    except Exception as e:
        logger.error(f"Error while broadcasting: {e}")
        raise e


async def _start_broadcast(message: Union[str, Message], users: list) -> None:
    """Private method for starting broadcast

    The API will not allow bulk notifications to more than ~30 users per second,
    if you go over that, you'll start getting 429 errors.
    Therefore we need timeout 0.034 seconds below.
    1 sec / 0.034 sec = 29,4 users per second
    https://core.telegram.org/bots/faq#broadcasting-to-users
    """
    if isinstance(message, Message):
        await MessageBroadcaster(chats=users, message=message, timeout=0.034).run()
        return

    if isinstance(message, str):
        await TextBroadcaster(chats=users, text=message, timeout=0.034).run()
        return
