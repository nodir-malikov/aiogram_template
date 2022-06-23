import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.misc.utils import Map


class CloseBtn(BoundFilter):
    """Filter for close ReplyKeyboardButton"""
    key = 'is_close_btn'

    def __init__(self, is_close_btn: typing.Optional[bool] = None):
        self.is_close_btn = is_close_btn

    async def check(self, obj):
        if self.is_close_btn is None:
            return False

        # get data from context
        texts: Map = ctx_data.get()['texts']

        if obj.text == texts.user.kb.reply.close:
            return True

        return False
