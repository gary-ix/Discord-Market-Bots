import { ActivityType, Client } from "discord.js";
import axios from "axios";
import { Bot } from "./types";
import logger from "./logger";

export async function updateDiscordBot(client: Client, bot: Bot, data: any) {
  const botData = cleanBotData(bot, data)

  // update activity
  if (client.user) {
    client.user.setActivity(`Watching ${botData.activity}`, { type: ActivityType.Custom });
    client.user.setStatus(botData.status);
  }

  // update info in all guilds
  client.guilds.cache.forEach(async guild => {
    if (!client.user) return;
    const member = await guild.members.fetch(client.user.id);
    member.setNickname(botData.nameUpdate);

    // const addRole = guild.roles.cache.find(role => role.name === botData.addRole);
    // const removeRole = guild.roles.cache.find(role => role.name === botData.removeRole);
    const addRole = (await guild.roles.fetch()).find(role => role.name === botData.addRole);
    const removeRole = (await guild.roles.fetch()).find(role => role.name === botData.removeRole);

    if (!addRole) {
      console.log(`Role ${addRole} not found in ${guild.name}`);

      return;
    }
    member.roles.add(addRole)
      .catch(logger.error);

    if (!removeRole) {
      console.log(`Role ${removeRole} not found in ${guild.name}`);
      return;
    }
    member.roles.remove(removeRole)
      .catch(logger.error);
  });

  // update bio info
  await updateBotBio(bot, botData)

  logger.info(`Finished updating ${bot.symbolName}`)
}

function cleanBotData(bot: Bot, data: any): any {
  const botData: any = { ...data };
  botData.nameUpdate = `${bot.symbolNick} - ${data.price}`;
  botData.addRole = parseFloat(data.pct) >= 0 ? "ticker-green" : "ticker-red";
  botData.removeRole = parseFloat(data.pct) >= 0 ? "ticker-red" : "ticker-green";
  botData.activity = parseFloat(data.pct) >= 0 ? `+${data.pct}%` : `${data.pct}%`;
  botData.status = parseFloat(data.pct) >= 0 ? "online" : "dnd"
  return botData;
}

async function updateBotBio(bot: Bot, botData: any): Promise<void> {
  const bioUpdate: string = `
        RTH High=${botData.rthH},   
        RTH Low=${botData.rthL},   
        RTH Open=${botData.rthO},   
        YH=${botData.yh},   
        YL=${botData.yl},   
        YC=${botData.yc},   
        ONH=${botData.onh},   
        ONL=${botData.onl},   
        IBH=${botData.ibh},   
        IBL=${botData.ibl},   
        VWAP=${botData.vwap},   
        RVOL=${botData.rvol}
    `.trim();

  const url: string = `https://discord.com/api/v9/applications/${bot.id}`;
  const data: { description: string } = { description: bioUpdate.replace(/,\s+/g, ", ") };
  const headers: { Authorization: string } = {
    Authorization: `Bot ${bot.token}`,
  };

  try {
    const response = await axios.patch(url, data, { headers, timeout: 10000 });
    if (response.status === 429) {
      logger.warn(`${bot.symbolNick} server update is being rate limited`);
    }
  } catch (error) {
    logger.error(error);
  }
};
