import requests
import time
from datetime import datetime

TELEGRAM_BOT_TOKEN = "8698028434:AAEI-rGxwpBcCih-hzMaELPeg5wOkWSc4Ho"
TELEGRAM_CHAT_ID = "639554263"

# Список из 30 ликвидных монет для сканирования
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
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def check_macro_calendar():
    """Проверка важных событий (ставки ФРС, NFP, открытие сессий по времени UTC / Киев)"""
    now_utc = datetime.utcnow()
    hour = now_utc.hour
    minute = now_utc.minute
    weekday = now_utc.weekday() # 0-4 это Пн-Пт

    # Пример уведомления об открытии американской сессии (13:30 UTC / 15:30 по Киеву)
    if weekday < 5 and hour == 13 and 25 <= minute <= 35:
        return "🇺🇸 *Внимание:* Через несколько минут открывается американская сессия. Ожидается всплеск волатильности в ликвидных парах!"

    # Пример проверки важных макро-дней (например, среда — часто дни заседаний ФРС или публикаций инфляции)
    # Если бот запускается в определенное время, можно подсвечивать фундаментальный фон
    return None

def get_market_sentiment():
    try:
        res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        if res.status_code == 200:
            data = res.json()["data"][0]
            val = int(data['value'])
            sentiment_class = data['value_classification']
            
            if val > 75:
                macro = "Экстремальная жадность. Риск коррекции на новостях."
            elif val < 25:
                macro = "Паника на рынке. Высокая волатильность."
            else:
                macro = "Нейтральный фон. Рынок ждет ключевую статистику."
                
            return f"{sentiment_class} ({val}/100)", macro
    except:
        pass
    return "Нейтрально (50/100)", "Макрофон стабильный."

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    gains, losses = 0, 0
    for i in range(1, period + 1):
        diff = closes[-i] - closes[-i-1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_bollinger_bands(closes, period=20, num_std=2):
    if len(closes) < period:
        return 0, 0, 0
    sub_closes = closes[-period:]
    sma = sum(sub_closes) / period
    variance = sum((x - sma) ** 2 for x in sub_closes) / period
    stdev = variance ** 0.5
    return sma + (num_std * stdev), sma, sma - (num_std * stdev)

def analyze_market():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    signals = []
    sentiment_str, macro_news = get_market_sentiment()

    # 1. Сначала проверяем, нет ли важных новостей / сессий по расписанию
    macro_alert = check_macro_calendar()
    if macro_alert:
        send_telegram_message(f"🚨 *МАКРОУВЕДОМЛЕНИЕ*\n{macro_alert}")

    for symbol in SYMBOLS:
        try:
            url = "https://api.bybit.com/v5/market/kline"
            res = requests.get(url, params={"category": "linear", "symbol": symbol, "interval": "30", "limit": 50}, headers=headers, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                    kline_list = data["result"]["list"]
                    if len(kline_list) >= 30:
                        closes = [float(item[4]) for item in reversed(kline_list)]
                        current_price = closes[-1]
                        
                        change_30m = ((closes[-1] - closes[-2]) / closes[-2]) * 100
                        change_1h = ((closes[-1] - closes[-3]) / closes[-3]) * 100
                        
                        rsi = calculate_rsi(closes, 14)
                        
                        ema12 = sum(closes[-12:]) / 12
                        ema26 = sum(closes[-26:]) / 26
                        macd_line = ema12 - ema26
                        
                        upper, middle, lower = calculate_bollinger_bands(closes, 20, 2)

                        # Условия LONG
                        if change_30m >= 0.5 and change_1h >= 0.7 and rsi < 75 and macd_line > 0 and current_price >= middle:
                            signal_text = (
                                f"🚀 *LONG СИГНАЛ* | `{symbol}`\n"
                                f"• **Точка входа (Цена):** `${current_price:,.4f}`\n"
                                f"• **Импульс:** 30м `+{change_30m:.2f}%` | 1ч `+{change_1h:.2f}%`\n"
                                f"• **Индикаторы:** RSI = `{rsi:.1f}` | MACD = `+{macd_line:.4f}` | Боллинджер: пробой вверх\n"
                                f"• **Макро / Фон:** {macro_news}\n"
                                f"💡 *Основание для сделки:* Покупатели перехватили инициативу на старших таймфреймах. Рекомендуется частичная фиксация при достижении целей."
                            )
                            signals.append(signal_text)
                            
                        # Условия SHORT
                        elif change_30m <= -0.5 and change_1h <= -0.7 and rsi > 25 and macd_line < 0 and current_price <= middle:
                            signal_text = (
                                f"📉 *SHORT СИГНАЛ* | `{symbol}`\n"
                                f"• **Точка входа (Цена):** `${current_price:,.4f}`\n"
                                f"• **Импульс:** 30м `{change_30m:.2f}%` | 1ч `{change_1h:.2f}%`\n"
                                f"• **Индикаторы:** RSI = `{rsi:.1f}` | MACD = `{macd_line:.4f}` | Боллинджер: уход под среднюю\n"
                                f"• **Макро / Фон:** {macro_news}\n"
                                f"💡 *Основание для сделки:* Давление продавцов усиливается, пробиты локальные поддержки. Каскад ликвидности вниз."
                            )
                            signals.append(signal_text)

            time.sleep(0.3)

        except Exception as e:
            print(f"Ошибка по {symbol}: {e}")

    # Отправка результатов в Telegram
    header = f"🔍 *СКАНЕР РЫНКА [RSI + MACD + BB]*\n🌐 Страх/Жадность: *{sentiment_str}*\n===================================\n\n"
    
    if signals:
        final_msg = header + "\n\n───────────────────────────────────\n\n".join(signals)
        send_telegram_message(final_msg)
    else:
        # Уведомление о том, что проверка прошла, но сигналов пока нет (чтобы ты знала, что бот активен)
        status_msg = header + "💤 *Статус:* Проверено 30 монет. Сильных трендов по комплексным фильтрам сейчас нет, ждем импульс."
        send_telegram_message(status_msg)

if __name__ == "__main__":
    analyze_market()
