import { ActivityType, Client, Events, GatewayIntentBits } from "discord.js";
import logger from "./utils/logger";
import { config } from "./utils/config";
import { commands } from "./commands";
import { deployCommands, deployCommandsToAll } from "./utils/deploy";

// Initialize the bot
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages
  ]
});

client.on(Events.ClientReady, () => {
  client.user?.setActivity("🧙🏻‍♂️ Summoning Market Info", { type: ActivityType.Custom });
  logger.info(`Logged in as ${client.user?.tag}!`);
  deployCommandsToAll();
});
client.on(Events.Debug, m => logger.debug(m));
client.on(Events.Warn, m => logger.warn(m));
client.on(Events.Error, m => logger.error(m));

client.on(Events.GuildCreate, async (guild) => {
  await deployCommands({ guildId: guild.id });
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isCommand()) {
    return;
  }
  const { commandName } = interaction;
  if (commands[commandName as keyof typeof commands]) {
    commands[commandName as keyof typeof commands].execute(interaction);
  }
});

client.login(config.DISCORD_TOKEN);

