from typing import List
from loguru import logger

from aiogram import md
from aiogram_broadcaster import MessageBroadcaster
from aiogram import types

from tgbot.models.users import User


async def get_mention(chat_id, full_name):
    return md.hlink(full_name, f'tg://user?id={chat_id}')


async def prepare_broadcast(m: dict, db):
    msg = types.Message
    msg = msg.to_object(m)
    all_users = await User.get_all_users(db)
    logger.success(f'{len(all_users)} users found for broadcast')
    users = [
        {'chat_id': i.telegram_id,
         'mention': await get_mention(i.telegram_id, i.fullname)} for i in all_users
    ]
    try:
        await start_broadcast(msg, users)
    except Exception as e:
        logger.error(f"Error while broadcasting: {e}")


async def start_broadcast(msg: types.Message, users: List):
    await MessageBroadcaster(chats=users, message=msg, timeout=0.034).run()
