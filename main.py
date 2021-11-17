import telebot
import os
import logging
import functools
import time
import requests
import json
import re

from dotenv import load_dotenv
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from collections.abc import Callable
from def_classes import User, Hotel
from datetime import datetime, timedelta


load_dotenv()  # загрузка параметров из .env

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))  # создание экземпляра бота

users_list = dict()
# словарь для хранения информации о всех пользователях,
# где ключ - имя пользователя, значение - экземпляр класса User конкретного пользователя
logging.basicConfig(
    filename='log_file.log',
    format="%(asctime)s - %(module)s - %(name)s - %(funcName)s - %(levelname)s: line %(lineno)d - %(message)s",
    level=logging.INFO,
    filemode='w')
logger = logging.getLogger(name='bot_logger')


def logger_dec_commands(func: Callable) -> Callable:
    """ Декоратор для логирования функций, обрабатывающих сообщения/команды пользователя.

        Записывает в log_file.log события: попытку старта функции, старт работы функции, завершение работы функции,
    время работы функции.
        Содержит информацию: имя функции; имя пользователя, вызвавшего функцию; сообщение/команда, введенные
    пользователем.
        При ошибке - записывает в log_file.log информацию об ошибке.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_name = args[0].from_user.username
        message_text = args[0].text
        logger.info('Try to start "{func_name}" function by "{user_name}" with "{message}"'.format(
            func_name=func.__name__,
            user_name=user_name,
            message=message_text))
        try:
            logger.info('Start "{func_name}" function by "{user_name}" with "{message}"'.format(
                func_name=func.__name__,
                user_name=user_name,
                message=message_text))
            start_time = time.time()
            result = func(*args, **kwargs)
            work_time = round(time.time() - start_time, 3)
            logger.info('End "{func_name}" function, work time = {work_time} ms'.format(
                func_name=func.__name__,
                work_time=work_time))
            return result
        except Exception as ex:
            logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=func.__name__))
            return 'Unknown Error. Try later'
    return wrapper


def logger_dec_simple(func: Callable) -> Callable:
    """ Декоратор для логирования функций, НЕ обрабатывающих сообщения/команды пользователя.

        Записывает в log_file.log события: попытку старта функции, старт работы функции, завершение работы функции,
    время работы функции.
        При ошибке - записывает в log_file.log информацию об ошибке.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info('Try to start "{func_name}" function'.format(func_name=func.__name__))
        try:
            logger.info('Start "{func_name}" function'.format(func_name=func.__name__))
            start_time = time.time()
            result = func(*args, **kwargs)
            work_time = round(time.time() - start_time, 3)
            logger.info('End "{func_name}" function, work time = {work_time} ms'.format(
                func_name=func.__name__,
                work_time=work_time))
            return result
        except Exception as ex:
            logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=func.__name__))
            return 'Unknown Error. Try later'
    return wrapper


@logger_dec_simple
def check_command(message: Message) -> bool:
    """ Функция проверяет, является ли сообщение от пользователя сообщением-командой.

        Проверяет, начинается ли сообщение на символ "/". Если начинается и сообщение является одной из основных команд,
    то управление передается функции-обработчику команд. Если сообщение начинается на "/" и не является одной из
    основных команд, то управление передается функции-обработчику обычных сообщений. В обоих случаях возвращает True для
    прерывания работы той функции, внутри которой производится проверка.
        Если сообщение не начинается на "/", то возвращает False для продолжения работы той функции, внутри которой
    производится проверка.
    """
    if message.text.startswith('/'):
        logger.warning("Function was stopped by user's command")
        commands = ['/start', '/help', '/lowprice', '/highprice', '/bestdeal']
        if message.text in commands:
            get_command_messages(message)
        else:
            get_text_messages(message)
        return True
    return False


