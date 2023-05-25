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
from decorate import Log
from port_descriptor import PortDescriptor
from metaclasses import ServerVerifier
from server_db import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow, \
    create_user_model, UsersWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem


# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
new_connection = False
conflag_lock = threading.Lock()


class Server(threading.Thread, metaclass=ServerVerifier):
    serv_port = PortDescriptor()

    def __init__(self, serv_addr, serv_port, db):
        self.serv_addr = serv_addr
        self.serv_port = serv_port
        self.db = db
        super().__init__()

    @Log()
    def create_msg_to_client(self, msg_from_client, username, clients, client):
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
            self.db.del_user_contacts(msg_from_client['user_login'], msg_from_client['contact_name'])
            return {
                "response": 202,
                'alert': 'Ok, add'
            }
        if 'user' in msg_from_client and 'action' in msg_from_client and msg_from_client['action'] == 'presence':
            if msg_from_client['user']['account_name'] in username.keys():

                return {
                    "response": 400,
                    'user': 'error',
                    "message": f"Привет клиент: {msg_from_client['user']['account_name']} такой username уже существует",
                    'time': datetime.datetime.now().timestamp(),
                }
            else:
                username[msg_from_client['user']['account_name']] = client
                return {
                    "response": 200,
                    "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
                    'time': datetime.datetime.now().timestamp(),
                }
        if 'action' in msg_from_client and msg_from_client['action'] == 'presence':
            server_logger.debug('Сформирован ответ на сообщение - presence')
            return {
                "response": 200,
                "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
                'time': datetime.datetime.now().timestamp(),
            }
        elif 'action' in msg_from_client and msg_from_client[
            'action'] == 'message' and 'user_to' in msg_from_client and 'user' in msg_from_client:
            if msg_from_client['user_to'] in username.keys():
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
            clients.remove(username[msg_from_client['user']['account_name']])
            username[msg_from_client['user']['account_name']].close()
            del username[msg_from_client['user']['account_name']]
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
        global new_connection
        s = socket(AF_INET, SOCK_STREAM)
        # проверка работы метакласса
        # s = socket()
        server_logger.info('Создан socket для соединения')
        s.bind((self.serv_addr, self.serv_port))
        # проверка работы метакласса
        # s.connect((self.serv_addr, self.serv_port))
        s.settimeout(0.4)

        clients = []
        messages = []

        username = {}

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
                clients.append(client)

            wait = 10
            receive_data, send_data, err_data = [], [], []
            try:
                if clients:
                    receive_data, send_data, err_data = select.select(clients, clients, [], wait)
            except OSError:
                pass
            if receive_data:
                for client_with_message in receive_data:

                    try:
                        data_from_client = self.get_message(client_with_message)
                        if 'user' in data_from_client and 'action' in data_from_client and data_from_client[
                            'action'] == 'presence':
                            if not data_from_client['user']['account_name'] in username.keys():
                                client_ip, client_port = client.getpeername()
                                self.db.user_login(data_from_client['user']['account_name'], client_ip, client_port)
                                new_connection = True
                        if 'action' in data_from_client and data_from_client[
                            'action'] == 'exit' and 'user' in data_from_client:
                            self.db.user_logout(data_from_client['user']['account_name'])
                            new_connection = True
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
                        data_msg = self.create_msg_to_client(data_from_client, username, clients, client_with_message)
                        if 'response' not in data_msg:
                            if 'action' in data_msg and data_msg['action'] == 'message':
                                messages.append(data_msg)
                        else:
                            if data_msg['response'] != 'close':
                                msg_jim = json.dumps(data_msg)
                                server_logger.debug('Сообщение отправлено клиенту ответ')
                                client_with_message.send(msg_jim.encode('utf-8'))
                                if 'user' in data_msg and data_msg['user'] == 'error':
                                    clients.remove(client_with_message)

                    except (Exception, OSError):
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        user = list(username.keys())[list(username.values()).index(client_with_message)]
                        new_connection = True
                        if user:
                            self.db.user_logout(user)
                        clients.remove(client_with_message)

            if messages:
                for message in messages:
                    try:
                        msg_jim = json.dumps(message)
                        server_logger.debug(
                            f'Сообщение отправлено клиенту {message["user_to"]} от клиента {message["user_from"]}')
                        username[message['user_to']].send(msg_jim.encode('utf-8'))
                    except ConnectionResetError:
                        server_logger.info(
                            f'Клиент {username[message["user_to"]].getpeername()} отключился от сервера.')
                        del username[message['user_to']]

                messages.clear()


@Log()
def pars_ip_and_port():
    try:
        server_logger.info('Проверка на наличие параметра -p и ввода порта')
        if '-p' in sys.argv:
            serv_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            serv_port = 7777
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        server_logger.critical(
            'После параметра -\'p\' необходимо указать номер порта. Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    except TypeError:
        server_logger.critical(
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    except ValueError:
        server_logger.critical(
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777

    try:
        server_logger.info('Проверка на наличие параметра -а и ввода IP адреса')
        if '-a' in sys.argv:
            serv_addr = sys.argv[sys.argv.index('-a') + 1]
        else:
            serv_addr = ''
        if serv_addr != '' and re.search(
                r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$",
                serv_addr) == None:
            raise ValueError
    except IndexError:
        server_logger.critical(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер. Взят по умолчанию')
        serv_addr = ''
    except ValueError:
        server_logger.critical(
            'Адрес может быть только вида и в диапазоне от 0.0.0.0 до 999.999.999.999 '
            'Поэтому присвоен адрес по умолчанию')
        serv_addr = ''
    return serv_addr, serv_port


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('del - удаление пользователя из списка пользователей')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    serv_addr, serv_port = pars_ip_and_port()

    db = ServerStorage()
    # проверка работы класса на правильный порт
    # new_serv = Server(serv_addr, 123)
    new_serv = Server(serv_addr, serv_port, db)
    new_serv.daemon = True
    new_serv.start()
    # new_serv.main()


    # Создаём графическое окуружение для сервера:
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # Загрузка файла конфигурации сервера
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    if not config['SETTINGS']['Database_path']:
        config['SETTINGS']['Database_path'] = dir_path
        with open('server.ini', 'w') as conf:
            config.write(conf)
            print('Настройки изменены')

    # Инициализируем параметры в окна
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(db))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    # Функция обновляющяя список подключённых, проверяет флаг подключения, и
    # если надо обновляет список
    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(db))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    # Функция создающяя окно со статистикой клиентов
    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(db))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    # Функция создающяя окно с настройками сервера.
    def server_config():
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    # Функция сохранения настроек
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    # Функция создающяя окно со списком клиентов
    def show_users():
        global users_window
        users_window = UsersWindow()
        users_window.users_table.setModel(create_user_model(db))
        users_window.users_table.resizeColumnsToContents()
        users_window.users_table.resizeRowsToContents()
        users_window.show()

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)
    main_window.show_users_button.triggered.connect(show_users)

    # Запускаем GUI
    server_app.exec_()


    """
    print_help()

    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(db.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[2]}')
        elif command == 'connected':
            for user in sorted(db.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[2]}:{user[3]}, время установки соединения: {user[4]}')
        elif command == 'loghist':
            name = input(
                'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(db.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[3]}. Вход с: {user[1]}:{user[2]}')
        elif command == 'del':
            name = input('Введите имя пользователя для его удаления с базы данных: ')
            db.user_delete(name)
        else:
            print('Команда не распознана.')
    """

if __name__ == '__main__':
    main()
