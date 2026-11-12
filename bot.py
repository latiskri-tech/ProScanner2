import requests

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
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка отправки в Telegram: {response.text}")
    except Exception as e:
        print(f"Ошибка соединения с Telegram: {e}")

def get_market_price():
    """Запрос цены через Bybit API с заголовками браузера (чтобы GitHub не блокировали)"""
    url = "https://api.bybit.com/v5/market/tickers"
    params = {"category": "linear", "symbol": "BTCUSDT"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["retCode"] == 0:
                price = float(data["result"]["list"][0]["lastPrice"])
                return price
    except Exception as e:
        print(f"Ошибка Bybit: {e}")

    # Запасной вариант через MEXC API, если Bybit ответит ошибкой
    try:
        mexc_url = "https://contract.mexc.com/api/v1/contract/ticker?symbol=BTC_USDT"
        response = requests.get(mexc_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data["data"]["lastPrice"])
    except Exception as e:
        print(f"Ошибка MEXC: {e}")

    return None

def analyze_market():
    price = get_market_price()
    
    if not price:
        return "⚠️ Не удалось получить данные с биржи."

    message = (
        f"🟢 **Crypto Bot Active**\n"
        f"Asset: `BTC/USDT`\n"
        f"-----------------------------------\n"
        f"• Current Price: `${price:,.2f}`\n"
        f"• Status: Мониторинг запущен, данные получены успешно!\n"
        f"-----------------------------------\n"
        f"⚙️ GitHub Actions Cron (15m)"
    )
    return message

if __name__ == "__main__":
    msg = analyze_market()
    if msg:
        send_telegram_message(msg)
