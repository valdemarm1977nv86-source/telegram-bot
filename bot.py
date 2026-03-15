import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from flask import Flask
from threading import Thread

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InputMediaPhoto
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

PHOTO1 = "photo1.jpg"
PHOTO2 = "photo2.jpg"

# ==============================
# GOOGLE SHEETS
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

sheet = client.open("batrak_leads").sheet1

# ==============================
# WEB SERVER (для Render)
# ==============================

app = Flask('')


@app.route('/')
def home():
    return "bot is running"


def run():
    app.run(host='0.0.0.0', port=10000)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ==============================
# START
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        media = [
            InputMediaPhoto(open(PHOTO1, "rb")),
            InputMediaPhoto(open(PHOTO2, "rb"))
        ]

        await update.message.reply_media_group(media)

        await update.message.reply_text(
            "САНИ – ВОЛОКУШИ МАКСИХОД"
        )

        await update.message.reply_text(
            """Свяжитесь с нами или оставьте номер телефона 📱

Контакты:

Компания МАКСИХОД  
г. Нижневартовск  
ул. Интернациональная 60

📞 +7 922 447 40 86
📧 MaxihodNV86@yandex.ru
"""
        )

        await update.message.reply_text(
            """👇 Нажимая кнопку ниже вы соглашаетесь  
с обработкой персональных данных."""
        )

        keyboard = [
            [KeyboardButton("📞 Оставить контакт", request_contact=True)]
        ]

        markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "Нажмите кнопку ниже чтобы оставить контакт",
            reply_markup=markup
        )

    except Exception as e:
        print("START ERROR:", e)


# ==============================
# ПОЛУЧЕНИЕ КОНТАКТА
# ==============================

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact

    name = contact.first_name
    phone = contact.phone_number
    user_id = update.effective_user.id
    username = update.effective_user.username

    text = f"""
🔥 Новая заявка

Имя: {name}
Username: @{username}
Телефон: {phone}
ID: {user_id}
"""

    # отправка админу
    await context.bot.send_message(ADMIN_ID, text)

    # запись в Google Sheets
    sheet.append_row([
        name,
        phone,
        username,
        user_id
    ])

    await update.message.reply_text(
        "Спасибо! Мы скоро свяжемся с вами."
    )


# ==============================
# MAIN
# ==============================

def main():

    keep_alive()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.CONTACT, contact)
    )

    print("BOT STARTED")

    application.run_polling()


if __name__ == "__main__":
    main()
