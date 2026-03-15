import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputMediaPhoto
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

PHOTO1 = "products/01_Maxihod_Sani/1.jpg"
PHOTO2 = "products/01_Maxihod_Sani/2.jpg"
DESCRIPTION = "products/01_Maxihod_Sani/description.txt"


# =========================
# HTTP СЕРВЕР (чтобы Render не засыпал)
# =========================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")


def run_web():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(("0.0.0.0", port), Handler)

    print("WEB SERVER STARTED")

    server.serve_forever()


# =========================
# СТАРТ БОТА
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        with open(DESCRIPTION, "r", encoding="utf-8") as f:
            text = f.read()

        media = [
            InputMediaPhoto(open(PHOTO1, "rb"), caption=text),
            InputMediaPhoto(open(PHOTO2, "rb"))
        ]

        await update.message.reply_media_group(media)

        keyboard = [[KeyboardButton("📞 Оставить контакт")]]

        await update.message.reply_text(
            "👇 Нажмите кнопку ниже чтобы оставить контакт",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    except Exception as e:

        print("ERROR START:", e)

        await update.message.reply_text(
            "Ошибка загрузки товара"
        )


# =========================
# СОГЛАСИЕ НА ДАННЫЕ
# =========================

async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📄 Согласие на обработку персональных данных

Нажимая кнопку ниже, вы соглашаетесь
на обработку вашего номера телефона
для связи по заявке.

Номер используется только
для обратного звонка.
"""

    keyboard = [[
        KeyboardButton(
            "📱 Поделиться номером",
            request_contact=True
        )
    ]]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


# =========================
# ПОЛУЧЕНИЕ НОМЕРА
# =========================

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
        "✅ Спасибо! Мы скоро свяжемся с вами."
    )


# =========================
# ОБРАБОТКА ОШИБОК
# =========================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    print("ERROR:", context.error)


# =========================
# MAIN
# =========================

def main():

    print("BOT STARTING...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("Оставить контакт"),
            consent
        )
    )

    application.add_handler(
        MessageHandler(filters.CONTACT, get_contact)
    )

    application.add_error_handler(error_handler)

    print("BOT STARTED")

    application.run_polling(
        drop_pending_updates=True
    )


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":

    threading.Thread(target=run_web).start()

    main()
