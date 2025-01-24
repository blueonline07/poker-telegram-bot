import os
from user import UserTable

import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
tb = UserTable()

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello, {} {}!".format(message.from_user.first_name, message.from_user.last_name))


@bot.message_handler(commands=['help'])
def send_help(message):
    pass


@bot.message_handler(commands=['join'])
def handle_join(message):
    try:
        tb.add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        bot.send_message(message.chat.id, f"Congratulations! You have joined the table, your user id is {message.from_user.id}")
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

@bot.message_handler(commands=['buy','sell'])
def handle_transaction(message):
    try:
        op = message.text.split(' ')[0][1:]
        amount = int(message.text.split(' ')[1])
        if op == 'buy':
            tb.update_balance(message.from_user.id, -amount)
        elif op == 'sell':
            tb.update_balance(message.from_user.id, amount)

        for user in tb.get_all_users():
            bot.send_message(user['id'], f"{message.from_user.first_name} {message.from_user.last_name} {op}s {amount}")

    except Exception as e:
        bot.send_message(message.chat.id, str(e))


@bot.message_handler(commands=['all'])
def show_table(message):
    try:
        sum_balance = 0
        users = tb.get_all_users()
        for user in users:
            sum_balance += user['balance']
            bot.send_message(message.chat.id, f"{user['first_name']} {user['last_name']}: {user['balance']}")

        bot.send_message(message.chat.id, f"Sum balance is {sum_balance}")
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

@bot.message_handler(commands=['leave'])
def leave_table(message):
    try:
        tb.delete_user(message.from_user.id)
        bot.send_message(message.chat.id, "you leaved the table")
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

@bot.message_handler(func=lambda message: True)
def execute(message):
    try:
        if message.text == 'delete all users':
            tb.delete_all_users()
    except Exception as e:
        bot.send_message(message.chat.id, str(e))
    bot.send_message(message.chat.id, "All users have been deleted")


bot.infinity_polling()