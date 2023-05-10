import datetime
import os
from enum import Enum, auto

from dotenv import load_dotenv
from requests.exceptions import HTTPError
from telegram import InlineKeyboardMarkup, InputMediaPhoto
from telegram import ParseMode, LabeledPrice
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, \
    PreCheckoutQueryHandler

from geo import fetch_coordinates, calculate_distance, get_nearest_pizzeria, fetch_address
from get_text import get_shipping_cost, ERROR_TEXT, LOCATION_TEXT, get_text_for_backet, get_text_for_show_products, \
    TEXT_FOR_PICKUP, TEXT_COURIER_LATE, TEXT_FOR_CHOICE_PAYMENTS, get_text_dilivery
from keyboard_generator import get_products_keyboard, get_keyboard_delete_products, get_show_keyboard, \
    get_choice_delivery_keyboard, get_keyboard_payment, get_choice_payment_keybord, get_check_order, \
    get_choice_answer_keyboard, get_menu_keyboard
from moltin import get_product_info, get_photo_link, get_cart_items, remove_cart_item, add_product_to_cart, \
    get_item_id_in_cart, create_customers, get_token_client_credential_token, \
    get_all_products, get_customers_token, create_cart, get_entries, take_products_from_cart, create_entry, \
    get_customer_coordinates, get_quantity, get_price, get_amount, get_entri


class Handlers(Enum):
    HANDLE_DESCRIPTION = auto()
    HANDLE_CART = auto()
    HANDLE_BACKET = auto()
    HANDLE_GEO = auto()
    HANDLE_DELIVERY = auto()
    HANDLE_PAYMENTS = auto()


