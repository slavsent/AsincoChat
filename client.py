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
            f'Введен не верный адрес {serv_addr}. '
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
            f'Введен не числовой порт`. '
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    except TypeError:
        client_logger.critical(
            f'Введен не верный порт {serv_port}. '
            'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
            'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    return serv_addr, serv_port


@Log()
def message_from_server(s, username):
    while True:
        try:
            data = s.recv(1000000)
            client_logger.debug('Получено сообщение от сервера')
            client_logger.debug('Попытка расшифровки сообщения от сервера')
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
            if 'response' in data_from_server:
                print(f'Сообщение от сервера: {data_from_server["message"]}, время: {data_from_server["time"]}')
            elif 'message' in data_from_server and 'user_to' in data_from_server and data_from_server[
                'user_to'] == username:
                print(
                    f'Получено сообщение от: {data_from_server["user_from"]}, время: {data_from_server["time"]}\n '
                    f'Сообщение: {data_from_server["message"]}')
        except (ValueError, json.JSONDecodeError):
            client_logger.error('Неудачная расшифровка сообщения!')
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            client_logger.error(f'Соединение с сервером было потеряно.')
            break
        else:
            client_logger.debug('Cообщениt от сервера успешно расшифровано')


@Log()
def user_command(sock, username):
    print('Для отправки сообщения клиенту введите команду - message, для выхода - exit.')

    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'exit':
            msg_jim = json.dumps(create_exit_message(username))
            client_logger.info('Сообщение переведено в формат JSON')

            sock.send(msg_jim.encode('utf-8'))
            client_logger.debug('Сообщение отправлено на сервер')
            print('Завершение соединения.')
            client_logger.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Введена не верная команда.')


@Log()
def create_exit_message(account_name):
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
def create_message(sock, account_name='Guest'):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        'action': 'message',
        'user_to': to_user,
        'message': message,
        'time': datetime.datetime.now().timestamp(),
        'user': {
            "account_name": account_name,
            "status": "I ok!"
        }
    }
    client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        msg_jim = json.dumps(message_dict)
        client_logger.info('Сообщение переведено в формат JSON')

        sock.send(msg_jim.encode('utf-8'))
        client_logger.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        client_logger.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def main():
    serv_addr, serv_port = arg_parser()
    client_name = input('Введите имя пользователя: ')

    s = socket(AF_INET, SOCK_STREAM)
    client_logger.info('Создан socket для соединения')

    try:
        s.connect((serv_addr, serv_port))
    except TimeoutError:
        client_logger.critical('Сервер не найден')
        return
    client_logger.debug('Установлено соединение с сервером')

    msg = 'Установка соединения'
    data_msg = create_msg_for_server(msg, client_name)
    msg_jim = json.dumps(data_msg)
    client_logger.info('Сообщение переведено в формат JSON')

    s.send(msg_jim.encode('utf-8'))
    client_logger.debug('Сообщение отправлено на сервер')

    receiver = threading.Thread(target=message_from_server, args=(s, client_name))
    receiver.daemon = True
    receiver.start()

    user_interface = threading.Thread(target=user_command, args=(s, client_name))
    user_interface.daemon = True
    user_interface.start()
    client_logger.debug('Запущены процессы')

    while True:
        time.sleep(1)
        if receiver.is_alive() and user_interface.is_alive():
            continue
        break


if __name__ == '__main__':
    main()
