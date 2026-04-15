import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = "8781840058:AAHiSIjYUn3J-QyFeuN2RGAXcSY_jaXyu58"
ADMIN_ID = 8071804675

logging.basicConfig(level=logging.INFO)

pending_replies = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Bu reklama bo'yicha murojaat boti.\n\n"
        "📢 Reklama narxlari va shartlar uchun xabaringizni yozing!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "username yo'q"
    text = update.message.text

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Javob berish", callback_data=f"reply_{user_id}")]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Yangi murojaat!\n\n👤 {user.full_name}\n🔗 {username}\n🆔 {user_id}\n\n💬 {text}",
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ Xabaringiz qabul qilindi! Tez orada javob beramiz.")

async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[1])
    pending_replies[ADMIN_ID] = user_id
    await query.message.reply_text(f"✍️ Javobingizni yozing → {user_id} ga yuboriladi.\nBekor qilish: /cancel")

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = update.effective_user
    if admin.id != ADMIN_ID:
        await handle_message(update, context)
        return
    if admin.id in pending_replies:
        target_id = pending_replies.pop(admin.id)
        try:
            await context.bot.send_message(chat_id=target_id, text=f"📬 Admin javobi:\n\n{update.message.text}")
            await update.message.reply_text("✅ Javob yuborildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")
    else:
        await update.message.reply_text("ℹ️ Avval '✍️ Javob berish' tugmasini bosing.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pending_replies:
        pending_replies.pop(update.effective_user.id)
        await update.message.reply_text("❌ Bekor qilindi.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(reply_button, pattern=r"^reply_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
