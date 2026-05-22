import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8374267625:AAHuAMy0IdrTbMXGV6FHX8VRLzbXwWsLDxA"

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()

keyboard = ReplyKeyboardMarkup(
    [["💰 رصيدي", "🎯 مهمة"], ["👥 دعوة", "💳 سحب"]],
    resize_keyboard=True
)

def get_user(user_id):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0

    return row[0]

def add_balance(user_id, amount):
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)

    await update.message.reply_text(
        "🔥 أهلاً بك في بوت الربح\nاختر 👇",
        reply_markup=keyboard
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = get_user(user_id)

    await update.message.reply_text(f"💰 رصيدك: {bal} نقطة")

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_balance(user_id, 10)
    await update.message.reply_text("🎯 ربحت +10 نقاط 🔥")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(f"👥 رابطك:\n{link}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💳 طلب السحب قيد المراجعة")

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 رصيدي":
        await balance(update, context)
    elif text == "🎯 مهمة":
        await task(update, context)
    elif text == "👥 دعوة":
        await refer(update, context)
    elif text == "💳 سحب":
        await withdraw(update, context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("bot running...")

app.run_polling()
