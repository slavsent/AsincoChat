import re
from socket import *
import json
import datetime
import sys
import threading
import time
import logging
from log.client_log_config import client_logger
from decorate import Log
from metaclasses import ClientVerifier
from client_db import ClientStorage
from Client.start_user import UserNameDialog
#from Client.main_win import ClientMainWindow

from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent, pyqtSignal, QObject

# Объект блокировки сокета и работы с базой данных
sock_lock = threading.Lock()
database_lock = threading.Lock()


# Исключение - ошибка сервера
class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


# Класс - Транспорт, отвечает за взаимодействие с сервером
class ClientTransport(threading.Thread, QObject):
    # Сигналы новое сообщение и потеря соединения
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        # Класс База данных - работа с базой
        self.database = database
        # Имя пользователя
        self.username = username
        # Сокет для работы с сервером
        #self.transport = None
        # Устанавливаем соединение:
        self.port = port
        self.ip_address = ip_address
        client_logger.info('Создан socket для соединения')
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.connection_init()
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_request()
            self.contacts_list_request()
        except OSError as err:
            if err.errno:
                client_logger.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            client_logger.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            client_logger.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        # Флаг продолжения работы транспорта.
        self.running = True

    @Log()
    def connection_init(self):
        self.sock.settimeout(5)
        # проверка metaclass
        # s.listen(5)
        # client, addr = s.accept()

        connected = False
        for i in range(5):
            client_logger.info(f'Попытка подключения №{i + 1}')
            try:
                self.sock.connect((self.ip_address, self.port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # Если соединится не удалось - исключение
        if not connected:
            client_logger.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        client_logger.debug('Установлено соединение с сервером')

        msg = 'Установка соединения'
        data_msg = self.create_msg_for_server(msg, self.username)
        msg_jim = json.dumps(data_msg)
        client_logger.info('Сообщение переведено в формат JSON')

        with sock_lock:
            self.sock.send(msg_jim.encode('utf-8'))
            client_logger.debug('Сообщение отправлено на сервер')
            data = self.sock.recv(1024)
            client_logger.debug('Получено сообщение от сервера')
            client_logger.debug('Попытка расшифровки сообщения от сервера')
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
            if 'response' in data_from_server and "message" in data_from_server:
                print(f'Сообщение от сервера: {data_from_server["message"]}, время: {data_from_server["time"]}')
            else:
                print(data_from_server)


    @Log()
    def create_msg_for_server(self, msg, username):
        client_logger.debug(f'Сформировано presence сообщение по сообщению клиента: {msg}')
        return {
            'action': 'presence',
            'time': datetime.datetime.now().timestamp(),
            'encoding': 'utf-8',
            'message': msg,
            'user': {
                "account_name": username,
                "status": "I ok!"
            }
        }

    # Функция запроса списка контактов пользовател
    @Log()
    def user_list_request(self):
        client_logger.debug(f'Запрос списка известных пользователей')
        data_msg = {
            'action': 'get_users',
            'time': datetime.datetime.now().timestamp(),
        }
        msg_jim = json.dumps(data_msg)
        with sock_lock:
            self.sock.send(msg_jim.encode('utf-8'))
            try:
                data = self.sock.recv(1000000)
                client_logger.debug('Получено сообщение от сервера')
                client_logger.debug('Попытка расшифровки сообщения от сервера')
                data_jim = data.decode('utf-8')
                data_from_server = json.loads(data_jim)
                if 'response' in data_from_server and data_from_server['response'] == 202:
                    self.database.add_users(data_from_server['alert'])

            except (ValueError, json.JSONDecodeError):
                client_logger.error('Неудачная расшифровка сообщения!')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                client_logger.error(f'Соединение с сервером было потеряно.')
            else:
                client_logger.debug('Cообщение от сервера успешно расшифровано')

    # Функция запроса списка контактов пользователя
    @Log()
    def contacts_list_request(self):
        client_logger.debug(f'Запрос списка известных пользователей {self.username}')
        data_msg = {
            'action': 'get_contacts',
            'time': datetime.datetime.now().timestamp(),
            'user_login': self.username,
        }
        msg_jim = json.dumps(data_msg)
        with sock_lock:
            self.sock.send(msg_jim.encode('utf-8'))
            try:
                data = self.sock.recv(1000000)
                client_logger.debug('Получено сообщение от сервера')
                client_logger.debug('Попытка расшифровки сообщения от сервера')
                data_jim = data.decode('utf-8')
                data_from_server = json.loads(data_jim)
                if 'response' in data_from_server and data_from_server['response'] == 202:
                    if data_from_server['alert']:
                        for contact in data_from_server['alert']:
                            self.database.add_contact(contact)
            except (ValueError, json.JSONDecodeError):
                client_logger.error('Неудачная расшифровка сообщения!')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                client_logger.error(f'Соединение с сервером было потеряно.')
            else:
                client_logger.debug('Cообщение от сервера успешно расшифровано')

    # Функция удаления клиента на сервере
    @Log()
    def remove_contact(self, contact):
        client_logger.debug(f'Удаление контакта {contact}')
        with sock_lock:
            try:
                data_msg = {
                    'action': 'del_contacts',
                    'time': datetime.datetime.now().timestamp(),
                    'user_login': self.username,
                    'contact_name': contact
                }
                msg_jim = json.dumps(data_msg)
                self.sock.send(msg_jim.encode('utf-8'))

                data = self.sock.recv(1024)
                client_logger.debug('Получено сообщение от сервера')
                time.sleep(1)
                client_logger.debug('Попытка расшифровки сообщения от сервера')
                data_jim = data.decode('utf-8')
                data_from_server = json.loads(data_jim)

                self.process_server_ans(data_from_server)
            except Exception:
                client_logger.error('Не удалось отправить информацию на сервер.')

    # Функция сообщающая на сервер о добавлении нового контакта
    @Log()
    def add_contact(self, contact):
        with sock_lock:
            try:
                data_msg = {
                    'action': 'add_contacts',
                    'time': datetime.datetime.now().timestamp(),
                    'user_login': self.username,
                    'contact_name': contact
                }
                msg_jim = json.dumps(data_msg)
                self.sock.send(msg_jim.encode('utf-8'))

                data = self.sock.recv(1024)
                client_logger.debug('Получено сообщение от сервера')
                time.sleep(1)
                client_logger.debug('Попытка расшифровки сообщения от сервера')
                data_jim = data.decode('utf-8')
                data_from_server = json.loads(data_jim)

                self.process_server_ans(data_from_server)
            except Exception:
                client_logger.error('Не удалось отправить информацию на сервер.')

    # Функция закрытия соединения, отправляет сообщение о выходе.
    @Log()
    def transport_shutdown(self):
        self.running = False
        with sock_lock:
            data_msg = {
                'action': 'exit',
                'time': datetime.datetime.now().timestamp(),
                'user': {
                    "account_name": self.username,
                    "status": "I ok!"
                }
            }
            msg_jim = json.dumps(data_msg)
            client_logger.info('Сообщение переведено в формат JSON')
            try:
                self.sock.send(msg_jim.encode('utf-8'))
                client_logger.debug('Сообщение отправлено на сервер')
            except OSError:
                pass

            print('Завершение соединения.')
            client_logger.info('Завершение работы по команде пользователя.')
        # Задержка неоходима, чтобы успело уйти сообщение о выходе
        time.sleep(0.5)

    # Функция отправки сообщения на сервер
    @Log()
    def send_message(self, to_user, message):
        time_send = datetime.datetime.now().timestamp()
        time_send_db = datetime.datetime.now()
        message_dict = {
            'action': 'message',
            'user_to': to_user,
            'message': message,
            'time': time_send,
            'user': {
                "account_name": self.username,
                "status": "I ok!"
            }
        }

        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        time.sleep(1)
        try:
            msg_jim = json.dumps(message_dict)
            client_logger.info('Сообщение переведено в формат JSON')
            with sock_lock:
                self.sock.send(msg_jim.encode('utf-8'))
                client_logger.info(f'Отправлено сообщение для пользователя {to_user}')

        except OSError as err:
            if err.errno:
                client_logger.critical(f'Потеряно соединение с сервером timeout.')
                raise ServerError('Потеряно соединение с сервером!')
                # sys.exit(1)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            client_logger.error(f'Соединение с сервером было потеряно.')
            raise ServerError('Потеряно соединение с сервером!')
            #sys.exit(1)
        self.database.save_message(self.username, to_user,
                                   message, time_send_db)

    @Log()
    def run(self):
        client_logger.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with sock_lock:
                try:
                    self.sock.settimeout(0.5)
                    data = self.sock.recv(1024)
                    client_logger.debug('Получено сообщение от сервера')


                    client_logger.debug('Попытка расшифровки сообщения от сервера')
                    data_jim = data.decode('utf-8')
                    data_from_server = json.loads(data_jim)
                    print(21)
                except (ValueError, json.JSONDecodeError):
                    client_logger.error('Неудачная расшифровка сообщения!')
                    self.running = False
                    self.connection_lost.emit()
                # Вышел таймаут соединения если errno = None, иначе обрыв соединения.
                except OSError as err:
                    print(22)
                    if err.errno:
                        print(25)
                        client_logger.critical(f'Потеряно соединение с сервером timeout.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    print(23)
                    client_logger.error(f'Соединение с сервером было потеряно.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    print(24)
                    client_logger.debug(f'Принято сообщение с сервера: {data_from_server}')
                    self.process_server_ans(data_from_server)
                finally:
                    self.sock.settimeout(5)

    # Функция обрабатывающяя сообщения от сервера. Ничего не возращает. Генерирует исключение при ошибке.
    @Log()
    def process_server_ans(self, message):
        client_logger.debug(f'Разбор сообщения от сервера: {message}')

        # Если это подтверждение чего-либо
        if 'response' in message:
            if message['response'] == 200 or message['response'] == 202 or message['response'] == 404:
                return
            elif message['response'] == 400:
                raise ServerError(f'{message["message"]}')
            else:
                client_logger.debug(f'Принят неизвестный код подтверждения {message["response"]}')

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о новом сообщении
        elif 'message' in message and 'user_to' in message and message['user_to'] \
                == self.username:
            client_logger.debug(f'Получено сообщение от пользователя {message["user_from"]}:{message["message"]}')
            date_message = datetime.datetime.fromtimestamp(message['time'])
            self.database.save_message(message['user_from'], message['user_to'],
                                       message["message"], date_message)
            self.new_message.emit(message["user_from"])
            print(
                f'Получено сообщение от: {message["user_from"]}, время: {date_message}\n'
                f'Сообщение: {message["message"]}')
        else:
            client_logger.debug(f'Принят неизвестный код подтверждения {message}')
