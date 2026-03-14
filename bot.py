import os
import json
import asyncio
from aiohttp import web
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import CommandStart

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ---------- CONFIG ----------

with open("config.json","r",encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["bot_token"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_product = {}

stats = {}


# ---------- GOOGLE ----------

def connect_google(sheet_name):

    try:

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "google.json", scope
        )

        client = gspread.authorize(creds)

        sheet = client.open(sheet_name).sheet1

        return sheet

    except Exception as e:

        print("Google connect error:",e)

        return None


def save_lead(product, username, phone):

    try:

        sheet_name = config["products"][product]["google_sheet"]

        sheet = connect_google(sheet_name)

        if sheet:

            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                username,
                phone
            ])

    except Exception as e:

        print("Save error:",e)


# ---------- клавиатура ----------

def product_keyboard():

    buttons = []

    for key,p in config["products"].items():

        buttons.append([KeyboardButton(text=p["name"])])

        stats[p["name"]] = 0

    return ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)


phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить номер",request_contact=True)]],
    resize_keyboard=True
)


# ---------- фото ----------

def load_photos(product):

    path = f"products/{product}/photos"

    photos = []

    try:

        if os.path.exists(path):

            for file in sorted(os.listdir(path)):

                if file.endswith((".jpg",".png",".jpeg")):

                    photos.append(FSInputFile(f"{path}/{file}"))

    except Exception as e:

        print("Photo error:",e)

    return photos


# ---------- описание ----------

def load_description(product):

    try:

        with open(f"products/{product}/description.txt","r",encoding="utf-8") as f:

            return f.read()

    except:

        return "Описание отсутствует"


# ---------- START ----------

@dp.message(CommandStart())
async def start(message: Message):

    try:

        await message.answer(
            "Выберите товар:",
            reply_markup=product_keyboard()
        )

    except Exception as e:

        print("Start error:",e)


# ---------- статистика ----------

@dp.message(F.text == "/stats")
async def show_stats(message: Message):

    text = "Статистика заявок:\n\n"

    for k,v in stats.items():

        text += f"{k} — {v}\n"

    await message.answer(text)


# ---------- выбор товара ----------

@dp.message()
async def choose_product(message: Message):

    try:

        for key,p in config["products"].items():

            if message.text == p["name"]:

                user_product[message.from_user.id] = key

                photos = load_photos(key)

                for ph in photos:

                    await message.answer_photo(ph)

                text = load_description(key)

                await message.answer(text)

                await message.answer(
                    "Оставьте номер телефона",
                    reply_markup=phone_kb
                )

                return

    except Exception as e:

        print("Product error:",e)


# ---------- контакт ----------

@dp.message(F.contact)
async def contact(message: Message):

    try:

        user_id = message.from_user.id

        if user_id not in user_product:

            return

        product = user_product[user_id]

        phone = message.contact.phone_number

        username = message.from_user.username or message.from_user.first_name

        save_lead(product,username,phone)

        product_name = config["products"][product]["name"]

        stats[product_name] += 1

        admin = config["products"][product]["admin_id"]

        await bot.send_message(
            admin,
            f"Новая заявка\nТовар: {product_name}\n@{username}\nТелефон: {phone}"
        )

        await message.answer("Спасибо! Мы скоро свяжемся с вами.")

    except Exception as e:

        print("Contact error:",e)


# ---------- WEB ----------

async def handle(request):

    return web.Response(text="Bot running")


async def start_web():

    app = web.Application()

    app.router.add_get("/",handle)

    port = int(os.environ.get("PORT",10000))

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(runner,"0.0.0.0",port)

    await site.start()


# ---------- MAIN ----------

async def main():

    await bot.delete_webhook(drop_pending_updates=True)

    while True:

        try:

            await asyncio.gather(
                dp.start_polling(bot),
                start_web()
            )

        except Exception as e:

            print("Bot crash:",e)

            await asyncio.sleep(5)


if __name__ == "__main__":

    asyncio.run(main())
