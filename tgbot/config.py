import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    skip_updates: bool
    admins_id: list
    use_webhook: bool
    use_redis: bool
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str
    redis_prefix: str
    global_timeout: int = 15


@dataclass
class WebhookConfig:
    host: str
    port: str
    path: str
    webapp_host: str
    webapp_port: str


@dataclass
class DbConfig:
    host: str
    port: str
    password: str
    user: str
    database: str


@dataclass
class Config:
    tg_bot: TgBot
    webhook: WebhookConfig
    db: DbConfig


def cast_str_list(value: str) -> list:
    return value.replace(" ", "").split(",")


def cast_bool(value: str) -> bool:
    return value.lower().strip() in ["true", "t", "1", "yes", "y", "on"]


def load_config(path: str) -> Config:
    """Loads config from file"""
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            skip_updates=cast_bool(tg_bot["skip_updates"]),
            admins_id=cast_str_list(tg_bot["admins_id"]),
            use_webhook=cast_bool(tg_bot.get("use_webhook")),
            use_redis=cast_bool(tg_bot.get("use_redis")),
            redis_host=tg_bot.get("redis_host"),
            redis_port=tg_bot.getint("redis_port"),
            redis_db=tg_bot.getint("redis_db"),
            redis_password=tg_bot.get("redis_password"),
            redis_prefix=tg_bot.get("redis_prefix"),
            global_timeout=tg_bot.getint("global_timeout"),
        ),
        webhook=WebhookConfig(**config["webhook"]),
        db=DbConfig(**config["db"]),
    )
