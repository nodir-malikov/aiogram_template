import configparser
from dataclasses import dataclass


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
    admin_id: list
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


def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes")


def cast_str_list(value: str) -> list:
    return value.replace(" ", "").split(",")


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            admin_id=cast_str_list(tg_bot["admin_id"]),
            use_redis=cast_bool(tg_bot.get("use_redis")),
            redis_host=tg_bot.get("redis_host"),
            redis_port=int(tg_bot.get("redis_port")),
            redis_db=int(tg_bot.get("redis_db")),
            redis_password=tg_bot.get("redis_password"),
            redis_prefix=tg_bot.get("redis_prefix")
        ),
        db=DbConfig(**config["db"]),
    )
