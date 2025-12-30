import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@your_channel")
FILE_PATH = "HelloWorld.pdf"  # файл должен быть в той же папке

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Старт", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите «Старт», чтобы начать:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        keyboard = [[InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Подпишитесь на канал: {CHANNEL_USERNAME}\nПосле этого нажмите кнопку ниже:",
            reply_markup=reply_markup,
        )
    elif query.data == "check_sub":
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ("member", "administrator", "creator"):
                with open(FILE_PATH, "rb") as f:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
                await query.edit_message_text("🎉 Файл отправлен! Спасибо за подписку.")
            else:
                keyboard = [[InlineKeyboardButton("🔄 Проверить снова", callback_data="check_sub")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"❌ Вы не подписаны. Подпишитесь на {CHANNEL_USERNAME} и нажмите кнопку ниже:",
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await query.edit_message_text("⚠️ Ошибка проверки. Убедитесь, что бот — админ канала.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()