Trading Robot for Bybit

This project is an automated trading system that uses technical indicators to make trading decisions on the Bybit futures market. After opening a position, the robot automatically notifies the user of the trade. The code includes detailed comments for each block. Additionally, there is a separate file (mail.py) for testing trade notification emails. However, the code requires some improvement. Frequent opening and closing of trades was detected on the daily time frame, leading to significant commission losses. Caution is advised when using this robot.

Project Structure Main Files:

exchange.py - Class for working with the Bybit API

strategy.py - Trading strategy implementation

main.py - Main strategy execution loop

trade_logger.py - Logging and notification system

.env - File with configuration parameters (not included in the repository)

Trading Logic

Indicators Used:

Ichimoku Kinko Hayo:

Tenkan Sen (9 periods)

Kijun Sen (26 periods)

Senkou Span A and B (form a cloud)

RSI (Relative Strength Index):

Period: 14 candles

Oversold/Oversold Levels: 70/30

Conditions for Opening Positions:

Long Position (BUY):

Price Above the Ichimoku Cloud

Tenkan Sen > Kijun Sen (Golden Cross)

RSI < 70 (not in overbought zone)

Short position (SELL):

Price below Ichimoku cloud

Tenkan Sen < Kijun Sen (dead cross)

RSI > 30 (not in oversold zone)

Closing conditions:

Long position: RSI crosses level 50 from above

Short position: RSI crosses level 50 from below

Risk management

RISK_PERCENT: Deposit percentage for one trade (default 1%)

Minimum position size: 0.001

Automatic position size calculation based on balance

Environment setup Requirements:

Python 3.7+

Bybit account (live or testnet)

Environment variables (.env):

env

API_KEY=your_bybit_api_key

API_SECRET=your_bybit_api_secret

SYMBOL=BTCUSDT

INTERVAL=15

RSI_OVERBOUGHT=70

RSI_OVERSOLD=30

RISK_PERCENT=1.0

TESTNET=True

EMAIL=your_email@yandex.ru

EMAIL_PASSWORD=your_email_password

EMAIL_RECIPIENT=recipient_email@example.com











Торговый робот для Bybit

Проект представляет собой автоматизированную торговую систему, использующую технические индикаторы для принятия торговых решений на фьючерсном рынке Bybit. После открытия позиций робот автоматически уведомляет пользователя о сделке. В коде предусмотрены подробные комментарии к каждому блоку. Кроме того присутствует отдельный файл для тестирования почтовых отправлений о сделках mail.py. Однако, код требует доработки. При дневном тайм фрейме выявлено частое открытие и закрытие сделок, что приводит к существенным потерям на комиссиях. Необходимо проявить осторожность при использовании данного робота. 

Структура проекта
Основные файлы:

exchange.py - Класс для работы с API Bybit

strategy.py - Реализация торговой стратегии

main.py - Основной цикл выполнения стратегии

trade_logger.py - Система логирования и уведомлений

.env - Файл с конфигурационными параметрами (не включен в репозиторий)

Торговая логика

Используемые индикаторы:

Ишимоку Кинко Хайо:

Tenkan Sen (9 периодов)

Kijun Sen (26 периодов)

Senkou Span A и B (формируют облако)

RSI (Relative Strength Index):

Период: 14 свечей

Уровни перекупленности/перепроданности: 70/30

Условия для открытия позиций:

Длинная позиция (BUY):

Цена выше облака Ишимоку

Tenkan Sen > Kijun Sen (золотой крест)

RSI < 70 (не в зоне перекупленности)

Короткая позиция (SELL):

Цена ниже облака Ишимоку

Tenkan Sen < Kijun Sen (мертвый крест)

RSI > 30 (не в зоне перепроданности)

Условия для закрытия позиций:

Длинная позиция: RSI пересекает уровень 50 сверху вниз

Короткая позиция: RSI пересекает уровень 50 снизу вверх

Управление рисками

RISK_PERCENT: Процент депозита для одной сделки (по умолчанию 1%)

Минимальный размер позиции: 0.001

Автоматический расчет размера позиции на основе баланса

Настройка окружени
я
Требования:

Python 3.7+

Учетная запись Bybit (реальная или тестовая сеть)

Переменные окружения (.env):

env

API_KEY=your_bybit_api_key

API_SECRET=your_bybit_api_secret

SYMBOL=BTCUSDT

INTERVAL=15

RSI_OVERBOUGHT=70

RSI_OVERSOLD=30

RISK_PERCENT=1.0

TESTNET=True

EMAIL=your_email@yandex.ru

EMAIL_PASSWORD=your_email_password

EMAIL_RECIPIENT=recipient_email@example.com
