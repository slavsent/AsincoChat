import datetime
from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

BASE = declarative_base()


class Users(BASE):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    info = Column(String(100))
    last_login = Column(DateTime)
    passwd = Column(String(256))
    pubkey = Column(Text, )

    def __init__(self, login: str, passwd, info='no info', last_login=datetime.datetime.now(), pubkey=None):
        self.login = login
        self.info = info
        self.last_login = last_login
        self.passwd = passwd
        self.pubkey = pubkey

    def __repr__(self):
        return f'Пользователь: id - {self.id} login - {self.login} доп. информация: {self.info}, дата и время последнего логина: {self.last_login}'


class ClientHistory(BASE):
    __tablename__ = 'users_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    ip_address = Column(String(32))
    port = Column(Integer)
    login_time = Column(DateTime)

    def __init__(self, user: Users, ip_address: str, port: int, login_time: datetime):
        self.user_id = user
        self.ip_address = ip_address
        self.port = port
        self.login_time = login_time

    def __repr__(self):
        return f'login: {self.id} {self.user_id} {self.ip_address} {self.port} {self.login_time}'


class ContactList(BASE):
    __tablename__ = 'contact_list'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    ip_address = Column(String(32))
    port = Column(Integer)
    login_date = Column(DateTime)

    def __init__(self, user: Users, ip_address: str, port: int, login_date: datetime):
        self.user_id = user
        self.ip_address = ip_address
        self.port = port
        self.login_date = login_date

    def __repr__(self):
        return f'login: {self.id} {self.user_id} {self.ip_address} {self.port} {self.login_date}'


class UserContacts(BASE):
    __tablename__ = 'user_contacts'
    id = Column(Integer, primary_key=True)
    user = Column(String(50))
    contact = Column(String(50))

    def __init__(self, user: int, contact: int):
        self.user = user
        self.contact = contact

    def __repr__(self):
        return f'Контакты: {self.id} {self.user} {self.contact}'


