import { ActivityType, Client, Events, GatewayIntentBits, Message, Guild, Interaction } from "discord.js";
import logger from "./utils/logger";
import { config } from "./utils/config";
import { commands } from "./commands";
import { deployCommands, deployCommandsToAll } from "./utils/deploy";
import { newsHeadline } from "./services/news-headline";

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
  const { commandName } = interaction;
  if (commands[commandName as keyof typeof commands]) {
    commands[commandName as keyof typeof commands].execute(interaction);
  }
});


client.on(Events.MessageCreate, async (message: Message) => {
  if (message.author.bot) return;


  // Check if message comes from news webhook bot
  //  && message.author.id === "1240686103959179274"
  if (message.channelId === "1248771982980284436") {
    await newsHeadline(message);

    // reply to the message
    // await message.reply("News headline received");
  }
});


client.login(config.DISCORD_TOKEN);

