from admin_commands import add_user, AUTHORIZED_USERS
from API.apikey import TELEGRAM_BOT_TOKEN_NSFW
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from llama_cpp import Llama
import json

# Загрузка списка разрешенных пользователей из файла

# Запуск Куночи здесь
llm = Llama(
    model_path=r"C:\Users\SystemX\Desktop\Telegram-python-bot\Kunoichi\kunoichi-7b.Q5_K_M.gguf",
    n_gpu_layers=-1,  # Закоментируй эту строчку, если хочешь, чтобы куноичи работал только на процессоре!
)

async def handle_kunoichi_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("К сожалению, у вас нет доступа к этому боту.")
        return
    user_input = update.message.text
    prompt = "###" + user_input + "\nAssistant:"

    output = llm(
        prompt,
        max_tokens=280, # <- Максимальное количество токенов в сообщении, лучше не менять, иначе он не закончит мысль.
        stop=["###"], # <- Стоп-слово для модели, иначе будет болтать сам с собой
        echo=False, # <- параметр, отвечающий за повторение промпта пользователя. 
        temperature=0.7,  # Установить температуру на 0.7 для получения более разнообразных, но все еще когерентных ответов
        top_k=50,  # Параметр топ-k для фильтрации токенов с наибольшей вероятностью (50 - хорошее значение)
        top_p=0.95,  # Параметр топ-p для фильтрации токенов с суммарной вероятностью 0.95
    )
    if 'choices' in output and len(output['choices']) > 0:
        response_text = output['choices'][0]['text'].strip()
    else:
        response_text = "Упс, не получилось выдать запрос. Модель выдала бяку :("
    await update.message.reply_text(response_text)



application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN_NSFW).build()

if __name__ == "__main__":

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kunoichi_message)
    application.add_handler(message_handler)

    add_user_handler = CommandHandler("adduser", add_user)
    application.add_handler(add_user_handler)
    # Запуск бота
    application.run_polling()
