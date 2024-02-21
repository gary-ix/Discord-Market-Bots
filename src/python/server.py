"""Python Flask Server"""

import os
import threading

from bot import start_discord_bots, update_bots
from config import bot_log
from flask import Flask, abort, request


def startup() -> None:
    """Loads env and starts discord bots"""
    thread: threading.Thread = threading.Thread(target=start_discord_bots)
    thread.start()


startup()
app: Flask = Flask(import_name=__name__)


@app.before_request
def auth() -> None:
    """Authorization middleware"""
    webhook_secret: str = os.getenv(key="WEBHOOK_SECRET", default="")
    if request.json and request.json.get("Authorization") == webhook_secret:
        return
    abort(code=401)


@app.route(rule="/heartbeat", methods=["GET"])
def heartbeat() -> str:
    """To quickly check if server is still alive"""
    return "Alive"


@app.route(rule="/6YVpcd3QEwkdADX51KG4czHLd3NVcFs9", methods=["POST"])
async def receive_webhook() -> tuple[str, int]:
    """Handle incoming ticker data webhook"""
    if request.json:
        await update_bots(data=request.json)
    return "Webhook received successfully", 200
