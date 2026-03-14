import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from openpyxl import Workbook, load_workbook
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1584040288

bot = Bot(token=TOKEN)
dp = Dispatcher()

visitors = 0
sources = {}

excel_file = "leads.xlsx"

phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
    resize_keyboard=True
)

policy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📜 Политика обработки данных", callback_data="policy")]
    ]
)


# загрузка описания
def load_description():

    if not os.path.exists("description.txt"):
        return "Описание товара не найдено"

    with open("description.txt", "r", encoding="utf-8") as f:
        return f.read()


# загрузка всех фото из папки
def load_photos():

    photos = []
    

    files = sorted(os.listdir())

    for file in files:
        if file.endswith(".jpg") or file.endswith(".png"):
            photos.append(FSInputFile(file))

    return photos


# excel
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
        f"Новый посетитель @{message.from_user.username}\nИсточник: {source}\nВсего: {visitors}"
    )

    photos = load_photos()

    if photos:

        media = MediaGroupBuilder()

        for p in photos:
            media.add_photo(p)

        await message.answer_media_group(media.build())

    text = load_description()

    await message.answer(text)

    await message.answer(
        "Перед отправкой номера ознакомьтесь с политикой обработки данных",
        reply_markup=policy_kb
    )


@dp.callback_query(F.data == "policy")
async def policy(callback):

    text = """
Политика обработки персональных данных

Отправляя номер телефона вы соглашаетесь на обработку персональных данных
в соответствии с ФЗ-152.

Данные используются только для связи с клиентом
и оформления заказа.
"""

    await callback.message.answer(text)
    await callback.message.answer("Теперь можно отправить номер", reply_markup=phone_kb)


@dp.message(F.contact)
async def contact(message: Message):

    phone = message.contact.phone_number
    username = message.from_user.username

    save_to_excel(username, phone, "telegram")

    await bot.send_message(
        ADMIN_ID,
        f"Новая заявка\n@{username}\nТелефон: {phone}"
    )

    await message.answer("Спасибо! Мы свяжемся с вами.")


# WEB SERVER для Render
async def handle(request):
    return web.Response(text="Bot running")


async def start_web():

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():

    await asyncio.gather(
        dp.start_polling(bot),
        start_web()
    )


if __name__ == "__main__":
    asyncio.run(main())
