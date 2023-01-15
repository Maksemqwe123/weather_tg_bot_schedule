import asyncio
import re

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from weather_tg_bot import *
from New_life_3.weatear import ru
from New_life_3.config import *
from buttons import *
from geolocation import *
from parsers.parser_pizza import *
from New_life_3.parsers.parser_kinogo import *
from New_life_3.parsers.parser_litres import all_books
from New_life_3.parsers.cook_parser import all_cooks
from New_life_3.parsers.parser_restaurant_pizza import *
from New_life_3.parsers.parser_coffee import *
from New_life_3.parsers.parser_cinema import *
from sqlite import Database
from geopy.geocoders import Nominatim
from aiogram.dispatcher import FSMContext
import aioschedule
import requests
import random
import aiofiles

db = Database('database')
number = random.randint(1, 20)

count_of_attempts = 1
metrix_1 = []
me = []
me_cinema = []
me_restaurant = []
koi = []
poi = []
users = {}


async def start_message(message: types.Message):
    welcome = message.from_user.full_name
    await message.answer(f'Привет {welcome}, я бот который подскажет как провести день, в связи с погодой🌤',
                         reply_markup=user_kb)
    await message.answer('В каком городе ты хочешь узнать погоду?🌤')
    if message.chat.type == 'private':
        db.create_table()
        if not db.create_profile(message.from_user.id):
            db.edit_profile(message.from_user.id, welcome)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено❌', reply_markup=house_or_street)


async def send_all(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == ADMIN_ID:
            text = message.text[9:]
            users_id = db.get_users()
            for row in users_id:
                try:
                    await bot.send_message(row[0], text)

                except:
                    db.set_active(row[0], 0)

            await bot.send_message(message.from_user.id, "Успешная рассылка")


async def today(message: types.Message):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={OPEN_WEATHER_TOKEN}&units=metric&lang={ru}"
        )
        data = r.json()

        # if message.chat.type == 'private':
        #     db.city_user(message.text)

        # if not db.create_profile(p):
        #     db.edit_profile(None, p)

        # if str(message.from_user.id) not in users.keys():
        #     users[str(message.from_user.id)] = message.from_user.full_name
        #
        #     async with aiofiles.open('users_datas.txt', 'w+') as users_file:
        #         for ID, username in users.items():
        #             await users_file.write(f'ID: {ID} | Username: {username}, CITY: {p}')
                    # db.city_user(message.text)

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        wind = data["wind"]["speed"]

        await message.answer(f'В городе: {city} \nТемпература воздуха: {cur_weather} C \nОжидается: {weather_description}\n'
                             f'Скорость ветра: {wind} м/c', reply_markup=house_or_street)

        if 5 > cur_weather > -4:
            await message.answer('cегодня на улице немного холодно❄️, возможно слякоть и гололёд🏊‍♂️⛸,'
                                 'можно остаться дома👨‍💻 или пойти на улицу🚶‍♂🚶‍♀')

        elif -4 > cur_weather > -8:
            await message.answer('сейчас на улице холодно❄️, оденься потеплее🧤, желательно ещё поесть перед выходом🍜🍳')

        elif -9 > cur_weather > -16:
            await message.answer('сейчас на улице довольно холодно🥶, посоветую тебе остаться дома👨‍💻,'
                                 'но если тебе не страшен холод, могу посоветовать куда можно сходить🚶‍♂🚶‍♀')

        elif cur_weather < -16:
            await message.answer('cейчас на улице очень холодно🥶☠️, останься лучше дома👨‍💻')

    except:
        await message.reply("Проверьте название города")


async def leisure(message: types.Message):
    await message.answer('можно посмотреть/почитать фильм/книгу, но перед этим,🎬📚 я бы посоветовал заварить чая/кофе.☕\n'
                         'могу подсказать как легко и просто приготовить вкусный десерт,🧁'
                         'так же проходит акция при заказе пиццы🍕', reply_markup=help_assistant_house)


class DataFilms(StatesGroup):
    Film_cimema = State()


async def street(message: types.Message):

    await DataFilms.Film_cimema.set()

    await message.answer('В каком городе вы хотите посмотреть развлечения🎬☕🍕', reply_markup=user_leisure)


