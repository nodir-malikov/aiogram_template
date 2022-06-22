import os
import asyncio

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault

from tgbot.config import load_config
from tgbot.filters import role, reply_kb
from tgbot.middlewares.throtling import ThrottlingMiddleware
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.services.database import create_db_session
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user


def init_logger():
    os.makedirs("logs", exist_ok=True)

    logger.add(
        sink="logs/bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{file}:{line} {message}",
        rotation="30 day",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,
        level="DEBUG",
    )

    logger.success("Logger initialized")


def register_all_middlewares(dp):
    dp.setup_middleware(ThrottlingMiddleware())
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(TranslationMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(role.AdminFilter)
    dp.filters_factory.bind(reply_kb.CloseBtn)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)


async def set_bot_commands(bot: Bot):
    """Initialize bot commands for bot to preview them when typing slash "/""""
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="me", description="Your info in DB"),
        BotCommand(command="phone", description="Add / Update phone number"),
        BotCommand(command="lang", description="Choose language"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def start_polling(dp, skip_updates=False):
    if skip_updates:
        await dp.skip_updates()
    await dp.start_polling()


async def close_all(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.session.close()


async def main():
    init_logger()
    logger.success("Starting bot")
    # load config from bot.ini file
    config = load_config("bot.ini")

    if config.tg_bot.use_redis:
        # use redis storage for FSM
        storage = RedisStorage2(host=config.tg_bot.redis_host,
                                port=config.tg_bot.redis_port,
                                db=config.tg_bot.redis_db,
                                password=config.tg_bot.redis_password,
                                prefix=config.tg_bot.redis_prefix)
    else:
        # use memory storage for FSM
        storage = MemoryStorage()

    # create bot instance
    # default parse_mode is HTML
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    # create dispatcher instance with storage
    dp = Dispatcher(bot, storage=storage)

    # adding config and db session to bot data
    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    await set_bot_commands(bot)

    # start
    try:
        await start_polling(dp, skip_updates=config.tg_bot.skip_updates)
    finally:
        await close_all(dp)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
