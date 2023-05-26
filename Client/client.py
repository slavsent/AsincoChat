import re
from socket import *
import json
import datetime
import sys
import threading
import time
import logging
sys.path.append('../')
from log.client_log_config import client_logger
from decorate import Log
from metaclasses import ClientVerifier
from client_db import ClientStorage
from Client.start_user import UserNameDialog
from Client.main_win import ClientMainWindow
from Client.sendler import ClientTransport, ServerError
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent


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
        #client_logger.critical(
        #    f'Введен не верный адрес {sys.argv[1]}. '
        #    'Адрес может быть только вида и в диапазоне от 0.0.0.0 до 999.999.999.999 '
        #    'Поэтому присвоен адрес и порт по умолчанию')
        serv_addr = '127.0.0.1'
        serv_port = 7777

    try:
        #client_logger.info('Проверка на наличие параметра ввода port при инициализации')
        serv_port = int(sys.argv[2])
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        #client_logger.debug('Не был введен параметр порта при инициализации, установлены по умолчанию 7777')
        serv_port = 7777
    except ValueError:
        #client_logger.critical(
        #    f'Введен не числовой порт {sys.argv[2]}. '
        #    'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
        #    'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    except TypeError:
        #client_logger.critical(
        #    f'Введен не верный порт {sys.argv[2]}. '
        #    'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
        #    'Поэтому присвоен порт по умолчанию 7777')
        serv_port = 7777
    return serv_addr, serv_port


def main():
    serv_addr, serv_port = arg_parser()

    # Создаём клиентокое приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке то запросим его
    start_dialog = UserNameDialog()
    client_app.exec_()
    # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, инааче выходим
    client_name = 'test1'
    if start_dialog.ok_pressed:
        client_name = start_dialog.client_name.text()
        del start_dialog
    else:
        exit(0)
    #print(client_name)

    database = ClientStorage(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    """
    try:
        transport = ClientTransport(serv_port, serv_addr, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    """
    transport = ClientTransport(serv_port, serv_addr, database, client_name)
    transport.daemon = True
    #transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат sents realise - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()




if __name__ == '__main__':
    main()

