import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Если на bothost.ru не задана переменная, будет использоваться это значение по умолчанию
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@teatime_english_with_larisa")
FILE_PATH = "gift.pdf"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Старт", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите «Старт», чтобы получить подарок:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        keyboard = [[InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"1. Подпишитесь на канал: {CHANNEL_USERNAME}\n"
            f"2. После этого нажмите кнопку ниже:",
            reply_markup=reply_markup,
        )
    elif query.data == "check_sub":
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ("member", "administrator", "creator"):
                # Проверяем, существует ли файл перед отправкой
                if not os.path.exists(FILE_PATH):
                    await query.edit_message_text(f"⚠️ Ошибка: Файл {FILE_PATH} не найден на сервере.")
                    return

                with open(FILE_PATH, "rb") as f:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
                await query.edit_message_text("🎉 Файл отправлен! Спасибо за подписку.")
            else:
                keyboard = [[InlineKeyboardButton("🔄 Проверить снова", callback_data="check_sub")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"❌ Вы не подписаны.\nПодпишитесь на {CHANNEL_USERNAME} и нажмите кнопку ниже:",
                    reply_markup=reply_markup,
                )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка проверки: {error_msg}")
            # Показываем точную ошибку пользователю для диагностики
            await query.edit_message_text(
                f"⚠️ Ошибка проверки: {error_msg}\n\n"
                f"Возможно, бот не добавлен в администраторы канала или не имеет нужных прав."
            )

# 🔍 Новая команда для проверки состояния бота
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = "🔍 <b>Диагностика бота:</b>\n\n"
    
    # 1. Проверка токена
    status_msg += f"✅ Токен загружен: {'Да' if BOT_TOKEN else 'НЕТ (проверьте переменные окружения!)'}\n"
    
    # 2. Проверка файла
    status_msg += f"✅ Файл {FILE_PATH} найден: {'Да' if os.path.exists(FILE_PATH) else 'НЕТ (добавьте его в ZIP-архив!)'}\n"
    
    # 3. Проверка канала
    try:
        chat = await context.bot.get_chat(CHANNEL_USERNAME)
        status_msg += f"✅ Канал {CHANNEL_USERNAME} найден: Да\n"
        status_msg += f"   Название: {chat.title}\n"
    except Exception as e:
        status_msg += f"❌ Канал {CHANNEL_USERNAME} НЕ найден. Ошибка: {e}\n"
        
    await update.message.reply_text(status_msg, parse_mode="HTML")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status)) # Добавляем команду диагностики
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
