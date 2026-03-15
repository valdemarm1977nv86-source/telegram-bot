import os
import random
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

PHOTO = "photo.jpg"

TEXT = """
🔥 БАТРАК — работа для тех, кто готов зарабатывать

💰 Высокие выплаты  
📍 Работа рядом  
⚡ Быстрый старт  

👇 Нажмите кнопку ниже чтобы оставить заявку
"""

POLICY = """
📄 Политика обработки персональных данных

Отправляя номер телефона через бота,
вы соглашаетесь на обработку персональных данных.

Собираемые данные:
• имя
• номер телефона
• username Telegram
"""

POST_INTERVAL = 3600


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_photo(
        photo=open(PHOTO, "rb"),
        caption=TEXT
    )

    keyboard = [
        [InlineKeyboardButton("✅ Согласен", callback_data="agree")]
    ]

    await update.message.reply_text(
        POLICY,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# AGREE
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


# CONTACT
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact

    name = contact.first_name
    phone = contact.phone_number
    user = update.message.from_user.username
    user_id = update.message.from_user.id

    text = f"""
🔥 Новая заявка

Имя: {name}
Username: @{user}
Телефон: {phone}
ID: {user_id}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Заявка отправлена."
    )


# AUTOPOST
async def autopost(context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=open(PHOTO, "rb"),
        caption=TEXT
    )


# MAIN
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(agree, pattern="agree"))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    app.job_queue.run_repeating(
        autopost,
        interval=POST_INTERVAL,
        first=60
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
