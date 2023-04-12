from socket import *
import json
import datetime
import sys
import re


def create_msg_to_client(msg_from_client):
    if msg_from_client['message'] == 'Error':
        return {
            "response": 400,
            "message": "Bad Request",
            'time': datetime.datetime.now().timestamp(),
        }
    elif msg_from_client['action'] == 'presence':
        return {
            "response": 200,
            "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
            'time': datetime.datetime.now().timestamp(),
        }
    else:
        return {
            "response": 200,
            "message": "Wait action",
            'time': datetime.datetime.now().timestamp(),
        }


def main():
    try:
        if '-p' in sys.argv:
            serv_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            serv_port = 7777
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта. Поэтому присвоен порт по умолчанию 7777')
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

    try:
        if '-a' in sys.argv:
            serv_addr = sys.argv[sys.argv.index('-a') + 1]
        else:
            serv_addr = ''
        if serv_addr != '' and re.search(
                r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$",
                serv_addr) == None:
            raise ValueError
    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер. Взят по умолчанию')
        serv_addr = ''
    except ValueError:
        print(
            'Адрес может быть только вида и в диапазоне от 0.0.0.0 до 999.999.999.999 '
            'Поэтому присвоен адрес по умолчанию')
        serv_addr = ''
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((serv_addr, serv_port))
    s.listen(5)
    client, addr = s.accept()
    while True:

        data = client.recv(1000000)
        try:
            data_jim = data.decode('utf-8')
            data_from_client = json.loads(data_jim)
        except (ValueError, json.JSONDecodeError):
            print('Неудачная расшифровка сообщения!')
            data_jim = {}
            data_from_client = {
                "message": 'Error',
                "time": 'Error'
            }

        print(data_jim)

        print(f'Сообщение от клиента: {data_from_client["message"]}, время: {data_from_client["time"]}')
        data_msg = create_msg_to_client(data_from_client)
        msg_jim = json.dumps(data_msg)

        client.send(msg_jim.encode('utf-8'))
        if data_from_client['message'] == 'close':
            client.close()
            return


if __name__ == '__main__':
    main()
