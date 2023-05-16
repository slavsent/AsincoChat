from socket import *
import json
import datetime
import sys
import re
import select
import logging
from log.server_log_config import server_logger
from decorate import Log
from port_descriptor import PortDescriptor
from metaclasses import ServerVerifier


class Server(metaclass=ServerVerifier):
    serv_port = PortDescriptor()

    def __init__(self, serv_addr, serv_port):
        self.serv_addr = serv_addr
        self.serv_port = serv_port

    @Log()
    def create_msg_to_client(self, msg_from_client, username, clients, client):
        if msg_from_client['message'] == 'Error':
            server_logger.debug('Сформирован ответ с - Bad Request')
            return {
                "response": 400,
                "message": "Bad Request",
                'time': datetime.datetime.now().timestamp(),
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
        if msg_from_client['action'] == 'presence':
            server_logger.debug('Сформирован ответ на сообщение - presence')
            return {
                "response": 200,
                "message": f"Привет клиент: {msg_from_client['user']['account_name']}",
                'time': datetime.datetime.now().timestamp(),
            }
        elif msg_from_client['action'] == 'message' and 'user_to' in msg_from_client and 'user' in msg_from_client:
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

    def main(self):

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
                        print(f'Сообщение от клиента: {data_from_client["message"]}, время: {data_from_client["time"]}')
                        server_logger.info(f'Просмотр сообщения от клиента - {data_from_client["message"]}')
                        data_msg = self.create_msg_to_client(data_from_client, username, clients, client_with_message)
                        if 'response' not in data_msg or data_msg['response'] != 'close':
                            if 'action' in data_msg and data_msg['action'] == 'message':
                                messages.append(data_msg)
                            else:
                                msg_jim = json.dumps(data_msg)
                                server_logger.debug('Сообщение отправлено клиенту ответ')
                                client_with_message.send(msg_jim.encode('utf-8'))
                                if 'user' in data_msg and data_msg['user'] == 'error':
                                    clients.remove(client_with_message)
                    except Exception:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            if messages:
                for message in messages:
                    try:
                        msg_jim = json.dumps(message)
                        server_logger.debug(
                            f'Сообщение отправлено клиенту {message["user_to"]} от клиента {message["user_from"]}')
                        username[message['user_to']].send(msg_jim.encode('utf-8'))
                    except:
                        server_logger.info(
                            f'Клиент {username[message["user_to"]].getpeername()} отключился от сервера.')
                        clients.remove(username[message['user_to']])
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


def main():
    serv_addr, serv_port = pars_ip_and_port()
    # проверка работы класса на правильный порт
    # new_serv = Server(serv_addr, 123)
    new_serv = Server(serv_addr, serv_port)
    new_serv.main()


if __name__ == '__main__':
    main()
