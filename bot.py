import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8638460779:AAH6ko7yOsCmH-84ESEOjFnN_KVtIWepkL4"
WEBAPP_URL =  https://aware-celery-rice.ngrok-free.dev/bingo/ # የ MiniApp URLህ

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Main Bot Reply Keyboard
    keyboard = [
        ["🎮 ጨዋታ ጀምር"],
        ["💰 Wallet", "👤 Profile"],
        ["➕ Deposit", "💸 Withdrawal"],
        ["📜 ታሪክ"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"ሰላም {user.first_name}! እንኳን ወደ Bingo Game Bot በደህና መጡ።\nእባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎮 ጨዋታ ጀምር":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Bingo አሁኑኑ ተጫወት", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await update.message.reply_text("ጨዋታውን ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ፦", reply_markup=keyboard)

    elif text == "💰 Wallet":
        await update.message.reply_text("💳 **የእርስዎ ቦርሳ (Wallet)**\n\nየአሁኑ ባላንስ፦ **0.00 ETB**", parse_mode="Markdown")

    elif text == "➕ Deposit":
        await update.message.reply_text("📥 **ገንዘብ ለማስገባት (Deposit)**\n\nቴሌብር / ባንክ በመጠቀም ማስገባት ይችላሉ።")

    elif text == "💸 Withdrawal":
        await update.message.reply_text("📤 **ገንዘብ ለማውጣት (Withdrawal)**\n\nማውጣት የሚፈልጉትን የገንዘብ መጠን ያስገቡ።")

    elif text == "📜 ታሪክ":
        await update.message.reply_text("📜 **የጨዋታ እና የፋይናንስ ታሪክ**\n\nምንም አይነት ታሪክ የለም።")

    elif text == "👤 Profile":
        user = update.effective_user
        profile_text = f"👤 **የተጠቃሚ መረጃ**\n\n" \
                       f"ስም፦ {user.first_name}\n" \
                       f"ID፦ `{user.id}`"
        await update.message.reply_text(profile_text, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()