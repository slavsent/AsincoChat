Server module documentation (server_v1.py)
=================================================

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

1. -p - Порт на котором принимаются соединения
2. -a - Адрес с которого принимаются соединения.

В случае не указания параметров будут использованы по умолчанию 127.0.0.1:7777

Примеры использования:

``python server.py -p 8080``

*Запуск сервера на порту 8080*

server_v1.py
~~~~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server_v1. **arg_parser** ()
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов:

        * адрес с которого принимать соединения
        * порт

server_v1. **config_load** ()
    Функция загрузки параметров конфигурации из ini файла.
    В случае отсутствия файла задаются параметры по умолчанию.


server_messeger.py
~~~~~~~~~~~~~~~~~~

.. autoclass:: server_utilit.server_messeger.ServerMesseger
   :members:

server_db.py
~~~~~~~~~~~~

.. autoclass:: server_db.ServerStorage
   :members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: server_utilit.main_win.MainWindow
   :members:

reg_user.py
~~~~~~~~~~~

.. autoclass:: server_utilit.reg_user.RegisterUser
   :members:

del_user.py
~~~~~~~~~~~

.. autoclass:: server_utilit.del_user.DelUserDialog
   :members:

config_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server_utilit.config_win.ConfigWindow
   :members:

list_users.py
~~~~~~~~~~~~~

.. autoclass:: server_utilit.list_users.UsersWindow
   :members:

history_users.py
~~~~~~~~~~~~~~~~

.. autoclass:: server_utilit.history_users.StatWindow
   :members:
