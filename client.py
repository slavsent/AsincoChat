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

# Объект блокировки сокета и работы с базой данных
sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, username, sock, database):
        self.username = username
        self.s = sock
        self.database = database
        super().__init__()

    @Log()
    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    data = self.s.recv(1024)
                    client_logger.debug('Получено сообщение от сервера')
                    client_logger.debug('Cообщениt от сервера успешно расшифровано')
                    client_logger.debug('Попытка расшифровки сообщения от сервера')
                    data_jim = data.decode('utf-8')
                    data_from_server = json.loads(data_jim)
                except (ValueError, json.JSONDecodeError):
                    client_logger.error('Неудачная расшифровка сообщения!')
                    # Вышел таймаут соединения если errno = None, иначе обрыв соединения.
                except OSError as err:
                    if err.errno:
                        client_logger.critical(f'Потеряно соединение с сервером timeout.')
                        break
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_logger.error(f'Соединение с сервером было потеряно.')
                    break
                else:
                    if 'message' in data_from_server and 'user_to' in data_from_server and data_from_server['user_to'] \
                            == self.username:
                        with database_lock:
                            date_message = datetime.datetime.fromtimestamp(data_from_server['time'])
                            self.database.save_message(data_from_server['user_from'], data_from_server['user_to'],
                                                       data_from_server["message"], date_message)
                        print(
                            f'Получено сообщение от: {data_from_server["user_from"]}, время: {date_message}\n'
                            f'Сообщение: {data_from_server["message"]}')
                    else:
                        print(data_from_server)


