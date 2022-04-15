from loguru import logger

from aiogram import md
from aiogram.types import Message
from aiogram_broadcaster import MessageBroadcaster


async def get_mention(chat_id, full_name):
    """
    Get mention for user
    """
    return md.hlink(full_name, f'tg://user?id={chat_id}')


async def broadcast(message: dict, users: list):
    """Broadcast message to users

    message: dict of aiogram.types.Message object which converted to dict via `to_python()` method
    users: list of tgbot.models.users.User object
    """

    msg = Message
    msg = msg.to_object(message)
    logger.success(f'{len(users)} users found for broadcast')
    users = [
        {
            'chat_id': user.telegram_id,
            'mention': await get_mention(user.telegram_id, user.fullname)
        } for user in users
    ]
    try:
        await _start_broadcast(msg, users)
    except Exception as e:
        logger.error(f"Error while broadcasting: {e}")
        raise e


async def _start_broadcast(message: Message, users: list):
    """Private method for starting broadcast

    The API will not allow bulk notifications to more than ~30 users per second,
    if you go over that, you'll start getting 429 errors.
    Therefore we need timeout 0.034 seconds below.
    1 sec / 0.034 sec = 29,4 users per second
    https://core.telegram.org/bots/faq#broadcasting-to-users
    """

    await MessageBroadcaster(chats=users, message=message, timeout=0.034).run()
