import * as fs from "fs";
import pino from "pino";

const streams = [
  {
    level: "info",
    stream: fs.createWriteStream("./logs/app.log", { flags: "a" }),
  },
  {
    level: "error",
    stream: fs.createWriteStream("./logs/error.log", { flags: "a" }),
  },
  {
    level: "info",
    stream: process.stdout,
  },
];

const logger = pino(
  {
    level: "info",
    timestamp: pino.stdTimeFunctions.isoTime,
    formatters: {
      bindings: () => {
        return {};
      },
      level: (label) => {
        return { severity: label.toUpperCase() };
      },
    },
  },

  pino.multistream(streams)
);

export default logger;
