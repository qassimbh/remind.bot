import json
import random
import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    CallbackQueryHandler, CallbackContext
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv("TOKEN") or "6288532598:AAE3vvrPIbsYrZ1LL0J4dscCgYcLIf_XRH0"
bot_username = "tathkeer_bot"
app = FastAPI()
application = Application.builder().token(TOKEN).build()

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    AZKAR = json.load(f)

USERS_FILE = "rshq.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def build_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌇 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("🛏️ أذكار النوم", callback_data="sleep")],
        [InlineKeyboardButton("🕌 أذكار الصلاة", callback_data="prayer")],
        [InlineKeyboardButton("🔁 ذكر عشوائي", callback_data="random")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text(
        f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً.\nاختر نوع الذكر:",
        reply_markup=build_keyboard()
    )

async def send_azkar(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    zkr_type = query.data
    if zkr_type == "random":
        category = random.choice(list(AZKAR.values()))
        text = random.choice(category)
        await query.message.reply_text(text)
    else:
        azkar_list = AZKAR.get(zkr_type, [])
        for zkr in azkar_list:
            await query.message.reply_text(zkr)

@application.post(f"/webhook/{TOKEN}")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# تسجيل الأوامر والمعالجات
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(send_azkar))

# إرسال أذكار كل ساعة
async def send_hourly_azkar():
    while True:
        users = load_users()
        all_azkar = []
        for category in AZKAR.values():
            all_azkar.extend(category)
        if all_azkar:
            text = random.choice(all_azkar)
            for user_id in users:
                try:
                    await application.bot.send_message(chat_id=user_id, text=text)
                except:
                    pass
        await asyncio.sleep(3600)

import asyncio
@app.on_event("startup")
async def on_startup():
    asyncio.create_task(application.initialize())
    asyncio.create_task(send_hourly_azkar())