@bot.message_handler(commands=['start', 'help', 'lowprice', 'highprice', 'bestdeal'])
@logger_dec_commands
def get_command_messages(message: Message) -> None:
    """ Функция, обрабатывающая команды 'start', 'help', 'lowprice', 'highprice', 'bestdeal' от пользователя."""
    text = message.text
    if message.from_user.id not in users_list:
        users_list[message.from_user.id] = User(message=message)
    # создание экземпляра класса User конкретного пользователя и добавление его в список пользователей, если ранее не
    # был создан
    users_list[message.from_user.id].command = text  # сохранение информации о команде в экземпляр класса User

    if text == "/start":
        bot.send_message(message.from_user.id,
                         f"Здравствуйте, {message.from_user.first_name}! \nВас приветствует бот TooEasyTravel!\n\n"
                         f"Я создан для того, чтобы помочь Вам найти самые лучшие и самые выгодные условия для "
                         f"проживания в гостиницах всего мира.\n\nЧтобы узнать, что именно я могу, введите команду "
                         f"/help (или нажмите на неё).")
        return
    elif text == "/help":
        bot.send_message(message.from_user.id,
                         'Поддерживаемые команды:\n'
                         '/help - Помощь по командам бота\n'
                         '/lowprice - Узнать топ самых дешёвых отелей в городе\n'
                         '/highprice - Узнать топ самых дорогих отелей в городе\n'
                         '/bestdeal - Узнать топ отелей, наиболее подходящих по цене и расположению от центра (самые '
                         'дешёвые и находятся ближе всего к центру)\n\nДля того, чтобы остановить выполнение любой '
                         'работающей команды, введите любую другую команду, начинающуюся на "/"')
        return

    bot.send_message(message.from_user.id, "Введите город, в котором необходимо выполнить поиск:")
    bot.register_next_step_handler(message, search_city)


@bot.message_handler(content_types='text')
@logger_dec_commands
def get_text_messages(message: Message) -> None:
    """ Функция - обработчик сообщений, не входящих в базовый набор команд.

        Проверяет текст, введенный пользователем. Если во введенном тексте есть приветствие из заранее определенного
    списка, то бот здоровается и предлагает помощь. Если сообщение пользователя не распознано как приветствие или
    команда, то бот сообщает, что команда не распознана и выдает подсказку по командам.
    """
    greetings = ['привет', 'hi', 'hello', 'здравствуй', 'добрый день', 'доброе утро', 'добрый вечер']
    users_greeting = re.sub(r"\W+?", '', message.text.lower())
    if users_greeting in greetings:
        bot.send_message(message.from_user.id,
                         f"Здравствуйте, {message.from_user.first_name}!\nЧем я могу Вам помочь?\nЧтобы узнать, что "
                         f"именно я могу, введите команду /help (или нажмите на неё).")
    else:
        bot.send_message(message.from_user.id,
                         'Введена неизвестная команда! \n Чтобы узнать, что именно я могу, введите команду /help (или '
                         'нажмите на неё).')


