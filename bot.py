import requests
import time

TELEGRAM_BOT_TOKEN = "8698028434:AAEI-rGxwpBcCih-hzMaELPeg5wOkWSc4Ho"
TELEGRAM_CHAT_ID = "639554263"

# Список из 30 ликвидных монет
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
    "AVAXUSDT", "DOGEUSDT", "NEARUSDT", "LINKUSDT", "DOTUSDT",
    "SUIUSDT", "PEPEUSDT", "FETUSDT", "RENDERUSDT", "UNIUSDT",
    "APTUSDT", "ARBUSDT", "OPUSDT", "INJUSDT", "TIAUSDT",
    "ICPUSDT", "ATOMUSDT", "ETCUSDT", "FILUSDT", "LDOUSDT",
    "SHIBUSDT", "TONUSDT", "POLUSDT", "ARPAUSDT"
]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": part, "parse_mode": "Markdown"}, timeout=10)
                time.sleep(0.5)
        else:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def analyze_market():
    headers = {"User-Agent": "Mozilla/5.0"}
    signals = []
    table_rows = []

    for symbol in SYMBOLS:
        try:
            url = "https://api.bybit.com/v5/market/kline"
            res_15m = requests.get(url, params={"category": "linear", "symbol": symbol, "interval": "15", "limit": 3}, headers=headers, timeout=4)
            res_30m = requests.get(url, params={"category": "linear", "symbol": symbol, "interval": "30", "limit": 3}, headers=headers, timeout=4)
            
            change_15m = 0.0
            change_30m = 0.0
            current_price = 0.0

            if res_15m.status_code == 200:
                d15 = res_15m.json()
                if d15["retCode"] == 0 and len(d15["result"]["list"]) >= 2:
                    k15 = d15["result"]["list"]
                    current_price = float(k15[0][4])
                    change_15m = ((current_price - float(k15[1][4])) / float(k15[1][4])) * 100

            if res_30m.status_code == 200:
                d30 = res_30m.json()
                if d30["retCode"] == 0 and len(d30["result"]["list"]) >= 2:
                    k30 = d30["result"]["list"]
                    change_30m = ((float(k30[0][4]) - float(k30[1][4])) / float(k30[1][4])) * 100

            if current_price > 0:
                arrow_15m = "🟢+" if change_15m > 0 else "🔴" if change_15m < 0 else "⚪"
                arrow_30m = "🟢+" if change_30m > 0 else "🔴" if change_30m < 0 else "⚪"
                
                table_rows.append(f"`{symbol:<9}`|15м:{arrow_15m}{change_15m:+.2f}%|30м:{arrow_30m}{change_30m:+.2f}%|`${current_price:,.4f}`")

                # Условия для сигналов на сильных трендах
                if change_15m >= 0.5 and change_30m >= 0.4:
                    signals.append(f"🚀 *LONG* | `{symbol}` (15м: `+{change_15m:.2f}%` | 30м: `+{change_30m:.2f}%`) | `${current_price:,.4f}`")
                elif change_15m <= -0.5 and change_30m <= -0.4:
                    signals.append(f"📉 *SHORT* | `{symbol}` (15м: `{change_15m:.2f}%` | 30м: `{change_30m:.2f}%`) | `${current_price:,.4f}`")

            time.sleep(0.1)

        except Exception as e:
            print(f"Ошибка по {symbol}: {e}")

    final_msg = ""
    if signals:
        final_msg += "⚡ *АКТИВНЫЕ СИГНАЛЫ (15м/30м)*\n" + "\n".join(signals) + "\n\n───────────────────────────\n\n"
    else:
        final_msg += "⚡ *Сигналы (15м/30м):* Сильных трендов сейчас нет.\n\n───────────────────────────\n\n"

    final_msg += "📊 *Полная сводка рынка (30 монет)*\n`Монета   | 15м      | 30м      | Цена`\n-----------------------------------\n" + "\n".join(table_rows)
    
    return final_msg

if __name__ == "__main__":
    msg = analyze_market()
    if msg:
        send_telegram_message(msg)
