import os
import json
import requests


def get_access_token():
    data = {
            'client_id': os.environ['CLIENT_ID'],
            'grant_type': 'implicit'
            }
    response_with_access_token = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response_with_access_token.raise_for_status()
    access_token = response_with_access_token.json()['access_token']
    return access_token


def get_products_list():
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
    }
    products_response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    products_response.raise_for_status()
    products = products_response.json()['data']
    return products


def add_to_cart(user_id, product_id, quantity):
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json',
    }
    data = json.dumps({"data": {"id": product_id, "type": "cart_item", "quantity": quantity}})
    add_to_cart_response = requests.post(f'https://api.moltin.com/v2/carts/{user_id}/items',
                                         headers=headers, data=data)
    add_to_cart_response.raise_for_status()


def get_cart_by_user_id(user_id):
    cart = []
    headers = {
            'Authorization': f'Bearer {get_access_token()}',
        }
    cart_items_response = requests.get(f'https://api.moltin.com/v2/carts/{user_id}/items', headers=headers)
    cart_items_response.raise_for_status()
    try:
        cart_products = cart_items_response.json()['data']
    except TypeError:
        return 'Cart is empty!'
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
    if not cart_products:
        return 'Cart is empty!'
    return cart


def get_products_from_cart(user_id):
    headers = {
            'Authorization': f'Bearer {get_access_token()}',
        }
    cart_items_response = requests.get(f'https://api.moltin.com/v2/carts/{user_id}/items', headers=headers)
    cart_items_response.raise_for_status()
    try:
        cart_products = cart_items_response.json()['data']
        return cart_products
    except TypeError:
        return 'Cart is empty!'


def get_product_by_id(product_id):
    headers = {
            'Authorization': f'Bearer {get_access_token()}',
        }
    product_response = requests.get(f'https://api.moltin.com/v2/products/{product_id}', headers=headers)
    product_response.raise_for_status()
    product = product_response.json()['data']
    return product


def get_photo_link_by_product_id(product_id):
    product_file_id = get_product_by_id(product_id)['relationships']['main_image']['data']['id']
    headers = {
            'Authorization': f'Bearer {get_access_token()}',
        }
    product_photos_response = requests.get(f'https://api.moltin.com/v2/files/{product_file_id}', headers=headers)
    product_photos_response.raise_for_status()
    photo_link = product_photos_response.json()['data']['link']['href']
    return photo_link


def get_product_card(product):
    product_name = product['name']
    product_price = product['meta']['display_price']['with_tax']['formatted']
    product_description = product['description']
    product_card = f'{product_name}\n\n{product_price} per kg\n\n{product_description}'
    return product_card


def remove_item_from_cart(user_id, item_id):
    headers = {
            'Authorization': f'Bearer {get_access_token()}',
        }
    remove_item_response = requests.delete(f'https://api.moltin.com/v2/carts/{user_id}/items/{item_id}', headers=headers)
    remove_item_response.raise_for_status()


def create_customer(username, user_email):
    headers = {
               'Authorization': f'Bearer {get_access_token()}',
               'Content-Type': 'application/json',
               }
    data = json.dumps({"data": {"type": "customer", "name": username, "email": user_email}})
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, data=data)
    response.raise_for_status()
