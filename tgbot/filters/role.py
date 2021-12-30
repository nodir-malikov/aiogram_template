import typing

from loguru import logger

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return True

        config: Config = obj.bot.get('config')
        if str(obj.from_user.id) in config.tg_bot.admin_id:
            return True
        else:
            logger.warning(
                f'AdminFilter -> User: {obj.from_user.id} is not admin'
            )
            return False
