import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# токен из переменной среды Render
TOKEN = os.getenv("BOT_TOKEN")

# загрузка конфигурации
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

PRODUCTS = config["products"]

# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = []

    for product_id, product in PRODUCTS.items():
        keyboard.append(
            [InlineKeyboardButton(product["name"], callback_data=product_id)]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите товар:",
        reply_markup=reply_markup
    )

# показать товар
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data
    product = PRODUCTS[product_id]

    folder = f"products/{product_id}"

    # описание
    description_path = os.path.join(folder, "description.txt")

    if os.path.exists(description_path):
        with open(description_path, "r", encoding="utf-8") as f:
            description = f.read()
    else:
        description = "Описание отсутствует"

    # фото
    photos = []

    for file in os.listdir(folder):
        if file.endswith(".jpg") or file.endswith(".png"):
            photos.append(os.path.join(folder, file))

    photos.sort()

    media = []

    for i, photo in enumerate(photos):
        if i == 0:
            media.append(InputMediaPhoto(open(photo, "rb"), caption=description))
        else:
            media.append(InputMediaPhoto(open(photo, "rb")))

    if media:
        await query.message.reply_media_group(media)
    else:
        await query.message.reply_text(description)

    keyboard = [
        [InlineKeyboardButton("📞 Оставить заявку", callback_data=f"order_{product_id}")]
    ]

    await query.message.reply_text(
        "Хотите заказать?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# заказ
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.replace("order_", "")
    product = PRODUCTS[product_id]

    user = query.from_user

    text = f"""
📦 Новая заявка

Товар: {product["name"]}

Имя: {user.first_name}
Username: @{user.username}

ID: {user.id}
"""

    await context.bot.send_message(
        chat_id=product["admin_id"],
        text=text
    )

    await query.message.reply_text("✅ Заявка отправлена!")

# запуск
def main():

    if not TOKEN:
        print("ERROR: BOT_TOKEN not found")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_product, pattern="^01_"))
    app.add_handler(CallbackQueryHandler(order, pattern="^order_"))

    print("BOT STARTED")

    app.run_polling()

if __name__ == "__main__":
    main()
