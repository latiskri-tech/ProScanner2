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
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Ошибка отправки в Telegram: {response.text}")
    except Exception as e:
        print(f"Ошибка соединения с Telegram: {e}")

def get_coincap_price():
    """Получает текущую цену BTC через публичное API CoinCap (без блокировок)"""
    url = "https://api.coincap.io/v2/assets/bitcoin"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data["data"]["priceUsd"])
    except Exception as e:
        print(f"Ошибка запроса к CoinCap: {e}")
    return None

def analyze_market():
    # Для демонстрации берем текущую цену. Поскольку проверка каждые 15 минут, 
    # в реальном боте можно сохранять историю или проверять изменение.
    current_price = get_coincap_price()
    
    if not current_price:
        return "⚠️ Не удалось получить данные о цене."

    message = (
        f"🚀 **Market Status Update** [CoinCap]\n"
        f"Asset: `BTC/USDT`\n"
        f"Timeframe: `15m check`\n"
        f"-----------------------------------\n"
        f"• Current Price: `${current_price:,.2f}`\n"
        f"• Status: Бот успешно запущен и мониторит рынок\n"
        f"-----------------------------------\n"
        f"⚙️ Автоматический запуск GitHub Actions"
    )
    return message

if __name__ == "__main__":
    msg = analyze_market()
    if msg:
        send_telegram_message(msg)