def get_menu_page(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    update_token(context.bot_data)
    query = update.callback_query
    query.answer()

    button_name = "Назад" if query.data == 'Вперед' else "Вперед"
    products = get_all_products(moltin_token)
    keyboard = get_products_keyboard(products, button_name)

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Выберите товар',
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_DESCRIPTION


def show_products(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    cart_name = query.message.chat_id
    moltin_token = context.bot_data['moltin_token']
    product_id = query.data

    query.answer()

    product_name, product_description, photo_id, sku = get_product_info(moltin_token, product_id)
    file_url = get_photo_link(moltin_token, photo_id)
    price = get_price(moltin_token, sku)
    quantity = get_quantity(moltin_token, product_id, cart_name)

    text = get_text_for_show_products(product_name, product_description, price, quantity)

    keyboard = get_show_keyboard(product_id)
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(chat_id=query.message.chat_id, photo=file_url, caption=text,
                           reply_markup=reply_markup,
                           parse_mode=ParseMode.MARKDOWN_V2)

    query.delete_message()
    return Handlers.HANDLE_CART


def show_bucket(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.message.chat_id
    query.answer()
    products = take_products_from_cart(moltin_token, cart_name)
    keyboard = get_keyboard_delete_products(products)

    reply_markup = InlineKeyboardMarkup(keyboard)
    pizza_information = get_cart_items(moltin_token, cart_name)
    total_amount = get_amount(moltin_token, cart_name)
    text = get_text_for_backet(pizza_information, total_amount)

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    query.delete_message()
    return Handlers.HANDLE_BACKET


def add_to_basket(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.message.chat_id
    product_id = query.data
    first_name = query.from_user.first_name
    product_name, product_description, photo_id, sku = get_product_info(moltin_token, product_id)
    file_url = get_photo_link(moltin_token, photo_id)
    price = get_price(moltin_token, sku)

    keyboard = get_show_keyboard(product_id)
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        add_product_to_cart(
            moltin_token,
            product_id,
            cart_name
        )

        quantity = get_quantity(moltin_token, product_id, cart_name)
        text = get_text_for_show_products(product_name, product_description, price, quantity)
        media = InputMediaPhoto(media=file_url, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        context.bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=media,
            reply_markup=reply_markup
        )

    except HTTPError:

        customer_email = create_customers(
            moltin_token,
            first_name,
            first_name,
            f'{first_name}@swanson.com'
        )
        customers_token = get_customers_token(moltin_token, customer_email)

        create_cart(moltin_token, customers_token, cart_name)
        add_product_to_cart(moltin_token, product_id, cart_name)

        quantity = get_quantity(moltin_token, product_id, cart_name)
        text = get_text_for_show_products(product_name, product_description, price, quantity)
        print(customer_email)
        print(customers_token)

        media = InputMediaPhoto(
            media=file_url,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        context.bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=media,
            reply_markup=reply_markup
        )
    query.answer("Продукт добавлен в корзину")


def remove_item_in_cart(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.message.chat_id
    product_id = query.data
    product_id_in_cart = get_item_id_in_cart(moltin_token, product_id, cart_name)
    remove_cart_item(moltin_token, product_id_in_cart, cart_name)

    products = take_products_from_cart(moltin_token, cart_name)
    keyboard = get_keyboard_delete_products(products)
    reply_markup = InlineKeyboardMarkup(keyboard)
    pizza_information = get_cart_items(moltin_token, cart_name)
    total_amount = get_amount(moltin_token, cart_name)
    text = get_text_for_backet(pizza_information, total_amount)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    query.answer(text='продукт удален из корзины')
    return Handlers.HANDLE_BACKET


def ask_address(update, context):
    chat_id = update.callback_query.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=LOCATION_TEXT)
    return Handlers.HANDLE_GEO


def get_coordinates(update, context):
    yandex_token = context.bot_data['yandex_token']
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    address = update.message.text
    pizza_data = get_entries(moltin_token)

    if update.message.location:
        user_coordinates = (update.message.location.latitude, update.message.location.longitude)
        context.user_data['entry_id'] = create_entry(moltin_token, user_coordinates[0], user_coordinates[1])
        calculated_distance_pizzerias = calculate_distance(user_coordinates, pizza_data)
        nearest_pizzeria = get_nearest_pizzeria(calculated_distance_pizzerias)

        keyboard = get_choice_delivery_keyboard(nearest_pizzeria)
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = get_shipping_cost(nearest_pizzeria)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=reply_markup)
        return Handlers.HANDLE_DELIVERY

    elif fetch_coordinates(yandex_token, address):

        user_coordinates = fetch_coordinates(yandex_token, address)
        context.user_data['entry_id'] = create_entry(moltin_token, user_coordinates[0], user_coordinates[1])

        calculated_distance_pizzerias = calculate_distance(user_coordinates, pizza_data)
        nearest_pizzeria = get_nearest_pizzeria(calculated_distance_pizzerias)

        context.user_data['delivery_man_chat_id'] = nearest_pizzeria['delivery_man_chat_id']
        keyboard = get_choice_delivery_keyboard(nearest_pizzeria)
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = get_shipping_cost(nearest_pizzeria)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=reply_markup)
        return Handlers.HANDLE_DELIVERY

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=ERROR_TEXT)


def late_courier(context):
    context.bot.send_message(chat_id=context.job.context, text=TEXT_COURIER_LATE)


def callback_minute(context):
    delivery_id, message_id_sms, order_time, location_message_id, street, total_amount, pizza_distance, = context.job.context

    time = context.job.context[2] - 1 if context.job.context[2] else 0
    context.job.context[2] = time
    text = get_text_dilivery(street, total_amount, pizza_distance, time)
    keyboard = get_check_order(location_message_id)

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(chat_id=delivery_id,
                                  message_id=message_id_sms,
                                  reply_markup=reply_markup,
                                  text=text,
                                  parse_mode=ParseMode.MARKDOWN_V2
                                  )


def arrange_delivery(update, context):
    query = update.callback_query
    query.answer()

    keyboard = get_keyboard_payment()
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=query.message.chat_id,
                             text="Нажмите на оплату что оплатить заказ!",
                             reply_markup=reply_markup)
    query.delete_message()
    return Handlers.HANDLE_PAYMENTS


def arrange_self_pickup(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    query = update.callback_query
    query.answer()
    flow_id = query.data.split(' ')[1]
    pizza_adress = get_entri(moltin_token, flow_id)
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=TEXT_FOR_PICKUP.format(pizza_adress=pizza_adress))
    query.delete_message()
    return Handlers.HANDLE_PAYMENTS


def payment_choice(update, context):
    query = update.callback_query
    query.answer()
    keyboard = get_choice_payment_keybord()
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=TEXT_FOR_CHOICE_PAYMENTS,
        reply_markup=reply_markup,
    )
    query.delete_message()