async def leisure_city(message: types.Message, state: FSMContext):
    leisure_city_people = message.text
    koi.append(leisure_city_people)
    await message.answer('Можно сходить в кино/театр,🎥🎭 можно весело провести время катаясь на коньках.⛸️'
                         'В холодную погоду не помешает выпить кофе/чая.☕🍵 Также можно пройтись по прекрасному парку,🌅'
                         'а в конце вечера можно сходить покушать пиццы🍕', reply_markup=help_assistant_street)

    await state.finish()


async def back_weather(message: types.Message):
    await message.answer('Погода на сегодня ожидается...', reply_markup=user_kb)


class DataGame(StatesGroup):
    Offer_game = State()


async def game(message: types.Message):
    global count_of_attempts, number

    if count_of_attempts == 1:
        await message.answer(f'Отгадай число \nя загадал число от 1 до 20, попробуй его угадать😉', reply_markup=menu)
    else:
        await message.answer(f'Введите число🧐')

    await DataGame.Offer_game.set()


async def back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('секунду⏱', reply_markup=house_or_street)


@dp.callback_query_handler(text='back_call')
async def back_call(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, 'секунду⏱', reply_markup=house_or_street)


async def back_street(message: types.Message):
    await message.answer('Сейчас подскажу', reply_markup=help_assistant_street)


async def back_house(message: types.Message):
    await message.answer('Сейчас подскажу', reply_markup=help_assistant_house)


async def pizza(message: types.Message):
    for i in all_parser_pizza[1:4]:
        await message.answer(i[0])


async def kinogo(message: types.Message):
    for i in kinogo_no_duplicates[1:4]:
        await message.answer(f'Название: {i[0]} \nCсылка: {i[-1]}')
    await message.answer('Хочешь посмотреть больше фильмов и выбрать свой любимый жанр❓'
                         '\nУ нас есть бот "I love you kinogo" который поможет вам с '
                         'выбором фильма🍿🎬', reply_markup=bot_films)

    # g = 1
    # while True:
    #     if g < 10:
    #         for i in kinogo_decription, r in kinogo_urls:
    #             await message.answer(f'Название: {i} \nCcылка: {r}\n')
    #             g += 1
    #             print(g)
    #             break
    #     else:
    #         g += 1
    #         print(g)
    #         break

            # if i[1] == i[8] and r[1] == r[8]:
            #     break
            # else:
            #     await message.answer(f'Название: {i} \nCcылка: {r}\n')


async def book(message: types.Message):
    for i in all_books[1:4]:
        await message.answer(f'Название:{i[0]} \nCcылка: {i[-1]}\n')


async def cook(message: types.Message):
    for i in all_cooks[1:4]:
        await message.answer(f'Название: {i[0]} \nCcылка: {i[-1]}\n')


class DataCinema(StatesGroup):
    Loc_cinema = State()


async def cinema(message: types.Message):
    parser_cinema = ParserGenre(koi)
    all_cinema = list(zip(items_genre, urls_genre))
    for i in all_cinema[1:4]:
        await message.answer(f'Название: {i[0]} \nCcылка: {i[1]}', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'Добавлена новая функция❗ \nМожно узнать о ближайшей кинотеатре который находится возле тебя🧭'
                         f' \nФункция работает только на телефоне📱',
                         reply_markup=me_location)

    await DataCinema.Loc_cinema.set()


async def location_cinema(message: types.Message, state: FSMContext):
    if message.location is not None:
        geolocation_me_cinema = (message.location.latitude, message.location.longitude)
        me_cinema.append(geolocation_me_cinema)
        ab_cinema = loc_geo_cinema[:]
        print(ab_cinema)
        ab_cinema.append(geolocation_me_cinema)
        ab_cinema.sort()
        print(ab_cinema)
        ab_index_cinema = ab_cinema.index(geolocation_me_cinema) - 1 if ab_cinema.index(geolocation_me_cinema) > 0 else 1
        print(ab_index_cinema)
        spend_cinema = (ab_cinema[ab_index_cinema])
        print(spend_cinema)
        await bot.send_location(message.chat.id, spend_cinema[0], spend_cinema[1], reply_markup=help_assistant_street)

        nom = Nominatim(user_agent='user')
        location_address = nom.reverse(spend_cinema)
        await message.answer(f'Находится: {location_address}')

        async with state.proxy() as data:
            data["answer1"] = location_address

        await state.finish()


