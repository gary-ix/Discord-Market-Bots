import { ActivityType, Client, Events, GatewayIntentBits, Message, Guild, Interaction } from "discord.js";
import logger from "./utils/logger";
import { config } from "./utils/config";
import { commands } from "./commands";
import { deployCommands, deployCommandsToAll } from "./utils/deploy";
import { newsHeadline } from "./services/news/news-headline";
import { setupNewsCalendar } from "./services/news/news-calendar";

// Initialize the bot
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.on(Events.ClientReady, () => {
  client.user?.setActivity("🧙🏻‍♂️ Summoning Market Info", { type: ActivityType.Custom });
  logger.info(`Logged in as ${client.user?.tag}!`);
  deployCommandsToAll();
  setupNewsCalendar(client);
});
client.on(Events.Debug, (m) => logger.debug(m));
client.on(Events.Warn, (m) => logger.warn(m));
client.on(Events.Error, (m) => logger.error(m));

client.on(Events.GuildCreate, async (guild: Guild) => {
  await deployCommands({ guildId: guild.id });
});

client.on(Events.InteractionCreate, async (interaction: Interaction) => {
  if (!interaction.isCommand()) {
    return;
  }
  
  // Check if the interaction is from a guild (server) and not a DM
  if (!interaction.guild) {
    await interaction.reply({ content: 'Commands can only be used in servers, not in DMs.', ephemeral: true });
    return;
  }

  const { commandName } = interaction;
  if (commands[commandName as keyof typeof commands]) {
    commands[commandName as keyof typeof commands].execute(interaction);
  }
});


client.on(Events.MessageCreate, async (message: Message) => {
  if (message.channelId === "1248771982980284436" && message.author.id === "1240686103959179274") {
    await newsHeadline(message);
  }
});


client.login(config.DISCORD_TOKEN);

