# Описание Telegram-бота *@TAS_Too_Easy_Travel_bot*

## Техническое описание:
1. Для работы бота требуется запустить скрипт main.py
2. В Telegram найти и запустить бота @TAS_Too_Easy_Travel_bot (https://t.me/TAS_TooEasyTravel_bot)
3. Следовать инструкциям в боте. 

Для поиска отелей используется Hotels API (https://rapidapi.com/apidojo/api/hotels4/)

Для создания бота используется pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md)

## Описание работы команд
### Команда /start
1. Запускается при запуске бота либо при вводе команды пользователем. 
2. Пользователю выводится приветственное сообщение, содержащее краткое описание бота и подсказку для дальнейших действий.
### Команда /help
1. После ввода команды пользователем выводится сообщение, содержащее справочную информацию о возможных командах боту с их кратким описанием.
### Команда /lowprice
1. После ввода команды у пользователя запрашивается:
    1. Город, где будет проводиться поиск.
    2. Количество отелей, которые необходимо вывести в результате (не больше 25 отелей).
2. При поиске города пользователю будет предложено выбрать город из найденных вариантов либо подтвердить правильность найденного города.
3. После ввода количества отелей - ожидайте результатов работы бота.
### Команда /highprice
1. После ввода команды у пользователя запрашивается:
    1. Город, где будет проводиться поиск.
    2. Количество отелей, которые необходимо вывести в результате (не больше 25 отелей).
2. При поиске города пользователю будет предложено выбрать город из найденных вариантов либо подтвердить правильность найденного города.
3. После ввода количества отелей - ожидайте результатов работы бота.
### Команда /bestdeal
1. После ввода команды у пользователя запрашивается:
    1. Город, где будет проводиться поиск.
    2. Количество отелей, которые необходимо вывести в результате (не больше 25 отелей).
    3. Диапазон цен.
    4. Диапазон расстояния, на котором находится отель от центра.
2. При поиске города пользователю будет предложено выбрать город из найденных вариантов либо подтвердить правильность найденного города.
3. После ввода максимального расстояния от центра города до отеля - ожидайте результатов работы бота.

## Дополнительная информация
1. На любом этапе работы бота можно прервать выполнение текущей команды. Для этого необходимо ввести любую
команду, начинающуюся с символа "/".
2. При вводе некорректных данных или при ошибках работы с сервером, содержащим данные об отелях, пользователю выводится соответствующее сообщение и выводится подсказка для дальнейших действий.
3. Telegram-бот создан в рамках работы над дипломным проектом по курсу Python-Basic образовательной платформы Skillbox.


