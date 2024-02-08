import json
import os
import threading

import discord
import requests
from dotenv import load_dotenv


def runBot(botInfo: dict) -> None:
    ticker: discord.Client = discord.Client(intents=discord.Intents.all())

    @ticker.event
    async def on_ready() -> None:
        if ticker.user:
            print(f"{ticker.user.name} Bot ready!", flush=True)

    @ticker.event
    async def on_message(message: discord.Message) -> None:
        if str(object=message.channel.id) == os.getenv(key="WEBHOOK_CHANNEL_ID"):
            raw_webhook: str = message.content.replace("^^", '"')
            webhookMessage: dict = json.loads(s=raw_webhook)

            for stock in webhookMessage["stocks"]:
                if stock["symbol"] == botInfo["symbolName"]:
                    updatedBotInfo: dict = getUpdatedBotInfo(
                        botInfo=botInfo, stock=stock
                    )

                    for guild in ticker.guilds:
                        await updateBotGuildInfo(
                            guild=guild, updatedBotInfo=updatedBotInfo, ticker=ticker
                        )

                    await ticker.change_presence(
                        status=updatedBotInfo["status"],
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=updatedBotInfo["pct_change_string"],
                        ),
                    )

                    await updateBotBio(
                        webhookMessage=webhookMessage, botInfo=botInfo, stock=stock
                    )

    def getUpdatedBotInfo(botInfo: dict, stock: dict) -> dict:
        updatedBotInfo: dict = {}
        updatedBotInfo["name_update"] = f'{botInfo["symbolNick"]} - {stock["price"]}'
        updatedBotInfo["add_role"] = (
            "ticker-green" if float(stock["pct_chg"]) >= 0 else "ticker-red"
        )
        updatedBotInfo["remove_role"] = (
            "ticker-red" if float(stock["pct_chg"]) >= 0 else "ticker-green"
        )
        updatedBotInfo["pct_change_string"] = (
            (f"+ {stock['pct_chg']}%")
            if float(stock["pct_chg"]) >= 0
            else (f"{stock['pct_chg']}%")
        )
        updatedBotInfo["status"] = (
            discord.Status.online
            if float(stock["pct_chg"]) >= 0
            else discord.Status.do_not_disturb
        )

        return updatedBotInfo

    async def updateBotGuildInfo(
        guild: discord.Guild, updatedBotInfo: dict, ticker: discord.Client
    ) -> None:
        try:
            await guild.me.edit(nick=updatedBotInfo["name_update"])

            add_role: discord.Role | None = discord.utils.get(
                guild.roles, name=updatedBotInfo["add_role"]
            )
            if add_role is not None:
                await guild.me.add_roles(add_role)

            remove_role: discord.Role | None = discord.utils.get(
                guild.roles, name=updatedBotInfo["remove_role"]
            )
            if remove_role is not None:
                await guild.me.remove_roles(remove_role)
        except:
            if ticker.user:
                print(
                    f"Exception trying to update {ticker.user.name} in guild: {guild.id}",
                    flush=True,
                )

    async def updateBotBio(webhookMessage: dict, botInfo: dict, stock: dict) -> None:
        us_session_open: bool = (
            webhookMessage["us_futures_open"] == "true"
            and botInfo["symbolNick"] != "BTC"
        )
        crypto_session_open: bool = (
            webhookMessage["crypto_open"] == "true" and botInfo["symbolNick"] == "BTC"
        )

        if us_session_open or crypto_session_open:
            bio_update: str = (
                f'Prior Day High: {stock["prior_high"]}\
                            \nPrior Day Low: {stock["prior_low"]}\
                            \nPrior Day Close: {stock["prior_close"]}'
            )

            requests.patch(
                url=(f'https://discord.com/api/v9/applications/{botInfo["botID"]}'),
                headers={
                    "Authorization": f'Bot {botInfo["botToken"]}',
                },
                json={"description": bio_update},
            )

    ticker.run(token=botInfo["botToken"])


def loadBotInfo() -> list[dict]:
    botInfoFile: str = os.path.join(os.getcwd(), "src", ".bots.json")

    with open(file=botInfoFile, mode="r") as json_file:
        data: dict = json.load(fp=json_file)
        thread_arguments: list[dict] = data.get("bots", [])
        return thread_arguments


if __name__ == "__main__":
    load_dotenv()

    botInfo: list[dict] = loadBotInfo()
    threads: list[threading.Thread] = []

    for bot in botInfo:
        thread: threading.Thread = threading.Thread(target=runBot, args=(bot,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
