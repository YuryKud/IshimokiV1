from pybit.unified_trading import HTTP, WebSocket
import logging
import time


class BybitAPI:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.http = HTTP(testnet=testnet, api_key=api_key,
                         api_secret=api_secret)
        self.ws = None

    def connect_websocket(self):
        try:
            self.ws = WebSocket(
                testnet=self.testnet,
                channel_type="linear",
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            self.ws.on_message = self._on_message
            logging.info("WebSocket connected.")
        except Exception as e:
            logging.error(f"Error connecting to WebSocket: {e}")
            time.sleep(5)
            self.connect_websocket()

    def _on_message(self, message):
        try:
            logging.info(f"WebSocket message received: {message}")
        except Exception as e:
            logging.error(f"Error processing WebSocket message: {e}")

    def get_kline_data(self, symbol, interval, start, end):
        """ Получение исторических свечных данных """
        try:
            response = self.http.get_kline(
                category="linear", symbol=symbol, interval=interval, start=start, end=end)
            if response["retCode"] != 0:
                logging.error(
                    f"Ошибка получения Kline: {response['retMsg']} (Код ошибки: {response['retCode']})")
                return []

            candles = response["result"]["list"]
            if not candles:
                logging.warning("Bybit вернул пустой список свечей.")
                return []

            return candles
        except Exception as e:
            logging.error(f"Ошибка в get_kline_data: {e}", exc_info=True)
            return []

    def place_order(self, symbol, side, qty, tp=None, sl=None, order_type="Market", recv_window=10000):
        """ Размещение ордера с тейк-профитом и стоп-лоссом """
        try:
            # Подготовка параметров для запроса
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(qty),
                "timeInForce": "GTC",
                "recvWindow": recv_window
            }

            # Добавляем takeProfit и stopLoss, только если они указаны
            if tp is not None:
                params["takeProfit"] = str(tp)
            if sl is not None:
                params["stopLoss"] = str(sl)

            response = self.http.place_order(**params)
            if response["retCode"] != 0:
                logging.error(
                    f"Ошибка размещения ордера: {response['retMsg']}")
            else:
                logging.info(f"Ордер размещён: {response}")
            return response
        except Exception as e:
            logging.error(f"Ошибка размещения ордера: {e}", exc_info=True)
            return None

    def get_open_positions(self, symbol):
        """ Получение открытых позиций для символа """
        try:
            response = self.http.get_positions(
                accountType="UNIFIED", category="linear", symbol=symbol)
            if response["retCode"] != 0:
                logging.error(
                    f"Ошибка получения позиций: {response['retMsg']} (Код ошибки: {response['retCode']})")
                return []

            positions = [pos for pos in response["result"]
                         ["list"] if float(pos["size"]) > 0]
            return positions
        except Exception as e:
            logging.error(f"Ошибка в get_open_positions: {e}", exc_info=True)
            return []

    def get_balance(self):
        """ Получение доступного баланса USDT из UNIFIED аккаунта """
        try:
            response = self.http.get_wallet_balance(
                accountType="UNIFIED", coin="USDT")
            if response["retCode"] != 0:
                logging.error(
                    f"Ошибка получения баланса: {response['retMsg']} (Код ошибки: {response['retCode']})")
                return 0

            for account in response.get("result", {}).get("list", []):
                for asset in account.get("coin", []):
                    if asset.get("coin") == "USDT":
                        available_balance = asset.get(
                            "availableToWithdraw") or asset.get("walletBalance") or "0"
                        try:
                            available_balance = float(available_balance)
                        except ValueError:
                            logging.error(
                                f"Ошибка преобразования баланса USDT: {available_balance}")
                            return 0

                        logging.info(
                            f"Баланс USDT в UNIFIED: {available_balance}")
                        return available_balance

            logging.warning("Баланс USDT не найден в UNIFIED аккаунте!")
            return 0
        except Exception as e:
            logging.error(f"Ошибка получения баланса (UNIFIED): {e}")
            return 0
