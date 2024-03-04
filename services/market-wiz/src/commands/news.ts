import {
  ActionRowBuilder,
  APIApplicationCommandOptionChoice,
  ButtonBuilder,
  ButtonStyle,
  CommandInteraction,
  EmbedBuilder,
  SlashCommandBuilder
} from "discord.js";
import axios from "axios";
import logger from "../logger";

const countryOptions = {
  "US": "USA",
};

const timeframeOptions = {
  "6": "Next 6 hours",
  "24": "Next 24 hours",
  "48": "Next 48 hours",
  "168": "Next 7 days",
};

const importanceOptions = {
  "High": "🔴",
  "Medium": "🔴🟠",
  "Low": "🔴🟠🟡",
}

export const data = new SlashCommandBuilder()
  .setName("news")
  .setDescription("Fetches economic calendar events")
  .addStringOption(option =>
    option
      .setName("country")
      .setDescription("The country/countires to fetch news for.")
      .setRequired(true)
      .addChoices(
        ...Object.entries(countryOptions)
          .map(([value, name]): APIApplicationCommandOptionChoice<string> => ({ name, value }))

      ))
  .addStringOption(option =>
    option
      .setName("timeframe")
      .setDescription("How far ahead to fetch news events.")
      .setRequired(true)
      .addChoices(
        ...Object.entries(timeframeOptions)
          .map(([value, name]): APIApplicationCommandOptionChoice<string> => ({ name, value }))

      ))
  .addStringOption(option =>
    option
      .setName("importance")
      .setDescription("Minimum impact level of news to fetch.")
      .setRequired(true)
      .addChoices(
        ...Object.entries(importanceOptions)
          .map(([value, name]): APIApplicationCommandOptionChoice<string> => ({ name, value }))

      ))

export async function execute(interaction: CommandInteraction) {
  const country = interaction.options.get("country")?.value?.toString();
  const timeframe = interaction.options.get("timeframe")?.value?.toString();
  const importance = interaction.options.get("importance")?.value?.toString();

  const countryName = countryOptions[country as keyof typeof countryOptions];
  const timeframeName = timeframeOptions[timeframe as keyof typeof timeframeOptions];
  const importanceName = importanceOptions[importance as keyof typeof importanceOptions];

  const newsString = `${importanceName} ${countryName} News Events for ${timeframeName}`;
  const replyMessage = `Peeking into the future for ${newsString}...please wait 🔮`;
  const errorMessage = "Oops! The mystical energies needed to foresee the future are currently unavailable. Please try again later 🧙🏻‍♂️";

  await interaction.reply({ content: replyMessage, ephemeral: true })
    .then(async () => {
      if (!country || !timeframe || !importance) throw new Error("Invalid options");
      const result = await createNewsEmbed({ country, timeframe, importance });
      if (!result) throw new Error("Error creating embed");
      await interaction.editReply({ embeds: [result.embed], components: [result.row as any], content: newsString });
    })

    .catch(async error => {
      logger.error(error);
      await interaction.editReply({ content: errorMessage })
    });
}

async function fetchNewsData(params: { country: string, timeframe: string, importance: number }) {
  const baseUrl = "https://economic-calendar.tradingview.com/events";

  const from = new Date();

  const to = new Date();
  to.setHours(to.getHours() + parseInt(params.timeframe));

  const url = `${baseUrl}?minImportance=${params.importance}` +
    `&from=${from.toISOString()}` +
    `&to=${to.toISOString()}` +
    `&countries=${params.country}`;

  const config = {
    method: "get",
    maxBodyLength: Infinity,
    url: url,
    headers: {}
  };

  try {
    const response = await axios.request(config);
    return response.data;
  } catch (error) {
    logger.error(error);
    return null;
  }
}

const getImportanceInt = (importance: string) => {
  if (importance === "High") return 1;
  if (importance === "Medium") return 0;
  return -1;
};

const getColorForImportance = (importance: number, title: string) => {
  if (title.toLowerCase().includes("fed")) return "🔵";
  if (importance === -1) return "🟡";
  if (importance === 0) return "🟠";
  if (importance === 1) return "🔴";
  return "⚪️";
};

const getCountryFlag = (countryName: string) => {
  if (countryName === "US") return "🇺🇸";
  return "";
}

async function createNewsEmbed(params: { country: string, timeframe: string, importance: string }) {
  const importanceNumber = getImportanceInt(params.importance);
  const data = await fetchNewsData(
    {
      country: params.country,
      timeframe: params.timeframe,
      importance: importanceNumber
    });
  if (!data) return null;

  const embed = new EmbedBuilder()
    .setColor("#1E1F20")
    .setTitle("📅 **Upcoming News Events**")
    .setTimestamp()
    .setFooter({
      text: "All event times are in Eastern Standard Timezone",
      iconURL: "https://cdn.discordapp.com/emojis/1212202807193767976.webp?quality=lossless"
    })

  if (data && data.result && data.result.length > 0) {
    const maxFields = Math.min(data.result.length, 25);
    for (let i = 0; i < maxFields; i++) {
      const event = data.result[i];
      const eventDate = new Date(event.date);
      const currentDate = new Date();
      const deltaMinutes = Math.round((eventDate.getTime() - currentDate.getTime()) / (1000 * 60));

      const date = new Date(event.date).toLocaleTimeString("en-US", {
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "America/New_York"
      });

      let timeDelta;
      if (deltaMinutes < 60) {
        timeDelta = `${deltaMinutes} minute${deltaMinutes !== 1 ? "s" : ""} from now`;
      } else {
        const deltaHours = Math.floor(deltaMinutes / 60);
        timeDelta = `${deltaHours} hour${deltaHours !== 1 ? "s" : ""} from now`;
      }

      const importanceColor = getColorForImportance(importanceNumber, event.title);
      const countryFlag = getCountryFlag(event.country);
      const prev = event.previous ? event.previous : " ";
      const forecast = event.forecast ? event.forecast : " ";

      embed.addFields(
        {
          name: `**__${importanceColor} ${event.title} __**`,
          value: (
            `- ${date} (${timeDelta})\n- Previous: ${prev}  |  Forecast: ${forecast}\n- Country ${countryFlag}`
          ),
          inline: false
        });
    }
  } else {
    embed.setDescription("*No news events were found to be scheduled with your selected criteria.*");
  }

  const openChartButton = new ButtonBuilder()
    .setLabel("See More News")
    .setStyle(ButtonStyle.Link)
    .setEmoji("📆")
    .setURL("https://www.tradingview.com/economic-calendar/?aff_id=133415")

  const row: ActionRowBuilder = new ActionRowBuilder()
    .addComponents(openChartButton);

  return { embed, row };
}

