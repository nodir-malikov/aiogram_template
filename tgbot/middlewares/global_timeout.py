from datetime import datetime, timedelta

from loguru import logger

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

from tgbot.config import Config
from tgbot.misc.utils import Map
from tgbot.middlewares.translate import TranslationMiddleware


class GlobalTimeoutMiddleware(BaseMiddleware):
    """
    Middleware for global timeout that cancels all handlers if user is on it.

    Set 'global_timeout' in FSMContext data with current time to activate.

    Timeout expires after 'global_timeout' + 'global_timeout' seconds in cfg.
    """

    async def on_pre_process_message(self, obj, *args):
        config: Config = obj.bot.get("config")
        timeout = config.tg_bot.global_timeout
        state: FSMContext = obj.bot.get("dp").current_state(
            chat=obj.from_user.id
        )
        data = await state.get_data()
        global_timeout = data.get("global_timeout")
        texts: Map = await TranslationMiddleware().reload_translations(
            obj, data
        )

        if not global_timeout:
            return True

        global_timeout = datetime.strptime(
            global_timeout, "%Y-%m-%d %H:%M:%S.%f"
        )

        until = global_timeout + timedelta(seconds=timeout)
        if until <= datetime.now():
            await state.update_data(global_timeout=None)
            return True

        timeout = (until - datetime.now()).seconds

        logger.warning(
            f"GlobalTimeoutMiddleware -> User: {obj.from_user.id} is on global timeout ({timeout}s left)."
        )
        await obj.answer(texts.service.global_timeout.format(timeout=timeout))
        raise CancelHandler()
