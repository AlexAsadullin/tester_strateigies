import json
import telebot 
from telebot import types 

TOKEN = '7175712627:AAEnewR_LaPlruldxttUpbT5GpnvDH1_duA'
bot = telebot.TeleBot(TOKEN) 

 
MESSG = {}

@bot.message_handler(commands=['start'])
def hello(message): # hello функция
    MESSG['chat_id'] = message.chat.id  # сохраняем id чата, в который пишем сообщения
    markup = types.InlineKeyboardMarkup()  # создаем кнопки "добавить задачу" и "мои задачи"
    markup.add(types.InlineKeyboardButton('Add task', callback_data='Add task'))
    markup.add(types.InlineKeyboardButton('My tasks', callback_data='My tasks'))

    bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name}! \n?',
                     reply_markup=markup)  # пишем сообщение с кнопками


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback): # функция для отслеживания нажатий кнопок
    global MESSG
    if callback.data == 'Add task':
        msg = bot.send_message(MESSG['chat_id'], 'Enter your task:')
        bot.register_next_step_handler(msg, create_task)  # вызываем функцию для создания сообщения

    elif callback.data == 'My tasks':
        bot.send_message(MESSG['chat_id'], text='Your tasks for now:')
        with open("tasks.txt", "r") as file:
            users_tasks = json.loads(file.read()) # считали все задачи из файла
        try:
            for key, value in users_tasks.items():
                today_todo = f'"{key}", remind at {value}'
                bot.send_message(MESSG['chat_id'], text=today_todo) # выводим задачи
        except KeyError:
            bot.send_message(MESSG['chat_id'], text='No tasks!') # если нет задач
        


def create_task(message): # функция для создания задачи
    global tasks
    tasks[message.text] = None # создали новый ключ
    MESSG['task'] = message.text
    msg = bot.send_message(MESSG['chat_id'], 'Type the deadline like:\nHOURS.MINUTES')
    bot.register_next_step_handler(msg, add_time)  # вызываем функцию для считывания срока
    # т.к. одна функция принимает только одно сообщение


def add_time(message):  # функция для добавления сроков
    global tasks
    time_s = str(message.text) # считали сообщение
    if '.' in time_s:
        tasks[MESSG['task']] = time_s # добавили срок по ключу
        bot.reply_to(message, 'Task added, well done!') # похвалили пользователя
        with open("tasks.txt", "w") as file:
            file.write(json.dumps(tasks)) # обновили данные в файле tasks
        file.close()
        with open("message.txt", "w") as file:
            file.write(json.dumps(MESSG)) # обновили данные в файле message
        file.close()
        hello(message) # вернулись к выбору добавить задачу или посмотереть существующие
    else:
        bot.reply_to(message, 'Wrong format, type: HOURS.MINUTES.') # если формат времени неверный
        hello(message)



bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()

bot.infinity_polling()