@logger_dec_commands
def search_city(message: Message) -> None:
    """ Функция осуществляет поиск города, введенного пользователем.

        На основании введенного пользователем текста ищет похожие города и предлагает выбрать из найденных конкретный
    город для последующего поиска необходимых отелей в нем.
        Если город не найден, то предлагается ввести другой город, функция запускается заново.
        Если найден только один город, то пользователю выдается запрос: верно ли найден город. Если пользователь
    отвечает "Да", то бот продолжает работу с этим городом. Если ответ - "Нет", то пользователю предлагается
    ввести другой город, функция запускается заново.
        Если найдено несколько городов, то пользователю предлагается выбрать из найденных вариантов тот, который его
    интересует. Если пользователь выбрал конкретный город, то бот продолжает работу с этим городом. Если пользователь
    выбрал "Нужного мне города нет в списке", то пользователю предлагается ввести другой город, функция запускается
    заново.
    """
    if check_command(message):
        return

    ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '
    en_alphabet = 'abcdefghijklmnopqrstuvwxyz- '
    cur_user = users_list[message.from_user.id]
    cur_city = ''.join(letter for letter in message.text.lower() if letter in (ru_alphabet + en_alphabet))
    # из запроса пользователя выбираем только буквы алфавита, пробелы и дефисы
    try:
        #  проверяем, на каком языке ввел название города пользователь и сохраняем эту информацию для запросов
        if all([True if sym in ru_alphabet else False for sym in cur_city]):
            cur_user.locale = 'ru_RU'
        elif all([True if sym in en_alphabet else False for sym in cur_city]):
            cur_user.locale = 'en_EN'
        else:
            raise ValueError('The name of the city was entered incorrectly. The name must contain characters of the '
                             'Russian or English alphabet or space or "-"')
    except (TypeError, ValueError) as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=search_city.__name__))
        bot.send_message(message.from_user.id, 'Название города должно быть текстом на русском или английском языках, '
                                               'допустимо использование пробелов и символа "-", попробуйте еще раз:')
        bot.register_next_step_handler(message, search_city)
        return

    city_url = "https://hotels4.p.rapidapi.com/locations/search"
    headers = {
        'x-rapidapi-host': 'hotels4.p.rapidapi.com',
        'x-rapidapi-key': os.getenv('KEY')
    }
    querystring = {"query": cur_city, "locale": cur_user.locale}

    bot.send_message(message.from_user.id, "Ожидайте результатов поиска города, это может занять какое-то время...")
    try:
        # в случае ошибки на сервере или превышении времени ожидания ответа - выдает соответствующее сообщение
        response_city = requests.request("GET", city_url, headers=headers, params=querystring, timeout=10)
        if response_city.status_code == 200:
            city_data = json.loads(response_city.text)
        else:
            raise
    except Exception as ex:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Да", callback_data="retry search_city"),
                     InlineKeyboardButton(text="Нет", callback_data="stop"))
        if type(ex) is requests.exceptions.ConnectTimeout:
            logger.error(f'Server timeout exceeded!: {ex}')
            bot.send_message(message.from_user.id, "Сервер не отвечает, попробовать еще раз?", reply_markup=keyboard)
        else:
            logger.error(f'{ex}')
            bot.send_message(message.from_user.id, "Ошибка сервера, попробовать еще раз?", reply_markup=keyboard)
        return

    founded_cities = dict()
    for i_item in city_data['suggestions']:
        # создание словаря из всех найденных городов по шаблону пользователя, где ключ - ID, значение - название города
        if i_item['group'] == 'CITY_GROUP':
            for j_item in i_item['entities']:
                if j_item['type'] == 'CITY':
                    cur_city = re.sub(r'<.*?>', '', j_item['caption'])
                    founded_cities[j_item['destinationId']] = cur_city
    cur_user.founded_cities = founded_cities  # сохранение словаря найденных городов в информацию текущего пользователя

    if len(cur_user.founded_cities) == 0:
        bot.send_message(message.from_user.id, 'Такой город не найден, попробуйте ввести другой город:')
        bot.register_next_step_handler(message, search_city)
        return
    elif len(cur_user.founded_cities) > 0:
        keyboard = InlineKeyboardMarkup()
        if len(cur_user.founded_cities) == 1:
            for city_id in cur_user.founded_cities.keys():
                keyboard.add(InlineKeyboardButton(text='Да', callback_data=city_id),
                             InlineKeyboardButton(text='Нет', callback_data='no'))
                bot.send_message(message.from_user.id,
                                 text=f'Найден город {cur_user.founded_cities[city_id]}.\nГород найден верно?',
                                 reply_markup=keyboard)
        else:
            for city_id in cur_user.founded_cities.keys():
                keyboard.add(InlineKeyboardButton(text=cur_user.founded_cities[city_id], callback_data=city_id))
            keyboard.add(InlineKeyboardButton(text="Нужного мне города нет в списке", callback_data="no"))
            bot.send_message(message.from_user.id,
                             text='Найдено несколько городов по Вашему запросу, выберите тот, который Вас интересует:',
                             reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call: CallbackQuery) -> None:
    """ Функция - обработчик нажатий на кнопки инлайн-клавиатур.

        Обработка нажатий на клавиатуру при выполненном поиске города:
        - если при нажатии на кнопку выбран конкретный город, то подтверждает выбор пользователя и переходит к запросу
    количества отелей, которые хочет увидеть пользователь;
        - если нажата кнопка "Нет" в случае нахождения одного города или кнопка "Нужного мне города нет в списке", то
    предлагает изменить запрос или ввести другой город, и переходит снова к функции поиска города.

        Обработка нажатий на клавиатуру при ошибке работы сервера:
        - если после возникновения ошибки на сервере пользователь решит попробовать выполнить команду еще раз, то
    вызывает соответствующую функцию;
        - если пользователь откажется от попыток выполнить ту же команду, то останавливает выполнение всех команд.
    """
    if call.data == "retry search_city":  # кнопка "Да" после сообщения об ошибке на сервере при поиске города
        bot.send_message(call.from_user.id, "Введите город, в котором необходимо выполнить поиск:")
        bot.register_next_step_handler(call.message, search_city)

    if call.data == "retry search_hotels":  # кнопка "Да" после сообщения об ошибке на сервере при поиске отелей
        bot.send_message(call.from_user.id, "Пробуем связаться с сервером еще раз...")
        search_hotels(users_list[call.from_user.id])

    if call.data == "stop":  # кнопка "Нет" после сообщения об ошибке на сервере при поиске города или отелей
        bot.send_message(call.from_user.id, "Работа бота остановлена. Введите любую команду для продолжения.\n/help - "
                                            "список доступных команд")

    if call.data.isdigit():  # кнопка "Да" или кнопка с названием города после выполненного поиска городов/города
        cur_user = users_list[call.from_user.id]
        cur_user.city = (call.data, cur_user.founded_cities.get(call.data))
        bot.send_message(call.message.chat.id, f'Вы выбрали {cur_user.city[1]}')
        bot.send_message(call.from_user.id, "Введите количество отелей для поиска (значение от 1 до 25):")
        bot.register_next_step_handler(call.message, set_hotel_num)

    if call.data == 'no':  # кнопка "Нет" или "Нужного мне города нет в списке" после выполненного поиска городов/города
        bot.send_message(call.message.chat.id, 'Очень жаль, что нужный Вам город не найден...\n'
                                               'Попробуйте изменить запрос или введите другой город, '
                                               'который Вас интересует:')
        bot.register_next_step_handler(call.message, search_city)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    # удаляем клавиатуру с кнопками после выбора пользователя во избежание повторных нажатий на кнопки


