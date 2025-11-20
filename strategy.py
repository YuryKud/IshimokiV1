import pandas as pd
import pandas_ta as ta  # Импортируем pandas_ta вместо talib


class Strategy:
    def __init__(self, api, symbol, interval, rsi_overbought, rsi_oversold):
        self.api = api
        self.symbol = symbol
        self.interval = interval
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def evaluate(self, candles):
        """
        Оценка сигнала стратегии на основе данных свечей.

        :param candles: Список свечей.
        :return: Сигнал "BUY", "SELL" или "HOLD".
        """
        # Переворачиваем данные свечей, чтобы последняя свеча была самой актуальной
        candles = candles[::-1]

        # Преобразование данных свечей в DataFrame
        df = pd.DataFrame([candle[:6] for candle in candles], columns=[
                          "timestamp", "open", "high", "low", "close", "volume"])
        df["close"] = df["close"].astype(float)

        # Расчёт индикаторов Ишимоку
        high = df["high"]
        low = df["low"]
        close = df["close"]
        tenkan_sen = (high.rolling(window=9).max() +
                      low.rolling(window=9).min()) / 2
        kijun_sen = (high.rolling(window=26).max() +
                     low.rolling(window=26).min()) / 2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        senkou_span_b = ((high.rolling(window=52).max() +
                         low.rolling(window=52).min()) / 2).shift(26)

        # Расчёт RSI с использованием pandas_ta
        df.ta.rsi(length=14, append=True)  # Добавляем RSI к DataFrame
        rsi = df["RSI_14"]  # Получаем RSI из DataFrame

        # Условия для BUY
        if close.iloc[-1] > senkou_span_a.iloc[-1] and close.iloc[-1] > senkou_span_b.iloc[-1]:  # Цена выше облака
            # Tenkan Sen выше Kijun Sen и RSI не в зоне перекупленности
            if tenkan_sen.iloc[-1] > kijun_sen.iloc[-1] and rsi.iloc[-1] < self.rsi_overbought:
                return "BUY"

        # Условия для SELL
        # Цена ниже облака
        elif close.iloc[-1] < senkou_span_a.iloc[-1] and close.iloc[-1] < senkou_span_b.iloc[-1]:
            # Tenkan Sen ниже Kijun Sen и RSI не в зоне перепроданности
            if tenkan_sen.iloc[-1] < kijun_sen.iloc[-1] and rsi.iloc[-1] > self.rsi_oversold:
                return "SELL"

        return "HOLD"

    def calculate_rsi(self, candles):
        """
        Расчет RSI на основе данных свечей.

        :param candles: Список свечей.
        :return: Последнее значение RSI.
        """
        # Переворачиваем данные свечей, чтобы последняя свеча была самой актуальной
        candles = candles[::-1]

        # Преобразование данных свечей в DataFrame
        df = pd.DataFrame([candle[:6] for candle in candles], columns=[
            "timestamp", "open", "high", "low", "close", "volume"])
        df["close"] = df["close"].astype(float)

        # Расчёт RSI с использованием pandas_ta
        df.ta.rsi(length=14, append=True)  # Добавляем RSI к DataFrame
        rsi = df["RSI_14"]  # Получаем RSI из DataFrame

        return rsi.iloc[-1]  # Возвращаем последнее значение RSI

    def check_cross_flag(self, candles):
        """
        Проверка флага пересечения Tenkan Sen и Kijun Sen.

        :param candles: Список свечей.
        :return: "golden_cross", "death_cross" или None, если пересечения нет.
        """
        # Переворачиваем данные свечей, чтобы последняя свеча была самой актуальной
        candles = candles[::-1]

        # Преобразование данных свечей в DataFrame
        df = pd.DataFrame([candle[:6] for candle in candles], columns=[
                          "timestamp", "open", "high", "low", "close", "volume"])
        df["close"] = df["close"].astype(float)

        # Расчёт индикаторов Ишимоку
        high = df["high"]
        low = df["low"]
        tenkan_sen = (high.rolling(window=9).max() +
                      low.rolling(window=9).min()) / 2
        kijun_sen = (high.rolling(window=26).max() +
                     low.rolling(window=26).min()) / 2

        # Проверка пересечения Tenkan Sen и Kijun Sen
        # увеличил показатель с 2 до 4 чтобы крест держался дольше
        if tenkan_sen.iloc[-1] > kijun_sen.iloc[-1] and tenkan_sen.iloc[-4] <= kijun_sen.iloc[-4]:
            return "golden_cross"  # Золотой крест: Tenkan Sen пересекает Kijun Sen снизу вверх
        # увеличил показатель с 2 до 4 чтобы крест держался дольше
        elif tenkan_sen.iloc[-1] < kijun_sen.iloc[-1] and tenkan_sen.iloc[-4] >= kijun_sen.iloc[-4]:
            return "death_cross"  # Мертвый крест: Tenkan Sen пересекает Kijun Sen сверху вниз

        return None  # Пересечения нет
