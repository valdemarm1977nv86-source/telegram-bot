import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from openpyxl import Workbook, load_workbook
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1584040288

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ФОТО
photo1 = FSInputFile("photo1.jpg")
photo2 = FSInputFile("photo2.jpg")

# статистика
visitors = 0
sources = {}

excel_file = "leads.xlsx"

# клавиатура телефона
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True
)

# кнопка политики
policy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📜 Политика обработки данных", callback_data="policy")]
    ]
)

# сохранение в excel
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


# START
@dp.message(CommandStart())
async def start(message: Message):

    global visitors
    visitors += 1

    args = message.text.split()

    source = "неизвестно"

    if len(args) > 1:
        source = args[1]

    if source not in sources:
        sources[source] = 0

    sources[source] += 1

    # отчет админу
    await bot.send_message(
        ADMIN_ID,
        f"""
🚀 Новый посетитель

👤 @{message.from_user.username}
ID: {message.from_user.id}

Источник: {source}

Всего посетителей: {visitors}

Статистика:
{sources}
"""
    )

    # фото
    media = MediaGroupBuilder()
    media.add_photo(photo1)
    media.add_photo(photo2)

    await message.answer_media_group(media.build())

    text = """
🛷 САНИ - ВОЛОКУШИ МАКСИХОД

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

📞 Контакты

Телефон / Max
+7 922 447 40 86


Email
MaxihodNV86@yandex.ru

━━━━━━━━━━━━━━

Чтобы узнать цену и наличие
нажмите кнопку ниже и отправьте номер телефона.
"""

    await message.answer(text)

    await message.answer(
        "👇 Перед отправкой номера можно ознакомиться с политикой обработки данных",
        reply_markup=policy_kb
    )


# политика
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
        "👇 Теперь можно отправить номер телефона",
        reply_markup=phone_kb
    )


# получение телефона
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

Мы свяжемся с вами в ближайшее время.
"""
    )


# веб сервер для Render
async def handle(request):
    return web.Response(text="Bot is running")

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
