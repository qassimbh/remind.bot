from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler
import json
import os
import random
import asyncio

TOKEN = "6288532598:AAE3vvrPIbsYrZ1LL0J4dscCgYcLIf_XRH0"
bot = Bot(token=TOKEN)

app = FastAPI()
users = set()

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

# حفظ المستخدمين
def save_user(user_id):
    if user_id not in users:
        users.add(user_id)
        with open("rshq.json", "w") as f:
            json.dump(list(users), f)

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "أخي"
    save_user(user_id)

    await update.message.reply_text(
        f"أهلاً وسهلاً {username} في بوت الأذكار، سيساعدك كثيراً.\n\n"
        "اختر نوع الذكر الذي تريده:",
        reply_markup=telegram.InlineKeyboardMarkup([
            [telegram.InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning")],
            [telegram.InlineKeyboardButton("🌇 أذكار المساء", callback_data="evening")],
            [telegram.InlineKeyboardButton("🌙 أذكار النوم", callback_data="sleep")],
            [telegram.InlineKeyboardButton("🕌 أذكار الصلاة", callback_data="prayer")],
            [telegram.InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="random")],
        ])
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "random":
        all_azkar = sum(azkar.values(), [])
        await query.message.reply_text(random.choice(all_azkar))
    elif choice in azkar:
        for line in azkar[choice]:
            await query.message.reply_text(line)

# تشغيل البوت
bot_app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(telegram.ext.CallbackQueryHandler(handle_callback))

@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await bot_app.process_update(update)
    return {"ok": True}

# جدولة إرسال الأذكار تلقائيًا
async def send_random_zekr():
    while True:
        all_azkar = sum(azkar.values(), [])
        zekr = random.choice(all_azkar)
        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=zekr)
            except Exception:
                pass
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    if os.path.exists("rshq.json"):
        with open("rshq.json", "r") as f:
            loaded = json.load(f)
            for user in loaded:
                users.add(user)
    asyncio.create_task(send_random_zekr())
