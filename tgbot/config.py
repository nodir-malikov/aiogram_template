import configparser
from dataclasses import dataclass
from tkinter import getboolean


@dataclass
class DbConfig:
    host: str
    port: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    skip_updates: bool
    admins_id: list
    use_redis: bool
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str
    redis_prefix: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def cast_str_list(value: str) -> list:
    return value.replace(" ", "").split(",")


def cast_bool(value: str) -> bool:
    return value.lower().strip() in ["true", "t", "1", "yes", "y", "on"]


def load_config(path: str):
    """Loads config from file"""
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            skip_updates=cast_bool(tg_bot["skip_updates"]),
            admins_id=cast_str_list(tg_bot["admins_id"]),
            use_redis=cast_bool(tg_bot.get("use_redis")),
            redis_host=tg_bot.get("redis_host"),
            redis_port=tg_bot.getint("redis_port"),
            redis_db=tg_bot.getint("redis_db"),
            redis_password=tg_bot.get("redis_password"),
            redis_prefix=tg_bot.get("redis_prefix")
        ),
        db=DbConfig(**config["db"]),
    )
