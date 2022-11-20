import logging
from time import sleep

import telebot
from telebot import types, logger

from modules.scraper import Scraper, NotifyCallBack
from modules.types import format_notify
from modules.config import CONFIG

# setup bot logger
telebot_log = logger
telebot_log.setLevel(CONFIG['logger']['level'])

# setup bot
bot = telebot.TeleBot(CONFIG['bot']['token'], parse_mode='HTML')
nonstop = False  # по умолчанию цикл не запущен
current_message: types.Message = None


# Обновление команд в меню бота
bot.set_my_commands(
    [
        types.BotCommand('start', 'Запустить бота'),
        types.BotCommand('stop', 'Остановить уведомления'),
        types.BotCommand('status', 'Проверить статус'),
    ]
)


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.from_user.id, text='Введите ссылку:')


@bot.message_handler(commands=['stop'])
def stop(message):
    global nonstop, current_message
    nonstop = False
    bot.send_message(message.from_user.id, text='Парсер остановлен')


@bot.message_handler(commands=['status'])
def status(message):
    if nonstop:
        bot.send_message(message.from_user.id, 'Уведомления включены')
    else:
        bot.send_message(message.from_user.id, 'Уведомления отключены')


def notify(sender_id: int, data: dict):  # callback if new data loaded
    text = format_notify(data)
    bot.send_message(sender_id, text)


@bot.message_handler(content_types=["text"])
def get_url(message):
    global nonstop, current_message
    url = None
    for entity in message.entities:
        if entity.type == "url":
            url = message.text[entity.offset:entity.length]
            break

    sender_id = message.from_user.id
    answer = bot.send_message(sender_id, "Parsing ...")
    bot.delete_message(sender_id, message.message_id)

    if url is None or nonstop:  # проверяем запущен ли уже цикл
        return  # выходим из гет_урл функции

    nonstop = True  # если цикл еще не запущен, указываем что запустили и продолжаем

    # create scraper instance, set_cookie get url
    scraper = Scraper()
    is_setup_ok = scraper.setup(url)

    if is_setup_ok:
        callback = NotifyCallBack(sender_id, notify)
        scraper.set_callback(callback)  # setup callback function for updates handler
        while nonstop:
            scraper.scrap()  # scrap data

    scraper.stop()
    del scraper
    start(answer)  # после выхода из цикла вызываем старт функцию


def run():
    while True:
        try:
            bot.infinity_polling(long_polling_timeout=1)

        except Exception as err:
            sleep(5)
            if nonstop and current_message is not None:
                get_url(current_message)
            else:
                continue


if __name__ == '__main__':
    run()
