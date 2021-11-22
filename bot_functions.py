from shop_api import get_products_list, get_cart_by_user_id, get_products_from_cart
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def send_menu(bot, update):
    query = update.callback_query
    keyboard = []
    for product in get_products_list():
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=product['id'])])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not get_cart_by_user_id(query.message.chat_id):
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
    if get_cart_by_user_id(query.message.chat_id):
        keyboard.append([InlineKeyboardButton('Оплатить', callback_data='Buy')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='Back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not get_cart_by_user_id(query.message.chat_id):
        text = 'Cart is empty!'
    else:
        text = ''.join(get_cart_by_user_id(query.message.chat_id))
    bot.send_message(chat_id=update.callback_query.message.chat_id,
                     text=text, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=query.message.message_id)