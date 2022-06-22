import os
import yaml

from pathlib import Path

from loguru import logger

from aiogram.types import Message, CallbackQuery, User as TgUser
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.models.users import User as DbUser
from tgbot.misc.utils import Map


def _load_translations(path: str = None) -> dict:
    if not path:
        path = os.path.join(os.getcwd(), "tgbot", "translations", "texts.yml")

    try:
        return yaml.safe_load(Path(os.path.join(path)).read_text(encoding='utf-8'))

    except Exception as e:
        logger.error(f"Error while parsing translations in YAML file: {path}")
        raise e


class TranslationMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.texts: dict = _load_translations()
        super().__init__()

    async def reload_translations(self, obj, data, code: str = None) -> Map:
        if not code:
            db_user: DbUser = data.get("db_user")
            telegram_user: TgUser = obj.from_user
            lang = telegram_user.language_code
            if db_user:
                if db_user.lang_code:
                    lang = db_user.lang_code
        else:
            lang = code
        # `texts` is a name of var passed to handler
        texts = Map(self.texts.get(lang, {}))

        return texts

    async def on_pre_process_message(self, obj: Message, data: dict) -> Map:
        data["texts"] = await self.reload_translations(obj, data)

    async def on_pre_process_callback_query(self, obj: CallbackQuery, data: dict) -> Map:
        data["texts"] = await self.reload_translations(obj, data)