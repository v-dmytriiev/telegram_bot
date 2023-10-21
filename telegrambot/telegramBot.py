import json
import telebot
from telebot import types
import os

file_url = 'C:\\Users\\wasko\\telegrambot\\data1.json'   # Here is your json file path.
file_url2 = 'C:\\Users\\wasko\\telegrambot\\data2.json'  # Here is your json file path.
file_url3 = 'C:\\Users\\wasko\\telegrambot\\data3.json'  # Here is your json file path.

bot = telebot.TeleBot(token=os.getenv('TOKEN'))  # Here should be your token defined in the bat [bot_run.bat] file.
AUTHORIZED_USERS = [499736117]  # Here are users who can use the bot.


help_text = "This bot shows up-to-date information about the servers currently in the test.\n\n" \
            "If you choose the '/start' command, the bot will offer you a choice of tests: [L10, L12, Burn-in].\n\n"\
            "Clicking on a server will display more information about it.\n\n" \
            "If you have any questions, please contact the bot developer.\n\n" \
            "An example of the commands you can use in this BOT : '/search', '/start', '/help', '/end"

servers = []


@bot.message_handler(commands=['help'])
def help_message(message):
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS:
        bot.send_message(message.from_user.id, help_text)
    else:
        bot.send_message(message.from_user.id, text=f"{message.from_user.first_name}, permission denied!")


@bot.message_handler(commands=['end'])
def end_work(message):
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS:
        user_name = f"Okay!See you later {message.from_user.first_name} ;)"
        bot.send_message(message.from_user.id, user_name)
    else:
        bot.send_message(message.from_user.id, text=f"{message.from_user.first_name}, permission denied!")


@bot.message_handler(commands=['search'])
def search_servers(messages):
    user_id = messages.from_user.id
    if user_id in AUTHORIZED_USERS:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        user_name = f"{messages.from_user.first_name}"
        search_options = ["serialnumber", "location", "status"]
        for option in search_options:
            button = types.InlineKeyboardButton(option, callback_data=option)
            keyboard.add(button)

        bot.send_message(messages.from_user.id, f"{user_name}, choose search criteria:", reply_markup=keyboard)
    else:
        bot.send_message(messages.from_user.id, text=f"{messages.from_user.first_name}, permission denied!")


