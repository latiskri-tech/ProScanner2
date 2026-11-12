import requests

TELEGRAM_BOT_TOKEN = "8698028434:AAEI-rGxwpBcCih-hzMaELPeg5wOkWSc4Ho"
TELEGRAM_CHAT_ID = "639554263"

# Список из 30 ликвидных фьючерсных монет
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
    "AVAXUSDT", "DOGEUSDT", "NEARUSDT", "LINKUSDT", "DOTUSDT",
    "SUIUSDT", "PEPEUSDT", "FETUSDT", "RENDERUSDT", "UNIUSDT",
    "APTUSDT", "ARBUSDT", "OPUSDT", "INJUSDT", "TIAUSDT",
    "ICPUSDT", "ATOMUSDT", "ETCUSDT", "FILUSDT", "LDOUSDT",
    "SHIBUSDT", "RENDERUSDT", "TONUSDT", "POLUSDT", "ARBPSDT"
]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def scan_markets():
    headers = {"User-Agent": "Mozilla/5.0"}
    signals = []

    for symbol in SYMBOLS:
        try:
            url = "https://api.bybit.com/v5/market/kline"
            params = {"category": "linear", "symbol": symbol, "interval": "15", "limit": 3}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data["retCode"] == 0 and len(data["result"]["list"]) >= 2:
                    klines = data["result"]["list"]
                    current_close = float(klines[0][4])
                    prev_close = float(klines[1][4])
                    
                    # Изменение за последние 15 минут в процентах
                    change_pct = ((current_close - prev_close) / prev_close) * 100
                    
                    # Порог срабатывания сигнала (можно изменить под себя)
                    if change_pct >= 0.4:
                        signals.append(f"🚀 *LONG* | `{symbol}`: `+{change_pct:.2f}%` | ${current_close:,.4f}")
                    elif change_pct <= -0.4:
                        signals.append(f"📉 *SHORT* | `{symbol}`: `{change_pct:.2f}%` | ${current_close:,.4f}")
        except Exception as e:
            print(f"Ошибка по {symbol}: {e}")

    return signals

if __name__ == "__main__":
    found_signals = scan_markets()
    if found_signals:
        header = f"⚡ *Топ-30 Scanner [15m]*\nНайдено сигналов: {len(found_signals)}\n-----------------------------------\n"
        msg = header + "\n".join(found_signals)
        send_telegram_message(msg)
    else:
        print("За последние 15 минут резких движений на монетах не было.")
