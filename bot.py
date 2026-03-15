import os
import json
import asyncio
import random

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

Отправляя номер телефона, вы соглашаетесь
на обработку персональных данных.

Собираемые данные:

• имя
• номер телефона
• username Telegram

Цель:

• связь с клиентом
• оформление заявки

Нажимая «Согласен» вы принимаете условия.
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
        "Нажмите кнопку ниже чтобы отправить номер",
        reply_markup=keyboard
    )

# ---------- CONTACT ----------

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    text = (
        "🔥 Новая заявка\n\n"
        f"Имя: {contact.first_name}\n"
        f"Username: @{user.username}\n"
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

async def autopost(app):

    await asyncio.sleep(60)

    while True:

        try:

            images = []

            for file in os.listdir(PRODUCT_FOLDER):

                if file.endswith(".jpg") or file.endswith(".png"):

                    images.append(
                        os.path.join(PRODUCT_FOLDER, file)
                    )

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

# ---------- MAIN ----------

async def main():

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(agree, pattern="agree")
    )

    app.add_handler(
        MessageHandler(filters.CONTACT, contact_handler)
    )

    asyncio.create_task(
        autopost(app)
    )

    print("BOT STARTED")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
