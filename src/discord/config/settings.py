"""Module for vars"""

# imports
import json
import os

from dotenv import load_dotenv

# global vars
setup_path: str = os.path.join(os.getcwd(), ".setup")


def get_bot_info() -> list[dict]:
    """
    Load bot information from a JSON file.

    Returns:
        list[dict]: A list of dictionaries containing bot information.
    """

    file_path: str = os.path.join(setup_path, ".bots.json")
    with open(file=file_path, mode="r", encoding="utf-8") as json_file:
        data: dict = json.load(fp=json_file)
        thread_arguments: list[dict] = data.get("bots", [])
        return thread_arguments


load_dotenv(dotenv_path=os.path.join(setup_path, ".env"))
bot_info: list[dict] = get_bot_info()
guild_id: int = int(os.getenv(key="GUILD_ID", default="0"))
ticker_green: int = int(os.getenv(key="GREEN_ROLE_ID", default="0"))
ticker_red: int = int(os.getenv(key="RED_ROLE_ID", default="0"))