class ServerStorage:
    def __init__(self, path):
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        BASE.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        self.session.commit()

        try:
            self.session.query(ClientHistory).delete()
            self.session.commit()
        except Exception:
            pass

    def user_login(self, username, ip_address, port, key):
        """
        Функция выполняющяяся при входе пользователя, записывает в базу факт входа
        :param username: login пользователя
        :param ip_address: ip_address пользователя
        :param port: port пользователя
        :param key: pubkey пользователя
        :return: внесение в бд информации о логинах пользователя
        """
        # print(username, ip_address, port)
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(Users).filter_by(login=username)
        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # Если нет, то создаздаём нового пользователя
        else:
            raise ValueError('Пользователь не зарегистрирован.')
            # old
            # Создаем экземпляр класса Users, через который передаем данные в таблицу
            # user = Users(username)
            # self.session.add(user)
            # self.session.commit()

        user = self.session.query(Users).filter_by(login=username).first()
        # Создаем экземпляр класса ClientHistory, через который передаем данные в таблицу
        new_active_user = ClientHistory(user.id, ip_address, port, user.last_login)
        self.session.add(new_active_user)

        # Создаем экземпляр класса ContactList, через который передаем данные в таблицу
        history = ContactList(user.id, ip_address, port, user.last_login)
        self.session.add(history)

        self.session.commit()

    def add_user(self, name, passwd_hash):
        """
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        :param name: логин
        :param passwd_hash: хэш пароля
        :return:
        """
        user_row = Users(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()

    def get_hash(self, name):
        """
        Метод получения хэша пароля пользователя.
        :param name: login
        :return:
        """
        user = self.session.query(Users).filter_by(login=name).first()
        return user.passwd

    def get_pubkey(self, name):
        """
        Метод получения публичного ключа пользователя.
        :param name: login
        :return:
        """
        user = self.session.query(Users).filter_by(login=name).first()
        return user.pubkey

    def user_logout(self, username):
        """
        Функция фиксирующая отключение пользователя
        :param username:
        :return:
        """
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы Users
        user = self.session.query(Users).filter_by(login=username).first()

        # Удаляем его из таблицы активных пользователей.
        # Удаляем запись из таблицы ClientHistory
        if user:
            self.session.query(ClientHistory).filter_by(user_id=user.id).delete()

            self.session.commit()

    def users_list(self, printable=None):
        """
        Функция возвращает список известных пользователей за все время.
        :param printable: если нужна печать то 1
        :return:
        """
        query = self.session.query(Users.login, Users.info, Users.last_login, )

        if printable == 1:
            users = self.session.query(Users).all()
            for el in users:
                print(el)
        return query.all()

    def active_users_list(self):
        """
        Функция возвращает список активных пользователей
        :return: список пользователей картеж
        """
        query = self.session.query(
            Users.login,
            Users.info,
            ClientHistory.ip_address,
            ClientHistory.port,
            ClientHistory.login_time
        ).join(Users)
        return query.all()

    def login_history(self, username=None, printable=None):
        """
        Функция возвращающая историю входов по пользователю или всем пользователям
        :param username: login пользователя
        :param printable: если нужна печать то 1
        :return: история входов по логину картеж
        """
        # Запрашиваем историю входа
        query = self.session.query(Users.login, ContactList.ip_address, ContactList.port, ContactList.login_date).join(
            Users)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(Users.login == username)
        if printable == 1:
            for el in query:
                print(f'Пользователь: {el[0]} адрес ip: {el[1]} порт: {el[2]} время входа на сервер: {el[3]}')
        return query.all()

    def user_delete(self, username):
        """
        Удаление пользователя из списка пользователей
        :param username:
        :return:
        """
        # Запрашиваем пользователя и удаляем его
        self.session.query(Users).filter_by(login=username).delete()

        self.session.commit()

    def add_user_contacts(self, user, contact):
        """
        Функция добавляет контакт для определенного пользователя
        :param user: пользователь
        :param contact: контакт
        :return:
        """
        rez = self.session.query(UserContacts).filter_by(user=user, contact=contact)
        if rez.count() < 1:
            contact_new = UserContacts(user, contact)
            self.session.add(contact_new)
            self.session.commit()

    def user_contacts(self, username):
        """
        Функция возвращает список контактов определенного пользователя
        :param username:
        :return:
        """
        query = self.session.query(UserContacts.user, UserContacts.contact, )
        if username:
            query = query.filter(UserContacts.user == username)
        rez = []
        if query:

            for contact in query:
                rez.append(contact[1])
        return rez

    def del_user_contacts(self, user, contact):
        """
        Функция добавляет контакт для определенного пользователя
        :param user: пользователь
        :param contact: контакт
        :return:
        """
        rez = self.session.query(UserContacts).filter_by(user=user, contact=contact).first()
        if rez:
            self.session.query(UserContacts).filter_by(user=user, contact=contact).delete()

            self.session.commit()

    def check_user(self, name):
        '''Метод проверяющий существование пользователя.'''
        if self.session.query(Users).filter_by(login=name).count():
            return True
        else:
            return False


# Отладка
if __name__ == '__main__':
    test_db = ServerStorage()

    # выполняем 'подключение' пользователя
    test_db.user_login('sergo', '192.168.1.25', 5555)
    test_db.user_login('ivan', '172.168.1.63', 7777)

    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя

    test_db.user_logout('sergo')
    # выводим список активных пользователей
    print(test_db.active_users_list())

    # запрашиваем историю входов по пользователю
    print(test_db.login_history('ivan'))
    test_db.login_history('sergo')
    print("С признаком печати:")
    test_db.login_history('sergo', 1)
    # выводим список известных пользователей
    print(test_db.users_list())
    print("Next:")
    test_db.users_list(1)
    test_db.user_delete('sergo')
    test_db.users_list(1)

    test_db.add_user_contacts('sen', 'tuk')
    test_db.add_user_contacts('sen', 'test')
    print('yes', test_db.user_contacts('sen'))
    print('no', test_db.user_contacts('tuk'))
    test_db.del_user_contacts('sen', 'test')
    print('yes', test_db.user_contacts('sen'))
