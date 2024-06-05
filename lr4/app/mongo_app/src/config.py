from sys import stdout

from colorama import Back
from loguru import logger

# from src.models.settings_model import Settings
from .models.settings_model import Settings

def get_config() -> Settings:
    config = Config()
    return config.settings


class Config:
    def __init__(self):
        config = {
            "debug_mode": True
        }
        self.settings = Settings(**config)  # validate model


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
