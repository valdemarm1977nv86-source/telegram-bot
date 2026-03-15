import os
import threading
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

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

PHOTO1 = "products/01_Maxihod_Sani/1.jpg"
PHOTO2 = "products/01_Maxihod_Sani/2.jpg"
DESCRIPTION = "products/01_Maxihod_Sani/description.txt"


# WEB SERVER (для Render)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")


def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("", port), Handler)
    print("WEB SERVER STARTED")
    server.serve_forever()


# /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        with open(DESCRIPTION, "r", encoding="utf-8") as f:
            text = f.read()

        await update.message.reply_photo(
            photo=open(PHOTO1, "rb"),
            caption=text
        )

        await update.message.reply_photo(
            photo=open(PHOTO2, "rb")
        )

        keyboard = [[KeyboardButton("📞 Оставить контакт", request_contact=True)]]

        await update.message.reply_text(
            "👇 Нажмите кнопку ниже чтобы оставить заявку",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    except Exception as e:

        print("PRODUCT ERROR:", e)

        await update.message.reply_text(
            "Ошибка загрузки товара"
        )


# получение контакта

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    text = f"""
🔥 Новая заявка

Имя: {contact.first_name}
Username: @{user.username}
Телефон: {contact.phone_number}
ID: {user.id}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Мы скоро свяжемся с вами."
    )


# main

def main():

    print("BOT STARTING...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.CONTACT, get_contact)
    )

    print("BOT STARTED")

    application.run_polling(
        drop_pending_updates=True
    )


# запуск

if __name__ == "__main__":

    threading.Thread(target=run_web).start()

    main()
