import asyncio
import logging
import os
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Логирование
logging.basicConfig(level=logging.INFO)

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")

# Список пользователей и их городов
users = {
    '@kkkv22': {'name': 'Женя', 'city': 'Warsaw', 'timezone': 'Europe/Warsaw'},
    'nikita': {'name': 'Никита', 'city': 'Warsaw', 'timezone': 'Europe/Warsaw'},
    '@roman_babun': {'name': 'Рома', 'city': 'Rivne', 'timezone': 'Europe/Kiev'},
    '@viktip09': {'name': 'Витек', 'city': 'Kelowna', 'timezone': 'America/Vancouver'},
}

admin_username = 'вставь_сюда_юзернейм_Вити'  # например: '@admin'

# Получение погоды
def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"{description.capitalize()}, {temp}°C"
    else:
        return "Не удалось получить погоду."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот прогноза погоды ☀️")

# Отправка погоды по расписанию
async def send_weather(application):
    for user, info in users.items():
        weather = get_weather(info["city"])
        now = datetime.now(timezone(info["timezone"])).strftime("%H:%M %d.%m")
        message = f"Погода для {info['name']} в {info['city']} на {now}:\n{weather}"

        try:
            await application.bot.send_message(chat_id=user, text=message)
        except Exception as e:
            logging.warning(f"Не удалось отправить сообщение {user}: {e}")

# Главная функция
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Планировщик
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather, 'cron', hour=8, minute=0, args=[app])  # каждый день в 08:00
    scheduler.start()

    print("Бот запущен.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
