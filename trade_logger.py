import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


class TradeLogger:
    def __init__(self, log_file="trade_logs.log", email_enabled=False):
        self.log_file = log_file
        self.email_enabled = email_enabled

        # Настройка логирования в файл
        self.logger = logging.getLogger("TradeLogger")
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_trade(self, action, symbol, price, quantity, reason, context, additional_info=None):
        """
        Логирование сделки с обоснованием и контекстом.

        :param action: Действие (например, "BUY" или "SELL").
        :param symbol: Торговый символ (например, "BTCUSDT").
        :param price: Цена сделки.
        :param quantity: Количество.
        :param reason: Обоснование сделки.
        :param context: Контекст сделки (например, наличие открытой позиции, тип креста и т.д.).
        :param additional_info: Дополнительная информация (опционально).
        """
        message = (
            f"Сделка: {action}\n"
            f"Символ: {symbol}\n"
            f"Цена: {price}\n"
            f"Количество: {quantity}\n"
            f"Обоснование: {reason}\n"
            f"Контекст: {context}\n"
        )

        if additional_info:
            message += f"Дополнительная информация: {additional_info}\n"

        # Логирование в файл
        self.logger.info(message)

        # Отправка по электронной почте (если включено)
        if self.email_enabled:
            self.send_email(message)

    def send_email(self, message):
        """
        Отправка сообщения по электронной почте.

        :param message: Текст сообщения.
        """
        try:
            email = os.getenv("EMAIL")
            password = os.getenv("EMAIL_PASSWORD")
            recipient = os.getenv("EMAIL_RECIPIENT")

            msg = MIMEMultipart()
            msg["From"] = email
            msg["To"] = recipient
            msg["Subject"] = "Торговое уведомление"

            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP("smtp.yandex.ru", 587)
            server.starttls()
            server.login(email, password)
            server.sendmail(email, recipient, msg.as_string())
            server.quit()

            self.logger.info("Сообщение отправлено по электронной почте.")
        except Exception as e:
            self.logger.error(f"Ошибка при отправке email: {e}")

    def disable(self):
        """
        Отключение логирования.
        """
        self.logger.handlers.clear()
        self.email_enabled = False
