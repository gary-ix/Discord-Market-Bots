"""Python Flask Server"""

# standard imports
import json
import os

# custom imports
import config.settings
import redis
from flask import Flask, abort, request


def initialize_app() -> tuple[redis.Redis, str]:
    r: redis.Redis | None = redis.Redis.from_url(
        url=os.getenv(key="REDIS_URL", default="redis://localhost:6379")
    )

    if not r:
        raise Exception("REDIS IS NONE ERROR")

    webhook_secret: str = os.getenv(key="WEBHOOK_SECRET", default="")
    if webhook_secret == "":
        raise Exception("WEBHOOK SECRET IS NONE")

    return r, webhook_secret


r, webhook_secret = initialize_app()
app: Flask = Flask(import_name=__name__)


@app.before_request
def auth() -> None:
    """Authorization middleware"""
    if request.json and request.json.get("Authorization") == webhook_secret:
        return
    abort(code=401)


@app.route(rule="/heartbeat", methods=["GET"])
def heartbeat() -> str:
    """To quickly check if server is still alive"""
    r.publish(channel="heartbeat", message="Alive")
    return "Alive"


@app.route(rule="/6YVpcd3QEwkdADX51KG4czHLd3NVcFs9", methods=["POST"])
async def ticker_data() -> tuple[str, int]:
    """Handle incoming ticker data webhook"""
    if request.json:
        r.publish(channel="ticker_updates", message=json.dumps(obj=request.json))
    return "Webhook received successfully", 200
