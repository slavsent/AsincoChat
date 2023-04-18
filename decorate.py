import sys
import logging
from log import client_log_config, server_log_config
import inspect


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