def send_invoice(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    query = update.callback_query
    chat_id = query.message.chat_id

    cart_name = query.message.chat_id

    title = "Пример оплаты пиццы"
    description = "Тестовая оплата"
    payload = "Пицца"
    provider_token = context.bot_data['yookassa_token']
    currency = "rub"
    price = get_amount(moltin_token, cart_name)
    prices = [LabeledPrice("Пицца", price)]
    context.bot.send_invoice(chat_id, title, description, payload,
                             provider_token, currency, prices,
                             need_name=False, need_phone_number=False,
                             need_email=False, need_shipping_address=False, is_flexible=False)
    return Handlers.HANDLE_PAYMENTS


def paid_cash(update, context):
    query = update.callback_query
    query.answer()
    yandex_token = context.bot_data['yandex_token']
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    delivery_id = context.user_data['delivery_man_chat_id']
    entry_id = context.user_data['entry_id']
    order_time = 60

    pizza_data = get_entries(moltin_token)
    cart_name = query.message.chat_id
    user_coordinates = get_customer_coordinates(moltin_token, entry_id)

    street = fetch_address(yandex_token, user_coordinates[1], user_coordinates[0])

    total_amount = get_amount(moltin_token, cart_name)

    calculated_distance_pizzerias = calculate_distance(user_coordinates, pizza_data)
    pizza_distance = get_nearest_pizzeria(calculated_distance_pizzerias)['pizza_distance']

    text_courier = get_text_dilivery(street, total_amount, pizza_distance, order_time)
    context.user_data['copy_text'] = text_courier
    location_message_id = context.bot.send_location(
        chat_id=delivery_id,
        latitude=user_coordinates[0],
        longitude=user_coordinates[1],
    )['message_id']
    keyboard = get_check_order(location_message_id)

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['copy_keyboard'] = reply_markup
    message_id_sms = context.bot.send_message(
        chat_id=delivery_id,
        text=text_courier,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup
    )['message_id']

    minute_job = context.job_queue.run_repeating(callback_minute, interval=60,
                                                 context=[delivery_id, message_id_sms, order_time, location_message_id,
                                                          street, total_amount, pizza_distance])
    context.job_queue.run_once(late_courier, 5, context=query.message.chat_id)
    context.user_data['minute_job'] = minute_job
    query.delete_message()

    keyboard_menu = get_menu_keyboard()
    r_p = InlineKeyboardMarkup(keyboard_menu)
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Заказ успешно оплачен курьер приедет в течении часа",
        reply_markup=r_p
    )

    return Handlers.HANDLE_DESCRIPTION


def successful_payment_callback(update, context):
    yandex_token = context.bot_data['yandex_token']
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    delivery_id = context.user_data['delivery_man_chat_id']
    entry_id = context.user_data['entry_id']
    cart_name = update.message.chat_id

    user_coordinates = get_customer_coordinates(moltin_token, entry_id)

    pizza_data = get_entries(moltin_token)

    total_amount = get_amount(moltin_token, cart_name)
    street = fetch_address(yandex_token, user_coordinates[1], user_coordinates[0])
    calculated_distance_pizzerias = calculate_distance(user_coordinates, pizza_data)
    pizza_distance = get_nearest_pizzeria(calculated_distance_pizzerias)['pizza_distance']
    order_time = 60

    text_courier = get_text_dilivery(street, total_amount, pizza_distance, order_time)
    context.user_data['copy_text'] = text_courier

    location_message_id = context.bot.send_location(
        chat_id=delivery_id,
        latitude=user_coordinates[0],
        longitude=user_coordinates[1],

    )['message_id']

    keyboard = get_check_order(location_message_id)

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['copy_keyboard'] = reply_markup
    message_id_sms = context.bot.send_message(
        chat_id=delivery_id,
        text=text_courier,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup
    )['message_id']
    context.job_queue.run_once(late_courier, 5, context=update.message.chat_id)
    minute_job = context.job_queue.run_repeating(callback_minute, interval=60,
                                                 context=[delivery_id, message_id_sms, order_time,
                                                          location_message_id,
                                                          street, total_amount, pizza_distance])
    context.user_data['minute_job'] = minute_job

    keyboard_menu = get_menu_keyboard()
    r_p = InlineKeyboardMarkup(keyboard_menu)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Заказ успешно оплачен курьер приедет в течении часа",
        reply_markup=r_p
    )
    return Handlers.HANDLE_DESCRIPTION


def delivered_order(update, context):
    query = update.callback_query

    delivery_id = context.user_data['delivery_man_chat_id']
    if delivery_id == query.message.chat_id:
        query = update.callback_query

        location_message_id = query.data.split(" ")[1]
        query.answer()
        keyboard = get_choice_answer_keyboard(location_message_id)

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text('Вы уверены?', reply_markup=reply_markup)


