Client module documentation (client_v1.py)
=================================================

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

client. **arg_parser** ()
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов:

        * адрес сервера
        * порт

    Выполняет проверку на корректность номера порта.

.. automodule:: client_v1
   :members:

client_db.py
~~~~~~~~~~~~~~

.. autoclass:: client_db.ClientStorage
        :members:

sendler.py
~~~~~~~~~~~~~~

.. autoclass:: Client.sendler.ClientTransport
        :members:

main_win.py
~~~~~~~~~~~~~~

.. autoclass:: Client.main_win.ClientMainWindow
        :members:

start_user.py
~~~~~~~~~~~~~~~

.. autoclass:: Client.start_user.UserNameDialog
        :members:


add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: Client.add_contact.AddContactDialog
        :members:


del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: Client.del_contact.DelContactDialog
        :members:
