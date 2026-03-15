import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1584040288

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHOTO1 = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/1.jpg")
PHOTO2 = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/2.jpg")
DESCRIPTION = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/description.txt")


# ======================
# HTTP SERVER ДЛЯ RENDER
# ======================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")


def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


# ======================
# START
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("🛒 Оставить заявку")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    try:

        with open(DESCRIPTION, "r", encoding="utf-8") as f:
            text = f.read()

        with open(PHOTO1, "rb") as p1:
            await update.message.reply_photo(photo=p1)

        with open(PHOTO2, "rb") as p2:
            await update.message.reply_photo(photo=p2)

        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )

    except Exception as e:

        print("ERROR:", e)

        await update.message.reply_text(
            "Ошибка загрузки товара",
            reply_markup=reply_markup
        )


# ======================
# СОГЛАСИЕ
# ======================

async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📄 Согласие на обработку персональных данных

Нажимая кнопку "Согласен", вы разрешаете
обработку вашего номера телефона для связи
по заявке.

Данные используются только для связи.
"""

    keyboard = [[KeyboardButton("✅ Согласен")]]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ======================
# ЗАПРОС ТЕЛЕФОНА
# ======================

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("📱 Поделиться номером", request_contact=True)]]

    await update.message.reply_text(
        "Нажмите кнопку чтобы отправить номер телефона",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ======================
# ПОЛУЧЕНИЕ КОНТАКТА
# ======================

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    username = user.username if user.username else "нет"

    text = f"""
🔥 Новая заявка

Имя: {user.first_name}
Username: @{username}
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


# ======================
# MAIN
# ======================

def main():

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Оставить"), consent)
    )

    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Согласен"), ask_phone)
    )

    application.add_handler(
        MessageHandler(filters.CONTACT, get_contact)
    )

    print("BOT STARTED")

    application.run_polling()


if __name__ == "__main__":

    threading.Thread(target=run_web).start()

    main()
