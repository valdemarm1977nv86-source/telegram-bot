import os
import json
import random
import asyncio
import logging
from threading import Thread

from flask import Flask

from telegram import (
Update,
KeyboardButton,
ReplyKeyboardMarkup,
InputMediaPhoto
)

from telegram.ext import (
Application,
CommandHandler,
MessageHandler,
ContextTypes,
filters
)

# ----------------
# CONFIG
# ----------------

with open("config.json","r",encoding="utf8") as f:
 config=json.load(f)

TOKEN=config["TOKEN"]
ADMIN_ID=config["ADMIN_ID"]
CHANNEL_ID=config["CHANNEL_ID"]

AUTOPUBLISH=config["AUTOPUBLISH"]
POST_INTERVAL=config["POST_INTERVAL"]

# ----------------
# LOGGING
# ----------------

logging.basicConfig(
format="%(asctime)s %(levelname)s %(message)s",
level=logging.INFO
)

# ----------------
# KEEP ALIVE
# ----------------

app=Flask("")

@app.route("/")
def home():
 return "bot running"

def run():
 app.run(host="0.0.0.0",port=10000)

def keep_alive():
 t=Thread(target=run)
 t.start()

# ----------------
# ADMIN ALERT
# ----------------

async def admin_alert(app,text):

 try:
  await app.bot.send_message(
  ADMIN_ID,
  "⚠️ "+text
  )
 except:
  pass

# ----------------
# START
# ----------------

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

 try:

  media=[
  InputMediaPhoto(open("products/01_Maxihod_Sani/1.jpg","rb")),
  InputMediaPhoto(open("products/01_Maxihod_Sani/2.jpg","rb"))
  ]

  await update.message.reply_media_group(media)

 except Exception as e:

  await admin_alert(
  context.application,
  "Фото ошибка "+str(e)
  )

 try:

  with open(
  "products/01_Maxihod_Sani/description.txt",
  "r",
  encoding="utf8"
  ) as f:

   text=f.read()

  await update.message.reply_text(text)

 except Exception as e:

  await admin_alert(
  context.application,
  "Description ошибка "+str(e)
  )

 keyboard=[
 [KeyboardButton(
 "📞 Оставить контакт",
 request_contact=True)]
 ]

 markup=ReplyKeyboardMarkup(
 keyboard,
 resize_keyboard=True
 )

 await update.message.reply_text(
 "👇 Нажмите кнопку чтобы оставить заявку",
 reply_markup=markup
 )

# ----------------
# CONTACT
# ----------------

async def contact(update:Update,context:ContextTypes.DEFAULT_TYPE):

 try:

  c=update.message.contact
  u=update.effective_user

  text=f"""
🔥 Новая заявка

Имя: {c.first_name}
Username: @{u.username}
Телефон: {c.phone_number}
ID: {u.id}
"""

  await context.bot.send_message(
  ADMIN_ID,
  text
  )

  await update.message.reply_text(
  "Спасибо! Мы свяжемся с вами."
  )

 except Exception as e:

  await admin_alert(
  context.application,
  "Ошибка контакта "+str(e)
  )

# ----------------
# AUTOPOST
# ----------------

async def autopost(context:ContextTypes.DEFAULT_TYPE):

 try:

  products=os.listdir("products")

  if not products:
   return

  product=random.choice(products)

  path=f"products/{product}"

  photos=[]

  for file in os.listdir(path):

   if file.endswith(".jpg"):
    photos.append(
     InputMediaPhoto(
     open(f"{path}/{file}","rb")
     )
    )

  with open(
  f"{path}/description.txt",
  "r",
  encoding="utf8"
  ) as f:

   text=f.read()

  await context.bot.send_media_group(
  CHANNEL_ID,
  photos
  )

  await context.bot.send_message(
  CHANNEL_ID,
  text
  )

 except Exception as e:

  await admin_alert(
  context.application,
  "Ошибка автопоста "+str(e)
  )

# ----------------
# MAIN
# ----------------

async def autopost_loop(app):

 await asyncio.sleep(120)

 while True:

  await autopost(app)

  delay=POST_INTERVAL+random.randint(300,1200)

  await asyncio.sleep(delay)

def main():

 keep_alive()

 application=Application.builder().token(TOKEN).build()

 application.add_handler(
 CommandHandler("start",start)
 )

 application.add_handler(
 MessageHandler(filters.CONTACT,contact)
 )

 if AUTOPUBLISH:

  asyncio.create_task(
  autopost_loop(application)
  )

 print("BOT STARTED")

 application.run_polling()

if __name__=="__main__":
 main()