@bot.callback_query_handler(func=lambda call: call.data in ["serialnumber", "location", "status"])
def handle_search_option(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    search_criteria = call.data
    message = bot.send_message(chat_id, f"Enter {search_criteria}:")

    bot.register_next_step_handler(message, lambda m: search_servers_by_criteria(m, search_criteria))


def search_servers_by_criteria(message, search_criteria):
    found_servers = []
    user_name = f"{message.from_user.first_name}"
    for server in servers:
        if server[search_criteria] == message.text:
            found_servers.append(server)
    if len(found_servers) > 0:
        button_list = []
        for server in found_servers:
            serialnumber = server.get('serialnumber')
            status = server.get('status')
            location = server.get('location')
            text = f"{serialnumber} - {location} - {status}"
            button = types.InlineKeyboardButton(text, callback_data=serialnumber)
            button_list.append(button)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*button_list)
        bot.send_message(message.chat.id, f"{user_name}, choose search criteria:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "No servers found with that criteria.")


buttons = []
servers_failed_count = 0
servers_pass_count = 0
servers_testing_count = 0
servers_other_count = 0


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS:
        user_name = f"{message.from_user.first_name}"
        key = types.InlineKeyboardMarkup(row_width=3)
        keys_l10 = types.InlineKeyboardButton('L10', callback_data='l10-status')
        keys_l12 = types.InlineKeyboardButton('L12', callback_data='l12-status')
        keys_burn = types.InlineKeyboardButton('Burn-in', callback_data='burn-in-status')
        key.add(keys_l10, keys_l12, keys_burn)
        bot.send_message(message.chat.id, f"{user_name}, choose test: ", reply_markup=key)
    else:
        bot.send_message(message.from_user.id, text=f"{message.from_user.first_name}, permission denied!")


@bot.callback_query_handler(func=lambda call: True)
def test(call):
    global servers_pass_count
    global servers_failed_count
    global servers_testing_count
    global servers_other_count
    user_name = f"{call.from_user.first_name}"
    if call.data == 'l10-status':
        buttons.clear()
        servers.clear()
        with open(file_url) as file:
            data = json.load(file)
        servers.extend(data["servers"]["server"])
        failed_servers = []
        passed_servers = []
        testing_servers = []
        other_servers = []
        failed_servers.clear(), passed_servers.clear(), testing_servers.clear()
        for server in servers:
            serialnumber = server.get('serialnumber')
            status = server.get('status')
            if status == 'FAILED':
                failed_servers.append(server)
                servers_failed_count = len(failed_servers)
            elif status == 'PASSED':
                passed_servers.append(server)
                servers_pass_count = len(passed_servers)
            elif status == 'TESTING':
                testing_servers.append(server)
                servers_testing_count = len(testing_servers)
            else:
                other_servers.append(server)
                servers_other_count = len(other_servers)

            location = server.get('location')
            text = f"{serialnumber} - {location} - {status}"
            button = types.InlineKeyboardButton(text, callback_data=serialnumber)
            buttons.append(button)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        text2 = f"[L10 - Test] {user_name}, choose  server:"
        count = f"FAILED : {servers_failed_count} PASSED : {servers_pass_count} TESTING : {servers_testing_count} " \
                f"OTHER : {servers_other_count}"
        bot.send_message(chat_id=call.from_user.id, text=text2, reply_markup=keyboard)
        bot.send_message(call.from_user.id, count)
    elif call.data == 'l12-status':
        buttons.clear()
        servers.clear()
        with open(file_url2) as file:
            data = json.load(file)
        servers.extend(data["servers"]["server"])
        failed_servers = []
        passed_servers = []
        testing_servers = []
        other_servers = []
        failed_servers.clear(), passed_servers.clear(), testing_servers.clear()
        for server in servers:
            serialnumber = server.get('serialnumber')
            status = server.get('status')
            if status == 'FAILED':
                failed_servers.append(server)
                servers_failed_count = len(failed_servers)
            elif status == 'PASSED':
                passed_servers.append(server)
                servers_pass_count = len(passed_servers)
            elif status == 'TESTING':
                testing_servers.append(server)
                servers_testing_count = len(testing_servers)
            else:
                other_servers.append(server)
                servers_other_count = len(other_servers)
            location = server.get('location')
            text = f"{serialnumber} - {location} - {status}"
            button = types.InlineKeyboardButton(text, callback_data=serialnumber)
            buttons.append(button)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        text2 = f"[L12 - Test] {user_name}, choose server:"
        bot.send_message(chat_id=call.from_user.id, text=text2, reply_markup=keyboard)
        count = f"FAILED : {servers_failed_count} PASSED : {servers_pass_count} TESTING : {servers_testing_count} " \
                f"OTHER : {servers_other_count}"
        bot.send_message(call.from_user.id, count)
    elif call.data == 'burn-in-status':
        buttons.clear()
        servers.clear()
        with open(file_url3) as file:
            data = json.load(file)
        servers.extend(data["servers"]["server"])
        failed_servers = []
        passed_servers = []
        testing_servers = []
        other_servers = []
        failed_servers.clear(), passed_servers.clear(), testing_servers.clear()
        for server in servers:
            serialnumber = server.get('serialnumber')
            status = server.get('status')
            if status == 'FAILED':
                failed_servers.append(server)
                servers_failed_count = len(failed_servers)
            elif status == 'PASSED':
                passed_servers.append(server)
                servers_pass_count = len(passed_servers)
            elif status == 'TESTING':
                testing_servers.append(server)
                servers_testing_count = len(testing_servers)
            else:
                other_servers.append(server)
                servers_other_count = len(other_servers)
            location = server.get('location')
            text = f"{serialnumber} - {location} - {status}"
            button = types.InlineKeyboardButton(text, callback_data=serialnumber)
            buttons.append(button)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        text2 = f"[Burn-in Test] {user_name}, choose server:"
        bot.send_message(chat_id=call.from_user.id, text=text2, reply_markup=keyboard)
        count = f"FAILED : {servers_failed_count} PASSED : {servers_pass_count} TESTING : {servers_testing_count} " \
                f"OTHER : {servers_other_count}"
        bot.send_message(call.from_user.id, count)
    else:
        for server in servers:
            if server['serialnumber'] == call.data:
                message_text = "Server Info:\n\n"
                for key, value in server.items():
                    message_text += f"{key}: {value}\n"
                bot.send_message(call.from_user.id, message_text)


bot.skip_pending = True
bot.polling(none_stop=True)
