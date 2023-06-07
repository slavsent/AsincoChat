import sys

sys.path.append('../')
from socket import *
import json
import datetime
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
from server_utilit.server_messeger import ServerMesseger
from server_utilit.main_win import MainWindow
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


@Log()
def pars_ip_and_port():
    """
    Парсер аргументов коммандной строки.
    :return: возвращает если правильно введи ip адрес и порт или по умолчанию 127.0.0.1:7777
    """
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
    """
    Основная функция
    :return:
    """
    # Загрузка параметров командной строки, если нет параметров, то задаём
    # значения по умоланию
    serv_addr, serv_port = pars_ip_and_port()

    # Загрузка файла конфигурации сервера
    config = configparser.ConfigParser()

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.getcwd()
    config.read(f"{dir_path}/{'server.ini'}")
    if not config['SETTINGS']['Database_path']:
        config['SETTINGS']['Database_path'] = dir_path
        with open('server.ini', 'w') as conf:
            config.write(conf)
            print('Настройки изменены')

    # Инициализация базы данных
    db = ServerStorage(os.path.join(
        config['SETTINGS']['Database_path'],
        config['SETTINGS']['Database_file']))

    # проверка работы класса на правильный порт
    # new_serv = Server(serv_addr, 123)

    # Создание экземпляра класса - сервера и его запуск:
    new_serv = ServerMesseger(serv_addr, serv_port, db)
    new_serv.daemon = True
    new_serv.start()
    # new_serv.main()

    # Создаём графическое окуружение для сервера:
    server_app = QApplication(sys.argv)
    server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_window = MainWindow(db, new_serv, config)

    # Запускаем GUI
    server_app.exec_()

    # По закрытию окон останавливаем обработчик сообщений
    new_serv.running = False


if __name__ == '__main__':
    main()
