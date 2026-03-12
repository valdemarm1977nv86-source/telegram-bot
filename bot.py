import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.environ.get("BOT_TOKEN")

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

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        photo1,
        caption="Добро пожаловать!",
    )

    await message.answer_photo(
        photo2,
        caption="Чтобы продолжить — отправьте номер телефона",
        reply_markup=phone_kb
    )

@dp.message(F.contact)
async def contact_handler(message: Message):
    phone = message.contact.phone_number
    user = message.from_user.username

    text = f"""
Спасибо! ✅

Ваш номер:
{phone}

Ваш username:
@{user}
"""

    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
