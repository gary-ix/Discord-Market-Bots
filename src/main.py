import os
from dotenv import load_dotenv
import json
import threading

import discord
import requests


def runBot(botInfo):
    ticker = discord.Client(intents=discord.Intents.all())

    @ticker.event
    async def on_ready():
        print(f"{ticker.user.name} Bot ready!", flush=True)

    @ticker.event
    async def on_message(message):
        if str(message.channel.id) == os.getenv("WEBHOOK_CHANNEL_ID"):
            raw_webhook = message.content.replace("^^", '"')
            webhookMessage = json.loads(raw_webhook)

            for stock in webhookMessage["stocks"]:
                if stock["symbol"] == botInfo["symbolName"]:
                    updatedBotInfo = getUpdatedBotInfo(botInfo, stock)

                    for guild in ticker.guilds:
                        await updateBotGuildInfo(guild, updatedBotInfo, ticker)

                    await ticker.change_presence(
                        status=updatedBotInfo["status"],
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=updatedBotInfo["pct_change_string"],
                        ),
                    )

                    await updateBotBio(webhookMessage, stock)

    ticker.run(botInfo["botToken"])


def loadBotInfo():
    botInfoFile = os.path.join(os.getcwd(), "src", ".bots.json")
    with open(botInfoFile, "r") as json_file:
        data = json.load(json_file)
        thread_arguments = data.get("bots", [])
        return thread_arguments


def getUpdatedBotInfo(botInfo, stock):
    updatedBotInfo = {}
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


async def updateBotGuildInfo(guild, updatedBotInfo, ticker):
    try:
        await guild.me.edit(nick=updatedBotInfo["name_update"])
        await guild.me.add_roles(
            discord.utils.get(guild.roles, name=updatedBotInfo["add_role"])
        )
        await guild.me.remove_roles(
            discord.utils.get(guild.roles, name=updatedBotInfo["remove_role"])
        )
    except:
        print(
            f"Exception trying to update {ticker.user.name} in guild: {guild.id}",
            flush=True,
        )


async def updateBotBio(webhookMessage, stock):
    if (
        webhookMessage["us_futures_open"] == "true" and botInfo["symbolNick"] != "BTC"
    ) or (webhookMessage["crypto_open"] == "true" and botInfo["symbolNick"] == "BTC"):
        bio_update = f'Prior Day High: {stock["prior_high"]}\
                        \nPrior Day Low: {stock["prior_low"]}\
                        \nPrior Day Close: {stock["prior_close"]}'
        r = requests.patch(
            url=(f'https://discord.com/api/v9/applications/{botInfo["botID"]}'),
            headers={
                "Authorization": f'Bot {botInfo["botToken"]}',
            },
            json={"description": bio_update},
        )


if __name__ == "__main__":
    load_dotenv()

    botInfo = loadBotInfo()
    threads = []

    for bot in botInfo:
        thread = threading.Thread(target=runBot, args=(bot,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
