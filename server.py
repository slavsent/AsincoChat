from socket import *
import json
import datetime
import sys
import re
import select
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


@Log()
def get_message(client):
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
    else:
        return data_from_client


def main():
    serv_addr, serv_port = pars_ip_and_port()

    s = socket(AF_INET, SOCK_STREAM)
    server_logger.info('Создан socket для соединения')
    s.bind((serv_addr, serv_port))
    s.settimeout(0.4)

    clients = []
    messages = []

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

        finally:
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
                        data_from_client = get_message(client_with_message)
                        print(f'Сообщение от клиента: {data_from_client["message"]}, время: {data_from_client["time"]}')
                        server_logger.info(f'Просмотр сообщения от клиента - {data_from_client["message"]}')
                        if data_from_client["message"] != "Error":
                            messages.append((data_from_client['user']['account_name'], data_from_client["message"]))
                        data_msg = create_msg_to_client(data_from_client)
                        msg_jim = json.dumps(data_msg)
                        server_logger.debug('Сообщение отправлено клиенту ответ')
                        client_with_message.send(msg_jim.encode('utf-8'))
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            if messages and send_data:
                message = {
                    "action": 'message',
                    "sender": messages[0][0],
                    'time': datetime.datetime.now().timestamp(),
                    "message": messages[0][1],
                }
                del messages[0]
                for waiting_client in send_data:
                    try:
                        msg_jim = json.dumps(message)
                        waiting_client.send(msg_jim.encode('utf-8'))
                        server_logger.debug('Сообщение отправлено клиенту рассылка')
                    except:
                        server_logger.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        clients.remove(waiting_client)


if __name__ == '__main__':
    main()
