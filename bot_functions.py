import requests
from shop_api import get_products_list, get_products_from_cart, get_access_token
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_cart_by_user_id(user_id):
    cart = []
    cart_products = get_products_from_cart(user_id)
    if not cart_products:
        return
    for product in cart_products:
        product_name = product['name']
        product_description = product['description']
        product_price = product['meta']['display_price']['with_tax']['unit']['formatted']
        product_value = product['meta']['display_price']['with_tax']['value']['formatted']
        product_quantity = product['quantity']
        cart.append(f'{product_name}\n\n{product_price} per kg\n\n{product_description}\n{product_quantity}кг in cart for {product_value}\n\n')
    cart_total_response = requests.get(f'https://api.moltin.com/v2/carts/{user_id}',
                                       headers=headers)
    cart_total_response.raise_for_status()
    cart_total = 'Total: {}'.format(cart_total_response.json()['data']['meta']['display_price']['with_tax']['formatted'])
    cart.append(cart_total)
    return cart


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
