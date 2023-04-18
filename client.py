import re
from socket import *
import json
import datetime
import sys
import logging
from log.client_log_config import client_logger
from decorate import Log


@Log()
def create_msg_for_server(msg):
    client_logger.debug(f'Сформировано presence сообщение по сообщению клиента: {msg}')
    return {
        'action': 'presence',
        'time': datetime.datetime.now().timestamp(),
        'encoding': 'utf-8',
        'message': msg,
        'user': {
            "account_name": "Guest",
            "status": "I ok!"
        }
    }


def main():
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
    else:
        try:
            client_logger.info('Проверка на наличие параметра ввода port при инициализации')
            serv_port = int(sys.argv[2])
            if serv_port < 1024 or serv_port > 65535:
                raise ValueError
        except IndexError:
            client_logger.debug('Не был введен параметр порта при инициализации, установлены по умолчанию 7777')
            serv_port = 7777
        except TypeError:
            client_logger.critical(
                f'Введен не верный порт {serv_port}. '
                'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
                'Поэтому присвоен порт по умолчанию 7777')
            serv_port = 7777
        except ValueError:
            client_logger.critical(
                f'Введен не числовой порт {serv_port}. '
                'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
                'Поэтому присвоен порт по умолчанию 7777')
            serv_port = 7777

    s = socket(AF_INET, SOCK_STREAM)
    client_logger.info('Создан socket для соединения')

    try:
        s.connect((serv_addr, serv_port))
    except TimeoutError:
        client_logger.critical('Сервер не найден')
        return
    client_logger.debug('Установлено соединение с сервером')

    while True:

        msg = str(input('Введите сообщение серверу: '))
        client_logger.info('Введено сообщение клиентом')
        data_msg = create_msg_for_server(msg)
        msg_jim = json.dumps(data_msg)
        client_logger.info('Сообщение переведено в формат JSON')

        s.send(msg_jim.encode('utf-8'))
        client_logger.debug('Сообщение отправлено на сервер')
        data = s.recv(1000000)
        client_logger.debug('Получено сообщение от сервера')
        try:
            client_logger.debug('Попытка расшифровки сообщения от сервера')
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
        except (ValueError, json.JSONDecodeError):
            client_logger.error('Неудачная расшифровка сообщения!')
            data_jim = {}
            data_from_server = {
                "message": 'Error',
                "time": 'Error'
            }
        else:
            client_logger.debug('Cообщениt от сервера успешно расшифровано')

        print(data_jim)
        print(f'Сообщение от сервера: {data_from_server["message"]}, время: {data_from_server["time"]}')
        client_logger.info(f'Расшифровано и выведено сообщение от сервера: {data_from_server["message"]}')
        if msg == 'close':
            client_logger.debug(f'Выход с текущего соединения по сообщению: {msg}')
            s.close()
            return


if __name__ == '__main__':
    main()
