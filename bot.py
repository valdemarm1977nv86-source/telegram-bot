import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

POST_GROUPS = [
    # сюда потом добавим группы
]

PRODUCT_PATH = "products/01_Maxihod_Sani"

# =========================
# WEB SERVER (для Render)
# =========================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("WEB SERVER STARTED")
    server.serve_forever()

# =========================
# КОМАНДА START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("Поделиться номером", request_contact=True)]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    photos = [
        f"{PRODUCT_PATH}/1.jpg",
        f"{PRODUCT_PATH}/2.jpg"
    ]

    text = open(f"{PRODUCT_PATH}/description.txt").read()

    try:
        await update.message.reply_photo(
            photo=open(photos[0], "rb"),
            caption=text,
            reply_markup=reply_markup
        )
    except:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )

# =========================
# ПОЛУЧЕНИЕ НОМЕРА
# =========================

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    text = f"""
Новая заявка

Имя: {user.first_name}
Username: @{user.username}
Телефон: {contact.phone_number}
ID: {user.id}
"""

    await context.bot.send_message(
        ADMIN_ID,
        text
    )

    await update.message.reply_text(
        "Спасибо! Мы скоро свяжемся с вами."
    )

# =========================
# АВТОПОСТ
# =========================

async def autopost(application):

    print("AUTOP POST START")

    photos = [
        f"{PRODUCT_PATH}/1.jpg",
        f"{PRODUCT_PATH}/2.jpg"
    ]

    text = open(f"{PRODUCT_PATH}/description.txt").read()

    for group in POST_GROUPS:

        try:

            await application.bot.send_photo(
                chat_id=group,
                photo=open(photos[0], "rb"),
                caption=text
            )

            print("POSTED:", group)

        except Exception as e:

            print("POST ERROR:", group, e)

            try:
                await application.bot.send_message(
                    ADMIN_ID,
                    f"Ошибка постинга в {group}\n{e}"
                )
            except:
                pass

# =========================
# ЦИКЛ АВТОПОСТА
# =========================

async def autopost_loop(application):

    await asyncio.sleep(120)

    while True:

        try:
            await autopost(application)
        except Exception as e:
            print("AUTOP ERROR:", e)

        await asyncio.sleep(7200)

# =========================
# MAIN
# =========================

def main():

    print("BOT STARTED")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    loop = asyncio.get_event_loop()

    loop.create_task(
        autopost_loop(application)
    )

    application.run_polling()

# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":

    from threading import Thread

    web_thread = Thread(target=run_web)
    web_thread.start()

    main()
