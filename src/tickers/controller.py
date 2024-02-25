import asyncio
import json
import logging
import os
import threading
from typing import Any

import redis
from bot import BotManager
from config.utils import create_controller_logger


class BotController:
    def __init__(self) -> None:
        self.logger: logging.Logger = create_controller_logger()
        self.bot_manager: BotManager = BotManager()
        self.redis: redis.Redis = self.initialize_redis()

        self.logger.info(msg="Bot Controller setup is complete")

    def initialize_redis(self) -> redis.Redis:
        r: redis.Redis | None = redis.Redis.from_url(
            url=os.getenv(key="REDIS_URL", default="redis://localhost:6379")
        )

        if not r:
            self.logger.critical(msg="REDIS IS NONE ERROR.")
            raise Exception("REDIS IS NONE ERROR.")

        if not r.ping():
            self.logger.critical(msg="COULD NOT CONNECT TO REDIS.")
            raise Exception("COULD NOT CONNECT TO REDIS.")

        self.logger.info(msg="Redis is ready.")
        return r

    async def redis_message_handler(self) -> None:
        pubsub = self.redis.pubsub()
        pubsub.subscribe("ticker_updates")

        for message in pubsub.listen():
            if (
                message["type"] == "message"
                and message["channel"].decode() == "ticker_updates"
            ):
                self.logger.info(msg="New ticker update message received")
                await self.bot_manager.update_bots(
                    data=json.loads(message["data"].decode())
                )

    async def start(self) -> None:
        thread = threading.Thread(target=self.bot_manager.start_bots)
        thread.start()
        await self.redis_message_handler()


if __name__ == "__main__":
    controller = BotController()
    asyncio.run(main=controller.start())
