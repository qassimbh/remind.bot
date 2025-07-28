from fastapi import FastAPI, Request
import json
import random
import asyncio
import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.ext import Defaults
from datetime import datetime

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"
bot = Bot(token=TOKEN)
app = FastAPI()
users_file = "rshq.json"
azkar_file = "azkar.json"

# تحميل بيانات الأذكار
with open(azkar_file, "r", encoding="utf-8") as f:
    azkar_data = json.load(f)

# حفظ المستخدمين
def load_users():
    if not os.path.exists(users_file):
        return []
    with open(users_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users, f)

# إعداد البوت
defaults = Defaults(parse_mode="HTML")
application = Application.builder().token(TOKEN).defaults(defaults).build()

# رسالة ترحيبية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_users()

    if user_id not in users:
        users.append(user_id)
        save_users(users)
        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً 🌿"
        )

    buttons = [
        [InlineKeyboardButton("📿 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("😴 أذكار النوم", callback_data="sleep")],
        [InlineKeyboardButton("🔁 ذكر عشوائي", callback_data="random")],
    ]
    await update.message.reply_text("اختر نوع الأذكار:", reply_markup=InlineKeyboardMarkup(buttons))

# إرسال الأذكار الكاملة
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section = query.data
    if section == "random":
        section = random.choice(list(azkar_data.keys()))
        text = random.choice(azkar_data[section])
        await query.message.reply_text(text)
    else:
        for zekr in azkar_data.get(section, []):
            await query.message.reply_text(zekr)

# إرسال أذكار عشوائية كل ساعة
async def send_random_zekr():
    while True:
        users = load_users()
        for user_id in users:
            section = random.choice(list(azkar_data.keys()))
            zekr = random.choice(azkar_data[section])
            try:
                await bot.send_message(chat_id=user_id, text=f"🕐 ذكر الساعة:\n{zekr}")
            except:
                pass
        await asyncio.sleep(3600)

# تشغيل Webhook
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "running"}

# تسجيل الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))

# بدء المهام
async def main():
    asyncio.create_task(send_random_zekr())
    await application.initialize()
    await application.start()
    print("Bot is running...")

import asyncio
asyncio.create_task(main())
