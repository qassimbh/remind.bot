from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
import json
import random
import os

TOKEN = os.getenv("BOT_TOKEN", "6288532598:AAE3vvrPIbsYrZ1LL0J4dscCgYcLIf_XRH0")
app = FastAPI()

application = Application.builder().token(TOKEN).build()

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar_data = json.load(f)

# قائمة المستخدمين لعدم تكرار رسالة الترحيب
users = set()

# رسالة الترحيب
WELCOME_MESSAGE = "أهلاً وسهلاً أخي الكريم في بوت الأذكار، سيساعدك كثيراً 🌿"

# عرض الأزرار
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌇 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("🛏️ أذكار النوم", callback_data="sleep")],
        [InlineKeyboardButton("🕌 أذكار بعد الصلاة", callback_data="prayer")],
        [InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="random")],
    ]
    return InlineKeyboardMarkup(buttons)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        await update.message.reply_text(WELCOME_MESSAGE)
    await update.message.reply_text("اختر نوع الأذكار:", reply_markup=get_main_keyboard())

# عند ضغط زر
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    if category == "random":
        all_azkar = []
        for items in azkar_data.values():
            all_azkar.extend(items)
        text = random.choice(all_azkar)
        await query.message.reply_text(text)
    else:
        azkar_list = azkar_data.get(category, [])
        for zekr in azkar_list:
            await query.message.reply_text(zekr)

# استقبال Webhook
@app.post(f"/webhook/{TOKEN}")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# تسجيل الهاندلرز
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))
