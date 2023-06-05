import logging
from log.server_log_config import server_logger


class PortDescriptor:

    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        if not (1023 < value < 65536):
            server_logger.critical(
                'В качестве порта может быть указано только число в диапазоне от 1024 до 65535. '
                'Поэтому присвоен порт по умолчанию 7777')
            instance.__dict__[self.my_attr] = 7777
        instance.__dict__[self.my_attr] = value

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr



