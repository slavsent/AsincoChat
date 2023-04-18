from socket import *
import json
import datetime
import sys
import re
import logging
from log.server_log_config import server_logger
from decorate import Log


@Log()
def create_msg_to_client(msg_from_client):
    if msg_from_client['message'] == 'Error':
        server_logger.debug('Сформирован ответ с - Bad Request')
        return {
            "response": 400,
            "message": "Bad Request",
            'time': datetime.datetime.now().timestamp(),
        }
    elif msg_from_client['action'] == 'presence':
        server_logger.debug('Сформирован ответ на сообщение - presence')
        return {
            "response": 200,
            "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
            'time': datetime.datetime.now().timestamp(),
        }
    else:
        server_logger.debug('Сформирован ответ на прочие сообщения чем presence и error')
        return {
            "response": 200,
            "message": "Wait action",
            'time': datetime.datetime.now().timestamp(),
        }


def main():
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

    s = socket(AF_INET, SOCK_STREAM)
    server_logger.info('Создан socket для соединения')
    s.bind((serv_addr, serv_port))
    s.listen(5)
    server_logger.info('Прослушивание адреса для соединения')
    client, addr = s.accept()
    server_logger.debug('Подключение клиента к серверу')
    while True:

        data = client.recv(1000000)
        server_logger.debug('Получение сообщения от клиента')
        try:
            server_logger.info('Попытка расшибровки сообщения от клиента')
            data_jim = data.decode('utf-8')
            data_from_client = json.loads(data_jim)
        except (ValueError, json.JSONDecodeError):
            server_logger.error('Неудачная расшифровка сообщения!')
            data_jim = {}
            data_from_client = {
                "message": 'Error',
                "time": 'Error'
            }

        print(data_jim)

        print(f'Сообщение от клиента: {data_from_client["message"]}, время: {data_from_client["time"]}')
        server_logger.info(f'Просмотр сообщения от клиента - {data_from_client["message"]}')
        data_msg = create_msg_to_client(data_from_client)
        msg_jim = json.dumps(data_msg)

        client.send(msg_jim.encode('utf-8'))

        server_logger.debug('Сообщение отправлено клиенту')
        if data_from_client['message'] == 'close':
            server_logger.debug(f'Выход с текущего соединения по сообщению: {data_from_client["message"]}')
            client.close()
            return


if __name__ == '__main__':
    main()
