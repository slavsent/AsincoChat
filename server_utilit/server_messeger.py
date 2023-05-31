import sys
import time

sys.path.append('../')
import hmac
import binascii
from socket import *
import json
import datetime
import sys
import re
import select
import os
import logging
import threading
import configparser
from log.server_log_config import server_logger
from decorate import Log, login_required
from port_descriptor import PortDescriptor
from metaclasses import ServerVerifier
from server_db import ServerStorage

# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
conflag_lock = threading.Lock()


class ServerMesseger(threading.Thread, metaclass=ServerVerifier):
    serv_port = PortDescriptor()

    def __init__(self, serv_addr, serv_port, db):
        self.serv_addr = serv_addr
        self.serv_port = serv_port
        self.db = db
        self.clients = []
        self.messages = []

        self.username = {}

        super().__init__()

    @Log()
    @login_required
    def create_msg_to_client(self, msg_from_client, client):
        if 'message' in msg_from_client and msg_from_client['message'] == 'Error':
            server_logger.debug('Сформирован ответ с - Bad Request')
            return {
                "response": 400,
                "message": "Bad Request",
                'time': datetime.datetime.now().timestamp(),
            }
        if 'action' in msg_from_client and msg_from_client['action'] == 'get_users':
            list_users = self.db.users_list()
            list_username = []
            for el in list_users:
                list_username.append(el[0])
            return {
                "response": 202,
                'alert': list_username,
            }
        if 'action' in msg_from_client and msg_from_client['action'] == 'get_contacts':
            list_users = self.db.user_contacts(msg_from_client['user_login'])
            return {
                "response": 202,
                'alert': list_users,
            }
        if 'action' in msg_from_client and msg_from_client['action'] == 'del_contacts':
            self.db.del_user_contacts(msg_from_client['user_login'], msg_from_client['contact_name'])
            return {
                "response": 404,
                'alert': 'Ok, delete'
            }
        if 'action' in msg_from_client and msg_from_client['action'] == 'add_contacts':
            self.db.add_user_contacts(msg_from_client['user_login'], msg_from_client['contact_name'])
            return {
                "response": 202,
                'alert': 'Ok, add'
            }
        if 'action' in msg_from_client and msg_from_client['action'] == 'PUBLIC_KEY_REQUEST':
            data = self.db.get_pubkey(msg_from_client['account_name'])
            return {
                "response": 511,
                'account_name': msg_from_client['account_name'],
                'data': data
            }
        if 'user' in msg_from_client and 'action' in msg_from_client and msg_from_client['action'] == 'presence':
            if msg_from_client['user']['account_name'] in self.username.keys():

                return {
                    "response": 400,
                    'user': 'error',
                    "message": f"Привет клиент: {msg_from_client['user']['account_name']} такой username уже существует",
                    'time': datetime.datetime.now().timestamp(),
                }
            else:
                self.username[msg_from_client['user']['account_name']] = client
                return {
                    "response": 200,
                    "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
                    'time': datetime.datetime.now().timestamp(),
                }
        elif 'action' in msg_from_client and msg_from_client[
            'action'] == 'message' and 'user_to' in msg_from_client and 'user' in msg_from_client:

            if msg_from_client['user_to'] in self.username.keys():
                return {
                    "action": 'message',
                    'user_from': msg_from_client['user']['account_name'],
                    'user_to': msg_from_client['user_to'],
                    "message": msg_from_client['message'],
                    'time': datetime.datetime.now().timestamp(),
                }

            return {
                "response": 400,
                "message": f"Привет клиент: {msg_from_client['user']['account_name']}. Такого получателя нет",
                'time': datetime.datetime.now().timestamp(),
            }
        elif 'action' in msg_from_client and msg_from_client['action'] == 'exit' and 'user' in msg_from_client:
            self.clients.remove(self.username[msg_from_client['user']['account_name']])
            self.username[msg_from_client['user']['account_name']].close()
            del self.username[msg_from_client['user']['account_name']]
            return {'response': 'close'}
        else:
            server_logger.debug('Сформирован ответ на прочие сообщения чем presence и error')
            return {
                "response": 200,
                "message": "Wait action",
                'time': datetime.datetime.now().timestamp(),
            }

    @Log()
    def get_message(self, client):
        data = client.recv(1000000)
        server_logger.debug('Получение сообщения от клиента')
        try:
            server_logger.info('Попытка расшибровки сообщения от клиента')
            data_jim = data.decode('utf-8')
            data_from_client = json.loads(data_jim)
        except (ValueError, json.JSONDecodeError):
            server_logger.error('Неудачная расшифровка сообщения!')
            data_from_client = {
                "message": 'Error',
                "time": 'Error'
            }
        return data_from_client

    def run(self):
        s = socket(AF_INET, SOCK_STREAM)
        # проверка работы метакласса
        # s = socket()
        server_logger.info('Создан socket для соединения')
        s.bind((self.serv_addr, self.serv_port))
        # проверка работы метакласса
        # s.connect((self.serv_addr, self.serv_port))
        s.settimeout(0.4)

        s.listen(5)
        server_logger.info('Прослушивание адреса для соединения')
        while True:
            try:
                server_logger.debug('Подключение клиента к серверу')
                client, addr = s.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'Установлено соедение с клиентом {addr}')
                self.clients.append(client)

            wait = 10
            receive_data, send_data, err_data = [], [], []
            try:
                if self.clients:
                    receive_data, send_data, err_data = select.select(self.clients, self.clients, [], wait)
            except OSError:
                pass
            if receive_data:
                for client_with_message in receive_data:

                    try:
                        data_from_client = self.get_message(client_with_message)
                        # print('in', data_from_client)
                        if 'user' in data_from_client and 'action' in data_from_client and data_from_client[
                            'action'] == 'presence':
                            self.autorize_user(data_from_client, client_with_message)
                            continue
                            # if not data_from_client['user']['account_name'] in self.username.keys():
                            #    client_ip, client_port = client.getpeername()
                            #    self.db.user_login(data_from_client['user']['account_name'], client_ip, client_port)
                        else:
                            if 'action' in data_from_client and data_from_client[
                                'action'] == 'exit' and 'user' in data_from_client:
                                self.db.user_logout(data_from_client['user']['account_name'])
                            if 'message' in data_from_client:
                                if 'user' in data_from_client:
                                    print(
                                        f'Сообщение от клиента: {data_from_client["user"]["account_name"]} '
                                        f'сообщение: {data_from_client["message"]}, время: {data_from_client["time"]}')
                                else:
                                    print(
                                        f'Сообщение от клиента: {data_from_client["message"]}, '
                                        f'время: {data_from_client["time"]}')
                                server_logger.info(f'Просмотр сообщения от клиента - {data_from_client["message"]}')

                            data_msg = self.create_msg_to_client(data_from_client, client_with_message)

                            # print('to', data_msg)
                            if 'response' not in data_msg:
                                if 'action' in data_msg and data_msg['action'] == 'message':
                                    self.messages.append(data_msg)
                            else:
                                if data_msg['response'] != 'close':
                                    msg_jim = json.dumps(data_msg)
                                    server_logger.debug('Сообщение отправлено клиенту ответ')
                                    client_with_message.send(msg_jim.encode('utf-8'))
                                    if 'user' in data_msg and data_msg['user'] == 'error':
                                        self.clients.remove(client_with_message)

                    except (Exception, OSError):

                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        user = list(self.username.keys())[list(self.username.values()).index(client_with_message)]
                        if user:
                            self.db.user_logout(user)
                            del self.username[user]
                        self.clients.remove(client_with_message)

            if self.messages:
                for message in self.messages:
                    try:
                        msg_jim = json.dumps(message)
                        server_logger.debug(
                            f'Сообщение отправлено клиенту {message["user_to"]} от клиента {message["user_from"]}')
                        self.username[message['user_to']].send(msg_jim.encode('utf-8'))
                    except ConnectionResetError:
                        server_logger.info(
                            f'Клиент {self.username[message["user_to"]].getpeername()} отключился от сервера.')
                        del self.username[message['user_to']]

                self.messages.clear()

    def service_update_lists(self):
        '''Метод реализующий отправки сервисного сообщения 205 клиентам.'''
        for client in self.username:
            try:
                msg = {
                    "response": 205,
                    "message": "Reload list users",
                    'time': datetime.datetime.now().timestamp(),
                }
                msg_jim = json.dumps(msg)
                self.username[client].send(msg_jim.encode('utf-8'))
            except OSError:
                self.remove_client(self.username[client])

    def remove_client(self, client):
        '''
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы:
        '''
        server_logger.info(f'Клиент {client.getpeername()} отключился от сервера.')
        for name in self.username:
            if self.username[name] == client:
                self.db.user_logout(name)
                del self.username[name]
                break
        self.clients.remove(client)
        client.close()

    def autorize_user(self, message, sock):
        '''Метод реализующий авторизцию пользователей.'''
        # Если имя пользователя уже занято то возвращаем 400
        server_logger.debug(f'Start auth process for {message["user"]["account_name"]}')
        if message['user']['account_name'] in self.username.keys():
            msg = {
                "response": 400,
                'user': 'error',
                "message": f"Привет клиент: {message['user']['account_name']} такой username уже существует",
                'time': datetime.datetime.now().timestamp(),
            }
            # print(msg)
            try:
                msg_jim = json.dumps(msg)
                sock.send(msg_jim.encode('utf-8'))
                server_logger.debug(f'Username busy, sending response: 400')
            except OSError:
                server_logger.debug('OS Error')
                pass
            self.clients.remove(sock)
            sock.close()
        # Проверяем что пользователь зарегистрирован на сервере.
        elif not self.db.check_user(message['user']['account_name']):
            msg = {
                "response": 400,
                'user': 'error',
                "message": f"Привет клиент: {message['user']['account_name']} такой пользователь не зарегистрирован.",
                'time': datetime.datetime.now().timestamp(),
            }
            # print(msg)
            try:
                msg_jim = json.dumps(msg)
                server_logger.debug(f'Unknown username, sending такой пользователь не зарегистрирован.')
                sock.send(msg_jim.encode('utf-8'))
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            server_logger.debug('Correct username, starting passwd check.')
            # Иначе отвечаем 511 и проводим процедуру авторизации
            # Словарь - заготовка
            message_auth = {
                "response": 511,
            }
            # Набор байтов в hex представлении
            random_str = binascii.hexlify(os.urandom(64))
            # В словарь байты нельзя, декодируем (json.dumps -> TypeError)
            message_auth['data'] = random_str.decode('ascii')
            # Создаём хэш пароля и связки с рандомной строкой, сохраняем
            # серверную версию ключа
            hash = hmac.new(self.db.get_hash(message['user']['account_name']), random_str, 'MD5')
            digest = hash.digest()
            server_logger.debug(f'Auth message = {message_auth}')
            try:
                # Обмен с клиентом
                # print(message_auth)
                msg_jim = json.dumps(message_auth)
                sock.send(msg_jim.encode('utf-8'))
                ans = self.get_message(sock)
            except OSError as err:
                server_logger.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans['data'])
            # Если ответ клиента корректный, то сохраняем его в список
            # пользователей.
            if "response" in ans and ans["response"] == 511 and hmac.compare_digest(
                    digest, client_digest):

                self.username[message['user']['account_name']] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    msg = {
                        "response": 200,
                        "message": f"Привет клиент: {message['user']['account_name']}",
                        'time': datetime.datetime.now().timestamp(),
                    }
                    # print(msg)
                    msg_jim = json.dumps(msg)
                    sock.send(msg_jim.encode('utf-8'))
                except OSError:
                    print('err')
                    self.remove_client(message['user']['account_name'])
                # добавляем пользователя в список активных и если у него изменился открытый ключ
                # сохраняем новый

                self.db.user_login(message['user']['account_name'], client_ip, client_port,
                                   message['user']['public_key'])
                self.username[message['user']['account_name']] = sock
                # return
            else:
                msg = {
                    "response": 400,
                    "message": f"Неверный пароль.",
                    'time': datetime.datetime.now().timestamp(),
                }
                # print(msg)
                try:
                    msg_jim = json.dumps(msg)
                    sock.send(msg_jim.encode('utf-8'))
                except OSError:
                    pass
                time.sleep(1)
                self.clients.remove(sock)
                sock.close()
