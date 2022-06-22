from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tgbot.models.users import User


class DbMiddleware(LifetimeControllerMiddleware):
    """Middleware for adding user into DB if he/she not exists"""

    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        db_session = obj.bot.get('db')
        telegram_user: types.User = obj.from_user
        user = await User.get_user(db_session=db_session, telegram_id=telegram_user.id)
        if not user:
            await User.add_user(
                db_session=db_session,
                telegram_id=telegram_user.id,
                firstname=telegram_user.first_name,
                lastname=telegram_user.last_name,
                username=telegram_user.username,
                lang_code=telegram_user.language_code,
            )

        data['db_session'] = db_session  # add user object to data
        data['db_user'] = user  # add user object to data
