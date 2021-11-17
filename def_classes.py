from telebot.types import Message
from typing import Tuple, Optional, List, Dict


class User:
    """ Класс, содержащий информацию о текущем пользователе.

        Содержит следующую информацию:
        - ID пользователя в телеграме;
        - текст команды, введенной пользователем;
        - имя пользователя;
        - язык, на котором пользователь вводит название города, по умолчанию - русский;
        - город, в котором осуществляется поиск отелей, в виде кортежа, где одно значение - ID города, а второе -
    название города;
        - словарь из всех найденных городов по шаблону пользователя, где ключ - ID, значение - название города;
        - количество отелей, отображаемых в результатах поиска, запрошенное пользователем;
        - минимальную, максимальную запрошенные стоимости номера за ночь;
        - минимальное, максимальное запрошенные расстояния от центра города до отеля;
        - список всех найденных отелей в выбранном пользователем городе. Элементы списка - экземпляры класса Hotel.
    """

    def __init__(self, message: Message):
        self.__id: int = message.from_user.id
        self.__command: str = message.text
        self.__user_name: str = message.from_user.username
        self.__locale: str = 'ru_RU'
        self.__city: Optional[Tuple[str]] = None
        self.__founded_cities: Dict[str] = dict()
        self.__hotels_num: str = '0'
        self.__min_price: str = '0'
        self.__max_price: str = '1000000000'
        self.__min_distance: str = '0'
        self.__max_distance: str = '1000000000'
        self.__founded_hotels: Optional[List['Hotel']] = None

    def __str__(self):
        return 'User: {user_name}, command: {command}, search in city: {city}\n' \
               'search settings:\n' \
               'locale = {locale}\n' \
               'number of hotels = {hotels_num}\n' \
               'min_price = {min_price}, max_price = {max_price},\n' \
               'min_distance = {min_distance}, max_distance = {max_distance}'.format(
                    user_name=self.__user_name,
                    command=self.__command,
                    city=self.__city,
                    locale=self.__locale,
                    hotels_num=self.__hotels_num,
                    min_price=self.__min_price,
                    max_price=self.__max_price,
                    min_distance=self.__min_distance,
                    max_distance=self.__max_distance,
               )

    @property
    def id(self) -> int:
        """Геттер. Возвращает ID текущего пользователя"""
        return self.__id

    @property
    def command(self) -> str:
        """Геттер. Возвращает команду, введенную пользователем"""
        return self.__command

    @property
    def user_name(self) -> str:
        """Геттер. Возвращает имя пользователя"""
        return self.__user_name

    @property
    def locale(self) -> str:
        """Геттер. Возвращает значение языка, на котором пользователь вводит название города"""
        return self.__locale

    @property
    def city(self) -> Tuple[str]:
        """Геттер. Возвращает город, в котором осуществляется поиск"""
        return self.__city

    @property
    def founded_cities(self) -> dict:
        """Геттер. Возвращает список найденных городов по шаблону пользователя"""
        return self.__founded_cities

    @property
    def hotels_num(self) -> str:
        """Геттер. Возвращает количество отелей, которое необходимо вывести пользователю"""
        return self.__hotels_num

    @property
    def min_price(self) -> str:
        """Геттер. Возвращает минимальную запрошенную стоимость номера за ночь"""
        return self.__min_price

    @property
    def max_price(self) -> str:
        """Геттер. Возвращает максимальную запрошенную стоимость номера за ночь"""
        return self.__max_price

    @property
    def min_distance(self) -> str:
        """Геттер. Возвращает минимальное запрошенное расстояние от центра города до отеля"""
        return self.__min_distance

    @property
    def max_distance(self) -> str:
        """Геттер. Возвращает максимальное запрошенное расстояние от центра города до отеля"""
        return self.__max_distance

    @property
    def founded_hotels(self) -> Optional[List['Hotel']]:
        """Геттер. Возвращает список всех найденных отелей в выбранном пользователем городе"""
        return self.__founded_hotels

    @city.setter
    def city(self, new_city: Tuple[str]) -> None:
        """Сеттер. Сохраняет название города, в котором осуществляется поиск"""
        if isinstance(new_city, tuple):
            self.__city = new_city
        else:
            raise TypeError('TypeError! The city should be "tuple" with ID of the city and the name of the city')

    @founded_cities.setter
    def founded_cities(self, new_dict: dict) -> None:
        """Сеттер. Сохраняет список найденных городов"""
        self.__founded_cities = new_dict

    @locale.setter
    def locale(self, new_locale: str) -> None:
        """Сеттер. Сохраняет значение языка, используемого пользователем для поиска города"""
        if isinstance(new_locale, str):
            if (new_locale == 'ru_RU') or (new_locale == 'en_EN'):
                self.__locale = new_locale
            else:
                raise ValueError('ValueError! The local value must be "ru_RU" or "en_EN"')
        else:
            raise TypeError('TypeError! The locale value must be "str"')

    @command.setter
    def command(self, new_command: str) -> None:
        """Сеттер. Сохраняет команду, которую ввел пользователь"""
        if new_command.startswith('/'):
            self.__command = new_command
        else:
            raise ValueError('ValueError! The command must start with the "/"')

    @hotels_num.setter
    def hotels_num(self, new_hotels_num: str) -> None:
        """Сеттер. Сохраняет количество отелей, которое необходимо вывести пользователю"""
        if new_hotels_num.isdigit() and 0 < int(new_hotels_num) < 26:
            self.__hotels_num = new_hotels_num
        else:
            raise ValueError('ValueError! The number of hotels must be a natural number from 1 to 25')

    @min_price.setter
    def min_price(self, new_min_price: str) -> None:
        """Сеттер. Сохраняет минимальную стоимость номера отеля за ночь, введенную пользователем"""
        if new_min_price.isdigit():
            self.__min_price = new_min_price
        else:
            raise ValueError('ValueError! The cost must be "int"')

    @min_distance.setter
    def min_distance(self, new_min_distance: str) -> None:
        """Сеттер. Сохраняет минимальное расстояние от центра города до отеля, введенное пользователем"""
        if new_min_distance.isdigit():
            self.__min_distance = new_min_distance
        else:
            raise ValueError('ValueError! The distance must be "int"')

    @max_price.setter
    def max_price(self, new_max_price: str) -> None:
        """ Сеттер. Сохраняет максимальную стоимость номера отеля за ночь, введенную пользователем.

            Если максимальное значение оказалось меньше ранее введенного минимального, то меняет местами максимальное и
        минимальное значения, чтобы всегда min_price <= max_price.
        """
        if new_max_price.isdigit():
            try:
                if int(new_max_price) >= int(self.__min_price):
                    self.__max_price = new_max_price
                else:
                    self.__max_price, self.__min_price = self.__min_price, new_max_price
            except ValueError:
                raise ValueError('ValueError! The cost must be "int"')
        else:
            raise ValueError('ValueError! The cost must be "int"')

    @max_distance.setter
    def max_distance(self, new_max_distance: str) -> None:
        """ Сеттер. Сохраняет минимальное расстояние от центра города до отеля, введенное пользователем.

            Если максимальное значение оказалось меньше ранее введенного минимального, то меняет местами максимальное и
        минимальное значения, чтобы всегда min_distance <= max_distance.
        """
        if new_max_distance.isdigit():
            try:
                if int(new_max_distance) >= int(self.__min_distance):
                    self.__max_distance = new_max_distance
                else:
                    self.__max_distance, self.__min_distance = self.__min_distance, new_max_distance
            except ValueError:
                raise ValueError('ValueError! The distance must be "int"')
        else:
            raise ValueError('ValueError! The distance must be "int"')

    @founded_hotels.setter
    def founded_hotels(self, new_founded_hotels: List['Hotel']) -> None:
        """Сеттер. Сохраняет список найденных отелей"""
        self.__founded_hotels = new_founded_hotels


class Hotel:
    """ Класс, содержащий информацию о найденном отеле.

        Содержит следующую информацию:
        - название;
        - адрес;
        - расстояние до центра от отеля;
        - стоимость одной ночи проживания в отеле.
    """
    def __init__(self, name: str, address: str, distance: str, price: str):
        self.__name = name
        self.__address = address
        self.__distance = distance
        self.__price = price

    def __str__(self):
        return 'Отель "{name}":\n\t- адрес: {address}\n\t' \
               '- расстояние до центра города: {distance}\n\t- стоимость одной ночи проживания: {price}'.format(
                    name=self.__name,
                    address=self.__address,
                    distance=self.__distance,
                    price=self.__price,
                    )

    @property
    def name(self) -> str:
        """Геттер. Возвращает название отеля"""
        return self.__name

    @property
    def address(self) -> str:
        """Геттер. Возвращает адрес отеля"""
        return self.__address

    @property
    def distance(self) -> str:
        """Геттер. Возвращает расстояние от центра города до отеля"""
        return self.__distance

    @property
    def price(self) -> str:
        """Геттер. Возвращает стоимость номера за ночь в отеле"""
        return self.__price
