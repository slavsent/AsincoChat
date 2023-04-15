import logging
from logging.handlers import TimedRotatingFileHandler
import os


path = os.path.dirname(os.path.abspath(__file__))
handler = TimedRotatingFileHandler(filename=os.path.join(path, 'server.log'), when="midnight", backupCount=10,
                                   encoding='utf-8')
formatting = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')
handler.setFormatter(formatting)

server_logger = logging.getLogger('server_log')
server_logger.addHandler(handler)
server_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    server_logger.critical('Критическая ошибка')
    server_logger.error('Ошибка')
    server_logger.debug('Отладочная информация')
    server_logger.info('Информационное сообщение')
