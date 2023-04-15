import logging
from logging.handlers import RotatingFileHandler
import os

path = os.path.dirname(os.path.abspath(__file__))
handler = RotatingFileHandler(filename=os.path.join(path, 'client.log'), maxBytes=200000, backupCount=10,
                              encoding='utf-8')
formatting = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')
handler.setFormatter(formatting)

client_logger = logging.getLogger('client_log')
client_logger.addHandler(handler)
client_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    client_logger.critical('Критическая ошибка')
    client_logger.error('Ошибка')
    client_logger.debug('Отладочная информация')
    client_logger.info('Информационное сообщение')
