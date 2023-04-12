import re
from socket import *
import json
import datetime
import sys


def create_msg_for_server(msg):
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
        serv_addr = str(sys.argv[1])
        if serv_addr != '' and re.search(
                r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$",
                serv_addr) == None:
            raise ValueError
    except IndexError:
        serv_addr = '127.0.0.1'
        serv_port = 7777
    except ValueError:
        print(
            'Адрес может быть только вида и в диапазоне от 0.0.0.0 до 999.999.999.999 '
            'Поэтому присвоен адрес и порт по умолчанию')
        serv_addr = '127.0.0.1'
        serv_port = 7777
    else:
        try:
            serv_port = int(sys.argv[2])
            if serv_port < 1024 or serv_port > 65535:
                raise ValueError
        except IndexError:
            serv_port = 7777
        except TypeError:
            print(
                'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
                'Поэтому присвоен порт по умолчанию 7777')
            serv_port = 7777
        except ValueError:
            print(
                'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
                'Поэтому присвоен порт по умолчанию 7777')
            serv_port = 7777

    s = socket(AF_INET, SOCK_STREAM)

    try:
        s.connect((serv_addr, serv_port))
    except TimeoutError:
        print('Сервер не найден')
        return

    while True:

        msg = str(input('Введите сообщение серверу: '))
        data_msg = create_msg_for_server(msg)
        msg_jim = json.dumps(data_msg)

        s.send(msg_jim.encode('utf-8'))
        data = s.recv(1000000)
        try:
            data_jim = data.decode('utf-8')
            data_from_server = json.loads(data_jim)
        except (ValueError, json.JSONDecodeError):
            print('Неудачная расшифровка сообщения!')
            data_jim = {}
            data_from_server = {
                "message": 'Error',
                "time": 'Error'
            }

        print(data_jim)
        print(f'Сообщение от сервера: {data_from_server["message"]}, время: {data_from_server["time"]}')
        if msg == 'close':
            s.close()
            return


if __name__ == '__main__':
    main()
