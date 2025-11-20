import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Данные для отправки почты
EMAIL = "yury.kud@yandex.ru"
# Убедитесь, что это правильный пароль или пароль приложения
EMAIL_PASSWORD = "mlpgztrflwxyslop"
EMAIL_RECIPIENT = "yury_kud@mail.ru"


def send_test_email():
    try:
        # Создание сообщения
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = EMAIL_RECIPIENT
        msg["Subject"] = "Тестовое сообщение"

        # Текст сообщения
        body = "Это тестовое сообщение для проверки отправки почты."
        msg.attach(MIMEText(body, "plain"))

        # Подключение к серверу и отправка сообщения
        print("Подключение к SMTP-серверу...")
        server = smtplib.SMTP("smtp.yandex.ru", 587)
        server.starttls()
        print("Авторизация...")
        server.login(EMAIL, EMAIL_PASSWORD)
        print("Отправка сообщения...")
        server.sendmail(EMAIL, EMAIL_RECIPIENT, msg.as_string())
        server.quit()

        print("Сообщение успешно отправлено!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Ошибка авторизации: {e}")
        print("Проверьте логин и пароль. Если используется двухфакторная аутентификация, убедитесь, что используется пароль приложения.")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")


# Запуск функции отправки тестового сообщения
send_test_email()
