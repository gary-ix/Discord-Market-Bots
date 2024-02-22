import asyncio
import json
import os
import threading
from typing import Any

print(f"\n\n\n\n{os.getcwd()}")

import redis
from bot import start_discord_bots, update_bots


def initialize_bots() -> None:
    """Loads env and starts discord bots"""
    thread: threading.Thread = threading.Thread(target=start_discord_bots)
    thread.start()


def initalize_redis() -> redis.Redis:
    r: redis.Redis | None = redis.Redis.from_url(
        url=os.getenv(key="REDIS_URL", default="redis://localhost:6379")
    )

    if not r:
        raise Exception("REDIS IS NONE ERROR")

    return r


async def handle_redis_messages(r: redis.Redis) -> None:
    pubsub = r.pubsub()
    pubsub.subscribe("ticker_updates")

    for message in pubsub.listen():
        if (
            message["type"] == "message"
            and message["channel"].decode() == "ticker_updates"
        ):
            await update_bots(data=json.loads(message["data"].decode()))


async def main() -> None:
    initialize_bots()
    await handle_redis_messages(r=initalize_redis())


if __name__ == "__main__":
    asyncio.run(main=main())
