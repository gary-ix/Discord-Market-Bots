"""Module for loading bot/server information."""

import json

# import logging
import os

from dotenv import load_dotenv

# from logging.config import dictConfig
# from logging.handlers import TimedRotatingFileHandler  # pylint:disable = W0611

print(os.path.join(os.getcwd(), ".setup"))
# setup_path: str = os.path.join(os.getcwd(), "..", "..", ".setup")
setup_path: str = os.path.join(os.getcwd(), ".setup")
# /home/bot_manager/code/Discord-Ticker-Bots/.setup/.bots.json


def loadbot_info() -> list[dict]:
    """
    Load bot information from a JSON file.

    Returns:
        list[dict]: A list of dictionaries containing bot information.
    """
    bot_info_path: str = os.path.join(setup_path, ".bots.json")

    with open(file=bot_info_path, mode="r", encoding="utf-8") as json_file:
        data: dict = json.load(fp=json_file)
        thread_arguments: list[dict] = data.get("bots", [])
        return thread_arguments


load_dotenv(os.path.join(setup_path, ".env"))
bot_info: list[dict] = loadbot_info()
guild_id: int = int(os.getenv(key="GUILD_ID", default="0"))
ticker_green: int = int(os.getenv(key="GREEN_ROLE_ID", default="0"))
ticker_red: int = int(os.getenv(key="RED_ROLE_ID", default="0"))

# # logger
# LOGGING_CONFIG = {
#     "version": 1,
#     "disabled_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": (
#                 "\n\n%(asctime)s"
#                 "\n%(levelname)s - %(name)s"
#                 "\n%(filename)s>'%(funcName)s'>%(lineno)d"
#                 "\n%(message)s"
#             ),
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#     },
#     "handlers": {
#         "file": {
#             "level": "INFO",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "./logs/bot.log",
#             "when": "midnight",
#             "interval": 1,
#             "backupCount": 14,
#             "formatter": "verbose",
#         },
#         "error_file": {
#             "level": "ERROR",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "./logs/bot_error.log",
#             "when": "midnight",
#             "interval": 1,
#             "backupCount": 14,
#             "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "Bot": {
#             "handlers": ["file", "error_file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "discord": {
#             "handlers": ["file", "error_file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# }

# dictConfig(config=LOGGING_CONFIG)
# bot_log: logging.Logger = logging.getLogger(name="Bot")
