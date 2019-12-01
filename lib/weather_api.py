import requests

class weather_data:
	# Адреса запросов текущей погоды и прогноза.
	weather_url = "http://api.openweathermap.org/data/2.5/weather?q=Moscow,ru&appid=" # !!! следует указать appid
	forecast_url = "http://api.openweathermap.org/data/2.5/forecast?q=Moscow,ru&appid=" # !!! следует указать appid
	# Список для перевода осадков/облочности
	weather_list = {
		'Clouds': 'Облачно',
		'Clear': 'Ясно',
		'Mist': 'Туман',
		'Fog': 'Туман',
		'Haze': 'Туман',
		'Snow': 'Снег',
		'Rain': 'Дождь',
		'Drizzle': 'Морось',
		'Thunderstorm': 'Гроза'
		}
	current = {}
	forecast = {}
	
	# Запрос текущей погоды
	def current_weather(self):
		# Запрос текущей погоды
		try:
			data = requests.get(self.weather_url)
		except requests.RequestException:
			return None
		# Извлечение данных
		self.current['temp'] = str(round(data.json()['main']['temp'] - 273.15, 1)) # Температура (перевод из Фаренгейта в Цельсия)
		self.current['pres'] = str(round(data.json()['main']['pressure'] * 0.750062, 1)) # Давление (перевод в мм ртутного столба)
		self.current['humid'] = str(round(data.json()['main']['humidity'], 1)) # Влажность
		# Облачность/осадки
		try:
			self.current['weather'] = self.weather_list[str(data.json()['weather'][0]['main'])]
		except Exception:
			self.current['weather'] = str(data.json()['weather'][0]['main'])
		# Возвращение результата
		return self.current
	
	# Запрос прогноза погоды через 12 часов
	def forecast_weather(self):
		# Запрос прогноза
		try:
			data = requests.get(self.forecast_url)
		except requests.RequestException:
			return None
		# Извлечение данных (...['list'][4]... - обращение к погоде через 12 часов)
		self.forecast['temp'] = str(round(data.json()['list'][4]['main']['temp'] - 273.15,1)) # Температура (перевод из Фаренгейта в Цельсия)
		self.forecast['pres'] = str(round(data.json()['list'][4]['main']['pressure'] * 0.750062,1)) # Давление (перевод в мм ртутного столба)
		self.forecast['humidity'] = str(round(data.json()['list'][4]['main']['humidity'],1)) # Влажность
		# Облачность/осадки
		try:
			self.forecast['weather'] = self.weather_list[str(data.json()['list'][4]['weather'][0]['main'])]
		except Exception:
			self.forecast['weather'] = str(data.json()['list'][4]['weather'][0]['main'])
		self.forecast['date'] = str(data.json()['list'][4]['dt_txt'])
		# Возвращение результата
		return self.forecast

	# Получение текущей погоды
	def get_current(self):
		try:
			return (self.current)
		except Exception:
			return None
	
	# Получение прогноза погоды
	def get_forecast(self):
		try:
			return (self.forecast)
		except Exception:
			return None
