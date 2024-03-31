from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
import asyncio
from PyCharacterAI import Client
from llama_cpp import Llama
from Vocabulary.vocabulary import PERSONALITIES, GENRES
from API.apikey import TELEGRAM_BOT_TOKEN, CHARACTER_AI_TOKEN
import json
# Текущая активная личность
current_character_id = PERSONALITIES["Sweetie"]

# Инициализируем клиент AI-чата
ai_client = Client()

# Инициализируем нейросеть Kunoichi
llm = Llama(
      model_path=r"C:\Users\SystemX\Desktop\PyCAI\kunoichi-7b.Q4_K_M.gguf",
      n_gpu_layers=-1, # Uncomment to use GPU acceleration
      max_tokens=256,
      # seed=1337, # Uncomment to set a specific seed
      n_ctx=2048, # Uncomment to increase the context window
)

KUNOICHI_MODE = 1

async def start_kunoichi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы в режиме общения с нейросетью Kunoichi. Пожалуйста, введите ваш вопрос.")
    return KUNOICHI_MODE

async def handle_kunoichi_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    prompt = "###" + user_input + "\nAssistant:"
    output = llm(
        prompt,
        max_tokens=None,
        stop=["###"],
        echo=False
)
    if 'choices' in output and len(output['choices']) > 0:
        response_text = output['choices'][0]['text'].strip()
    else:
        response_text = "Sorry, I couldn't generate a response."
    await update.message.reply_text(response_text)
    return KUNOICHI_MODE

async def stop_kunoichi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы вышли из режима Kunoichi.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('kunoichi', start_kunoichi)],
    states={
        KUNOICHI_MODE: [MessageHandler(filters.TEXT & ~filters.Command('/stop_kunoichi'), handle_kunoichi_message)],
    },
    fallbacks=[CommandHandler('stop_kunoichi', stop_kunoichi)]
)


# Кнопка под сообщением бота, она же - инлайн-кнопка
inline_buttons = [
    [InlineKeyboardButton(genre, callback_data=genre)] for genre in GENRES
]
inline_reply_markup = InlineKeyboardMarkup(inline_buttons)

async def authenticate_and_create_chat():
    await ai_client.authenticate_with_token(CHARACTER_AI_TOKEN)
    return await ai_client.create_or_continue_chat(current_character_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("Выбрать жанр")],
        [KeyboardButton("Купить доступ к NSFW версии чат-бота")],
        [KeyboardButton("Общаться с Kunoichi")],
        [KeyboardButton("Контакты")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Привет! Что вы хотите сделать?", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character_id
    text = update.message.text

    if text == "Вернуться в начало":
        await start(update, context)
    elif text == "Выбрать жанр":
        await update.message.reply_text('Отлично! Выберите желаемый жанр. Также, личность можно выбрать, просто написав в чат его название', reply_markup=inline_reply_markup)
    elif text == "Купить доступ к NSFW версии чат-бота":
        await update.message.reply_text("NSFW версия чат-бота стоит 100RUB. Данная версия снимает ограничения и цензуру с личностей. Покупая доступ к NSFW, вы подтверждаете, что достигли совершеннолетия. Чтобы купить доступ к NSFW, перейдите по ссылке: [Функция в разработке!]")
    elif text == "Контакты":
        await update.message.reply_text("Бот был создан @maddodev и @Maxim_pivo. Если в нашем списке не оказалось вашей личности, напишите нам и мы обязательно её добавим! ")
    elif text in PERSONALITIES:
        current_character_id = PERSONALITIES[text]
        ai_chat = await authenticate_and_create_chat()
        if ai_chat is None:
            await update.message.reply_text("Извините, произошла ошибка при создании чата.")
            return
        ai_response = await ai_chat.send_message(text)
        if ai_response is None:
            await update.message.reply_text("Извините, не удалось получить ответ от личности.")
            return
        await update.message.reply_text(ai_response.text)
    # else:
    #     output = llm(
    #         text + " A: ", # Prompt
    #         max_tokens=32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
    #         stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
    #         echo=True # Echo the prompt back in the output
    #     )
    #     await update.message.reply_text(output)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character_id
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in GENRES:
        personalities_list = GENRES[data]
        inline_buttons = [
            [InlineKeyboardButton(personality_name, callback_data=personality_name)] for personality_name in personalities_list
        ]
        inline_reply_markup = InlineKeyboardMarkup(inline_buttons)
        await query.edit_message_text(text=f'Выберите личность из жанра "{data}":', reply_markup=inline_reply_markup)
    elif data in PERSONALITIES:
        current_character_id = PERSONALITIES[data]
        ai_chat = await authenticate_and_create_chat()
        await query.edit_message_text(f"Вы выбрали личность: {data}")

if __name__ == '__main__':   # Запуск бота

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


    callback_query_handler = CallbackQueryHandler(handle_callback_query)
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT, handle_message)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(callback_query_handler)

    application.run_polling()
