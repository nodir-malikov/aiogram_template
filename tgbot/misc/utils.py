import logging
import asyncio
import validators

from typing import Dict, List, Optional, Union

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils import exceptions
from aiogram.dispatcher import FSMContext

from aiogram_broadcaster.base import BaseBroadcaster
from aiogram_broadcaster.types import ChatsType, ChatIdType


async def clear_state_data_startswith(
    state: FSMContext, startswith: str
) -> None:
    """Clear state data which starts with `startswith`"""
    data = await state.get_data()
    await state.set_data(
        {k: v for k, v in data.items() if not k.startswith(startswith)}
    )


async def find_button_text(buttons: list, callback_data: str) -> str:
    """Find button text from callback keyboard by callback_data"""
    for button in buttons:
        if isinstance(button, list):
            text = await find_button_text(button, callback_data)
            if text:
                return text
        elif (
            isinstance(button, InlineKeyboardButton)
            and button.callback_data == callback_data
        ):
            return button.text
    return ""


async def humanize_time(seconds, texts: "Map"):
    """Convert seconds to human readable format"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months, weeks = divmod(weeks, 4)
    years, months = divmod(months, 12)

    years = int(years)
    months = int(months)
    weeks = int(weeks)
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    time_parts = []
    if years > 0:
        time_parts.append(
            f"{years} {texts.service.year if years == 1 else texts.service.years}"
        )
    if months > 0:
        time_parts.append(
            f"{months} {texts.service.month if months == 1 else texts.service.months}"
        )
    if weeks > 0:
        time_parts.append(
            f"{weeks} {texts.service.week if weeks == 1 else texts.service.weeks}"
        )
    if days > 0:
        time_parts.append(
            f"{days} {texts.service.day if days == 1 else texts.service.days}"
        )
    if hours > 0:
        time_parts.append(
            f"{hours} {texts.service.hour if hours == 1 else texts.service.hour}"
        )
    if minutes > 0:
        time_parts.append(
            f"{minutes} {texts.service.minute if minutes == 1 else texts.service.minutes}"
        )
    if seconds > 0:
        time_parts.append(
            f"{seconds} {texts.service.second if seconds == 1 else texts.service.seconds}"
        )

    return ", ".join(time_parts) if time_parts else f"0 {texts.service.second}"


async def check_buttons_texts(buttons: str) -> bool:
    """Check if buttons texts are not too long"""
    buttons = buttons.split("\n")
    for button in buttons:
        if len(button) > 64 or len(button) < 1:
            return False
    return True


async def check_buttons_links(links: str, buttons: str) -> bool:
    """Check if buttons links are valid"""
    links = links.split("\n")
    buttons = buttons.split("\n")
    if not len(links) == len(buttons):
        return False

    for link in links:
        if not validators.url(link) or len(link) < 1:
            return False
    return True


class Map(dict):
    """Adds the ability to select dict elements using a dot"""

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
                    if isinstance(v, dict):
                        self[k] = Map(v)

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class ForwardMessageBroadcaster(BaseBroadcaster):
    """Message broadcaster for forwarding messages"""

    def __init__(
        self,
        chats: ChatsType,
        from_chat_id: ChatIdType,
        message_id: Union[str, int],
        kwargs: Optional[Dict] = None,
        disable_notification: Optional[bool] = None,
        bot: Optional[Bot] = None,
        bot_token: Optional[str] = None,
        timeout: float = 0.05,
        logger=__name__,
    ):
        self._setup_chats(chats, kwargs)
        self.from_chat_id = from_chat_id
        self.message_id = message_id
        self.disable_notification = disable_notification
        self._setup_bot(bot, bot_token)
        self.timeout = timeout

        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)

        self.logger = logger

        self._id: int = len(BaseBroadcaster.running)
        self._is_running: bool = False
        self._successful: List[Dict] = []
        self._failure: List[Dict] = []

    async def send(
        self,
        chat_id: ChatIdType,
        from_chat_id: ChatIdType,
        message_id: Union[str, int],
        chat_args: Dict,
    ) -> bool:
        try:
            await self.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                disable_notification=self.disable_notification,
            )
        except exceptions.RetryAfter as e:
            self.logger.debug(
                f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
            )
            await asyncio.sleep(e.timeout)
            return await self.send(chat_id, chat_args)  # Recursive call
        except (
            exceptions.BotBlocked,
            exceptions.ChatNotFound,
            exceptions.UserDeactivated,
            exceptions.ChatNotFound,
        ) as e:
            self.logger.debug(f"Target [ID:{chat_id}]: {e.match}")
        except exceptions.TelegramAPIError:
            self.logger.exception(f"Target [ID:{chat_id}]: failed")
        else:
            self.logger.debug(f"Target [ID:{chat_id}]: success")
            return True
        return False

    async def _start_broadcast(self) -> None:
        for chat in self.chats:
            logging.info(str(self))
            chat_id, chat_args = self._parse_args(chat)
            if await self.send(
                chat_id=chat_id,
                from_chat_id=self.from_chat_id,
                message_id=self.message_id,
                chat_args=chat_args,
            ):
                self._successful.append(chat)
            else:
                self._failure.append(chat)
            await asyncio.sleep(self.timeout)
