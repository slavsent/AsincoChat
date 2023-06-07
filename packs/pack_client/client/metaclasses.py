import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):

        # Список методов, которые используются в функциях класса:
        methods = []
        # Атрибуты, используемые в функциях классов
        attrs = []
        # перебираем ключи
        for func in clsdict:
            # Пробуем
            try:
                # Возвращает итератор по инструкциям в предоставленной функции
                # , методе, строке исходного кода или объекте кода.
                ret = dis.get_instructions(clsdict[func])
                # Если не функция то ловим исключение
                # (если порт)
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for i in ret:
                    # print(i)
                    # if i.opname == 'LOAD_GLOBAL':
                    if i.opname == 'LOAD_METHOD':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    # elif i.opname == 'LOAD_ATTR':
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        # print('metod', methods)
        # print('atribut', attrs)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)


# Метакласс для проверки корректности клиентов:
class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # Список методов и атрибутов, которые используются в функциях класса:
        methods = []
        attrs = []
        for func in clsdict:
            # Пробуем
            try:
                ret = dis.get_instructions(clsdict[func])
                # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    # print(i)
                    if i.opname == 'LOAD_METHOD' or i.opname == 'LOAD_ATTR' or i.opname == 'LOAD_NAME':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    # elif i.opname == 'LOAD_ATTR':
                    if i.opname == 'LOAD_GLOBAL' or i.opname == 'LOAD_FAST':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        # print('metod', methods)
        # print('atribut', attrs)
        # Если обнаружено использование недопустимого метода accept, listen:
        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Если в классе нет s=socket():

        if not ('socket' in attrs or 'sock' in attrs):
            raise TypeError('В классе обнаружено не использование создание socket')
        if ('create_msg_for_server' in methods) or ('ClientReader' in methods) or (
                'run_main_command' in methods) or (
                'Client' in methods):
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)
