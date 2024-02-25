"""Discord Bots"""

# standard imports
import logging
import threading

import discord
import requests

# custom imports
from config.settings import bot_list, green_bot_role, guild_id, red_bot_role
from config.utils import create_bot_logger
from discord.ui import Button, View

DISCORD_BOTS: dict = {}
BOT_LOGGERS: dict = {}
API_BASE_URL = "https://discord.com/api/v9/"


class DiscordBot:
    def __init__(self, bot_info, bot_logger) -> None:
        self.bot: dict = bot_info
        self.logger: logging.Logger = bot_logger
        self.client: discord.Client = discord.Client(
            intents=discord.Intents(messages=True)
        )
        self.setup_events()

    def setup_events(self) -> None:

        @self.client.event
        async def on_ready() -> None:
            if self.client.user:
                self.logger.debug(msg=f"{self.client.user.name} Bot ready!")
                DISCORD_BOTS[self.bot["botID"]] = self.client

        @self.client.event
        async def on_message(message) -> None:
            if self.client.user:
                if f"<@{self.client.user.id}>" in message.content:
                    await message.reply(
                        embed=await self.message_embed(), view=self.message_view()
                    )

    def run(self) -> None:
        self.client.run(
            token=self.bot["botToken"],
            root_logger=False,
            log_level=logging.ERROR,
            log_handler=self.logger.handlers[0] if self.logger.handlers else None,
            log_formatter=logging.Formatter(
                fmt=f"\n\n{self.bot['symbolNick']} - %(asctime)s\n%(levelname)s - %(name)s\n%(filename)s>'%(funcName)s'>%(lineno)d\n%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ),
        )

    async def message_embed(self) -> discord.Embed:

        def create_embed_fields(embed: discord.Embed, data: str) -> None:
            pairs: list[str] = [pair.strip() for pair in data.split(sep=",")]

            for pair in pairs:
                key, value = pair.split(sep="=")
                embed.add_field(name=f"**__{key}__**", value=value, inline=True)

        app_info: discord.AppInfo = await self.client.application_info()
        embed: discord.Embed = discord.Embed(
            color=self.client.user.accent_color if self.client.user else 0x000000,
        )
        create_embed_fields(embed=embed, data=app_info.description)

        return embed

    def message_view(self) -> discord.ui.View:

        def tradingview_url() -> str:
            base_url: str = "https://www.tradingview.com/chart/HIHGAUrW/?theme=dark"
            symbol: str = f"&symbol={self.bot['symbolName']}"
            interval: str = "&interval=5"
            ref: str = "&aff_id=133415"
            return f"{base_url}{symbol}{interval}{ref}"

        view = View()
        btn_open = Button(label="Open Chart", url=tradingview_url(), emoji="📈")
        view.add_item(item=btn_open)
        return view


class BotManager:
    def __init__(self) -> None:
        self.bot_list: list[dict] = bot_list

    def start_bots(self) -> None:
        threads: list[threading.Thread] = []
        for bot in self.bot_list:
            bot_logger: logging.Logger = create_bot_logger(
                bot_nickname=bot["symbolNick"]
            )
            BOT_LOGGERS[bot["symbolNick"]] = bot_logger
            discord_bot = DiscordBot(bot_info=bot, bot_logger=bot_logger)
            thread = threading.Thread(target=discord_bot.run, name=bot["symbolNick"])
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    async def update_bots(self, data: dict) -> None:
        """
        Updates Discord Ticker Bots

        Args:
            data (dict): incoming price data
        """

        def clean_bot_data(bot: dict, raw_data: dict) -> dict:
            bot_data: dict = raw_data

            bot_data["name_update"] = f'{bot["symbolNick"]} - {raw_data["price"]}'

            bot_data["add_role"] = (
                green_bot_role if float(raw_data["pct_change"]) >= 0 else red_bot_role
            )

            bot_data["remove_role"] = (
                red_bot_role if float(raw_data["pct_change"]) >= 0 else green_bot_role
            )

            bot_data["pct_change_string"] = (
                (f"+ {raw_data['pct_change']}%")
                if float(raw_data["pct_change"]) >= 0
                else (f"{raw_data['pct_change']}%")
            )

            bot_data["status"] = (
                discord.Status.online
                if float(raw_data["pct_change"]) >= 0
                else discord.Status.do_not_disturb
            )

            return bot_data

        async def update_bot_server_info(bot: dict, bot_data: dict) -> None:
            try:
                url: str = f"{API_BASE_URL}guilds/{guild_id}/members/@me/nick"
                headers: dict[str, str] = {
                    "Authorization": f"Bot {bot['botToken']}",
                }
                data: dict[str, str] = {"nick": bot_data["name_update"]}

                response: requests.Response = requests.patch(
                    url=url, headers=headers, json=data, timeout=30
                )
                response.raise_for_status()

                add_role_url: str = (
                    f'{API_BASE_URL}guilds/{guild_id}/members/{bot["botID"]}/roles/{bot_data["add_role"]}'
                )
                remove_role_url: str = (
                    f'{API_BASE_URL}guilds/{guild_id}/members/{bot["botID"]}/roles/{bot_data["remove_role"]}'
                )

                add: requests.Response = requests.put(
                    url=add_role_url, headers=headers, timeout=10
                )
                remove: requests.Response = requests.delete(
                    url=remove_role_url, headers=headers, timeout=10
                )

                if add.status_code == 429 or remove.status_code == 429:
                    BOT_LOGGERS[bot["symbolNick"]].warning(
                        f"{bot['symbolNick']} server update is being rate limited"
                    )

            except requests.exceptions.RequestException as e:
                BOT_LOGGERS[bot["symbolNick"]].error(f"Error {e}")

        async def update_bot_bio(bot: dict, bot_data: dict) -> None:
            bio_update: str = (
                f'RTH High={bot_data["rthH"]},   '
                f'RTH Low={bot_data["rthL"]},   '
                f'RTH Open={bot_data["rthO"]},   '
                f'YH={bot_data["yh"]},   '
                f'YL={bot_data["yl"]},   '
                f'YC={bot_data["yc"]},   '
                f'ONH={bot_data["onh"]},   '
                f'ONL={bot_data["onl"]},   '
                f'IBH={bot_data["ibh"]},   '
                f'IBL={bot_data["ibl"]},   '
                f'VWAP={bot_data["vwap"]},   '
                f'RVOL={bot_data["rvol"]}'
            )

            url: str = f'https://discord.com/api/v9/applications/{bot["botID"]}'
            headers: dict[str, str] = {
                "Authorization": f'Bot {bot["botToken"]}',
            }
            data: dict[str, str] = {"description": bio_update}

            response: requests.Response = requests.patch(
                url=url, headers=headers, json=data, timeout=10
            )
            response.raise_for_status()

            if response.status_code == 429:
                BOT_LOGGERS[bot["symbolNick"]].warning(
                    f"{bot['symbolNick']} server update is being rate limited"
                )

        async def update_presence(bot: dict, bot_data: dict) -> None:
            bot_id: str = bot["botID"]

            if bot_id in DISCORD_BOTS:
                discord_bot: discord.Client = DISCORD_BOTS[bot_id]
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=bot_data["pct_change_string"],
                )
                discord_bot.loop.create_task(
                    discord_bot.change_presence(
                        status=bot_data["status"], activity=activity
                    )
                )

        async def update_bot(bot) -> None:
            bot_data: dict = clean_bot_data(bot=bot, raw_data=raw_data)
            await update_bot_server_info(bot=bot, bot_data=bot_data)
            await update_presence(bot=bot, bot_data=bot_data)
            await update_bot_bio(bot=bot, bot_data=bot_data)

        for raw_data in data["stocks"]:
            for bot in bot_list:
                if bot["symbolName"] == raw_data["symbol"]:
                    await update_bot(bot=bot)
                    BOT_LOGGERS[bot["symbolNick"]].info(
                        f"{bot['symbolNick']} was updated."
                    )
