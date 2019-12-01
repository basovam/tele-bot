import datetime
import time
import string
import os

from PIL import Image, ImageDraw

import sys
sys.path.append('/home/pi/Documents/python/lib') # Задание пути к локальным библиотекам
import alphavantage_api
import telegram_api
import moon
import weather_api

# Задание пути к файлу лога
log_file_path = "/home/pi/Documents/python/bot.log"

# Запрос текущей погоды в Москве
def current_moscow_weather():
	w = weather_api.weather_data() # Создание объекта
	curr = w.current_weather() # Запрос данных
	weather_message = "Температура: " + curr['temp'] + ". Давление: " +curr['pres'] + ". " + curr['weather'] + "." # Формирование строки-ответа
	return weather_message

# Запрос курса валют
def exchange_rate(text):
	wordlist = text.split() # Разделение сообщения на слова
	i = wordlist.index('/currencyexchangerate')+1 # Определение индекса первой валюты
	if i < len(wordlist): # Проверка на наличие первой валюты
		from_cur = wordlist.pop(i) # Извлечение первой валюты
		if i < len(wordlist): # Проверка на наличие второй валюты
			to_cur = wordlist.pop(i) # Извлечение второй валюты
			ad = alphavantage_api.alphavantage_data() # Создание объекта
			ret_mess = ad.currency_exchange_rate(from_cur, to_cur) # Запрос данных
			if ret_mess is not None: # Проверка на корректность ответа
				return ret_mess
		return ("Ошибка в данных.") # Возврат сообщения об ошибке
	return ("Необходимо указать коды валют, например: /currencyexchangerate eur rub") # Возврат сообщения об ошибке

#Запрос свечного графика котировок акции
def stock(text):
	wordlist = text.split() # Разделение сообщения на слова
	i = wordlist.index('/stock')+1 # Определение индекса кода/названия акции
	if i < len(wordlist): # Проверка на наличие кода/названия акции
		name = wordlist.pop(i) # Извлечение кода/названия акции
		try: # Попытка извлечения даты начала построения графика
			date_start = wordlist.pop(i)
		except Exception:
			date_start = None
		try: # Попытка извлечения даты окончания построения графика
			date_end = wordlist.pop(i)
		except Exception:
			date_end = None
		try: # Попытка извлечения размера графика
			acc = wordlist.pop(i)
		except Exception:
			acc = None
		ad = alphavantage_api.alphavantage_data() # Создание объекта
		ret_img = ad.stock_daily(name,date_start,date_end,acc) # Запрос данных
		return ret_img
	# Возврат сообщения
	return ('''Необходимо указать тикет компании, возможно указание даты начала построения графика или дат начала и окончания построения графика (по умолчанию график строится за последние 100 торговых дней).
Например: /stock ibm 2019-01-25 2019-08-25
При указании больших промежутков времени обработка запроса может занять длительное время - более нескольких минут.''')
	
tb = telegram_api.telegram_bot() # Создание объекта для бота
	
raw_data = tb.get_updates_json() # Запрос данных
mess_data = raw_data['result'] # Извлечение данных о новых сообщениях
for mess in mess_data: # Цикл по новым сообщениям
	# Запись информации о сообщении в лог
	log_file = open(log_file_path,"a")
	# Время обработки | Id чата/пользователя | Имя пользователя | текст сообщения
	log_file.write(str(datetime.datetime.now()) + " | " + str(mess['message']['chat']['id']) + " | " + str(mess['message']['chat']['first_name']) + " | " + str(mess['message']['text']) + " |\n")	 
	log_file.close()
	chat_id = mess['message']['chat']['id'] # Извлечение Id чата/пользователя 
	mess_txt = mess['message']['text'] # Извлечение текста сообщения
	mess_txt = mess_txt.lower() # Приведение текста к нижнему регистру
	mess_snd = 1 # Установка признака обработки сообщения
	if mess_txt.find('/start') + 1: # Базовое приветствие
		tb.send_mess(chat_id, 'Здравствуйте.') # Отправка сообщения
		mess_snd = 0 # Сообщение обработано
	if mess_txt.find('/help') + 1: # Список доступных команд
		tb.send_mess(chat_id, '''Возможные команды:
/Start - повторение приветствия;
/Help - вывод справки;

/MoonPhase - текущая фаза Луны;
/CurrentMoscowWeather - текущая погода в Москве;

/CurrencyExchangeRate - курсы валют (не забудте указать коды валют, например: /currencyexchangerate eur rub);
/Stock - график котировок, необходимо указать тикет компании, возможно указание дат начала и окончания построения графика, например: /stock ibm 2019-01-25 2019-08-25 (при указании больших промежутков времени обработка запроса может занять длительное время).''')
		mess_snd = 0 # Сообщение обработано
	if mess_txt.find('/moonphase')+1: # Запрос фазы луны
		date = datetime.date.today() # Получение текущей даты
		moon_message = moon.moon_phase(date.year, date.month, date.day) + "." # Запрос фазы луны
		tb.send_mess(chat_id, moon_message) # Отправка сообщения
		mess_snd = 0 # Сообщение обработано
	if mess_txt.find('/currentmoscowweather')+1: # Запрос текущей погоды в Москве
		tb.send_mess(chat_id, current_moscow_weather()) # Отправка сообщения
		mess_snd = 0 # Сообщение обработано
	if mess_txt.find('/currencyexchangerate')+1: # Запрос курса валют
		tb.send_mess(chat_id, exchange_rate(mess_txt)) # Отправка сообщения
		mess_snd = 0 # Сообщение обработано
	if mess_txt.find('/stock')+1: # Запрос графика котировок
		img_name = 'stock-'+str(id)+'-'+str(datetime.datetime.now())+'.png' # Создание имени изображения
		rep = stock(mess_txt) # Запрос графика
		if type(rep) is not str: # Если получено изображение
			rep.save(img_name) # Сохранение изображения
			tb.send_foto(chat_id, img_name) # Отправка изображения
			os.remove(img_name) # Удаление сохраненного изображения
		else:
			tb.send_mess(chat_id, rep)  # Отправка сообщения об ошибке
		mess_snd = 0 # Сообщение обработано
	if mess_snd: # Если сообщение не обработано
		# Отправка сообщения с заготовленым текстом
		tb.send_mess(chat_id, 'Увы, пока что я не в состоянии разговаривать.')