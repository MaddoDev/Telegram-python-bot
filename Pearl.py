
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
from PyCharacterAI import Client
from Vocabulary.vocabulary import PERSONALITIES, GENRES
from API.apikey import TELEGRAM_BOT_TOKEN, CHARACTER_AI_TOKEN


# Текущая активная личность
current_character_id = PERSONALITIES["Sweetie"]

# Инициализируем клиент AI-чата
ai_client = Client()

async def authenticate_and_create_chat(character_id): # Должен создавать новый чат, но не делает, надо будет потом это проверить
    await ai_client.authenticate_with_token(CHARACTER_AI_TOKEN) # Все проблемы из-за него, за ним глаз да глаз
    return await ai_client.create_or_continue_chat(character_id)

# Создаем стартовые кнопочки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("Выбрать жанр")],
        [KeyboardButton("Купить доступ к NSFW версии чат-бота")],
        [KeyboardButton("Общаться с Куноичи")],
        [KeyboardButton("Контакты")]
        ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Привет! Что вы хотите сделать?", reply_markup=reply_markup)

async def show_personalities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton(personality)] for personality in PERSONALITIES.keys()]
    buttons.append([KeyboardButton("Вернуться в начало")])
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    await update.message.reply_text('Выберите личность:', reply_markup=reply_markup)

def genre_keyboard():
    # Создаем список кнопок, каждая кнопка - это жанр
    buttons = [InlineKeyboardButton(text=genre, callback_data=genre) for genre in GENRES]
    # Группируем кнопки по две в ряд
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(keyboard)

# Используем эту функцию, когда нужно показать пользователю жанры
genre_markup = genre_keyboard()

def personality_keyboard(selected_genre):
    # Получаем список личностей для выбранного жанра
    personalities_list = GENRES[selected_genre]
    # Создаем список кнопок, каждая кнопка - это личность
    buttons = [InlineKeyboardButton(text=personality, callback_data=PERSONALITIES[personality])
               for personality in personalities_list]
    # Группируем кнопки по две в ряд
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(keyboard)

# В этом хендле расписано на какие сообщения реагирует бот.
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character_id, ai_chat
    text = update.message.text

    if text == "Вернуться в начало":
        await start(update, context)
    elif text == "Выбрать жанр":
        await update.message.reply_text('Отлично! Выберите желаемый жанр. Также, личность можно выбрать, просто написав в чат его название', reply_markup=genre_markup)
    elif text == "Купить доступ к NSFW версии чат-бота":
        await update.message.reply_text("Бот был создан @maddodev и @Maxim_pivo.")
    elif text == "Контакты":
        await update.message.reply_text("Бот был создан @maddodev и @Maxim_pivo. За всеми техническими неполадками обращайтесь к нам. Если в нашем списке не оказалось вашей личности, вы также можете написать нам и мы обязательно её добавим! ")
    elif text in PERSONALITIES:
        current_character_id = PERSONALITIES[text]
        ai_chat = await authenticate_and_create_chat(current_character_id)
        if ai_chat is None:
            await update.message.reply_text("Извините, произошла ошибка при создании чата.")
            return
        ai_response = await ai_chat.send_message(text)
        if ai_response is None:
            await update.message.reply_text("Извините, не удалось получить ответ от личности.")
            return
        await update.message.reply_text(ai_response.text)
    else:
        ai_chat = await authenticate_and_create_chat(current_character_id)
        ai_response = await ai_chat.send_message(text)
        await update.message.reply_text(ai_response.text)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character_id, ai_chat
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in GENRES:
        personality_markup = personality_keyboard(data)
        await query.edit_message_text(
            text=f"Выберите личность из жанра {data}:",
            reply_markup=personality_markup
        )
    elif data in PERSONALITIES.values():
        personality_name = get_personality_name_by_id(data)
        current_character_id = data
        ai_chat = await authenticate_and_create_chat(current_character_id)
        await query.edit_message_text(f"Вы выбрали личность: {personality_name}.")
        for name, character_id in PERSONALITIES.items():
            if character_id == data:
                current_character_id = character_id
            break

def get_personality_name_by_id(personality_id):
    for name, p_id in PERSONALITIES.items():
        if p_id == personality_id:
            return name
        

if __name__ == '__main__':   # Запуск бота
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    callback_query_handler = CallbackQueryHandler(handle_callback_query)
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT, handle_message)


    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(callback_query_handler)
    
    application.run_polling()
    
