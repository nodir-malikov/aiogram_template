import re

from aiogram.types import InlineKeyboardButton


async def onlydigits(text: str) -> str:
    """Remove all non-digits from string"""
    return re.sub(r'[^\d]', '', text)


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
