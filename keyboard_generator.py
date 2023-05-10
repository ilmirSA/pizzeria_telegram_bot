from telegram import InlineKeyboardButton


def get_show_keyboard(product_id):
    keyboard = [
        [InlineKeyboardButton("Положить в корзину", callback_data=product_id), ],
        [InlineKeyboardButton("Корзина", callback_data='Корзина')],
        [InlineKeyboardButton("Назад", callback_data='Назад')],

    ]

    return keyboard


def get_choice_delivery_keyboard(nearest_pizza):
    keyboard = [
        [InlineKeyboardButton("Самовывоз", callback_data=f"Самовывоз {nearest_pizza['id']}")],
        [InlineKeyboardButton("Доставка", callback_data=f"Доставка")]
    ]

    return keyboard


def get_choice_payment_keybord():
    keyboard = [
        [InlineKeyboardButton("Наличными", callback_data='Наличными')],
        [InlineKeyboardButton("Картой", callback_data="Картой")]
    ]
    return keyboard


def get_check_order(location_id):
    keyboard = [
        [InlineKeyboardButton("Доставил", callback_data=f'Доставил {location_id}')],

    ]
    return keyboard


def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Меню", callback_data="Вперед")],

    ]
    return keyboard


def get_choice_answer_keyboard(location_message_id):
    keyboard = [
        [InlineKeyboardButton("Да", callback_data=f'Да {location_message_id}')],
        [InlineKeyboardButton("Нет", callback_data='Нет')],

    ]
    return keyboard


def get_keyboard_delete_products(products):
    inline_buttons = [InlineKeyboardButton(f"Удалить {button.get('name')}", callback_data=button.get('product_id')) for
                      button
                      in
                      products]
    pay_button = InlineKeyboardButton("Оплатить", callback_data='Оплатить')
    back_button = InlineKeyboardButton("Назад", callback_data='Назад')
    inline_buttons.append(pay_button)
    inline_buttons.append(back_button)
    cart_menu = [inline_buttons[i:i + 1] for i in range(0, len(inline_buttons), 1)]
    return cart_menu


def create_inline_buttons(start, end, button_name, products):
    inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                      products[start:end]]
    bucket_button = InlineKeyboardButton("Корзина", callback_data='Корзина')
    back_button = InlineKeyboardButton(button_name, callback_data=button_name)
    inline_buttons.append(bucket_button)
    inline_buttons.append(back_button)
    return inline_buttons


def get_keyboard_payment():
    inline_button = [[InlineKeyboardButton('Оплата', callback_data='Оплата')]]
    return inline_button


def get_products_keyboard(products, button_name):
    left = 0
    middle = round(len(products) / 2)
    right = len(products)
    if button_name == 'Назад':
        inline_buttons = create_inline_buttons(middle, right, button_name, products)
        products_menu = [inline_buttons[i:i + 1] for i in range(0, len(inline_buttons), 1)]
        return products_menu
    elif button_name == 'Вперед':
        inline_buttons = create_inline_buttons(left, middle, button_name, products)
        products_menu = [inline_buttons[i:i + 1] for i in range(0, len(inline_buttons), 1)]
        return products_menu
