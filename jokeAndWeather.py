# мой бот погоды и шуток
import telebot
from telebot import types
import requests
import botTok
import darkskyTok
import time
import json
from math import ceil, floor

bot = telebot.TeleBot(botTok.token)
me = 157302061
intro_text = 'Привет!\nС помощью этого бота ты можешь узнать погоду (на текущий момент, а так же прогноз на день и на неделю) или получить рандомный анекдот.\nДля выбора того или иного действия просто нажми на соответствующую кнопку.'



#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------- 
# При старте создаем кнопки для запроса погоды или шутки
@bot.message_handler(commands = ["start"])
def startBot(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, selective=True, row_width=1)
    markup.add(types.KeyboardButton(text = 'Погода', request_location=True), types.KeyboardButton('Анекдот'))
    bot.send_message(message.chat.id, intro_text, reply_markup=markup)

@bot.message_handler(commands = ["help"])
def startBot(message):
    bot.send_message(message.chat.id, intro_text[7:])




#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------- 
# Запрос текущей погоды DarkSky (подразумевается работа c API этог сайта)
@bot.message_handler(content_types=['location'], func=lambda message: message.chat.type == 'private')
def weather_from_darksky(message):
    try:
        if (message.chat.id != me):
            bot.send_message(me, message)
        longitude = message.location.longitude
        latitude = message.location.latitude
        # отправляем запрос на darkSky, используя токен + координаты Ростова + единицы измерения в цельсиях
        res = requests.get("https://api.darksky.net/forecast/" + darkskyTok.darkskyToken + "/{},{}?lang=ru&units=si".format(latitude, longitude))
        # получаем из ответа json
        data = res.json()
        # берем текущее время с сервера в секундах:
        vrem = data['currently']['time']
        # и получаем из него нормальные дату и время
        vrem = time.ctime(vrem)
        # берем описание погоды на текущий момент
        curr_weather = data['currently']['summary']
        # теперь возьмем прогноз на день
        day_weather = data['hourly']['summary']
        # и прогноз на неделю
        week_weather = data['daily']['summary']
        # берем температуру в Цельсиях:
        t_cel = data['currently']['temperature']
        # берем скорость ветра в м/с
        veter = data['currently']['windSpeed']
        veter_low = floor(veter)
        veter_high = ceil(veter)
        try:
            wind_dir = data['currently']['windBearing']
        except KeyError:
            wind_dir = 0
        output = "Время запроса: " + vrem + "\n" + "Сейчас: " + curr_weather + "\n" + "темература воздуха: " + str(t_cel) + "°C" + "\n" + "ветер: "+wind_direction(wind_dir) + str(veter_low) + "-" + str(veter_high) + " м/с" + "\n"  +\
    "Прогноз на день: " + day_weather+ "\n" + "Прогноз на неделю: " + week_weather
        bot.send_message(message.chat.id, '\n {} \n'.format(output))
    except Exception as e:
        print("Exception (weather): ", e)
        bot.send_message(message.chat.id, 'Извините, что-то пошло не так. Попробуйте еще раз.')
        bot.send_message(me, 'Проблема с погодой: \n{}'.format(e))

# функция для описания направления ветра, так как сервер выдает только градусы
def wind_direction(deg):
    if deg <= 23 or deg >= 338:
        return "северный "
    elif deg in range(23, 68):
        return "северо-восточный "
    elif deg in range(68, 113):
        return "восточный "
    elif deg in range(113, 158):
        return "юго-восточный "
    elif deg in range(158, 203):
        return "южный "
    elif deg in range(203, 248):
        return "юго-западный "
    elif deg in range(248, 293):
        return "западный "
    # если ничего не вернулось, то остается единственный результат:
    return "северо-западный "


#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
# запрос анекдота на rzunemogu.ru

@bot.message_handler(regexp = "^Анекдот$", func=lambda message: message.chat.type == 'private')
def joke(message):
    #запрос на сервер с указанием типа шутки
    res = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=1')
    try:
        #декодируем ответ, отключив строгую проверку для декодера
        strk=json.JSONDecoder(strict=False).decode(res.content.decode('windows-1251'))
        # если всё норм,то указываем 🔞 или нет
        bot.send_message(message.chat.id, ' анекдот \n {}'.format(strk['content']))
    except:
        #эта строка для случаев,когда что-то не так с ответом или его декодированием
        strk = {'content':'что-то пошло не так :( попробуй еще раз'}
        bot.send_message(message.chat.id, strk['content'])



#----------------------------------------------------------------------------------------------------

bot.polling()