@logger_dec_commands
def set_hotel_num(message: Message) -> None:
    """ Функция осуществляет поиск отелей по введенным пользователем параметрам и выводит пользователю результат.

        Сохраняет информацию о количестве запрошенных отелей в экземпляр класса User текущего пользователя.

        Если введены команды '/lowprice' или '/highprice', то сразу вызывает функцию search_hotels для поиска отелей,
    если введена команда '/bestdeal', то вызывает функцию set_min_price для получения недостающих параметров поиска.
    """
    if check_command(message):
        return

    cur_user = users_list[message.from_user.id]
    try:
        cur_user.hotels_num = message.text  # проверка корректности введенных данных
    except ValueError as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=set_hotel_num.__name__))
        bot.send_message(message.from_user.id,
                         "Количество отелей должно быть целым числом от 1 до 25, попробуйте еще раз:")
        bot.register_next_step_handler(message, set_hotel_num)
        return

    if cur_user.command == '/lowprice' or cur_user.command == '/highprice':
        search_hotels(cur_user=cur_user)
    elif cur_user.command == '/bestdeal':
        bot.send_message(message.from_user.id, "Введите минимальную стоимость номера за ночь в рублях:")
        bot.register_next_step_handler(message, set_min_price)


@logger_dec_commands
def set_min_price(message: Message) -> None:
    """ Функция сохраняет минимальное значение стоимости номера за ночь, введенное пользователем.

        После работы передает управление функции set_max_price.
    """
    if check_command(message):
        return

    try:
        users_list[message.from_user.id].min_price = message.text  # проверка корректности введенных данных
        bot.send_message(message.from_user.id, "Введите максимальную стоимость номера за ночь в рублях:")
        bot.register_next_step_handler(message, set_max_price)
    except ValueError as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=set_min_price.__name__))
        bot.send_message(message.from_user.id, "Минимальная стоимость отеля должна быть целым положительным числом, "
                                               "попробуйте еще раз:")
        bot.register_next_step_handler(message, set_min_price)


