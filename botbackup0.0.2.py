# Удачный вариант бота со списком личностей.

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from PyCharacterAI import Client

# Загружаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = '6956061902:AAE2Lc-e8oYPbpjJ7Fe6rQEjII3JgmzYNA0'
CHARACTER_AI_TOKEN = '9938692966813a4e31c9ce5cc9d306ffd22c369d'

PERSONALITIES = {
    "Elon Musk": "b_Yo9_TKUggpWjoftwf3AqZCS4FY1n4T0cC8aVEdhY4",
    "Sweetie": "0klw7c6BSjwHDTiif9hc14mLemXRWKxanUd1ekVw2h8",
    "Giga Chad": "sEiSmGMnzTdaO7PxIcAPhccXGUh6OPt57E-r595wbE0",
    "Rias Gremory": "ZkF50Bv9InV3NaWxMAc6n2ksu7w-OerMtGIgz9q0nDw",

}

# Текущая активная личность
current_character_id = PERSONALITIES["Sweetie"]

# Инициализируем клиент AI-чата
ai_client = Client()

async def authenticate_and_create_chat():
    await ai_client.authenticate_with_token(CHARACTER_AI_TOKEN)
    return await ai_client.create_or_continue_chat(current_character_id)

async def switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_character_id, ai_chat
    personality_name = ' '.join(context.args)
    if personality_name in PERSONALITIES:
        current_character_id = PERSONALITIES[personality_name]
        ai_chat = await authenticate_and_create_chat()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Личность изменена на {personality_name}.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не нашел такую личность.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте! Я бот, который использует AI-чат для общения. Cписок личностей: AI, Elon Musk, Giga Chad, Rias Gremory. Для смены личности напишите /switch личность")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ai_chat
    ai_chat = await authenticate_and_create_chat()
    ai_response = await ai_chat.send_message(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ai_response.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    switch_handler = CommandHandler('switch', switch)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

    application.add_handler(start_handler)
    application.add_handler(switch_handler)
    application.add_handler(message_handler)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(application.run_polling())
    loop.close()
