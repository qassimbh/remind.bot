import json
import random
import asyncio
import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackContext
)

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"
bot = Bot(token=TOKEN)
app = FastAPI()

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

# قائمة المستخدمين لحفظ من استلموا الرسالة الترحيبية
users_file = "rshq.json"
if os.path.exists(users_file):
    with open(users_file, "r", encoding="utf-8") as f:
        known_users = json.load(f)
else:
    known_users = []

# دالة لإرسال ذكر عشوائي
async def send_random_zekr(context: CallbackContext):
    zekr = random.choice(azkar)
    for user_id in known_users:
        try:
            await bot.send_message(chat_id=user_id, text=zekr)
        except Exception:
            pass

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in known_users:
        known_users.append(user_id)
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(known_users, f)
        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً"
        )
    zekr = random.choice(azkar)
    await update.message.reply_text(zekr)

# إعداد التطبيق
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# إعداد Webhook
@app.post(f"/webhook/{TOKEN}")
async def webhook_endpoint(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

# بدء إرسال الأذكار التلقائي كل ساعة
async def start_background_task():
    while True:
        await send_random_zekr(None)
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_background_task())
