import os

import requests
from dotenv import load_dotenv


def get_cart_items(api_token, cart_name):
    ''' Возвращает текст для функции show_bucket() '''
    headers = {
        'Authorization': api_token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)

    response.raise_for_status()

    cart_products = response.json()['data']

    products_info = []
    for pizza in cart_products:
        products_info.append(
            {'name': pizza.get('name'),
             'description': pizza.get('description'),
             'quantity': pizza.get('quantity'),
             'price': str(pizza['meta']['display_price']['with_tax']['unit']['formatted']).replace('.', ','),
             'total_price': str(pizza['meta']['display_price']['with_tax']['value']['formatted']).replace('.', ',')
             }
        )
    return products_info


def get_quantity_in_cart(api_token, cart_name):
    headers = {
        'Authorization': api_token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)

    response.raise_for_status()

    cart_products = response.json()['data']


def add_product_to_cart(token, product_id, cart_name):
    '''Добавляет продукты в корзину'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',

    }

    body_parameters = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            "quantity": 1,
        }
    }

    response = requests.post(f'https://api.moltin.com/v2/carts/{cart_name}/items',
                             headers=headers,
                             json=body_parameters)

    response.raise_for_status()
    return response.json()


def get_item_id_in_cart(token, product_id, cart_name):
    ''' возвращает уникальный id продукта в корзине он нужен что бы удалить его потом из корзины'''
    headers = {
        'Authorization': token,
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']

    for item in cart_items:
        if item.get('product_id', None) == product_id:
            return item['id']
    return None


def get_quantity(token, product_id, cart_name):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()

    product_info = response.json()['data']
    for pizza in product_info:
        if pizza.get('product_id', None) == product_id:
            return pizza['quantity']
    return 0


def remove_cart_item(token, product_id, cart_name):
    ''' Удаляет продукт из коризны'''
    headers = {
        'Authorization': token,
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_name}/items/{product_id}',

                               headers=headers)
    response.raise_for_status()


def create_cart(token, customers_token, cart_name):
    ''' Создает корзину'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'x-moltin-customer-token': customers_token

    }
    body_parameters = {
        'data': {
            'name': cart_name,

        },
    }
    response = requests.post('https://api.moltin.com/v2/carts', headers=headers, json=body_parameters)
    print(response.json())
    response.raise_for_status()


def get_token_client_credential_token(client_id, client_secret):
    ''' функция для получения API токена '''
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token


def get_customers_token(token, email):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    json_data = {
        'data': {
            'type': 'token',
            'email': email,
            'password': 'mysecretpassword',
            'authentication_mechanism': 'password',
        },
    }

    response = requests.post('https://api.moltin.com/v2/customers/tokens', headers=headers, json=json_data)
    response.raise_for_status()
    customers_token = response.json()['data']['token']
    return customers_token


def create_customers(token, firstname, lastname, email):
    ''' Создать покупателя'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    body_parameters = {
        'data': {
            'type': 'customer',
            'name': f'{firstname} {lastname}',
            'email': email,
            'password': 'mysecretpassword',
        },
    }

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=body_parameters)
    response.raise_for_status()

    customers_email = response.json()['data']['email']
    customers_id = response.json()['data']['id']

    return customers_email,customers_id


def get_product_info(token, product_id):
    ''' Информация о продукте '''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/pcm/products//{product_id}',
                            headers=headers)

    response.raise_for_status()
    product_info = response.json()

    product_name = product_info['data']['attributes']['name']
    product_description = product_info['data']['attributes']['description']
    photo_id = product_info['data']['relationships']['main_image']['data']['id']
    sku = product_info['data']['attributes']['sku']
    return product_name, product_description, photo_id, sku


def get_cart_info(token, cart_name):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}', headers=headers)
    response.raise_for_status()
    cart_info = response.json()
    return cart_info


def get_photo_link(token, photo_id):
    ''' Получить ссылку на фото продукта'''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/files/{photo_id}', headers=headers)
    response.raise_for_status()
    photo_info = response.json()
    file_url = photo_info['data']['link']['href']
    return file_url


def get_amount(token, cart_name):
    ''' возвращает общую сумму коризны'''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f"https://api.moltin.com/v2/carts/{cart_name}/", headers=headers)
    response.raise_for_status()
    cart_info = response.json()
    return cart_info['data']['meta']['display_price']['with_tax']['amount']


def get_all_products(token):
    products = []
    headers = {
        'Authorization': token,
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers).json()

    for product in response['data']:
        item = {'name': product.get('attributes')['name'], 'id': product.get('id')}
        products.append(item)
    return products


def take_products_from_cart(token, cart_name):
    products = []
    headers = {
        'Authorization': token,
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    for product in response.json()['data']:
        item = {'name': product.get('name'), 'product_id': product.get('product_id')}
        products.append(item)
    return products


def create_flows(token, name, slug, description):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    json_data = {
        'data': {
            'type': 'flow',
            'name': name,
            'slug': slug,
            'description': description,
            'enabled': True,
        },
    }

    response = requests.post('https://api.moltin.com/v2/flows', headers=headers, json=json_data)

    return response.json()


def create_field(token, name, fields_type, flows_id):
    import requests

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    json_data = {
        'data': {
            'type': 'field',
            'name': name,
            'slug': name,
            'field_type': fields_type,
            'description': f' is the {name} of the buyer',
            'required': True,
            'default': 0,
            'enabled': True,
            'relationships': {
                'flow': {
                    'data': {
                        'type': 'flow',
                        'id': flows_id,
                    },
                },
            },
        },
    }

    response = requests.post('https://api.moltin.com/v2/fields', headers=headers, json=json_data)
    response.raise_for_status()


def create_entry(token, lat, lon):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    data = {"data":
        {
            "type": "entry",
            "Latitude": float(lat),
            'Longitude': float(lon),

        }

    }

    response = requests.post('https://api.moltin.com/v2/flows/customer_address/entries', headers=headers, json=data)
    response.raise_for_status()
    address_costumers_info = response.json()

    return address_costumers_info['data']['id']


def get_entries(token):
    headers = {
        'Authorization': token,
    }

    response = requests.get('https://api.moltin.com/v2/flows/pizza/entries', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_customer_coordinates(token, enry_id):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/flows/customer_address/entries/{enry_id}', headers=headers)
    response.raise_for_status()
    customer_coordinates_info = response.json()
    latitude = customer_coordinates_info['data']['Latitude']
    longitude = customer_coordinates_info['data']['Longitude']

    return latitude, longitude


def delete_cart(token):
    headers = {
        'Authorization': token,
    }

    response = requests.delete('https://api.moltin.com/v2/carts/5637051476', headers=headers)
    response.raise_for_status()


def get_entri(token, flow_id):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/flows/pizza/entries/{flow_id}', headers=headers)
    response.raise_for_status()
    pizza_information = response.json()['data']
    pizza_address = pizza_information['Address']

    return pizza_address


def get_price(token, sku):
    headers = {
        'Authorization': token,
    }
    data = {'page[limit]': '30'}

    response = requests.get('https://api.moltin.com/pcm/pricebooks/fbea1d56-a0d0-430e-ad48-82985790e3fa/prices',
                            headers=headers, params=data)
    response.raise_for_status()
    prices = response.json()['data']
    for price in prices:
        if price['attributes']['sku'] == sku:
            return price['attributes']['currencies']['RUB']['amount']
    return 0


def get_customers(token):
    headers = {
        'Authorization': token,
    }

    response = requests.get('https://api.moltin.com/v2/customers', headers=headers)
    print(response.json())


