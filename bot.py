
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")

USERS = {
    "Женя": {"chat_id": "@kkkv22", "city": "Warsaw"},
    "Никита": {"chat_id": "nikita_chat_id", "city": "Warsaw"},
    "Рома": {"chat_id": "@roman_babun", "city": "Rivne"},
    "Витек": {"chat_id": "@viktip09", "city": "Kelowna"},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает!")

def get_weather(city: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return "Не удалось получить погоду."
    weather = response["weather"][0]["description"]
    temp = response["main"]["temp"]
    return f"Погода в {city}: {weather}, {temp}°C"

async def send_weather(application):
    for user, data in USERS.items():
        try:
            weather = get_weather(data["city"])
            await application.bot.send_message(chat_id=data["chat_id"], text=weather)
        except Exception as e:
            logging.error(f"Ошибка при отправке погоды {user}: {e}")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather, "cron", hour=9, minute=0, args=[application])
    scheduler.start()

    await application.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
