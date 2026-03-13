import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

bot = Bot(token=TOKEN)
dp = Dispatcher()

photo1 = FSInputFile("photo1.jpg")
photo2 = FSInputFile("photo2.jpg")

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Согласен на обработку данных и отправить номер", request_contact=True)]
    ],
    resize_keyboard=True
)

PRODUCT_TEXT = """
🛷 САНИ-ВОЛОКУШИ MAКСИХОД

❄️ Сани-волокуши из высокопрочного пластика низкого давления.

Подходят для:

• зимнего отдыха
• охоты
• рыбалки
• экспедиций
• перевозки грузов

✅ Есть готовые модели
✅ Изготавливаем под заказ

━━━━━━━━━━━━━━

📦 МОДЕЛИ САНЕЙ

🛷 MAX ЭКО 205
Длина: 205 см
Ширина по дну: 55 см
Ширина в развале: 75 см
Высота борта: 27 см
Длина дышла: 100 см
Толщина: 6 мм
Вес: 30 кг

🛷 MAX ЭКО 215
Длина: 215 см
Ширина по дну: 55 см
Ширина в развале: 75 см
Высота борта: 27 см
Длина дышла: 100 см
Толщина: 6 мм
Вес: 30 кг

🛷 MAX ЭКО PRO 250
Длина: 250 см
Ширина по дну: 70 см
Ширина в развале: 85 см
Высота борта: 39 см
Длина дышла: 120 см
Толщина: 8 мм
Вес: 50 кг

🛷 MAX ЭКО 265
Длина: 265 см
Ширина по дну: 55 см
Ширина в развале: 75 см
Высота борта: 27 см
Длина дышла: 100 см
Толщина: 6 мм
Вес: 30 кг

━━━━━━━━━━━━━━

⚙ ДОПОЛНИТЕЛЬНО

• Стоячее складное место позади саней
• Ящик-сидушка
• Мягкая накладка
• Ручки для пассажира
• Тент для груза
• Сумка-вкладыш
• Накладки-коньки против заноса

━━━━━━━━━━━━━━

📞 КОНТАКТЫ

☎ Телефон/MAX
+7 922 447-40-86

📧 Почта
MaxihodNV86@yandex.ru

━━━━━━━━━━━━━━

📩 Если вас заинтересовал товар:

Свяжитесь с нами  
или

📱 оставьте номер телефона  
и мы вам перезвоним.

Перед отправкой номера вы подтверждаете  
согласие на обработку персональных данных.
"""

@dp.message(CommandStart(deep_link=True))
async def start_with_source(message: Message, command: CommandStart):

    source = command.args

    await message.answer_photo(photo1)

    await message.answer(PRODUCT_TEXT)

    await message.answer_photo(
        photo2,
        caption="Нажмите кнопку ниже чтобы оставить номер",
        reply_markup=phone_kb
    )

    text = f"""
👀 Новый посетитель

Имя: {message.from_user.full_name}
Username: @{message.from_user.username}
ID: {message.from_user.id}

Источник:
{source}
"""

    await bot.send_message(ADMIN_ID, text)

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer_photo(photo1)

    await message.answer(PRODUCT_TEXT)

    await message.answer_photo(
        photo2,
        caption="Нажмите кнопку ниже чтобы оставить номер",
        reply_markup=phone_kb
    )

@dp.message(F.contact)
async def contact_handler(message: Message):

    phone = message.contact.phone_number

    username = message.from_user.username
    if username:
        username = f"@{username}"
    else:
        username = "нет username"

    text = f"""
🔥 НОВАЯ ЗАЯВКА

Имя: {message.from_user.full_name}

Телефон:
{phone}

Username:
{username}

ID:
{message.from_user.id}
"""

    await bot.send_message(ADMIN_ID, text)

    await message.answer(
        "✅ Спасибо! Мы получили ваш номер и скоро свяжемся с вами."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

