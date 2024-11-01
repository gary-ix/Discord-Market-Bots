import axios from "axios";

const data = "{\"payload\":{\"symbol\":\"={\\\"adjustment\\\":\\\"splits\\\",\\\"currency-id\\\":\\\"XTVCUSDT\\\",\\\"session\\\":\\\"extended\\\",\\\"symbol\\\":\\\"BINANCE:BTCUSDT\\\"}\",\"resolution\":\"1\",\"message\":\"\",\"sound_file\":null,\"sound_duration\":0,\"popup\":false,\"expiration\":\"2024-11-30T13:22:00.000Z\",\"condition\":{\"type\":\"pine_alert\",\"series\":[{\"type\":\"study\",\"study\":\"Script@tv-scripting-101\",\"offsets_by_plot\":{},\"inputs\":{\"__profile\":false,\"in_0\":\"CME_MINI:ES1!\",\"in_1\":\"CME_MINI:NQ1!\",\"in_10\":\"0930-1659\",\"in_11\":\"1700-0929\",\"in_12\":\"0930-1030\",\"in_13\":\"0930-1700\",\"in_14\":20,\"in_2\":\"CME_MINI:RTY1!\",\"in_3\":\"CBOT_MINI:YM1!\",\"in_4\":\"TVC:VIX\",\"in_5\":\"TVC:DXY\",\"in_6\":\"CBOT:UB1!\",\"in_7\":\"BINANCE:BTCUSDT\",\"in_8\":\"COMEX:GC1!\",\"in_9\":\"NYMEX:CL1!\",\"pineFeatures\":\"{\\\"import\\\":1,\\\"indicator\\\":1,\\\"plot\\\":1,\\\"str\\\":1,\\\"array\\\":1,\\\"math\\\":1,\\\"alert\\\":1,\\\"request.security\\\":1,\\\"type\\\":1,\\\"user_methods\\\":1,\\\"builtin_methods\\\":1}\"},\"pine_id\":\"USER;19b25c9e453441899068b60b69bf3c8b\",\"pine_version\":\"96.0\"}]},\"auto_deactivate\":false,\"email\":false,\"sms_over_email\":false,\"mobile_push\":false,\"web_hook\":\"https://discordbots.theprogrammergary.com/6YVpcd3QEwkdADX51KG4czHLd3NVcFs9\",\"name\":\"TICKERS (ES1! · CME, NQ1! · CME, RTY1! · CME, YM1! · CBOT, VIX · TVC, DXY · TVC, UB1! · CBOT, BTCUSDT · Binance, GC1! · COMEX, CL1! · NYMEX, 0930-1659, 1700-0929, 0930-1030, 0930-1700, 20): Any alert() function call\",\"active\":true,\"ignore_warnings\":true,\"alert_id\":1639407556}}";

export const extendTradingViewAlert = async () => {
  // Add date formatting utilities
  const formatBuildTime = (date: Date) => {
    return date.getFullYear() + "_" + 
           String(date.getMonth() + 1).padStart(2, "0") + "_" + 
           String(date.getDate()).padStart(2, "0") + "-" + 
           String(date.getHours()).padStart(2, "0") + "_" + 
           String(date.getMinutes()).padStart(2, "0");
  };

  // Get current date and future expiration date
  const now = new Date();
  const expirationDate = new Date(now);
  expirationDate.setDate(now.getDate() + 30);

  // Parse and update the data object
  const parsedData = JSON.parse(data);
  parsedData.payload.expiration = expirationDate.toISOString();
  const updatedData = JSON.stringify(parsedData);

  const config = {
    method: "post",
    maxBodyLength: Infinity,
    url: `https://pricealerts.tradingview.com/modify_restart_alert?log_username=GoodGains&build_time=${formatBuildTime(now)}&maintenance_unset_reason=initial_operated`,
    headers: { 
      "accept": "*/*", 
      "accept-language": "en;q=0.7", 
      "cache-control": "no-cache", 
      "content-type": "text/plain;charset=UTF-8", 
      "cookie": "device_t=X1FTMkFROjM.ytKQD-xd5jbzF1VMYw4ddUMedNoZ23MY5432KMfnyKI; sessionid=51v594jorb40xti5ma36vkpfadmh8f20; sessionid_sign=v3:GGpr5JqTEOsgBSaz6LxFCLtUkbqyGfyV1tW56Gq5mT4=; png=bb50a08e-ae2d-49e7-bba7-59f4b7f54f53; etg=bb50a08e-ae2d-49e7-bba7-59f4b7f54f53; cachec=bb50a08e-ae2d-49e7-bba7-59f4b7f54f53; _sp_ses.cf1a=*; _sp_id.cf1a=.1729014926.1.1730463683..601d1c92-a3be-4151-b123-031ee9a1f6d0..564dfa62-2429-4301-8482-9ebf319e978c.1729014926180.16", 
      "origin": "https://www.tradingview.com", 
      "pragma": "no-cache", 
      "priority": "u=1, i", 
      "referer": "https://www.tradingview.com/", 
      "sec-ch-ua": "\"Chromium\";v=\"130\", \"Brave\";v=\"130\", \"Not?A_Brand\";v=\"99\"", 
      "sec-ch-ua-mobile": "?0", 
      "sec-ch-ua-platform": "\"macOS\"", 
      "sec-fetch-dest": "empty", 
      "sec-fetch-mode": "cors", 
      "sec-fetch-site": "same-site", 
      "sec-gpc": "1", 
      "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    },
    data: updatedData
  };

  try {
    const response = await axios.request(config);
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
