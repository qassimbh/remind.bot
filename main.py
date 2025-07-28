from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import json
import asyncio
import os

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

with open("rshq.json", "r", encoding="utf-8") as f:
    rshq = json.load(f)

# تحميل المستخدمين أو تهيئة الملف
users_file = "users.json"
if os.path.exists(users_file):
    with open(users_file, "r") as f:
        users = set(json.load(f))
else:
    users = set()

# إنشاء تطبيق FastAPI و Telegram Application
app = FastAPI()
application = Application.builder().token(TOKEN).build()

# إرسال رسالة الترحيب وأزرار الأذكار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users.add(user_id)
        with open(users_file, "w") as f:
            json.dump(list(users), f)

        welcome = f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار 🌿\nسيساعدك كثيراً على ذكر الله ❤️"
        await update.message.reply_text(welcome)

    buttons = [
        [InlineKeyboardButton("🌞 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("😴 أذكار النوم", callback_data="sleep")],
        [InlineKeyboardButton("🙏 أذكار بعد الصلاة", callback_data="prayer")],
        [InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="random")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("اختر نوع الذكر الذي تريده:", reply_markup=reply_markup)

# التعامل مع ضغط الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
   
