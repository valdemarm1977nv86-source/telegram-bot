import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.environ.get("BOT_TOKEN")

ADMIN_ID = 1584040288

bot = Bot(token=TOKEN)
dp = Dispatcher()

photo1 = FSInputFile("photo1.jpg")
photo2 = FSInputFile("photo2.jpg")

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True
)

# статистика источников
sources = {}

@dp.message(CommandStart())
async def start(message: Message):

    user = message.from_user
    args = message.text.split()

    source = "неизвестно"

    if len(args) > 1:
        source = args[1]

    if source not in sources:
        sources[source] = 0

    sources[source] += 1

    # отчет админу
    report = f"""
🚀 Новый посетитель бота

👤 username: @{user.username}
🆔 id: {user.id}

📍 источник: {source}

📊 статистика источников:
{sources}
"""

    await bot.send_message(ADMIN_ID, report)

    await message.answer_photo(photo1)

    text = """
🛷 САНИ-ВОЛОКУШИ МАКСИХОД

Сани-волокуши из высокопрочного пластика низкого давления.

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

MAX ЭКО 205

Длина: 205 см  
Ширина по дну: 55 см  
Ширина в развале: 75 см  
Высота борта: 27 см  
Длина дышла: 100 см  

━━━━━━━━━━━━━━

📞 Контакты

Telegram: @valdemarnv86  
Почта: MaxihodNV86@yandex.ru  

━━━━━━━━━━━━━━

📜 Политика обработки персональных данных

Отправляя номер телефона ,
вы даете согласие на обработку персональных данных
для связи с вами по вопросу покупки товара.
"""

    await message.answer(text)

    await message.answer_photo(photo2)

    await message.answer(
        "👇 Нажмите кнопку ниже чтобы оставить номер телефона",
        reply_markup=phone_kb
    )


@dp.message(F.contact)
async def contact_handler(message: Message):

    phone = message.contact.phone_number
    user = message.from_user

    text = f"""
📞 Новая заявка

Телефон: {phone}
username: @{user.username}
id: {user.id}
"""

    await bot.send_message(ADMIN_ID, text)

    await message.answer(
        "✅ Спасибо! Ваша заявка отправлена.\nМы скоро свяжемся с вами."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


