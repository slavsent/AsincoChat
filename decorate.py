import sys
import logging
from log import client_log_config, server_log_config
import inspect
import socket


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server_log')
else:
    LOGGER = logging.getLogger('client_log')


class Log:

    def __call__(self, func):
        def decorator(*args, **kwargs):
            res = func(*args, **kwargs)
            name_modul = str(inspect.stack()[-1].filename).split('\\')[-1]
            LOGGER.debug(f'Вызов из модуля {name_modul} функция {func.__name__} '
                         f'вызванная из функции {inspect.stack()[1][3]}')
            return res
        return decorator


def login_required(func):
    '''
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    '''

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server_utilit.server_messeger import ServerMesseger
        if isinstance(args[0], ServerMesseger):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].username:
                        if args[0].username[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if 'action' in arg and arg['action'] == 'presence':
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
