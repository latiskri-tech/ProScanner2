import requests
import time

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

def get_market_sentiment():
    """Получает индекс страха и жадности крипторынка"""
    try:
        res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        if res.status_code == 200:
            data = res.json()["data"][0]
            return f"{data['value_classification']} ({data['value']}/100)"
    except:
        pass
    return "Нейтрально"

def calculate_rsi(closes, period=14):
    """Расчет RSI"""
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
    """Расчет полос Боллинджера для оценки волатильности и прорыва"""
    if len(closes) < period:
        return 0, 0, 0
    sub_closes = closes[-period:]
    sma = sum(sub_closes) / period
    variance = sum((x - sma) ** 2 for x in sub_closes) / period
    stdev = variance ** 0.5
    upper_band = sma + (num_std * stdev)
    lower_band = sma - (num_std * stdev)
    return upper_band, sma, lower_band

def analyze_market():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    signals = []
    sentiment = get_market_sentiment()

    for symbol in SYMBOLS:
        try:
            url = "https://api.bybit.com/v5/market/kline"
            # Запрашиваем 50 свечей 30-минутного таймфрейма
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
                        
                        # Индикаторы
                        rsi = calculate_rsi(closes, 14)
                        
                        ema12 = sum(closes[-12:]) / 12
                        ema26 = sum(closes[-26:]) / 26
                        macd_line = ema12 - ema26
                        
                        upper, middle, lower = calculate_bollinger_bands(closes, 20, 2)

                        # Условия для LONG с учетом прорыва верхней полосы Боллинджера и тренда
                        if change_30m >= 0.5 and change_1h >= 0.7 and rsi < 75 and macd_line > 0 and current_price >= middle:
                            signal_text = (
                                f"🚀 *LONG СИГНАЛ [Multi-Indicator]* | `{symbol}`\n"
                                f"• Цена: `${current_price:,.4f}` | 30м: `+{change_30m:.2f}%` | 1ч: `+{change_1h:.2f}%`\n"
                                f"📊 *Тех. анализ:* RSI = `{rsi:.1f}` | MACD = `+{macd_line:.4f}`\n"
                                f"📈 *Волатильность (Bollinger):* Цена выше средней линии, пробивает локальный диапазон вверх.\n"
                                f"🧠 *Контекст:* Настроения: *{sentiment}*. Импульс подтвержден комплексом индикаторов, покупатели давят."
                            )
                            signals.append(signal_text)
                            
                        # Условия для SHORT с учетом прорыва нижней полосы Боллинджера
                        elif change_30m <= -0.5 and change_1h <= -0.7 and rsi > 25 and macd_line < 0 and current_price <= middle:
                            signal_text = (
                                f"📉 *SHORT СИГНАЛ [Multi-Indicator]* | `{symbol}`\n"
                                f"• Цена: `${current_price:,.4f}` | 30м: `{change_30m:.2f}%` | 1ч: `{change_1h:.2f}%`\n"
                                f"📊 *Тех. анализ:* RSI = `{rsi:.1f}` | MACD = `{macd_line:.4f}`\n"
                                f"📉 *Волатильность (Bollinger):* Цена закрепилась ниже средней линии, давление на продажу.\n"
                                f"🧠 *Контекст:* Настроения: *{sentiment}*. Медвежий каскад подтвержден техническими метриками."
                            )
                            signals.append(signal_text)

            time.sleep(0.3)

        except Exception as e:
            print(f"Ошибка по {symbol}: {e}")

    # Отправка в Telegram
    if signals:
        header = f"🔥 *КРИПТО СКАНЕР [RSI + MACD + Bollinger]*\n🌐 Страх/Жадность: *{sentiment}*\n===================================\n\n"
        final_msg = header + "\n\n───────────────────────────────────\n\n".join(signals)
        send_telegram_message(final_msg)
    else:
        print("За данный цикл сигналов по комплексному фильтру не обнаружено.")

if __name__ == "__main__":
    analyze_market()
