export interface Bot {
    token: string;
    id: string;
    symbolName: string;
    symbolNick: string;
}

export interface BotConfig {
    bots: Bot[];
}
