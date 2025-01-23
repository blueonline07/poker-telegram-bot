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
        bot.send_message(message.chat.id, "Congratulations, {}! You have joined the table".format(message.from_user.username))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Something went wrong. Please try again later")

@bot.message_handler(commands=['buy','sell'])
def handle_transaction(message):
    try:
        op = message.text.split(' ')[0][1:]
        amount = int(message.text.split(' ')[1])
        print(op)
        if op == 'buy':
            tb.update_balance(message.from_user.id, -amount)
        elif op == 'sell':
            tb.update_balance(message.from_user.id, amount)

        users = tb.get_all_users()
        user_ids = [user["id"] for user in users]
        for user_id in user_ids:
            bot.send_message(user_id, f"{message.from_user.first_name} {message.from_user.last_name} {op}s {amount}. Their balance is now {tb.get_user(message.from_user.id)['balance']}.")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Something went wrong. Please try again later")


@bot.message_handler(commands=['check'])
def check_balance(message):
    bot.send_message(message.chat.id, tb.get_user(message.from_user.id)["balance"])


@bot.message_handler(commands=['all'])
def show_table(message):
    users = tb.get_all_users()
    for user in users:
        bot.send_message(message.chat.id, f"{user['first_name']} {user['last_name']}: {user['balance']}")

@bot.message_handler(commands=['leave'])
def leave_table(message):
    tb.delete_user(message.from_user.id)
    bot.send_message(message.chat.id, "you leaved the table")

bot.infinity_polling()
