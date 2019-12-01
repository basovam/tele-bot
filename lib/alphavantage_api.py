import datetime
import re
import requests
import string
import time

from PIL import Image, ImageDraw

class alphavantage_data:
	alpha_url="https://www.alphavantage.co/query?"
	apikey="&apikey=" # !!! следует указать apikey

	def next_date(self, dat):
		# Выделение года, месяца и дня из полученной строки формата YYYY-MM-DD
		y = int(dat[:4])
		m = int(dat[5:7])
		d = int(dat[8:])+1 # Увеличение дня
		if (d > 28) and (m == 2) and (y % 4): # Проверка февраля в обычный год
			d = 1
			m = 3
		elif (d > 29) and (m == 2) and not (y % 4): # Проверка февраля в високосный год
			d = 1
			m = 3
		elif (d > 30) and ((m == 4) or (m == 6) or (m == 9) or (m == 11)): # Проверка месяцев в 30 дней
			d = 1
			m = m + 1
		elif (d > 31):
			d = 1
			m = m + 1
		if (m > 12): # Проверка увеличения года
			m = 1
			y = y + 1
		# Сохранение даты в верном формате
		r = str(y)
		if (m < 10): # Проверка числа символов в месяце
			r = r + '-0' + str(m)
		else:
			r = r + '-' + str(m)
		if (d < 10): # Проверка числа символов в дне
			r = r + '-0' + str(d)
		else:
			r = r + '-' + str(d)
		return r
	
	# Проверка даты на формат и корректность
	def is_date(self, dat):
		try:
			# Выделение года, месяца и дня из полученной строки формата YYYY-MM-DD
			y = int(dat[:4])
			m = int(dat[5:7])
			d = int(dat[8:])+1 # день увеличивыется на 1 чтобы далее не делать провеку на равенство
			if (m > 12): # некорректный месяц
				return (0)
			elif (d > 28) and (m == 2) and (y % 4): # здесь и далее - некорректное число дней в соответствующем месяце
				return (0)
			elif (d > 29) and (m == 2) and not (y % 4): # проверка для високосного года
				return (0)
			elif (d > 30) and ((m == 4) or (m == 6) or (m == 9) or (m == 11)):
				return (0)
			elif (d > 31):
				return (0)
			else:
				return (1)
		except Exception:
			return (0)

	# Запрос котировок за последние 100 дней, symbol - код бумаги
	def stock_series_daily(self, symbol):
		# Задание соответствующей функции API
		function = "function=TIME_SERIES_DAILY"
		try:
			# Запрос данных
			data = requests.get(self.alpha_url + function + "&symbol=" + symbol + self.apikey)	
			return (data.json())
		except Exception:
			return None
			
	# Запрос котировок за последние 20 лет, symbol - код бумаги
	def stock_series_daily_full(self, symbol):
		# Задание соответствующей функции API
		function = "function=TIME_SERIES_DAILY"
		try:
			# Запрос данных
			data = requests.get(self.alpha_url + function + "&symbol=" + symbol + '&outputsize=full' + self.apikey)	
			return (data.json())
		except Exception:
			return None
	
	# Запрос курса валют
	def currency_exchange_rate(self, from_currency, to_currency):
		# Задание соответствующей функции API
		function = "function=CURRENCY_EXCHANGE_RATE"
		try:
			# Запрос данных
			data = requests.get(self.alpha_url + function + "&from_currency=" + from_currency + "&to_currency=" + to_currency + self.apikey)
			# Округление и преобразование типов полученных данных
			return str(round(float(data.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']), 2))
		except Exception:
			# Проверка на случай некорректного ответа
			return None
	
	# Отрисовка свечного графика котировок
	def stock_daily(self, text, date_start=None, date_end=None, accuracy=None):
		# Задание размеров графика, если был получен соответствующий параметр
		if accuracy is not None:
			try:
				g_high = int(accuracy)
				if g_high < 50: # ограничение минимального размера графика
					g_high = 500
			except Exception:
				# Задание значения по умолчанию в случае ошибок
				g_high = 500
		else:
			# Задание значения по умолчанию
			g_high = 500
			
		# Проверка дат начала и окончания на наличие, соответствие формату и корректность с возвратом сообщения об ошибке
		if (date_start is not None) and ((re.match('\d\d\d\d-\d\d-\d\d', date_start) is None) or not self.is_date(date_start)):
			return ("Неверная дата начала")
		if (date_end is not None) and ((re.match('\d\d\d\d-\d\d-\d\d', date_end) is None) or not self.is_date(date_end)):
			return ("Неверная дата окончания")
		if (date_start is not None) and (date_end is not None) and (date_end <= date_start):
			return ("Дата окончания больше или равна дате начала.")
		today = datetime.datetime.today().strftime('%Y-%m-%d')
		if (date_start is not None) and (today < date_start):
			return ("Дата начала превышает текущую")
		if (date_end is not None) and (today < date_end):
			return ("Дата окончания превышает текущую")
			
		# Задание информации об акции
		stock_info = {
				'Symbol': text.upper(),
				'Name': 'Company name: '
			}
		
		# Попытка получения котировок
		data = self.stock_series_daily(stock_info['Symbol'])
		if data.get('Error Message') is not None: # Если попытка неудачна
			# Задание функции поиска кода акции из API
			function = "function=SYMBOL_SEARCH"
			try:
				# Запрос результатов поиска
				info_data = requests.get(self.alpha_url + function + "&keywords=" + text + self.apikey)
				# Извлечение информации об акции из полученных данных
				stock_info['Symbol'] = info_data.json()['bestMatches'][0]['1. symbol']
				stock_info['Name'] += info_data.json()['bestMatches'][0]['2. name']
				# Повторная попытка получения котировок
				data = self.stock_series_daily(stock_info['Symbol'])
				# Возврат сообщения об ошибке в зависимости от результатов запроса
				if data is None:
					return ("Ошибка в получении даных. Попробуйте повторить запрос позже.")
				if data.get('Error Message') is not None:
					return ("Акция не найдена")
			except Exception:
				# Возврат сообщения об ошибке
				return ("Акция не найдена")
		else: # Если попытка удачна, то проводится поиск по коду для получения названия компании
			# Задание функции поиска кода акции из API
			function = "function=SYMBOL_SEARCH"
			try:
				# Запрос результатов поиска
				info_data = requests.get(self.alpha_url + function + "&keywords=" + text + self.apikey)
				if info_data.json()['bestMatches'][0]['1. symbol'] == stock_info['Symbol']: # Если компания успешно найдена
					stock_info['Name'] += info_data.json()['bestMatches'][0]['2. name'] # Сохраняется название компании
				else:
					stock_info['Name'] += '-- Not Found --' # В случае ошибок при поиске в место названия сохраняется сообщение об ошибке.
			except Exception:
				stock_info['Name'] += '-- Not Found --' # В случае ошибок при поиске в место названия сохраняется сообщение об ошибке.
		if data is None: # В случае ошибки при запросе котировок возвращается сообщение об ошибке
			return ("Ошибка в получении даных. Попробуйте повторить запрос позже.")
		
		# Поиск минимальной даты в полученных данных
		min_date = data['Meta Data']['3. Last Refreshed']
		for date in data['Time Series (Daily)']:
			if date < min_date:
				min_date = date
		# Если задана дата начала графика и она меньше найденной минимальной запрашиваются полные данные по котировкам
		if (date_start is not None) and (min_date > date_start):
			data = self.stock_series_daily_full(stock_info['Symbol'])
		
		# Поиск минимальной и максимальной цены и числа торговых дней (bar_count)
		max = 0
		min = 100000
		bar_count = 0
		for date in data['Time Series (Daily)']:
			if (((date_start is None) and (date_end is None)) or 
			((date_start is not None) and (date_end is None) and (date >= date_start)) or 
			((date_start is not None) and (date_end is not None) and (date >= date_start) and (date <= date_end))):
				# Округление - для корректного отображения информации на графике
				max_i = round(float(data['Time Series (Daily)'][date]['2. high']), 2) # Максимум ищется среди дневных максимумов
				min_i = round(float(data['Time Series (Daily)'][date]['3. low']), 2) # Минимум ищется среди дневных минимумов
				if max_i > max:
					max = max_i
				if min_i < min:
					min = min_i
				bar_count += 1
				
		# Вычисление промежуточных значений для отображения на графике
		half = round(((max + min) / 2), 2)
		top_half = round(((max + half) / 2), 2)
		low_half = round(((half + min) / 2), 2)
		
		# Задание переменных цвета
		text_color = (0,0,0)
		line_color = (128,128,128)
		
		# Задание отступа исходя из числа символов в цене
		if (max >= 10000):
			y_axis = 55
		elif (max >= 1000):
			y_axis = 50
		elif (max >= 100):
			y_axis = 45
		elif (max >= 10):
			y_axis = 40
		else:	
			y_axis = 35
		
		# Задание размеров изображения
		width = y_axis + bar_count*6 + 20 # Ширина - отступ в начале, число торговых дней, отступ в конце
		high = g_high + 50 # Высота - размер графика, отступ
		
		# Создание изображения
		img = Image.new('RGB', (width, high), color = (255,255,255))
		d = ImageDraw.Draw(img)
		
		# Отрисовка текста : кода акции, названия компании, цен вдоль вертикальной оси
		d.text((y_axis,5), stock_info['Name'], fill=text_color)
		d.text((y_axis,15), stock_info['Symbol'], fill=text_color)
		d.text((5,25), str(max), fill=text_color)
		d.text((5,g_high//4 + 25), str(top_half), fill=text_color)
		d.text((5,g_high//2 + 25), str(half), fill=text_color)
		d.text((5,g_high//2 + g_high//4 + 25), str(low_half), fill=text_color)
		d.text((5,g_high + 25), str(min), fill=text_color)
		
		# Отрисовка осей графика и насечек напротив цен
		d.line((y_axis, 25, y_axis, g_high + 30), fill=line_color)
		d.line((y_axis + 1, 31, y_axis + 2, 31), fill=line_color)
		d.line((y_axis + 1, g_high//4 + 31, y_axis + 2, g_high//4 + 31), fill=line_color)
		d.line((y_axis + 1, g_high//2 + 31, y_axis + 2, g_high//2 + 31), fill=line_color)
		d.line((y_axis + 1, g_high//2 + g_high//4 + 31, y_axis + 2, g_high//2 + g_high//4 + 31), fill=line_color)
		d.line((y_axis, g_high + 31, width-14, g_high + 31), fill=line_color)
		
		# Отрисовка графика
		# Задание даты начала
		if date_start is not None:
			date = date_start
		else:
			date = min_date
			
		i = 0 # Счетчик
		# Определение числа дат, отображаемых вдоль нижней оси
		if bar_count <= 50:
			n = 2
		elif bar_count <= 100:
			n = 3
		elif bar_count <= 200:
			n = 4
		else:
			n = 5
		x = (bar_count-1)//n # Коэффициент для определения момента печати даты
		# Цикл по датам
		while ((date_end is None) and (date <= data['Meta Data']['3. Last Refreshed'])) or ((date_end is not None) and (date <= date_end)):
			try:
				# Определение цвета свечи
				if float(data['Time Series (Daily)'][date]['1. open']) < float(data['Time Series (Daily)'][date]['4. close']):
					color = (0, 255, 0) # Зеленая, растущая
				else:
					color = (255, 0, 0) # Красная, падающая
				# Рассчет координат свечи
				# (цена - минимум)/(максимум - минимум) = Искомая координата / Высота графика
				# Высота + отступ - (цена - минимум) * Высота графика / (максимум - минимум)
				ho = g_high + 30 - round(((float(data['Time Series (Daily)'][date]['1. open']) - min) * g_high/(max-min)), 0) # Открытие
				hh = g_high + 30 - round(((float(data['Time Series (Daily)'][date]['2. high']) - min) * g_high/(max-min)), 0) # Максимум за день
				hl = g_high + 30 - round(((float(data['Time Series (Daily)'][date]['3. low']) - min) * g_high/(max-min)), 0) # Минимум за день
				hc = g_high + 30 - round(((float(data['Time Series (Daily)'][date]['4. close']) - min) * g_high/(max-min)), 0) # Закрытие
				# Отрисовка свечи по координатам
				d.rectangle(((y_axis + 2 + 6 * i, ho), (y_axis + 6 + 6 * i, hc)), fill=color)
				d.line((y_axis + 4 + 6 * i, ho, y_axis + 4 + 6 * i, hh), fill=color)
				d.line((y_axis + 4 + 6 * i, hc, y_axis + 4 + 6 * i, hl), fill=color)
				if not (i % x) or (i == bar_count): # Проверка на необходимость печати даты
					# Вывод даты
					d.text((y_axis - 9 + 6 * i, g_high + 35), str(date[5:]), fill=text_color)
				# Переход к следующей дате
				date = self.next_date(date)
				i += 1
			except Exception:
				# Переход к следующей дате
				date = self.next_date(date)
		# Возврат полученного изображения
		return img