def delete_order(update, context):
    query = update.callback_query
    delivery_id = context.user_data['delivery_man_chat_id']

    text = context.user_data['copy_text']
    reply_markup = context.user_data['copy_keyboard']

    if query.data.split(" ")[0] == 'Да':
        update.callback_query.message.delete()
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.data.split(" ")[1])
        context.user_data['minute_job'].schedule_removal()

    else:
        update.callback_query.message.delete()
        context.bot.send_message(
            chat_id=delivery_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup
        )


def precheckout_callback(update, context):
    query = update.pre_checkout_query

    if query.invoice_payload != 'Пицца':

        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                              error_message="Something went wrong...")
    else:
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return Handlers.HANDLE_PAYMENTS


def update_token(bot_data):
    token_creation_time = bot_data['token_creation_time']
    time_is_now = datetime.datetime.now()
    time_interval = time_is_now - token_creation_time
    if time_interval.total_seconds() >= 3500:
        new_token = get_token_client_credential_token(
            bot_data['client_id'],
            bot_data['client_secret'],
        )
        return new_token
    return bot_data['moltin_token']


def start(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)

    moltin_token = context.bot_data['moltin_token']

    products = get_all_products(moltin_token)
    keyboard = get_products_keyboard(products, 'Вперед')
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите товар',
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_DESCRIPTION


def cancel(update, context):
    update.message.reply_text('Всего хорошего!.')
    return ConversationHandler.END


def main():
    load_dotenv()

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    yandex_api_token = os.getenv('YANDEX_API_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    yookassa_token = os.getenv('YOOKASSA_TOKEN')

    updater = Updater(token=tg_token, use_context=True)
    conv_handler = ConversationHandler(per_chat=False,
                                       entry_points=[CommandHandler('start', start)],

                                       states={

                                           Handlers.HANDLE_DESCRIPTION: [
                                               CallbackQueryHandler(get_menu_page, pattern='^' + 'Вперед' + '$'),
                                               CallbackQueryHandler(get_menu_page, pattern='^' + 'Назад' + '$'),
                                               CallbackQueryHandler(show_bucket, pattern='^' + 'Корзина' + '$'),
                                               CallbackQueryHandler(show_products)

                                           ],
                                           Handlers.HANDLE_CART: [
                                               CallbackQueryHandler(get_menu_page, pattern='^' + 'Назад' + '$'),
                                               CallbackQueryHandler(show_bucket, pattern='^' + 'Корзина' + '$'),
                                               CallbackQueryHandler(add_to_basket),
                                           ],
                                           Handlers.HANDLE_BACKET: [
                                               CallbackQueryHandler(get_menu_page, pattern='^' + 'Назад' + '$'),
                                               CallbackQueryHandler(ask_address, pattern='^' + 'Оплатить' + '$'),
                                               CallbackQueryHandler(remove_item_in_cart),

                                           ],

                                           Handlers.HANDLE_GEO: [
                                               MessageHandler(Filters.location, get_coordinates),
                                               MessageHandler(Filters.text, get_coordinates),
                                           ],
                                           Handlers.HANDLE_DELIVERY: [
                                               CallbackQueryHandler(arrange_delivery, pattern='^' + 'Доставка'),
                                               CallbackQueryHandler(arrange_self_pickup, pattern='^' + 'Самовывоз')
                                           ],
                                           Handlers.HANDLE_PAYMENTS: [
                                               CallbackQueryHandler(payment_choice, pattern='^' + 'Оплата'),
                                               CallbackQueryHandler(send_invoice, pattern='^' + 'Картой'),

                                               CallbackQueryHandler(paid_cash, pattern='^' + 'Наличными'),
                                               PreCheckoutQueryHandler(precheckout_callback),
                                               MessageHandler(Filters.successful_payment,
                                                              successful_payment_callback),

                                           ],

                                       },
                                       fallbacks=[CommandHandler('cancel', cancel)]
                                       )

    delivered_handler = CallbackQueryHandler(delivered_order, pattern='^' + 'Доставил')
    delete_order_handler = CallbackQueryHandler(delete_order)

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(delivered_handler)
    updater.dispatcher.add_handler(delete_order_handler)
    updater.dispatcher.bot_data['moltin_token'] = get_token_client_credential_token(client_id, client_secret)
    updater.dispatcher.bot_data['token_creation_time'] = datetime.datetime.now()
    updater.dispatcher.bot_data['client_id'] = client_id
    updater.dispatcher.bot_data['client_secret'] = client_secret
    updater.dispatcher.bot_data['yandex_token'] = yandex_api_token
    updater.dispatcher.bot_data['yookassa_token'] = yookassa_token

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
