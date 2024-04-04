from telegram import Update
from telegram.ext import ContextTypes
import json

# from StartModel import AUTHORIZED_USERS
ADMIN_ID = 893632509
AUTHORIZED_USERS = []

try:
    with open('authorized_users.json', 'r') as file:
        AUTHORIZED_USERS = json.load(file)
except FileNotFoundError:
    pass

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы должны быть администратором, чтобы использовать эту команду.")
        return

    new_user_id = update.message.text.split()[1]
    if new_user_id.isdigit():
        new_user_id = int(new_user_id)
        if new_user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(new_user_id)
            with open('authorized_users.json', 'w') as file:
                json.dump(AUTHORIZED_USERS, file)
            await update.message.reply_text(f"ID {new_user_id} успешно добавлен в список авторизованных пользователей.")
        else:
            await update.message.reply_text(f"ID {new_user_id} уже находится в списке авторизованных пользователей.")
    else:
        await update.message.reply_text("Некорректный ID пользователя. Введите команду в формате: /adduser <user_id>")