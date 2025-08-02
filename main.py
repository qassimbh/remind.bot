from fastapi import FastAPI, Request
import json, random, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = "6288532598:AAE3vvrPIbsYrZ1LL0J4dscCgYcLIf_XRH0"

app = FastAPI()
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# تحميل ملفات الأذكار والمستخدمين
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

try:
    with open("rshq.json", "r", encoding="utf-8") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

# /start: رسالة ترحيبية مرة واحدة + الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = True
        with open("rshq.json", "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً ❤️"
        )

    keyboard = [
        [InlineKeyboardButton("أذكار الصباح ☀️", callback_data="morning")],
        [InlineKeyboardButton("أذكار المساء 🌙", callback_data="evening")],
        [InlineKeyboardButton("أذكار النوم 🛏️", callback_data="sleep")],
        [InlineKeyboardButton("أذكار بعد الصلاة 🕌", callback_data="prayer")],
        [InlineKeyboardButton("ذكر عشوائي 🔁", callback_data="random")],
    ]
    await update.message.reply_text("اختر نوع الذكر الذي تريده:", reply_markup=InlineKeyboardMarkup(keyboard))

# التعامل مع ضغط الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "random":
        section = random.choice(list(azkar.values()))
        text = random.choice(section)
        await query.message.reply_text(text)
    else:
        texts = azkar.get(choice, [])
        for text in texts:
            await query.message.reply_text(text)

# إرسال ذكر عشوائي لكل المستخدمين كل ساعة
async def send_azkar_periodically():
    while True:
        for user_id in user_data:
            section = random.choice(list(azkar.values()))
            text = random.choice(section)
            try:
                await bot.send_message(chat_id=int(user_id), text=text)
            except:
                pass
        await asyncio.sleep(3600)

# ربط المعالجات
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# عند بدء التشغيل
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"https://tathkeer-bot.onrender.com/webhook/{TOKEN}")
    asyncio.create_task(send_azkar_periodically())

# استقبال webhook من تيليجرام
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}
