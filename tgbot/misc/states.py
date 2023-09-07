from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminBroadcast(StatesGroup):
    """Admin broadcast states group"""

    wait_message = State()
    wait_buttons = State()
    wait_buttons_texts = State()
    wait_buttons_links = State()
    wait_confirm = State()