@logger_dec_commands
def set_max_price(message: Message) -> None:
    """ Функция сохраняет максимальное значение стоимости номера за ночь, введенное пользователем.

        После работы передает управление функции set_min_distance.
    """
    if check_command(message):
        return

    try:
        users_list[message.from_user.id].max_price = message.text  # проверка корректности введенных данных
        bot.send_message(message.from_user.id, "Введите минимальное необходимое расстояние от центра города до отеля "
                                               "в километрах:")
        bot.register_next_step_handler(message, set_min_distance)
    except ValueError as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=set_max_price.__name__))
        bot.send_message(message.from_user.id, "Максимальная стоимость отеля должна быть целым положительным числом, "
                                               "попробуйте еще раз:")
        bot.register_next_step_handler(message, set_max_price)


@logger_dec_commands
def set_min_distance(message: Message) -> None:
    """ Функция сохраняет минимальное расстояние от центра города до отеля, введенное пользователем.

        После работы передает управление функции set_max_distance.
    """
    if check_command(message):
        return

    try:
        users_list[message.from_user.id].min_distance = message.text  # проверка корректности введенных данных
        bot.send_message(message.from_user.id, "Введите максимальное необходимое расстояние от центра города до отеля "
                                               "в километрах:")
        bot.register_next_step_handler(message, set_max_distance)
    except ValueError as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=set_min_distance.__name__))
        bot.send_message(message.from_user.id, "Минимальное расстояние от центра города до отеля должно быть целым "
                                               "положительным числом, попробуйте еще раз:")
        bot.register_next_step_handler(message, set_min_distance)


@logger_dec_commands
def set_max_distance(message: Message) -> None:
    """ Функция сохраняет максимальное расстояние от центра города до отеля, введенное пользователем.

        После работы вызывает функцию search_hotels для поиска отелей по заданным параметрам.
    """
    if check_command(message):
        return

    try:
        users_list[message.from_user.id].max_distance = message.text  # проверка корректности введенных данных
        search_hotels(cur_user=users_list[message.from_user.id])
    except ValueError as ex:
        logger.error('Error: "{ex}" in "{func_name}"'.format(ex=ex, func_name=set_max_distance.__name__))
        bot.send_message(message.from_user.id, "Максимальное расстояние от центра города до отеля должно быть целым "
                                               "положительным числом, попробуйте еще раз:")
        bot.register_next_step_handler(message, set_max_distance)