class DataRestaurant(StatesGroup):
    Loc_restaurant = State()


async def restaurant(message: types.Message):
    parser_cinema = ParserRestaurant(koi)
    all_pizza = list(zip(items_restaurant, urls_restaurant, address_restaurant))
    for i in all_pizza[1:4]:
        await message.answer(f'Название: {i[0]} \nCcылка: {i[1]} \nНаходится: {i[2]} ', reply_markup=types.ReplyKeyboardRemove())

    await message.answer(f'Добавлена новая функция❗ \nМожно узнать о ближайшей кофейни которая находится возле тебя🧭'
                         f' \nФункция работает только на телефоне📱',
                         reply_markup=me_location)
    await DataRestaurant.Loc_restaurant.set()


async def location_restaurant(message: types.Message, state: FSMContext):

    geolocator_restaurant = Nominatim(user_agent="Restaurant")  # Указываем название приложения (так нужно, да)
    for i in address_restaurant:
        location_restaurant = geolocator_restaurant.geocode(i, timeout=10)
        if location_restaurant is None:
            locations_latitude_and_longitude_restaurant.append(None)
        else:
            locations_restaurant = location_restaurant.latitude, location_restaurant.longitude

            locations_latitude_and_longitude_restaurant.append(locations_restaurant)

    location_no_duplicates_restaurant = list(set(locations_latitude_and_longitude_restaurant))
    loc_geo_restaurant = list(filter(None, location_no_duplicates_restaurant))
    print(loc_geo_restaurant)

    if message.location is not None:
        geolocation_me_restaurant = (message.location.latitude, message.location.longitude)
        print(geolocation_me_restaurant)
        me_restaurant.append(geolocation_me_restaurant)
        ab_restaurant = loc_geo_restaurant[:]
        print(ab_restaurant)
        ab_restaurant.append(geolocation_me_restaurant)
        ab_restaurant.sort()
        print(ab_restaurant)
        ab_index_restaurant = ab_restaurant.index(geolocation_me_restaurant) - 1 if ab_restaurant.index(geolocation_me_restaurant) > 0 else 1
        print(ab_index_restaurant)
        spend_restaurant = (ab_restaurant[ab_index_restaurant])
        print(spend_restaurant)
        await bot.send_location(message.chat.id, spend_restaurant[0], spend_restaurant[1], reply_markup=help_assistant_street)

        nom = Nominatim(user_agent='user')
        location_address_restaurant = nom.reverse(spend_restaurant)
        await message.answer(f'Находится: {location_address_restaurant}')

        async with state.proxy() as data:
            data["answer3"] = location_address_restaurant

        await state.finish()


class DataCoffee(StatesGroup):
    Loc_coffee = State()


async def coffee(message: types.Message):
    parser_cinema = ParserCoffee(koi)
    all_coffee = list(zip(items_coffee, urls_coffee, address_coffee))
    for i in all_coffee[1:4]:
        await message.answer(f'Название: {i[0]} \nCcылка: {i[1]} \nАдрес: {i[2]}', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'Добавлена новая функция❗ \nМожно узнать о ближайшей кофейни которая находится возле тебя🧭'
                         f' \nФункция работает только на телефоне📱',
                         reply_markup=me_location)

    await DataCoffee.Loc_coffee.set()


async def location_coffee(message: types.Message, state: FSMContext):

    geolocator = Nominatim(user_agent="Tester")  # Указываем название приложения (так нужно, да)
    for i in address_coffee:
        location_coffee = geolocator.geocode(i, timeout=10)
        if location_coffee is None:
            locations_latitude_and_longitude.append(None)
        else:
            locations = location_coffee.latitude, location_coffee.longitude

            locations_latitude_and_longitude.append(locations)

    location_no_duplicates = list(set(locations_latitude_and_longitude))
    loc_geo = list(filter(None, location_no_duplicates))
    print(loc_geo)

    if message.location is not None:
        geolocation_me = (message.location.latitude, message.location.longitude)
        print(geolocation_me)
        me.append(geolocation_me)
        ab = loc_geo[:]
        print(ab)
        ab.append(geolocation_me)
        ab.sort()
        print(ab)
        ab_index = ab.index(geolocation_me) - 1 if ab.index(geolocation_me) > 0 else 1
        print(ab_index)
        spend = (ab[ab_index])
        print(spend)
        await bot.send_location(message.chat.id, spend[0], spend[1], reply_markup=help_assistant_street)

        nom = Nominatim(user_agent='user')
        location_address = nom.reverse(spend)
        await message.answer(f'Находится: {location_address}')

        async with state.proxy() as data:
            data["answer2"] = location_address

        await state.finish()


