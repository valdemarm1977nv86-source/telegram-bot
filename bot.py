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
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

# ---------- FLASK SERVER ----------

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive"


def run_web():
    app.run(host="0.0.0.0", port=8080)


# ---------- CONFIG ----------

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]
CHANNEL_ID = config["CHANNEL_ID"]

POST_INTERVAL = config["POST_INTERVAL"]
RANDOM_DELAY_MIN = config["RANDOM_DELAY_MIN"]
RANDOM_DELAY_MAX = config["RANDOM_DELAY_MAX"]

PRODUCT_FOLDER = "products/01_Maxihod_Sani"


# ---------- START ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📄 Политика обработки персональных данных

Отправляя номер телефона через данного бота,
вы даете согласие на обработку персональных данных.

Собираемые данные:
• имя
• номер телефона
• username Telegram

Цель:
• связь с клиентом
• оформление заявки
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Согласен", callback_data="agree")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)


# ---------- AGREEMENT ----------

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
        "Нажмите кнопку чтобы отправить номер",
        reply_markup=keyboard
    )


# ---------- CONTACT ----------

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    username = user.username if user.username else "нет"

    text = (
        "🔥 Новая заявка\n\n"
        f"Имя: {contact.first_name}\n"
        f"Username: @{username}\n"
        f"Телефон: {contact.phone_number}\n"
        f"ID: {user.id}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Мы скоро свяжемся с вами."
    )


# ---------- AUTOPOST ----------

async def autopost(bot):

    await asyncio.sleep(60)

    while True:

        try:

            images = []

            for file in os.listdir(PRODUCT_FOLDER):
                if file.endswith(".jpg") or file.endswith(".png"):
                    images.append(os.path.join(PRODUCT_FOLDER, file))

            images.sort()

            with open(
                f"{PRODUCT_FOLDER}/description.txt",
                "r",
                encoding="utf-8"
            ) as f:
                caption = f.read()

            media = []

            for i, img in enumerate(images):

                if i == 0:
                    media.append(
                        InputMediaPhoto(
                            media=open(img, "rb"),
                            caption=caption
                        )
                    )
                else:
                    media.append(
                        InputMediaPhoto(
                            media=open(img, "rb")
                        )
                    )

            await bot.send_media_group(
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


# ---------- MAIN ----------

async def main():

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(agree, pattern="agree"))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    asyncio.create_task(
        autopost(application.bot)
    )

    print("BOT STARTED")

    await application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


# ---------- RUN ----------

if __name__ == "__main__":

    Thread(target=run_web).start()

    asyncio.run(main())