@logger_dec_simple
def search_hotels(cur_user: User) -> None:
    """ Функция осуществляет поиск отелей по введенным пользователем параметрам и выводит пользователю результат.

        Формирует разные запросы на сервер в зависимости от команды, введенной пользователем.
        Формирует список отелей на основании информации, полученной от сервера, и с учетом параметров, указанных
    пользователем. Если выполняется команда "/lowprice" или "/highprice", то минимальные цена и расстояния от центра
    города принимаются равными 0, а максимальные - равными 1000000000, чтобы не влиять на выбор отелей для сохранения в
    список найденных отелей. Отели в списке хранятся в виде экземпляров класса Hotel с информацией о названии отеля, его
    адресе, стоимости номера за ночь и расстоянии от центра города до отеля.
        Сформированный список сохраняется в экземпляр класса User текущего пользователя.
        Из списка найденных отелей текущего пользователя выводятся в телеграм информационные сообщения о каждом
    найденном отеле.
    """
    bot.send_message(cur_user.id, "Ожидайте результатов поиска, это может занять какое-то время...")
    cur_city_id = cur_user.city[0]
    check_in_date = datetime.now().date()  # дата заезда - день запроса
    check_out_date = check_in_date + timedelta(days=1)  # дата выезда - следующий день после дня запроса
    url_hotels = "https://hotels4.p.rapidapi.com/properties/list"
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': os.getenv('KEY')
    }

    if cur_user.command == '/lowprice':  # формирование строки-запроса в соответствии с командой пользователя
        querystring = {"destinationId": cur_city_id,
                       "pageNumber": "1",
                       "pageSize": cur_user.hotels_num,
                       "checkIn": str(check_in_date),
                       "checkOut": str(check_out_date),
                       "adults1": "1",
                       "sortOrder": "PRICE",
                       "locale": 'ru_RU',
                       "currency": "RUB"}
    elif cur_user.command == '/highprice':
        querystring = {"destinationId": cur_city_id,
                       "pageNumber": "1",
                       "pageSize": cur_user.hotels_num,
                       "checkIn": str(check_in_date),
                       "checkOut": str(check_out_date),
                       "adults1": "1",
                       "sortOrder": "PRICE_HIGHEST_FIRST",
                       "locale": 'ru_RU',
                       "currency": "RUB"}
    elif cur_user.command == '/bestdeal':
        querystring = {"destinationId": cur_city_id,
                       "pageNumber": "1",
                       "pageSize": "50",
                       "checkIn": str(check_in_date),
                       "checkOut": str(check_out_date),
                       "adults1": "1",
                       "sortOrder": "PRICE",
                       "locale": 'ru_RU',
                       "currency": "RUB",
                       }

    try:
        # в случае ошибки на сервере или превышении времени ожидания ответа - выдает соответствующее сообщение
        response_hotels = requests.request("GET", url_hotels, headers=headers, params=querystring, timeout=10)
        if response_hotels.status_code == 200:
            hotels_data = json.loads(response_hotels.text)
        else:
            raise
    except Exception as ex:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Да", callback_data="retry search_hotels"),
                     InlineKeyboardButton(text="Нет", callback_data="stop"))
        if type(ex) is requests.exceptions.ConnectTimeout:
            logger.error(f'Server timeout exceeded!: {ex}')
            bot.send_message(cur_user.id, "Сервер не отвечает, попробовать еще раз?", reply_markup=keyboard)
        else:
            logger.error(f'{ex}')
            bot.send_message(cur_user.id, "Ошибка сервера, попробовать еще раз?", reply_markup=keyboard)
        return

    founded_hotels = []
    if hotels_data['result'] == 'OK':
        hotels_list = hotels_data['data']['body']['searchResults']['results']
        for hotel in hotels_list:
            hotel_name = hotel['name']
            if hotel.get('address').get('extendedAddress'):
                if hotel['address']['extendedAddress'] != '':
                    hotel_address = ' '.join((hotel['address']['streetAddress'],
                                              hotel['address']['extendedAddress'],
                                              hotel['address']['locality']))
                else:
                    hotel_address = ', '.join((hotel['address']['streetAddress'], hotel['address']['locality']))
            else:
                hotel_address = cur_user.city[1]
            hotel_distance = hotel['landmarks'][0]['distance']
            hotel_price = hotel['ratePlan']['price']['current']

            check_distance = re.sub(r"[^0123456789,]", "", hotel_distance)
            check_distance = re.sub(r",", ".", check_distance)  # численное значение расстояния до центра города
            check_price = re.sub(r"[^0123456789]", "", hotel_price)  # численное значение стоимости номера в отеле

            if ((float(cur_user.min_distance) < float(check_distance) < float(cur_user.max_distance))
                    and (float(cur_user.min_price) < float(check_price) < float(cur_user.max_price))):
                founded_hotels.append(Hotel(name=hotel_name,
                                            address=hotel_address,
                                            distance=hotel_distance,
                                            price=hotel_price))

            if len(founded_hotels) == int(cur_user.hotels_num):
                break

        cur_user.founded_hotels = founded_hotels
    else:
        logger.error('Search hotels ERROR! Result is not "OK"')
        bot.send_message(cur_user.id, 'Возникла непредвиденная ошибка, попробуйте снова.')
        return

    if len(cur_user.founded_hotels) > 0:
        bot.send_message(cur_user.id, f'Найдено {len(cur_user.founded_hotels)} отелей, соответствующих требованиям:')
        for hotel in cur_user.founded_hotels:
            bot.send_message(cur_user.id, str(hotel))
    else:
        bot.send_message(cur_user.id, f'Отелей, соответствующих требованиям, не найдено.')


if __name__ == '__main__':
    bot.polling()