# class Client(threading.Thread, metaclass=ClientVerifier):
class Client(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, username, sock, database):
        self.username = username
        self.s = sock
        self.database = database
        super().__init__()

    @Log()
    def create_exit_message(self, account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            'action': 'exit',
            'time': datetime.datetime.now().timestamp(),
            'user': {
                "account_name": account_name,
                "status": "I ok!"
            }
        }

    @Log()
    def create_message(self, sock, account_name, database):
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        time_send = datetime.datetime.now().timestamp()
        time_send_now = datetime.datetime.now()
        message_dict = {
            'action': 'message',
            'user_to': to_user,
            'message': message,
            'time': time_send,
            'user': {
                "account_name": account_name,
                "status": "I ok!"
            }
        }

        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        time.sleep(1)
        try:
            msg_jim = json.dumps(message_dict)
            client_logger.info('Сообщение переведено в формат JSON')
            with sock_lock:
                sock.send(msg_jim.encode('utf-8'))
                client_logger.info(f'Отправлено сообщение для пользователя {to_user}')

        except OSError as err:
            if err.errno:
                client_logger.critical(f'Потеряно соединение с сервером timeout.')
                sys.exit(1)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            client_logger.error(f'Соединение с сервером было потеряно.')
            sys.exit(1)
        else:
            with database_lock:
                self.database.save_message(account_name, to_user, message, time_send_now)

    # Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    @Log()
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            # Если отправка сообщения - соответствующий метод
            if command == 'message':
                self.create_message(self.s, self.username, self.database)

            # Вывод помощи
            elif command == 'help':
                self.print_help()

            # Выход. Отправляем сообщение серверу о выходе.
            elif command == 'exit':
                with sock_lock:
                    msg_jim = json.dumps(self.create_exit_message(self.username))
                    client_logger.info('Сообщение переведено в формат JSON')
                    self.s.send(msg_jim.encode('utf-8'))
                    client_logger.debug('Сообщение отправлено на сервер')
                    print('Завершение соединения.')
                    client_logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break

            # Список контактов
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            # Редактирование контактов
            elif command == 'edit':
                self.edit_contacts(self.s, self.database, self.username)

            # история сообщений.
            elif command == 'history':
                self.print_history(self.database, self.username)

            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция изменеия контактов
    @Log()
    def edit_contacts(self, s, database, client_name):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемого контакта: ')
            if database.check_contact(edit):
                with database_lock:
                    database.del_contact(edit)
                with sock_lock:
                    try:
                        data_msg = {
                            'action': 'del_contacts',
                            'time': datetime.datetime.now().timestamp(),
                            'user_login': client_name,
                            'contact_name': edit
                        }
                        msg_jim = json.dumps(data_msg)
                        s.send(msg_jim.encode('utf-8'))
                    except Exception:
                        client_logger.error('Не удалось отправить информацию на сервер.')
            else:
                client_logger.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            edit = input('Введите имя добавляемого контакта: ')
            if database.check_user(edit):
                with database_lock:
                    database.add_contact(edit)
                with sock_lock:
                    try:
                        data_msg = {
                            'action': 'add_contacts',
                            'time': datetime.datetime.now().timestamp(),
                            'user_login': client_name,
                            'contact_name': edit
                        }
                        msg_jim = json.dumps(data_msg)
                        s.send(msg_jim.encode('utf-8'))
                    except Exception:
                        client_logger.error('Не удалось отправить информацию на сервер.')

    # Функция выводящяя историю сообщений
    @Log()
    def print_history(self, database, client_name):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = database.get_history(to_who=client_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = database.get_history(from_user=client_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = database.get_history()
                for message in history_list:
                    print(
                        f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')

    # Функция выводящяя справку по использованию.
    @Log()
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


@Log()
def database_load(sock, db, client_name):
    try:
        users_list = user_list_request(sock)
    except Exception:
        client_logger.error('Ошибка запроса списка известных пользователей.')
    else:
        db.add_users(users_list)

    # Загружаем список контактов
    time.sleep(1)
    try:
        contacts_list = contacts_list_request(sock, client_name)
    except Exception:
        client_logger.error('Ошибка запроса списка контактов.')
    else:
        if contacts_list:
            for contact in contacts_list:
                db.add_contact(contact)


# Функция запроса списка контактов пользовател
@Log()
def user_list_request(sock):
    client_logger.debug(f'Запрос списка известных пользователей')
    data_msg = {
        'action': 'get_users',
        'time': datetime.datetime.now().timestamp(),
    }
    msg_jim = json.dumps(data_msg)
    with sock_lock:
        sock.send(msg_jim.encode('utf-8'))
        try:
            data = sock.recv(1000000)
            client_logger.debug('Получено сообщение от сервера')
            client_logger.debug('Попытка расшифровки сообщения от сервера')
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
            if 'response' in data_from_server and data_from_server['response'] == 202:
                return data_from_server['alert']
        except (ValueError, json.JSONDecodeError):
            client_logger.error('Неудачная расшифровка сообщения!')
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            client_logger.error(f'Соединение с сервером было потеряно.')
        else:
            client_logger.debug('Cообщениt от сервера успешно расшифровано')


# Функция запроса списка контактов пользователя
@Log()
def contacts_list_request(sock, username):
    client_logger.debug(f'Запрос списка известных пользователей {username}')
    data_msg = {
        'action': 'get_contacts',
        'time': datetime.datetime.now().timestamp(),
        'user_login': username,
    }
    msg_jim = json.dumps(data_msg)
    with sock_lock:
        sock.send(msg_jim.encode('utf-8'))
        try:
            data = sock.recv(1000000)
            client_logger.debug('Получено сообщение от сервера')
            client_logger.debug('Попытка расшифровки сообщения от сервера')
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
            if 'response' in data_from_server and data_from_server['response'] == 202:
                return data_from_server['alert']
        except (ValueError, json.JSONDecodeError):
            client_logger.error('Неудачная расшифровка сообщения!')
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            client_logger.error(f'Соединение с сервером было потеряно.')
        else:
            client_logger.debug('Cообщениt от сервера успешно расшифровано')


@Log()
def arg_parser():
    try:
        client_logger.info('Проверка на наличие параметра ввода IP при инициализации')
        serv_addr = str(sys.argv[1])
        if serv_addr != '' and re.search(
                r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$",
                serv_addr) == None:
            raise ValueError
    except IndexError:
        client_logger.debug('Не были введены параметры при инициализации, установлены по умолчанию 127.0.0.1:7777')
        serv_addr = '127.0.0.1'
        serv_port = 7777
    except ValueError:
        client_logger.critical(
            f'Введен не верный адрес {sys.argv[1]}. '
            'Адрес может быть только вида и в диапазоне от 0.0.0.0 до 999.999.999.999 '
            'Поэтому присвоен адрес и порт по умолчанию')
        serv_addr = '127.0.0.1'
        serv_port = 7777

    try:
        client_logger.info('Проверка на наличие параметра ввода port при инициализации')
        serv_port = int(sys.argv[2])
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        client_logger.debug('Не был введен параметр порта при инициализации, установлены по умолчанию 7777')
        serv_port = 7777
    except ValueError:
        client_logger.critical(
            f'Введен не числовой порт {sys.argv[2]}. '
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    except TypeError:
        client_logger.critical(
            f'Введен не верный порт {sys.argv[2]}. '
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    return serv_addr, serv_port


@Log()
def create_msg_for_server(msg, username):
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


def main():
    serv_addr, serv_port = arg_parser()

    client_name = input('Введите имя пользователя: ')
    s = socket(AF_INET, SOCK_STREAM)
    client_logger.info('Создан socket для соединения')
    s.settimeout(1)
    # проверка metaclass
    # s.listen(5)
    # client, addr = s.accept()
    try:
        s.connect((serv_addr, serv_port))
    except TimeoutError:
        client_logger.critical('Сервер не найден')
        return
    except ConnectionRefusedError:
        client_logger.critical(' Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        return
    client_logger.debug('Установлено соединение с сервером')

    msg = 'Установка соединения'
    data_msg = create_msg_for_server(msg, client_name)
    msg_jim = json.dumps(data_msg)
    client_logger.info('Сообщение переведено в формат JSON')

    with sock_lock:
        s.send(msg_jim.encode('utf-8'))
        client_logger.debug('Сообщение отправлено на сервер')
        data = s.recv(1024)
        client_logger.debug('Получено сообщение от сервера')
        client_logger.debug('Попытка расшифровки сообщения от сервера')
        data_jim = data.decode('utf-8')
        data_from_server = json.loads(data_jim)
        if 'response' in data_from_server and "message" in data_from_server:
            print(f'Сообщение от сервера: {data_from_server["message"]}, время: {data_from_server["time"]}')
        else:
            print(data_from_server)
    time.sleep(1)
    database = ClientStorage(client_name)
    database_load(s, database, client_name)

    time.sleep(1)
    user_interface = Client(client_name, s, database)
    user_interface.daemon = True
    user_interface.start()
    client_logger.debug('Запущены процессы')

    receiver = ClientReader(client_name, s, database)
    receiver.daemon = True
    receiver.start()

    while True:
        time.sleep(1)
        if receiver.is_alive() and user_interface.is_alive():
            continue
        break


if __name__ == '__main__':
    main()
