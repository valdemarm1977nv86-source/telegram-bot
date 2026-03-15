import logging
import os
import random
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InputFile
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

POST_INTERVAL = 3600
RANDOM_DELAY_MIN = 300
RANDOM_DELAY_MAX = 900

PHOTO_PATH = "photo.jpg"

TEXT = """
🔥 БАТРАК — работа для тех, кто готов зарабатывать

💰 Высокие выплаты
📍 Работа рядом
⚡ Быстрый старт

👇 Нажмите кнопку ниже чтобы оставить заявку
"""

POLICY = """
📄 Политика обработки персональных данных

Отправляя номер телефона через бота,
вы соглашаетесь на обработку персональных данных.

Собираемые данные:
• имя
• номер телефона
• username Telegram
"""

logging.basicConfig(level=logging.INFO)

# Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)
sheet = client.open("batrak_leads").sheet1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with open(PHOTO_PATH, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=TEXT
        )

    keyboard = [
        [InlineKeyboardButton("✅ Согласен", callback_data="agree")]
    ]

    await update.message.reply_text(
        POLICY,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    contact_button = KeyboardButton(
        "📞 Отправить контакт",
        request_contact=True
    )

    keyboard = [[contact_button]]

    await query.message.reply_text(
        "Нажмите кнопку чтобы отправить номер",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact

    name = contact.first_name
    phone = contact.phone_number
    user = update.message.from_user.username
    user_id = update.message.from_user.id

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        name,
        phone,
        user,
        user_id
    ])

    text = f"""
🔥 Новая заявка

Имя: {name}
Username: @{user}
Телефон: {phone}
ID: {user_id}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Ваша заявка отправлена."
    )


async def autopost(context: ContextTypes.DEFAULT_TYPE):

    with open(PHOTO_PATH, "rb") as photo:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=TEXT
        )


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(agree, pattern="agree"))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    interval = POST_INTERVAL + random.randint(
        RANDOM_DELAY_MIN,
        RANDOM_DELAY_MAX
    )

    app.job_queue.run_repeating(
        autopost,
        interval=interval,
        first=60
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
