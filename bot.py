import asyncio
import os

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault

from tgbot.config import load_config
from tgbot.filters.role import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.middlewares.throtling import ThrottlingMiddleware
from tgbot.services.database import create_db_session


os.makedirs("logs", exist_ok=True)

logger.add(
    sink="logs/bot.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{file}:{line} {message}",
    rotation="1 day",
    retention="15 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
    enqueue=True,
    catch=True,
    level="DEBUG",
)


def register_all_middlewares(dp):
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Need help?"),
        BotCommand(command="admin", description="Admin panel")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    logger.success("Starting bot")
    config = load_config("bot.ini")

    if config.tg_bot.use_redis:
        storage = RedisStorage2(host=config.tg_bot.redis_host,
                                port=config.tg_bot.redis_port,
                                db=config.tg_bot.redis_db,
                                password=config.tg_bot.redis_password,
                                prefix=config.tg_bot.redis_prefix)
    else:
        storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    await set_bot_commands(bot)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.new_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
