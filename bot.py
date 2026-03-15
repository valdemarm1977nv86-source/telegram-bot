import os
import json
import asyncio
import random
from threading import Thread
from flask import Flask

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ---------------- CONFIG ----------------

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]
CHANNEL_ID = config["CHANNEL_ID"]

POST_INTERVAL = config["POST_INTERVAL"]
RANDOM_DELAY_MIN = config["RANDOM_DELAY_MIN"]
RANDOM_DELAY_MAX = config["RANDOM_DELAY_MAX"]

PRODUCT_FOLDER = "products/01_Maxihod_Sani"

# ---------------- KEEP ALIVE ----------------

app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📄 Политика обработки персональных данных

Отправляя свой номер телефона через данного бота,
вы даете согласие на обработку персональных данных.

Собираемые данные:
• имя
• номер телефона
• Telegram username

Цель обработки данных:
• связь с клиентом
• оформление заявки
• консультация по товару

Данные не передаются третьим лицам
и используются только для связи с клиентом.

Нажимая кнопку «Согласен», вы подтверждаете
согласие на обработку персональных данных.
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Согласен", callback_data="agree")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# ---------------- AGREEMENT ----------------

async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    button = KeyboardButton(
        "📞 Отправить контакт",
        request_contact=True
    )

    keyboard = ReplyKeyboardMarkup(
        [[button]],
        resize_keyboard=True
    )

    await query.message.reply_text(
        "Нажмите кнопку ниже чтобы отправить номер телефона",
        reply_markup=keyboard
    )

# ---------------- CONTACT ----------------

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    name = contact.first_name
    phone = contact.phone_number
    username = user.username

    text = (
        "🔥 Новая заявка\n\n"
        f"Имя: {name}\n"
        f"Username: @{username}\n"
        f"Телефон: {phone}\n"
        f"ID: {user.id}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Мы скоро свяжемся с вами."
    )

# ---------------- AUTOPOST ----------------

async def autopost(app):

    while True:

        try:

            images = []

            for file in os.listdir(PRODUCT_FOLDER):

                if file.endswith(".jpg") or file.endswith(".png"):

                    images.append(
                        os.path.join(PRODUCT_FOLDER, file)
                    )

            images.sort()

            media = []

            for img in images:

                media.append(
                    InputMediaPhoto(
                        media=open(img, "rb")
                    )
                )

            with open(
                f"{PRODUCT_FOLDER}/description.txt",
                "r",
                encoding="utf-8"
            ) as f:

                caption = f.read()

            media[0].caption = caption

            await app.bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=media
            )

            print("POSTED SUCCESS")

        except Exception as e:

            print("POST ERROR:", e)

        delay = POST_INTERVAL + random.randint(
            RANDOM_DELAY_MIN,
            RANDOM_DELAY_MAX
        )

        await asyncio.sleep(delay)

# ---------------- MAIN ----------------

async def main():

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        CallbackQueryHandler(agree, pattern="agree")
    )

    application.add_handler(
        MessageHandler(filters.CONTACT, contact_handler)
    )

    asyncio.create_task(
        autopost(application)
    )

    print("BOT STARTED")

    await application.run_polling()

# ---------------- RUN ----------------

keep_alive()

asyncio.run(main())
