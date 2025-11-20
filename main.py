import os
from dotenv import load_dotenv
import logging
from exchange import BybitAPI
from strategy import Strategy
from trade_logger import TradeLogger
import time

# Загрузка переменных из .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SYMBOL = os.getenv("SYMBOL")
INTERVAL = os.getenv("INTERVAL", 15)
RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", 70))
RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", 30))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 1.0))
TESTNET = os.getenv("TESTNET", "True") == "True"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("trading.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Инициализация API и стратегии
bybit_api = BybitAPI(API_KEY, API_SECRET, TESTNET)
strategy = Strategy(bybit_api, SYMBOL, INTERVAL, RSI_OVERBOUGHT, RSI_OVERSOLD)

# Инициализация TradeLogger
# Включить/отключить email уведомления
trade_logger = TradeLogger(email_enabled=True)


def get_position_size(balance, risk_percent, last_price):
    """
    Расчет размера позиции на основе процента риска и последней цены.

    :param balance: Доступный баланс.
    :param risk_percent: Процент риска от депозита.
    :param last_price: Последняя цена актива.
    :return: Размер позиции или None, если расчет невозможен.
    """
    if balance == 0:
        logging.warning("Баланс равен 0, невозможно открыть позицию.")
        return None

    position_value = balance * risk_percent
    position_size = position_value / last_price

    # Округление до 3 знаков после запятой
    position_size = round(position_size, 3)

    # Минимальный размер позиции (например, 0.001)
    min_position_size = 0.001

    # Если размер позиции меньше минимального, возвращаем None
    if position_size < min_position_size:
        logging.warning(
            f"Размер позиции ({position_size}) меньше минимального ({min_position_size}). Позиция не будет открыта."
        )
        return None

    return position_size


def main():
    """
    Основной цикл стратегии.
    """
    logging.info("Запуск стратегии...")
    while True:
        try:
            # Получение баланса
            balance = bybit_api.get_balance()
            if balance == 0:
                logging.warning("Баланс равен 0, пропуск итерации.")
                time.sleep(60)
                continue

            # Получение данных свечей
            candles = bybit_api.get_kline_data(
                SYMBOL, INTERVAL, start=None, end=None)
            if not candles or len(candles) < 2:
                logging.warning("Недостаточно данных для анализа.")
                time.sleep(60)
                continue

            # Цена закрытия предыдущей завершенной свечи
            previous_close = float(candles[-2][4])

            # Расчет размера позиции
            position_size = get_position_size(
                balance, RISK_PERCENT, previous_close)
            if position_size is None:
                logging.warning("Невозможно рассчитать размер позиции.")
                time.sleep(60)
                continue

            logging.info(
                f"Доступный баланс: {balance} USDT. Размер позиции: {position_size}")

            # Проверка открытых позиций
            open_positions = bybit_api.get_open_positions(SYMBOL)
            has_open_position = len(open_positions) > 0
            current_position_side = open_positions[0]["side"].lower(
            ) if has_open_position else None

            # Оценка сигнала стратегии
            signal = strategy.evaluate(candles[:-1])

            # Проверка флага пересечения Tenkan Sen и Kijun Sen
            cross_flag = strategy.check_cross_flag(candles[:-1])

            # Проверка RSI для закрытия позиции
            rsi_value = strategy.calculate_rsi(candles[:-1])
            if has_open_position:
                if current_position_side == "buy" and rsi_value < 50:
                    logging.info(
                        "Закрытие длинной позиции по RSI (пересечение 50 сверху вниз)...")
                    bybit_api.place_order(SYMBOL, "Sell", position_size)
                    trade_logger.log_trade(
                        action="SELL",
                        symbol=SYMBOL,
                        price=previous_close,
                        quantity=position_size,
                        reason="Закрытие длинной позиции по RSI (пересечение 50 сверху вниз).",
                        context=context
                    )
                    continue  # Пропустить оставшуюся часть цикла, так как позиция закрыта
                elif current_position_side == "sell" and rsi_value > 50:
                    logging.info(
                        "Закрытие короткой позиции по RSI (пересечение 50 снизу вверх)...")
                    bybit_api.place_order(SYMBOL, "Buy", position_size)
                    trade_logger.log_trade(
                        action="BUY",
                        symbol=SYMBOL,
                        price=previous_close,
                        quantity=position_size,
                        reason="Закрытие короткой позиции по RSI (пересечение 50 снизу вверх).",
                        context=context
                    )
                    continue  # Пропустить оставшуюся часть цикла, так как позиция закрыта

            # Формирование контекста для логирования
            context = {
                "has_open_position": has_open_position,
                "current_position_side": current_position_side,
                "cross_flag": cross_flag,
                "rsi_value": rsi_value,
            }

            # Логика открытия/закрытия позиций
            if signal == "BUY":
                if has_open_position:
                    if current_position_side == "sell":
                        logging.info(
                            "Закрытие короткой позиции перед открытием длинной...")
                        bybit_api.place_order(SYMBOL, "Buy", position_size)
                        trade_logger.log_trade(
                            action="BUY",
                            symbol=SYMBOL,
                            price=previous_close,
                            quantity=position_size,
                            reason="Закрытие короткой позиции перед открытием длинной.",
                            context=context
                        )
                    else:
                        logging.info(
                            "Длинная позиция уже открыта. Новый ордер не размещается.")
                else:
                    # Проверка на золотой крест перед открытием новой позиции
                    if cross_flag == "golden_cross":
                        logging.info("Сигнал на покупку. Размещение ордера...")
                        bybit_api.place_order(SYMBOL, "Buy", position_size)
                        trade_logger.log_trade(
                            action="BUY",
                            symbol=SYMBOL,
                            price=previous_close,
                            quantity=position_size,
                            reason="Сигнал на покупку: цена выше облака Ишимоку, Tenkan Sen > Kijun Sen, RSI < 70.",
                            context=context
                        )
                    else:
                        logging.info(
                            "Сигнал на покупку есть, но золотой крест не сформирован. Позиция не открыта.")
            elif signal == "SELL":
                if has_open_position:
                    if current_position_side == "buy":
                        logging.info(
                            "Закрытие длинной позиции перед открытием короткой...")
                        bybit_api.place_order(SYMBOL, "Sell", position_size)
                        trade_logger.log_trade(
                            action="SELL",
                            symbol=SYMBOL,
                            price=previous_close,
                            quantity=position_size,
                            reason="Закрытие длинной позиции перед открытием короткой.",
                            context=context
                        )
                    else:
                        logging.info(
                            "Короткая позиция уже открыта. Новый ордер не размещается.")
                else:
                    # Проверка на мертвый крест перед открытием новой позиции
                    if cross_flag == "death_cross":
                        logging.info("Сигнал на продажу. Размещение ордера...")
                        bybit_api.place_order(SYMBOL, "Sell", position_size)
                        trade_logger.log_trade(
                            action="SELL",
                            symbol=SYMBOL,
                            price=previous_close,
                            quantity=position_size,
                            reason="Сигнал на продажу: цена ниже облака Ишимоку, Tenkan Sen < Kijun Sen, RSI > 30.",
                            context=context
                        )
                    else:
                        logging.info(
                            "Сигнал на продажу есть, но мертвый крест не сформирован. Позиция не открыта.")
            else:
                logging.info("Нет торгового сигнала.")

            time.sleep(60)  # Пауза между итерациями (60 секунд)

        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}", exc_info=True)
            time.sleep(60)


if __name__ == "__main__":
    main()  # Запуск основной функции
