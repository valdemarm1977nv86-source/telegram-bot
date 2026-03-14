import os
import logging
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

PRODUCT_NAME = "Сани-волокуши MAXIHOD"

PRODUCT_TEXT = """
🛷 Сани-волокуши MAXIHOD

Прочные санки для:

• рыбалки  
• охоты  
• перевозки груза  

📍 Нижневартовск

Чтобы узнать цену — нажмите кнопку ниже
"""

BOT_LINK = "https://t.me/batrak_sales_bot"

groups_file = "groups.txt"
backup_file = "backup_leads.txt"

logging.basicConfig(level=logging.INFO)


# ---------------- WEB SERVER (для Render) ----------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")


def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ---------------- СОХРАНЕНИЕ ГРУПП ----------------

def save_group(chat_id):

    try:

        if not os.path.exists(groups_file):
            open(groups_file, "w").close()

        with open(groups_file, "r") as f:
            groups = f.read().splitlines()

        if str(chat_id) not in groups:

            with open(groups_file, "a") as f:
                f.write(str(chat_id) + "\n")

    except Exception as e:
        logging.error(e)


# ---------------- РЕЗЕРВ ЛИДОВ ----------------

def save_backup(text):

    try:

        with open(backup_file, "a", encoding="utf-8") as f:
            f.write(text + "\n\n")

    except:
        pass


# ---------------- УВЕДОМЛЕНИЯ АДМИНУ ----------------

async def notify_admin(context, text):

    try:
        await context.bot.send_message(ADMIN_ID, f"⚠️ {text}")
    except:
        pass


# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        chat = update.effective_chat

        if chat.type in ["group", "supergroup"]:
            save_group(chat.id)
            return

        keyboard = [
            [KeyboardButton("📞 Поделиться номером", request_contact=True)]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(PRODUCT_TEXT)

        await update.message.reply_text(
            "Отправляя номер телефона вы соглашаетесь "
            "с обработкой персональных данных.",
            reply_markup=reply_markup
        )

    except Exception as e:
        await notify_admin(context, f"Ошибка start: {e}")


# ---------------- ПОЛУЧЕНИЕ НОМЕРА ----------------

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        contact = update.message.contact
        user = update.message.from_user

        phone = contact.phone_number

        text = f"""
🔥 Новая заявка

Товар: {PRODUCT_NAME}
Имя: {user.first_name}
Username: @{user.username}
Телефон: {phone}

Источник: Telegram
Дата: {datetime.now()}
"""

        await context.bot.send_message(ADMIN_ID, text)

        save_backup(text)

        await update.message.reply_text(
            "Спасибо! Мы скоро свяжемся с вами."
        )

    except Exception as e:
        await notify_admin(context, f"Ошибка контакта: {e}")


# ---------------- АВТОПОСТИНГ ----------------

async def autopost(context: ContextTypes.DEFAULT_TYPE):

    try:

        if not os.path.exists(groups_file):
            return

        with open(groups_file) as f:
            groups = f.read().splitlines()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔘 Открыть бота", url=BOT_LINK)]
        ])

        for group in groups:

            try:

                await context.bot.send_message(
                    chat_id=int(group),
                    text=PRODUCT_TEXT,
                    reply_markup=keyboard
                )

                await asyncio.sleep(15)

            except Exception as e:
                logging.error(e)

    except Exception as e:
        await notify_admin(context, f"Ошибка автопоста: {e}")


# ---------------- РУЧНОЙ ПОСТ ----------------

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await autopost(context)

    await update.message.reply_text("Пост отправлен.")


# ---------------- MAIN ----------------

def main():

    print("BOT STARTED")

    threading.Thread(target=run_web).start()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("post", post_command))

    application.add_handler(
        MessageHandler(filters.CONTACT, contact_handler)
    )

    job_queue = application.job_queue

    job_queue.run_repeating(
        autopost,
        interval=7200,
        first=120
    )

    application.run_polling()


if __name__ == "__main__":
    main()
