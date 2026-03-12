import os
from aiogram import Bot, Dispatcher

TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


photo1 = FSInputFile("photo1.jpg")
photo2 = FSInputFile("photo2.jpg")


phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📲 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True
)

consent_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="☑ Согласен", callback_data="agree")],
        [InlineKeyboardButton(text="📄 Политика конфиденциальности", url="https://yandex.ru/legal/confidential/")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ]
)


def save_client(name, username, phone):
    with open("clients.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            name,
            username,
            phone
        ])


@dp.message(Command("start"))
async def start(message: types.Message):

    text = """
❄️ <b>САНИ-ВОЛОКУШИ «МАКСИХОД»</b>

Надёжные сани из прочного пластика
для перевозки грузов по снегу и бездорожью.

<b>Подходят для:</b>
🏹 охоты
🎣 рыбалки
🏕 экспедиций
📦 перевозки грузов

<b>Преимущества:</b>
✔ усиленная конструкция
✔ вместительный грузовой отсек
✔ задняя площадка для дополнительного груза
✔ устойчивость и лёгкое скольжение
✔ подходят для снегохода и ручной тяги

📞 <b>Если вам понравился наш товар — свяжитесь с нами:</b>

📱 Телефон / Max  
+7 922 447-40-86

📧 Email  
MaxihodNV86@yandex.ru

Или оставьте свой телефон —
наш менеджер свяжется с вами.
"""

    await message.answer_photo(photo1)
    await message.answer_photo(photo2)

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=phone_kb
    )


@dp.message(lambda message: message.contact)
async def get_contact(message: types.Message):

    phone = message.contact.phone_number
    name = message.from_user.full_name
    username = message.from_user.username

    save_client(name, username, phone)

    text_admin = f"""
Новый клиент!

Имя: {name}
Username: @{username}
Телефон: {phone}
"""

    await bot.send_message(ADMIN_ID, text_admin)

    await message.answer(
        "Перед отправкой данных подтвердите согласие на обработку персональных данных.",
        reply_markup=consent_kb
    )


@dp.callback_query(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):

    await callback.message.answer(
        "✅ Спасибо! Наш менеджер скоро свяжется с вами."
    )


@dp.callback_query(lambda c: c.data == "cancel")
async def cancel(callback: types.CallbackQuery):

    await callback.message.answer(
        "Вы отменили отправку данных."
    )


async def main():
    print("🚀 Бот запущен и готов принимать сообщения")

    try:
        await dp.start_polling(bot)

    except Exception as e:
        print("❌ Произошла ошибка:")
        print(e)

    finally:
        input("Нажмите ENTER чтобы закрыть программу...")


if __name__ == "__main__":
    asyncio.run(main())

