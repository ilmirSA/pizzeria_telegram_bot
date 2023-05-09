import textwrap


def get_text(nearest_pizza):
    distance = int(nearest_pizza['pizza_distance'])
    address = nearest_pizza['Address']
    text = ""
    address_distance_text = f"Пиццерия находиться неподолеку она всего в {distance} метрах от вас вот ее адрес {address}"
    if distance <= 0.5:
        text = f'''Доставка будет бесплатной  или можете забрать ее самостоятельно ,{address_distance_text}'''

    elif distance <= 5:
        text = f'''Доставка будет стоить 100 рублей или можете забрать пиццу самостоятельно.{address_distance_text}'''

    elif distance <= 20:
        text = f'''Доставка будет будет стоить 300 рублей или можете забрать пиццу самостоятельно.{address_distance_text}'''
    else:
        text = f'''Так далеко мы не сможешь доставить пиццу поэтому предлагаю вам забрать ее самостоятельно.{address_distance_text}'''
    return text


def get_text_for_backet(pizza_information, total_amount, ):
    text = [f'''
                *{product.get('name')}*
                _{product.get('description')}_
                *Цена за одну пиццу: {product.get('price')} RUB*
                *Количество: {product.get('quantity')}*
                *Цена за {product.get('quantity')}: {product.get('total_price')} RUB*
                '''
            for product in pizza_information]

    total_price = f"*Общая цена {total_amount} RUB*"
    text.append(total_price)
    text = ''.join(text)
    text_dedented = textwrap.dedent(text)

    return text_dedented


def get_text_for_show_products(product_name, product_description, price, quantity):
    text = f'''
        *Пицца:* {product_name}
        *Состав:* _{product_description}_
        *Цена за одну пиццу:* {price}
        *В корзине лежит*: {quantity}
        '''
    text_dedented = textwrap.dedent(text)
    return text_dedented


def get_text_dilivery(street, amount, pizza_radius,time_divilery):

    cost_delivery = "Доставка бесплатная"

    if int(pizza_radius) <=5:
        cost_delivery='100'
    elif int(pizza_radius) <=20:
        cost_delivery='300'


    text = f'''
    *По адресу: {street}*
    *Доставка: {cost_delivery}*
    *Сумма заказа: {amount}*
    *Доставить через {time_divilery} минут*
            '''
    text_dedented = textwrap.dedent(text)
    return text_dedented

TEXT_FOR_PICKUP = "Вы можете забрать пиццу по этому  адресу {pizza_adress}. Приятного аппетита, досвидания!)"

ERROR_TEXT = 'Некорректный адрес введите его заново'
TEXT_COURIER_LATE = 'Приятного аппетита!если курьер не успел доставить пиццу в течении часа напшите в тех поддержку и вы получите ее бесплатно !'
LOCATION_TEXT = "Хорошо,пришлите нам ваш адрес текcтом или геолокацию"
TEXT_FOR_CHOICE_PAYMENTS = 'Выберите способ оплаты'
