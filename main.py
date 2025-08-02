from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import json
import asyncio
import os
import random

TOKEN = "6288532598:AAE3vvrPIbsYrZ1LL0J4dscCgYcLIf_XRH0"
WEBHOOK_URL = "https://remind-bot-ev7z.onrender.com"

# تحميل الأذكار من الملف
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar_data = json.load(f)

app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

# حفظ المستخدمين لرسالة الترحيب وإرسال الأذكار التلقائي
users_file = "rshq.json"
if os.path.exists(users_file):
    with open(users_file, "r") as f:
        registered_users = json.load(f)
else:
    registered_users = []

# رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in registered_users:
        registered_users.append(user_id)
        with open(users_file, "w") as f:
            json.dump(registered_users, f)

        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً"
        )

    keyboard = [
        [
            InlineKeyboardButton("أذكار الصباح 🌤️", callback_data="الصباح"),
            InlineKeyboardButton("أذكار المساء 🌙", callback_data="المساء"),
        ],
        [
            InlineKeyboardButton("أذكار النوم 😴", callback_data="النوم"),
            InlineKeyboardButton("أذكار الصلاة 🕌", callback_data="الصلاة"),
        ],
        [
            InlineKeyboardButton("ذكر عشوائي 🔀", callback_data="عشوائي"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع الأذكار:", reply_markup=reply_markup)

# معالجة الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "عشوائي":
        category = random.choice(list(azkar_data.values()))
        dhikr = random.choice(category)
        await query.message.reply_text(dhikr)
    else:
        for dhikr in azkar_data.get(choice, []):
            await query.message.reply_text(dhikr)

# إرسال ذكر عشوائي لكل المستخدمين كل ساعة
async def send_automatic_azkar():
    while True:
        await asyncio.sleep(3600)
        if not registered_users:
            continue
        category = random.choice(list(azkar_data.values()))
        dhikr = random.choice(category)
        for user_id in registered_users:
            try:
                await bot_app.bot.send_message(chat_id=user_id, text=dhikr)
            except:
                pass

# تعيين الأوامر والمعالجات
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(button_handler))

# Webhook endpoint
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}")
    asyncio.create_task(send_automatic_azkar())
