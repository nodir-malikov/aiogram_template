import os
import yaml

from pathlib import Path

from loguru import logger

from aiogram.types import Message, CallbackQuery, User as TgUser
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.models.models import TGUser as DbTGUser
from tgbot.misc.utils import Map


def _load_translations(path: str = None) -> dict:
    """Loads translations from yaml file"""
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
        """Reloads translations memory with other language code"""
        available_langs = self.texts.get('available_langs', [])
        if not code:
            db_user: DbTGUser = data.get("db_user")
            telegram_user: TgUser = obj.from_user
            lang = telegram_user.language_code
            if db_user and db_user.lang_code:
                lang = db_user.lang_code
        else:
            lang = code
        if lang not in available_langs:
            lang = available_langs[0]

        return Map(self.texts.get(lang, {}))

    async def on_pre_process_message(self, obj: Message, data: dict) -> Map:
        # `texts` is a name of var passed to handler
        # root
        data["texts_original"] = Map(self.texts)
        # only with choosen language
        data["texts"] = await self.reload_translations(obj, data)

    async def on_pre_process_callback_query(self, obj: CallbackQuery, data: dict) -> Map:
        data["texts_original"] = Map(self.texts)
        data["texts"] = await self.reload_translations(obj, data)
