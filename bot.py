import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from openpyxl import Workbook, load_workbook
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")

ADMIN_ID = 1584040288

bot = Bot(token=TOKEN)
dp = Dispatcher()

photo1 = FSInputFile("photo1.jpg")
photo2 = FSInputFile("photo2.jpg")
photo3 = FSInputFile("photo3.jpg")

visitors = 0
sources = {}

excel_file = "leads.xlsx"


def save_to_excel(username, phone, source):
    if not os.path.exists(excel_file):
        wb = Workbook()
        ws = wb.active
        ws.append(["Дата", "Username", "Телефон", "Источник"])
        wb.save(excel_file)

    wb = load_workbook(excel_file)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        username,
        phone,
        source
    ])

    wb.save(excel_file)


phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True
)

policy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📜 Политика обработки данных", callback_data="policy")]
    ]
)

models_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="MAX ЭКО 205", callback_data="model205")],
        [InlineKeyboardButton(text="MAX ЭКО 240", callback_data="model240")]
    ]
)


@dp.message(CommandStart())
async def start(message: Message):

    global visitors

    visitors += 1

    args = message.text.split()
    source = "unknown"

    if len(args) > 1:
        source = args[1]

    if source not in sources:
        sources[source] = 0

    sources[source] += 1

    await bot.send_message(
        ADMIN_ID,
        f"""
🚀 Новый посетитель

👤 @{message.from_user.username}
ID {message.from_user.id}

Источник: {source}

Всего посетителей: {visitors}

Статистика источников:
{sources}
"""
    )

    media = MediaGroupBuilder()
    media.add_photo(photo1)
    media.add_photo(photo2)

    await message.answer_media_group(media.build())

    text = """
🛷 САНИ ВОЛОКУШИ МАКСИХОД

Сани из высокопрочного пластика низкого давления.

Подходят для:

• охоты  
• рыбалки  
• экспедиций  
• перевозки грузов  

✅ Есть готовые модели  
✅ Изготавливаем под заказ

━━━━━━━━━━━━━━

Выберите модель чтобы посмотреть фото и характеристики
"""

    await message.answer(text, reply_markup=models_kb)


@dp.callback_query(F.data == "model205")
async def model1(callback):

    await callback.message.answer_photo(
        photo3,
        caption="""
🛷 MAX ЭКО 205

Длина: 205 см  
Ширина по дну: 55 см  
Ширина в развале: 75 см  
Высота борта: 27 см  

Подходит для:

✔ рыбалки  
✔ охоты  
✔ перевозки груза
"""
    )

    await callback.message.answer(
        """
Если вас заинтересовал товар:

1️⃣ отправьте номер телефона  
2️⃣ мы свяжемся с вами
""",
        reply_markup=policy_kb
    )


@dp.callback_query(F.data == "policy")
async def policy(callback):

    text = """
📜 Политика обработки персональных данных

Отправляя номер телефона через данного бота,
вы даете согласие на обработку персональных данных
в соответствии с Федеральным законом №152-ФЗ.

Данные используются исключительно для:

• связи с клиентом  
• консультации по товару  
• оформления заказа

Ваши данные не передаются третьим лицам.
"""

    await callback.message.answer(text)

    await callback.message.answer(
        "Нажмите кнопку ниже чтобы отправить номер",
        reply_markup=phone_kb
    )


@dp.message(F.contact)
async def contact(message: Message):

    phone = message.contact.phone_number
    username = message.from_user.username

    save_to_excel(username, phone, "telegram")

    await bot.send_message(
        ADMIN_ID,
        f"""
📞 Новая заявка

Username: @{username}
Телефон: {phone}
"""
    )

    await message.answer(
        """
✅ Спасибо за заявку!

Менеджер свяжется с вами в ближайшее время.

Пока можете посмотреть другие модели 👇
"""
    )

    await message.answer(
        "Выберите модель",
        reply_markup=models_kb
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


