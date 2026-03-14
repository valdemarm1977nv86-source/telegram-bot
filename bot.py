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

ADMIN_ID = 123456789  # сюда потом поставим твой Telegram ID

GROUPS = [
    "@fishing_shop3"
]

# =========================
# HTTP SERVER (для Render)
# =========================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("🛒 Оставить заявку")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    text = open(
        "products/01_Maxihod_Sani/description.txt",
        encoding="utf-8"
    ).read()

    try:

        await update.message.reply_photo(
            photo=open("products/01_Maxihod_Sani/1.jpg", "rb"),
            caption=text,
            reply_markup=reply_markup
        )

        await update.message.reply_photo(
            photo=open("products/01_Maxihod_Sani/2.jpg", "rb")
        )

    except Exception as e:

        print("PHOTO ERROR:", e)

        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )

# =========================
# КНОПКА ЗАЯВКИ
# =========================

async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
Перед отправкой номера телефона необходимо согласие
на обработку персональных данных.

Нажимая кнопку "Согласен" вы разрешаете
нам связаться с вами по вашему запросу.
"""

    keyboard = [
        [KeyboardButton("✅ Согласен")]
    ]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =========================
# ЗАПРОС ТЕЛЕФОНА
# =========================

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)]
    ]

    await update.message.reply_text(
        "Нажмите кнопку ниже чтобы отправить номер телефона",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =========================
# ПОЛУЧЕНИЕ ТЕЛЕФОНА
# =========================

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    text = f"""
🔥 НОВАЯ ЗАЯВКА

Имя: {user.first_name}
Телефон: {contact.phone_number}
Username: @{user.username}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Мы скоро с вами свяжемся."
    )

# =========================
# АВТОПОСТ
# =========================

async def autopost(application):

    text = open(
        "products/01_Maxihod_Sani/description.txt",
        encoding="utf-8"
    ).read()

    for group in GROUPS:

        try:

            await application.bot.send_photo(
                chat_id=group,
                photo=open("products/01_Maxihod_Sani/1.jpg", "rb"),
                caption=text
            )

            await application.bot.send_photo(
                chat_id=group,
                photo=open("products/01_Maxihod_Sani/2.jpg", "rb")
            )

        except Exception as e:

            print("POST ERROR:", e)

# =========================
# MAIN
# =========================

async def main():

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("🛒 Оставить заявку"),
            consent
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("✅ Согласен"),
            ask_phone
        )
    )

    application.add_handler(
        MessageHandler(
            filters.CONTACT,
            get_contact
        )
    )

    # автопост каждые 2 часа
    asyncio.create_task(
        autopost(application)
    )

    print("BOT STARTED")

    await application.run_polling()

# =========================

if __name__ == "__main__":

    from threading import Thread

    Thread(target=run_web).start()

    asyncio.run(main())
