import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@teatime_english_with_larisa")

# 📁 Три файла (все должны лежать в папке с bot.py)
FILE_1 = "СОГЛАСИЕ_на_получение_рекламных_и_информационных_рассылок.pdf"   # Первый файл на шаге 2
FILE_2 = "Политика_обработки_персональных_данных.pdf"   # Второй файл на шаге 2
FILE_3 = "Adult_vocabulary_от_Ларисы.pdf"    # Финальный файл после проверки подписки

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Шаг 1: Приветствие и кнопка «ДА»"""
    keyboard = [[InlineKeyboardButton("ДА", callback_data="yes")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello ✨️\nВы хотите получить Adult Vocabulary?",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    # ===== Шаг 2: После нажатия «ДА» =====
    if query.data == "yes":
        keyboard = [[InlineKeyboardButton("Согласен", callback_data="agree")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем текстовое сообщение
        await query.edit_message_text(
            "Буквально через минуту мой бот вышлет вам Adult Vocabulary "
            "только с действительно самой необходимой лексикой на английском.\n\n"
            "Оставаясь в этом боте и отвечая на сообщения - вы даете свое согласие "
            "на рекламные и информационные рассылки, а также соглашаетесь "
            "с политикой обработки персональных данных\n\n"
            "P.S. Никакого спама с моей стороны не будет. Просто соблюдаем правила игры.",
            reply_markup=reply_markup,
        )

        # Отправляем 2 файла
        for file_path in [FILE_1, FILE_2]:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id, document=f
                    )
            else:
                logger.error(f"Файл не найден: {file_path}")

    # ===== Шаг 3: После нажатия «Согласен» =====
    elif query.data == "agree":
        keyboard = [[InlineKeyboardButton("Подписался", callback_data="subscribed")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "И последнее - проверьте подписаны ли вы на мой канал "
            "«За чашкой английского» @teatime_english_with_larisa, в котором каждый день выходит "
            "самая полезная информация для вашего английского: "
            "лексика 2026 года, свежие статьи, челленджи, видео и подкасты",
            reply_markup=reply_markup,
        )

    # ===== Шаг 4: Проверка подписки =====
    elif query.data == "subscribed":
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME, user_id=user_id
            )

            if member.status in ("member", "administrator", "creator"):
                # ✅ Подписан — отправляем финальный файл
                if os.path.exists(FILE_3):
                    with open(FILE_3, "rb") as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=f,
                            caption="Вот ваш файл. Учите только реальный английский ❤️",
                        )
                else:
                    await query.message.reply_text(
                        f"⚠️ Файл {FILE_3} не найден на сервере."
                    )
            else:
                # ❌ Не подписан
                await query.message.reply_text(
                    "Увы, я не нашла Вас в числе подписчиков моего канала. Попробуйте еще раз."
                )

        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            await query.message.reply_text(
                "⚠️ Ошибка проверки. Убедитесь, что бот — админ канала."
            )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
