import { APIApplicationCommandOptionChoice, CommandInteraction, SlashCommandBuilder } from "discord.js";
import puppeteer, { Browser } from "puppeteer";
import logger from "../utils/logger";

const marketOptions = {
  "SPX500": "S&P 500",
  "NASDAQ100": "NDX 100",
  "DJCA": "DOW JONES",
  "DAX": "DAX"
};

const timeframeOptions = {
  "change": "Daily",
  "Perf.W": "Weekly",
  "Perf.1M": "Monthly",
  "Perf.Y": "Yearly",
  "Perf.YTD": "YTD"
};

let browser: Browser | null = null;

export const data = new SlashCommandBuilder()
  .setName("heatmap")
  .setDescription("Fetches a market heatmap")
  .addStringOption(option =>
    option
      .setName("market")
      .setDescription("The market index")
      .setRequired(true)
      .addChoices(
        ...Object.entries(marketOptions).map(([value, name]): APIApplicationCommandOptionChoice<string> => ({ name, value }))

      ))
  .addStringOption(option =>
    option
      .setName("timeframe")
      .setDescription("The lookback period")
      .setRequired(true)
      .addChoices(
        ...Object.entries(timeframeOptions).map(([value, name]): APIApplicationCommandOptionChoice<string> => ({ name, value }))

      ))

export async function execute(interaction: CommandInteraction) {
  const market = interaction.options.get("market")?.value?.toString();
  const timeframe = interaction.options.get("timeframe")?.value?.toString();
  
  const marketName = marketOptions[market as keyof typeof marketOptions];
  const timeframeName = timeframeOptions[timeframe as keyof typeof timeframeOptions];

  const heatmapString = `${marketName} ${timeframeName} Heatmap`
  const replyMessage = `Summoning ${heatmapString}...please wait 🪄`;
  const heatmapURL = `https://www.tradingview.com/heatmap/stock/?theme=dark#%7B%22dataSource%22%3A%22${market}%22%2C%22blockColor%22%3A%22${timeframe}%22%2C%22blockSize%22%3A%22market_cap_basic%22%2C%22grouping%22%3A%22sector%22%7D`;
  const errorMessage = "Alas, the stars are not in alignment for a heatmap. Please try again later 🧙🏻‍♂️";

  await interaction.reply(replyMessage)
    .then(async () => {
      if (!market || !timeframe) throw new Error("Invalid options");
      const screenshotPath = await takeScreenshot(heatmapURL);
      await interaction.editReply({ content: heatmapString, files: [screenshotPath] });
    })
    .catch(async error => {
      logger.error(error);
      await interaction.editReply(errorMessage);
    });
}

async function launchBrowser(): Promise<Browser> {
  if (!browser) {
    browser = await puppeteer.launch({
      executablePath: "/usr/bin/google-chrome",
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
      defaultViewport: { width: 1920, height: 1080 }
    });
  }
  return browser;
}

async function takeScreenshot(url: string) {
  const browser = await launchBrowser();
  if (!browser) throw new Error("Browser not initialized");
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "networkidle2" });
  await page.waitForSelector("[data-name=\"heatmap-top-bar_fullscreen\"]");
  await page.click("[data-name=\"heatmap-top-bar_fullscreen\"]");
  const screenshotPath = "screenshot.png";
  await page.screenshot({ path: screenshotPath });
  await page.close();

  return screenshotPath;
}