class Other(StatesGroup):
    Other_city = State()


async def other_city(message: types.Message):
    koi.clear()
    items_restaurant.clear()
    urls_restaurant.clear()
    address_restaurant.clear()
    locations_latitude_and_longitude_restaurant.clear()

    items_coffee.clear()
    urls_coffee.clear()
    address_coffee.clear()
    locations_latitude_and_longitude.clear()

    await Other.Other_city.set()

    await message.answer('В каком городе вы хотите посмотреть развлечения🎬☕🍕', reply_markup=user_leisure)


async def new_city(message: types.Message, state: FSMContext):
    new_city_people = message.text
    koi.append(new_city_people)
    await message.answer('Можно сходить в кино/театр,🎥🎭 можно весело провести время катаясь на коньках.⛸️'
                         'В холодную погоду не помешает выпить кофе/чая.☕🍵 Также можно пройтись по прекрасному парку,🌅'
                         'а в конце вечера можно сходить покушать пиццы🍕', reply_markup=help_assistant_street)

    await state.finish()
# @dp.message_handler(Text(equals='Узнать ближайшее местоположение кофейни', ignore_case=True))
# async def location(message: types.Message):
#     if message.location is not None:
#         geolocation_me = (message.location.latitude, message.location.longitude)
#
#         for i in l:
#             distance = h3.point_dist(geolocation_me, i, unit='m')  # to get distance in meters
#             metrix = (round(distance))
#             print(f'Дистанция между точка {metrix} m')
#             metrix_1.append(metrix)
#         await message.answer(min(metrix_1))


    # Подключить машинное состояние и записать в бд, после будем сравнивать как местоположение кофейни и пользователя

    # await message.answer(f'Название: {coffee_title[0]} \nCcылка: {coffee_urls[0]}')
    # await message.answer(f'Название: {coffee_title[1]} \nCcылка: {coffee_urls[1]}')
    # await message.answer(f'Название: {coffee_title[2]} \nCcылка: {coffee_urls[2]}')
    # await message.answer(f'Название: {coffee_title[3]} \nCcылка: {coffee_urls[3]}')

# @dp.message_handler(Text(equals='Какое представление можно посмотреть?', ignore_case=True))
# async def theatre(message: types.Message):
#     await message.answer(f'Название: {theatre_title[0]} \n{theatre_urls[0]} \nАдрес: {theatre_address[0]}'
#                          f'\nНачало:{theatre_time[0]} \nCтоимость: {theatre_cash[0]}')
#     await message.answer(f'Название: {theatre_title[1]} \n{theatre_urls[1]} \nАдрес: {theatre_address[1]}'
#                          f'\nНачало: {theatre_time[1]} \nCтоимость: {theatre_cash[1]}')
#     await message.answer(f'Название: {theatre_title[2]} \n{theatre_urls[2]} \nАдрес: {theatre_address[2]}'
#                          f'\nНачало: {theatre_time[2]} \nCтоимость: {theatre_cash[2]}')
#     await message.answer(f'Название: {theatre_title[3]} \n{theatre_urls[3]} \nАдрес: {theatre_address[3]}'
#                          f'\nНачало: {theatre_time[3]} \nCтоимость: {theatre_cash[3]}')

