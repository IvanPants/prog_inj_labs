from sys import stdout

from colorama import Back
from loguru import logger

from .settings_model import Settings


def get_config() -> Settings:
    config = Config()
    return config.settings


class Config:
    def __init__(self):
        config = {
            "debug_mode": True
        }

        settings = Settings(**config)  # validate model
        #
        db_string = (f'postgresql://{settings.postgres_user}:{settings.postgres_pass}@{settings.postgres_host}:'
                     f'{settings.postgres_port}/{settings.postgres_name}')
        # db_string = 'postgresql://postgres:12345@localhost:5432/user_db'

        # DATABASE_URL = 'postgresql://postgres:12345@localhost:5432/user_db'
        # db_string = 'postgres://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)

        # db_string = 'postgres://{}:{}@{}:{}/{}'.format(settings.postgres_user, settings.postgres_pass,
        #                                                settings.postgres_host, settings.postgres_port,
        #                                                settings.postgres_name)

        settings.postgres_str = db_string  # add to setting
        self.settings = settings  # add attribute


def logger_set_up(_settings: Settings):
    """Loguru set up"""
    logger.remove()  # this removes duplicates in the console if we use the custom log format
    logger.configure(extra={"object_id": "None"})  # Default values if not bind extra variable
    logger.level("HL", no=38, color=Back.MAGENTA, icon="🔺")
    logger.level(f"TRACE", color="<fg #1b7c80>")  # выставить цвет
    logger.level(f"SUCCESS", color="<bold><fg #2dd644>")  # выставить цвет

    logger.add(sink=stdout,
               format=_settings.log_format,
               colorize=True,
               enqueue=True,  # for better work of async
               level=1)  # mb backtrace=True?
