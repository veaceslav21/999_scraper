import os

import telebot
from telebot import types
import csv
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.getenv('TG_TOKEN'))


@bot.message_handler(commands=['start', 'help'])
def start(message):  # The name of func can be different
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Recent Cars'))
    mess = "<b>This bot return all cars that was added in last 24h on www.999.md</b>\n" \
           "P.s. To see all cars press the button bellow"

    bot.send_message(message.chat.id, mess, reply_markup=markup, parse_mode='html')


def get_car_data():
    with open('today_cars.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        if not csv_reader.fieldnames:
            yield "<b>Car's data isn't collected yet.\nTry again later.</b>"
        for car in csv_reader:
            mess = f"<b>Brand:</b> {car['brand']}\n" \
                   f"<b>Year:</b> {car['year']}\n" \
                   f"<b>Mileage:</b> {car['mileage']}\n" \
                   f"<b>Eng_Vol:</b> {car['eng_volume']}\n" \
                   f"<b>Fuel_Type:</b> {car['fuel_type']}\n" \
                   f"<b>Price:</b> {car['price']}\n" \
                   f"<b>Link:</b> {car['car_link']}\n"
            yield mess


@bot.message_handler(content_types=['text'])
def list_all_cars(message):
    if message.text == 'Recent Cars':
        for mess in get_car_data():
            bot.send_message(message.chat.id, mess, parse_mode='html')


bot.polling(none_stop=True)
