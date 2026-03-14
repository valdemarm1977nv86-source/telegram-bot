import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHOTO1 = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/1.jpg")
PHOTO2 = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/2.jpg")
DESCRIPTION = os.path.join(BASE_DIR, "products/01_Maxihod_Sani/description.txt")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("🛒 Оставить заявку")]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    text = open(DESCRIPTION, encoding="utf-8").read()

   try:

    with open(PHOTO1, "rb") as p1:
        await update.message.reply_photo(
            photo=p1,
            caption=text,
            reply_markup=reply_markup
        )

except Exception as e:

    print("PHOTO1 ERROR:", PHOTO1)
    print(e)

try:

    with open(PHOTO2, "rb") as p2:
        await update.message.reply_photo(photo=p2)

except Exception as e:

    print("PHOTO2 ERROR:", PHOTO2)
    print(e)


async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("✅ Согласен")]]

    await update.message.reply_text(
        "Перед отправкой телефона нужно согласие на обработку персональных данных.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("📱 Поделиться номером", request_contact=True)]]

    await update.message.reply_text(
        "Нажмите кнопку чтобы отправить номер телефона",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact
    user = update.message.from_user

    text = f"""
🔥 Новая заявка

Имя: {user.first_name}
Username: @{user.username}
Телефон: {contact.phone_number}
ID: {user.id}
"""

    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

    await update.message.reply_text("Спасибо! Мы скоро свяжемся с вами.")


def main():

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.Regex("🛒 Оставить заявку"), consent)
    )

    application.add_handler(
        MessageHandler(filters.Regex("✅ Согласен"), ask_phone)
    )

    application.add_handler(
        MessageHandler(filters.CONTACT, get_contact)
    )

    print("BOT STARTED")

    application.run_polling()


if __name__ == "__main__":
    main()
