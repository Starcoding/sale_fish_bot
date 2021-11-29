import os
import json
import requests
import redis
from datetime import datetime
from db_connect import get_database_connection


def request_new_token(db):
    data = {
                'client_id': os.environ['CLIENT_ID'],
                'grant_type': 'implicit'
                }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    db.set('auth_credentials', response.text)
    return response.json()['access_token']

def get_access_token():
    db = get_database_connection()
    try:
        auth_credentials = json.loads(db.get('auth_credentials'))
        if auth_credentials:
            if datetime.now().timestamp() > auth_credentials['expires']:
                return request_new_token(db)
            return auth_credentials['access_token']
    except:
        return request_new_token(db)
    return request_new_token(db)


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
        return


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