async def info_game(message: types.Message, state: FSMContext):
    global number, count_of_attempts

    async with state.proxy() as data:
        data["answer2"] = count_of_attempts

    await state.finish()

    try:
        if int(message.text) == number:
            await message.answer(f'Вы угадали!🎉\nКоличество попыток: {count_of_attempts}', reply_markup=house_or_street)
            number = random.randint(1, 20)

        elif int(message.text) < number:
            await message.answer(f'Попробуйте ещё раз🙃 \nЗагаданное число больше')
            count_of_attempts += 1
            await game(message)

        else:
            await message.answer(f'Попробуйте ещё раз🙃 \nЗагаданное число меньше')
            count_of_attempts += 1
            await game(message)
    except ValueError:
        await message.answer(f'Ошибка❗\nДанные должны иметь числовой тип')
        await game(message)


async def send_reminder():
    all_info = db.all_user_db()
    for all_user in all_info:
        id_user = all_user[1]
        full_name = all_user[3]
    # r = tuple(all_info)
    # Z = r[1:4]
    # p = Z[1]
    # print(int(p[1]))
        await bot.send_message(chat_id=id_user, text=f'Привет {full_name}, хочешь узнать на сегодня погоду?🙃')
        break


async def scheduler():
    aioschedule.every(1).minutes.do(send_reminder)
    # aioschedule.every().day.at("9:30").do(send_reminder)
    # aioschedule.every(10).seconds.do(send_reminder)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(start_message, commands='start', state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(send_all, commands='sendall', state='*')


def register_handlers_weather_house_street(dp: Dispatcher):
    dp.register_message_handler(today, Text(equals=cities, ignore_case=True))
    dp.register_message_handler(leisure, Text(equals='Что можно поделать дома ?🏠', ignore_case=True))
    dp.register_message_handler(street, Text(equals='Как можно провести время на улице ?🚶‍♂🚶‍♀', ignore_case=True),
                                state=None)
    dp.register_message_handler(leisure_city, state=DataFilms.Film_cimema)


def register_handlers_back_game(dp: Dispatcher):
    dp.register_message_handler(back_weather, Text(equals='Узнать погоду в городе🌤', ignore_case=True))
    dp.register_message_handler(game, Text(equals='Сыграть в игру🔮', ignore_case=True), state=None)
    dp.register_message_handler(info_game, state=DataGame.Offer_game)
    dp.register_message_handler(back, Text(equals='Выйти в главное меню📋', ignore_case=True), state='*')
    dp.register_message_handler(back_street, Text(equals='Как можно провести время на улице ?🚶‍♂🚶‍♀', ignore_case=True))
    dp.register_message_handler(back_house, Text(equals='Что можно поделать дома ?🏠', ignore_case=True))


def register_handlers_eats_drinks(dp: Dispatcher):
    dp.register_message_handler(pizza, Text(equals='Что за акция на пиццу?🍕', ignore_case=True))
    dp.register_message_handler(cook, Text(equals='Какой десерт можно легко приготовить?🧁', ignore_case=True))
    dp.register_message_handler(restaurant, Text(equals='Куда можно сходить поесть ?🍽', ignore_case=True), state=None)
    dp.register_message_handler(coffee, Text(equals='Где и какой кофе можно выпить?☕️', ignore_case=True), state=None)


def register_handlers_film_book(dp: Dispatcher):
    dp.register_message_handler(kinogo, Text(equals='Какой фильм можно посмотреть?🎬', ignore_case=True))
    dp.register_message_handler(book, Text(equals='Какую книгу можно почитать?📚', ignore_case=True))
    dp.register_message_handler(cinema, Text(equals='На какой фильм в кинотеатр можно сходить ?🎬', ignore_case=True),
                                state=None)


def register_handlers_location_new_city(dp: Dispatcher):
    dp.register_message_handler(location_cinema, content_types=["location"], state=DataCinema.Loc_cinema)
    dp.register_message_handler(location_restaurant, content_types=["location"], state=DataRestaurant.Loc_restaurant)
    dp.register_message_handler(location_coffee, content_types=["location"], state=DataCoffee.Loc_coffee)
    dp.register_message_handler(other_city, Text(equals='Выбрать другой город🏙️🌃', ignore_case=True), state=None)
    dp.register_message_handler(new_city, state=Other.Other_city)
        # if g < 10:
        #         youi = [int(g) for i in kinogo_decription if g < 10]
        #         youi_1 = [int(g) for r in kinogo_decription if g < 10]
        #         await message.answer(f'Название: {r} \nCcылка: {i}\n')
        #         break
        #     else:
        #         g += 1
        #         print(g)
