from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json, random, asyncio, os

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# تحميل الأذكار من الملفات
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

with open("rshq.json", "r", encoding="utf-8") as f:
    rshq = json.load(f)

# تحميل أو إنشاء ملف المستخدمين
users_file = "users.json"
if os.path.exists(users_file):
    with open(users_file, "r") as f:
        users = set(json.load(f))
else:
    users = set()

# إنشاء تطبيق FastAPI و Telegram
app = FastAPI()
application = Application.builder().token(TOKEN).build()

# صفحة اختبار بسيطة
@app.get("/")
async def root():
    return {"status": "Bot is live!"}

# نقطة دخول Webhook
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# أمر /start
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
        [InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="random")]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("اختر نوع الذكر الذي تريده:", reply_markup=markup)

# التعامل مع ضغط الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "random":
        text = random.choice(rshq)
    else:
        text = random.choice(azkar.get(choice, ["لا يوجد أذكار حالياً."]))

    await query.edit_message_text(text)

# إرسال ذكر عشوائي كل ساعة
async def send_azkar_every_hour():
    while True:
        await asyncio.sleep(3600)
        message = random.choice(rshq)
        for user_id in users:
            try:
                await application.bot.send_message(chat_id=int(user_id), text=message)
            except:
                continue

# ربط الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# عند بدء التطبيق
@app.on_event("startup")
async def startup_event():
    await application.initialize()
    asyncio.create_task(send_azkar_every_hour())
