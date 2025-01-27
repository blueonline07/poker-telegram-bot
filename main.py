import os
from gc import callbacks

from user import UserTable
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TRANSACTION_BOT_TOKEN = os.environ.get('TRANSACTION_BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
trans_bot = telebot.TeleBot(TRANSACTION_BOT_TOKEN)
db_params = {
    'dbname': 'poker',
    'user': 'ldkhang',
    'password': '1201',
    'host': 'localhost',  # or the host of your PostgreSQL server
    'port': 5432  # or the port your PostgreSQL server is running on
}

tb = UserTable(db_params)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello, {} {}!".format(message.from_user.first_name, message.from_user.last_name))


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, ("/join: join the table\n"
                                       "/leave: leave the table\n"
                                       "/buy <amount>: buy <amount> [from] chips\n"
                                       "/sell <amount>: sell <amount> chips\n"
                                       "/all: show table status\n"))

@bot.message_handler(commands=['join'])
def handle_join(message):
    try:
        print(message.chat.id)
        tb.add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        bot.send_message(message.chat.id, f"Congratulations! You have joined the table, your user id is {message.from_user.id}")
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

@bot.message_handler(commands=['buy','sell'])
def handle_transaction(message):
    try:
        parts = message.text.split(' ')
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Please enter amount of chips to buy")
        op = parts[0][1:]
        amount = int(parts[1])
        f = None
        if len(parts) > 2:
            f = parts[2]

        if op == 'buy':
            if f == 'from':
                buy_from(message, amount)
            else:
                tb.update_balance(message.from_user.id, -amount)
                for user in tb.get_all_users():
                    trans_bot.send_message(user['id'],
                                           f"{message.from_user.first_name} {message.from_user.last_name} {op}s {amount}")
        elif op == 'sell':
            tb.update_balance(message.from_user.id, amount)
            for user in tb.get_all_users():
                trans_bot.send_message(user['id'],
                                       f"{message.from_user.first_name} {message.from_user.last_name} {op}s {amount}")



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

def buy_from(message, amount):
    users = tb.get_all_users()
    # Create an inline keyboard with options
    markup = InlineKeyboardMarkup(row_width=2)

    for user in users:
        callback_data = f"from:{message.chat.id}:to:{user['id']}:{amount}"
        markup.add(InlineKeyboardButton(f"{user['first_name']} {user['last_name']}", callback_data=callback_data))

    bot.send_message(message.chat.id,"choose one user to buy from" ,reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("from"))
def handle_choice(call):
    parts = call.data.split(':')
    amount = parts[4]
    target = parts[3]
    source = parts[1]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("yes", callback_data=f"yes:{source}:{target}:{amount}"))
    markup.add(InlineKeyboardButton("no", callback_data=f"no:{source}:{target}:{amount}"))
    user = tb.get_user(call.message.chat.id)
    bot.send_message(target, f"{user['first_name']} {user['last_name']} wants to buy {amount} from you", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('yes') or call.data.startswith('no'))
def handle_ok(call):
    parts = call.data.split(':')
    amount = int(parts[3])
    ok = parts[0]
    source = parts[1]
    target = parts[2]
    if ok == 'yes':
        tb.update_balance(source, -amount)
        tb.update_balance(target, amount)
        buyer = tb.get_user(source)
        seller = tb.get_user(target)
        users = tb.get_all_users()

        for user in users:
            trans_bot.send_message(user['id'],f"{buyer['first_name']} {buyer['last_name']} buys {amount} from {seller['first_name']} {seller['last_name']}")

    elif ok == 'no':
        bot.send_message(source, 'haha sorry')
    bot.delete_message(call.message.chat.id, call.message.id)

bot.infinity_polling()
