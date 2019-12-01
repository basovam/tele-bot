import socks
import socket
import requests

class telegram_bot:
	tel_url = "https://api.telegram.org/bot<<ID>>:<<KEY>>/" # !!! следует указать Id бота и ключ доступа
	offset_file_path = "/home/pi/Documents/python/upd_offset" # путь к файлу с Id последнего сообщения
	my_chat = # !!! следует указать ID чата владельца
	
	# Установка proxy для доступа к серверам telegram
	def set_proxy(self):
		# Установка параметров proxy
		socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
		# Сохранение оригинальных настроек в переменную для возврата к ним
		proxy_tmp = socket.socket
		# Смена настроек
		socket.socket = socks.socksocket
		# Возврат оригинальных настроек
		return (proxy_tmp)
		
	# Получение новых сообщений
	def get_updates_json(self):
		# Установка proxy
		prox_tmp = self.set_proxy()
		# Считывание Id последнего сообщения
		offset_file = open(self.offset_file_path,"r")
		offset = offset_file.read()
		offset_file.close()
		# Запрос новых сообщений
		try:
			response = requests.get(self.tel_url + 'getUpdates?offset=' + offset)
			# Если сообщения есть
			if len(response.json()['result']) > 0:
				# Поиск последнего сообщения
				total_updates = len(response.json()['result']) - 1
				# Запись Id последнего сообщения
				offset_file = open(self.offset_file_path,"w")
				offset_file.write(str(int(response.json()['result'][total_updates]['update_id']) + 1))
				offset_file.close()
			# Возврат к оригинальным настройкам proxy
			socket.socket = prox_tmp
			return response.json()
		except Exception:
			# Возврат к оригинальным настройкам proxy
			socket.socket = prox_tmp
			return None
	
	# Отправка сообщения владельцу
	def send_mess_to_me(self, text):
		# Установка proxy
		prox_tmp = self.set_proxy()
		# Задание параметров
		params = {'chat_id': self.my_chat, 'text': text}
		# Отправка сообщения
		response = requests.post(self.tel_url + 'sendMessage', data=params)
		# Возврат к оригинальным настройкам proxy
		socket.socket = prox_tmp
		return response
	
	# Отправка сообщения
	def send_mess(self, chat, text):
		# Установка proxy
		prox_tmp = self.set_proxy()
		# Задание параметров
		params = {'chat_id': chat, 'text': text}
		# Отправка сообщения
		response = requests.post(self.tel_url + 'sendMessage', data=params)
		# Возврат к оригинальным настройкам proxy
		socket.socket = prox_tmp
		return response
	
	# Отправка изображения владельцу	
	def send_foto_to_me(self, foto_name):
		# Установка proxy
		prox_tmp = self.set_proxy()
		# Задание параметров
		params = {'chat_id': self.my_chat}
		# Открытие изображения. foto_name - путь к изображению.
		files = {'photo': open(foto_name, 'rb')}
		# Отправка сообщения
		response = requests.post(self.tel_url + 'sendPhoto', files=files, data=params)
		# Возврат к оригинальным настройкам proxy
		socket.socket = prox_tmp
		return response
	
	# Отправка изображения
	def send_foto(self, chat, foto_name):
		# Установка proxy
		prox_tmp = self.set_proxy()
		# Задание параметров
		params = {'chat_id': chat}
		# Открытие изображения. foto_name - путь к изображению.
		files = {'photo': open(foto_name, 'rb')}
		# Отправка сообщения
		response = requests.post(self.tel_url + 'sendPhoto', files=files, data=params)
		# Возврат к оригинальным настройкам proxy
		socket.socket = prox_tmp
		return response