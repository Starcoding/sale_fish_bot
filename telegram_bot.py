import os
import logging
import redis
import json
from shop_api import (get_products_list, get_product_by_id,
                      get_product_card, get_photo_link_by_product_id,
                      add_to_cart, get_cart_by_user_id,
                      get_products_from_cart, remove_item_from_cart,
                      create_customer)
from telegram.ext import Filters, Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler


_database = None


def send_menu(bot, update):
    query = update.callback_query
    keyboard = []
    for product in get_products_list():
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=product['id'])])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if get_cart_by_user_id(query.message.chat_id) == 'Cart is empty!':
        text = 'Корзина пуста!'
    else:
        text = ''.join(get_cart_by_user_id(query.message.chat_id))
    bot.send_message(chat_id=update.callback_query.message.chat_id,
                     text='Please choose!', reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=query.message.message_id)


def send_cart(bot, update):
    query = update.callback_query
    keyboard = []
    products_in_cart = get_products_from_cart(query.message.chat_id)
    for product in products_in_cart:
        keyboard.append([InlineKeyboardButton('Убрать из корзины {}'.format(product['name']),
                        callback_data=product['id'])])
    if not get_cart_by_user_id(query.message.chat_id) == 'Cart is empty!':
        keyboard.append([InlineKeyboardButton('Оплатить', callback_data='Buy')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='Back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if get_cart_by_user_id(query.message.chat_id) == 'Cart is empty!':
        text = 'Cart is empty!'
    else:
        text = ''.join(get_cart_by_user_id(query.message.chat_id))
    bot.send_message(chat_id=update.callback_query.message.chat_id,
                     text=text, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=query.message.message_id)


def start(bot, update):
    keyboard = []
    for product in get_products_list():
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=product['id'])])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Выберите товар!', reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(bot, update):
    query = update.callback_query
    if query.data == "Cart":
        send_cart(bot, update)
        return 'HANDLE_CART'
    else:
        product_info = get_product_card(get_product_by_id(query.data))
        image_link = get_photo_link_by_product_id(query.data)
        keyboard = [
                    [InlineKeyboardButton('1 кг.', callback_data=json.dumps({'id': query.data, 'quantity': 1})),
                     InlineKeyboardButton('5 кг.', callback_data=json.dumps({'id': query.data, 'quantity': 5})),
                     InlineKeyboardButton('10 кг.', callback_data=json.dumps({'id': query.data, 'quantity': 10}))],
                    [InlineKeyboardButton('Назад', callback_data='Back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_photo(chat_id=query.message.chat_id, photo=image_link,
                       caption=product_info,
                       reply_markup=reply_markup,
                       )
        bot.delete_message(chat_id=query.message.chat_id,
                           message_id=query.message.message_id)
        return "HANDLE_DESCRIPTION"


def handle_description(bot, update):
    query = update.callback_query
    if query.data == 'Back':
        send_menu(bot, update)
        return "HANDLE_MENU"
    else:
        product_id = json.loads(query.data)['id']
        quantity = json.loads(query.data)['quantity']
        add_to_cart(query.message.chat_id, product_id, quantity)
        bot.answer_callback_query(callback_query_id=query.id,
                                  text='Товар успешно добавлен в корзину!',
                                  show_alert=True)
        return "HANDLE_DESCRIPTION"


def handle_cart(bot, update):
    query = update.callback_query
    if query.data == 'Back':
        send_menu(bot, update)
        return "HANDLE_MENU"
    elif query.data == 'Buy':
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text='Пожалуйста пришлите свою электронную почту')
        bot.delete_message(chat_id=query.message.chat_id,
                           message_id=query.message.message_id)
        return 'WAITING_EMAIL'
    else:
        remove_item_from_cart(query.message.chat_id, query.data)
        send_cart(bot, update)
        return "HANDLE_CART"


def waiting_email(bot, update):
    if update.message:
        bot.send_message(chat_id=update.message.chat_id,
                         text=f'Вы прислали {update.message.text}')
        create_customer(update.message.from_user['username'], update.message.text)
    return "END"


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
