import requests

# Твои данные бота и чата
TELEGRAM_BOT_TOKEN = "8698028434:AAEI-rGxwpBcCih-hzMaELPeg5wOkWSc4Ho"
TELEGRAM_CHAT_ID = "639554263"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Ошибка отправки в Telegram: {response.text}")
    except Exception as e:
        print(f"Ошибка соединения с Telegram: {e}")

def get_binance_kline(symbol="BTCUSDT", interval="15m", limit=20):
    """Запрос бесплатных публичных свечей с Binance (отлично работает на GitHub)"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка запроса к Binance: {e}")
    return None

def analyze_market():
    symbol = "BTCUSDT"
    klines = get_binance_kline(symbol, interval="15m", limit=20)
    
    if not klines:
        return "⚠️ Не удалось получить данные с биржи."

    # Binance возвращает цены закрытия на индексе 4
    closes = [float(k[4]) for k in klines]
    current_price = closes[-1]
    prev_price = closes[-2]

    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    signal_type = None
    if change_pct > 0.5:
        signal_type = "🚀 **LONG Signal**"
    elif change_pct < -0.5:
        signal_type = "📉 **SHORT Signal**"
    else:
        print(f"Рынок спокоен. Изменение за 15м: {change_pct:.2f}%. Сигнал не сформирован.")
        return None

    message = (
        f"{signal_type} [Binance Futures / Spot]\n"
        f"Asset: `{symbol}`\n"
        f"Timeframe: `15m`\n"
        f"-----------------------------------\n"
        f"• Current Price: `${current_price:,.2f}`\n"
        f"• 15m Change: `{change_pct:+.2f}%`\n"
        f"• Status: Условия по стратегии выполнены\n"
        f"-----------------------------------\n"
        f"⚙️ Автоматический запуск GitHub Actions"
    )
    return message

if __name__ == "__main__":
    msg = analyze_market()
    if msg:
        send_telegram_message(msg)
