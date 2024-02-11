"""Discord Bots"""

# standard imports
import threading

import discord
import requests

# custom imports
from config import bot_info, guild_id, logger, ticker_green, ticker_red
from discord.ui import Button, View

api: str = "https://discord.com/api/v9/guilds/"
bot_clients: dict = {}


@logger.catch()
def start_bot(bot_identity: dict) -> None:
    """
    Discord Ticker Bot

    Args:
        bot_identity (dict): Bot info like token, ID, nickname, etc

    """

    ticker: discord.Client = discord.Client(intents=discord.Intents.all())

    @ticker.event
    async def on_ready() -> None:
        if ticker.user:
            logger.info(f"{ticker.user.name} Bot ready!")
            bot_clients[bot_identity["botID"]] = ticker

    @ticker.event
    async def on_message(message) -> None:
        if ticker.user:
            if f"<@{ticker.user.id}>" in message.content:
                await message.reply(embed=await message_embed(), view=message_view())

    async def message_embed() -> discord.Embed:
        embed_title: str = (
            f"**__{ticker.user.name if ticker.user else bot_identity['nickname']}__**"
        )
        app_info: discord.AppInfo = await ticker.application_info()
        embed_description: str = app_info.description
        embed: discord.Embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            color=ticker.user.accent_color if ticker.user else 0x000000,
            url=ticker_url(),
        )

        if ticker.user:
            if ticker.user.avatar:
                embed.set_thumbnail(url=ticker.user.avatar.url)

        return embed

    def message_view() -> discord.ui.View:
        view = View()
        btn_open = Button(label="Open Chart", url=ticker_url(), emoji="📈")
        view.add_item(item=btn_open)
        return view

    def ticker_url() -> str:
        base_url: str = "https://www.tradingview.com/chart/?theme=dark"
        symbol: str = f"&symbol={bot_identity['symbolName']}"
        interval: str = "&interval=1"
        ref: str = "&aff_id=133415"
        return f"{base_url}{symbol}{interval}{ref}"

    ticker.run(token=bot_identity["botToken"])


def start_discord_bots() -> None:
    """Spawns discord bot threads"""

    threads: list[threading.Thread] = []
    for ticker in bot_info:
        thread: threading.Thread = threading.Thread(target=start_bot, args=(ticker,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


async def update_bots(data: dict) -> None:
    """
    Updates Discord Ticker Bots

    Args:
        data (dict): incoming price data
    """

    def create_status_info(bot: dict, ticker: dict) -> dict:
        status_info: dict = {}

        status_info["name_update"] = f'{bot["symbolNick"]} - {ticker["price"]}'

        status_info["add_role"] = (
            ticker_green if float(ticker["pct_change"]) >= 0 else ticker_red
        )

        status_info["remove_role"] = (
            ticker_red if float(ticker["pct_change"]) >= 0 else ticker_green
        )

        status_info["pct_change_string"] = (
            (f"+ {ticker['pct_change']}%")
            if float(ticker["pct_change"]) >= 0
            else (f"{ticker['pct_change']}%")
        )

        status_info["status"] = (
            discord.Status.online
            if float(ticker["pct_change"]) >= 0
            else discord.Status.do_not_disturb
        )

        return status_info

    async def update_bot_server_info(bot: dict, status_info: dict) -> None:
        try:
            url: str = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me/nick"
            headers: dict[str, str] = {
                "Authorization": f"Bot {bot['botToken']}",
            }
            data: dict[str, str] = {"nick": status_info["name_update"]}

            response: requests.Response = requests.patch(
                url=url, headers=headers, json=data, timeout=10
            )
            response.raise_for_status()

            add_role_url: str = (
                f'{api}{guild_id}/members/{bot["botID"]}/roles/{status_info["add_role"]}'
            )
            remove_role_url: str = (
                f'{api}{guild_id}/members/{bot["botID"]}/roles/{status_info["remove_role"]}'
            )

            add: requests.Response = requests.put(
                url=add_role_url, headers=headers, timeout=10
            )
            remove: requests.Response = requests.delete(
                url=remove_role_url, headers=headers, timeout=10
            )

            if add.status_code == 429 or remove.status_code == 429:
                logger.warning(
                    f"{bot['symbolNick']} server update is being rate limited"
                )

        except requests.exceptions.RequestException as e:
            print(f"Error {e}")

    async def update_bot_bio(bot: dict, bio_info: dict) -> None:
        today_levels: str = (
            "**__Today's Levels__**"
            f'\nH={bio_info["today_high"]}   '
            f'L={bio_info["today_low"]}   '
            f'O={bio_info["today_open"]}   '
            f'ONH={bio_info["onh"]}   '
            f'ONL={bio_info["onl"]}   '
            f'IBH={bio_info["ibh"]}   '
            f'IBL={bio_info["ibl"]}   '
            f'VWAP={bio_info["vwap"]}   '
            f'RVOL={bio_info["rvol"]}'
        )

        yesterday_levels: str = (
            "**__Yesterday's Levels__**"
            f'\nH={bio_info["prior_high"]}   '
            f'L={bio_info["prior_low"]}   '
            f'C={bio_info["prior_close"]}'
        )

        bio_update: str = today_levels + "\n\n" + yesterday_levels

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
            logger.warning(f"{bot['symbolNick']} bio update is being rate limited")

    async def update_presence(bot: dict, status_info: dict) -> None:
        bot_id: str = bot["botID"]

        if bot_id in bot_clients:
            ticker: discord.Client = bot_clients[bot_id]
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=status_info["pct_change_string"],
            )
            ticker.loop.create_task(
                ticker.change_presence(status=status_info["status"], activity=activity)
            )

    for ticker in data["stocks"]:
        for bot in bot_info:
            if bot["symbolName"] == ticker["symbol"]:
                status_info: dict = create_status_info(bot=bot, ticker=ticker)
                await update_bot_server_info(bot=bot, status_info=status_info)
                await update_presence(bot=bot, status_info=status_info)
                await update_bot_bio(bot=bot, bio_info=ticker)
