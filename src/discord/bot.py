"""Discord Bots"""

# standard imports
import threading

import requests

# custom imports
from config.settings import bot_list, guild_id, ticker_green, ticker_red

import discord
from discord.ui import Button, View

DISCORD_BOTS: dict = {}
API_BASE_URL = "https://discord.com/api/v9/"


class DiscordBot:
    def __init__(self, bot_info) -> None:
        self.bot: dict = bot_info
        self.client: discord.Client = discord.Client(
            intents=discord.Intents(messages=True)
        )
        self.setup_events()

    def setup_events(self) -> None:

        @self.client.event
        async def on_ready() -> None:
            if self.client.user:
                print(f"{self.client.user.name} Bot ready!")
                DISCORD_BOTS[self.bot["botID"]] = self.client

        @self.client.event
        async def on_message(message) -> None:
            if self.client.user:
                if f"<@{self.client.user.id}>" in message.content:
                    await message.reply(
                        embed=await self.message_embed(), view=self.message_view()
                    )

    def run(self) -> None:
        self.client.run(token=self.bot["botToken"], root_logger=True)

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

        def ticker_url() -> str:
            base_url: str = "https://www.tradingview.com/chart/HIHGAUrW/?theme=dark"
            symbol: str = f"&symbol={self.bot['symbolName']}"
            interval: str = "&interval=5"
            ref: str = "&aff_id=133415"
            return f"{base_url}{symbol}{interval}{ref}"

        view = View()
        btn_open = Button(label="Open Chart", url=ticker_url(), emoji="📈")
        view.add_item(item=btn_open)
        return view


class BotManager:
    def __init__(self) -> None:
        self.bot_list: list[dict] = bot_list

    def start_bots(self) -> None:
        threads: list[threading.Thread] = []
        for bot in self.bot_list:
            bot = DiscordBot(bot_info=bot)
            thread = threading.Thread(target=bot.run)
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

        def clean_bot_data(bot: dict, ticker: dict) -> dict:
            bot_data: dict = {}

            bot_data["name_update"] = f'{bot["symbolNick"]} - {ticker["price"]}'

            bot_data["add_role"] = (
                ticker_green if float(ticker["pct_change"]) >= 0 else ticker_red
            )

            bot_data["remove_role"] = (
                ticker_red if float(ticker["pct_change"]) >= 0 else ticker_green
            )

            bot_data["pct_change_string"] = (
                (f"+ {ticker['pct_change']}%")
                if float(ticker["pct_change"]) >= 0
                else (f"{ticker['pct_change']}%")
            )

            bot_data["status"] = (
                discord.Status.online
                if float(ticker["pct_change"]) >= 0
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
                    print(f"{bot['symbolNick']} server update is being rate limited")

            except requests.exceptions.RequestException as e:
                print(f"Error {e}")

        async def update_bot_bio(bot: dict, bio_info: dict) -> None:
            bio_update: str = (
                f'RTH High={bio_info["rthH"]},   '
                f'RTH Low={bio_info["rthL"]},   '
                f'RTH Open={bio_info["rthO"]},   '
                f'YH={bio_info["yh"]},   '
                f'YL={bio_info["yl"]},   '
                f'YC={bio_info["yc"]},   '
                f'ONH={bio_info["onh"]},   '
                f'ONL={bio_info["onl"]},   '
                f'IBH={bio_info["ibh"]},   '
                f'IBL={bio_info["ibl"]},   '
                f'VWAP={bio_info["vwap"]},   '
                f'RVOL={bio_info["rvol"]}'
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
                print(f"{bot['symbolNick']} bio update is being rate limited")

        async def update_presence(bot: dict, bot_data: dict) -> None:
            bot_id: str = bot["botID"]

            if bot_id in DISCORD_BOTS:
                ticker: discord.Client = DISCORD_BOTS[bot_id]
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=bot_data["pct_change_string"],
                )
                ticker.loop.create_task(
                    ticker.change_presence(status=bot_data["status"], activity=activity)
                )

        for ticker in data["stocks"]:
            for bot in bot_list:
                if bot["symbolName"] == ticker["symbol"]:
                    bot_data: dict = clean_bot_data(bot=bot, ticker=ticker)
                    await update_bot_server_info(bot=bot, bot_data=bot_data)
                    await update_presence(bot=bot, bot_data=bot_data)
                    await update_bot_bio(bot=bot, bio_info=ticker)
