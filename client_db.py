import datetime
from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

BASE = declarative_base()


class Users(BASE):
    """
    Класс создания таблицы пользователей
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))

    def __init__(self, username: str):
        self.username = username

    def __repr__(self):
        return f'Известные пользователи: id - {self.id} username - {self.username}'


class MessageHistory(BASE):
    """
    Класс истории сообщений пользователя
    """
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    from_user = Column(String(50))
    to_user = Column(String(50))
    message = Column(String(256))
    date_message = Column(DateTime)

    def __init__(self, from_user: str, to_user: str, message: str, date_message: datetime):
        self.from_user = from_user
        self.to_user = to_user
        self.message = message
        self.date_message = date_message

    def __repr__(self):
        return f'Message: {self.id} {self.from_user} {self.to_user} {self.from_user} {self.date_message}'


class Contacts(BASE):
    """
    Класс списка контактов пользователя
    """
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))

    def __init__(self, username: str):
        self.username = username

    def __repr__(self):
        return f'Contact: {self.id} {self.username}'


class ClientStorage:
    """
    Класс - оболочка для работы с базой данных клиента.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется классический подход.
    """
    def __init__(self, name_db):
        # Создаём движок базы данных, поскольку разрешено несколько
        # клиентов одновременно, каждый должен иметь свою БД
        # Поскольку клиент мультипоточный необходимо отключить
        # проверки на подключения с разных потоков,
        # иначе sqlite3.ProgrammingError
        self.engine = create_engine(f'sqlite:///client_db_{name_db}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        # Создаём объект MetaData
        BASE.metadata.create_all(self.engine)

        # Создаём сессию
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()

        # Необходимо очистить таблицу контактов, т.к. при запуске они
        # подгружаются с сервера.
        try:
            self.session.query(Contacts).delete()
            self.session.commit()
        except Exception:
            pass

    def add_contact(self, contact):
        """
        Функция добавления контактов
        :param contact: username контакта
        :return:
        """
        if not self.session.query(Contacts).filter_by(username=contact).count():
            contact_new = Contacts(contact)
            self.session.add(contact_new)
            self.session.commit()

    def del_contact(self, contact):
        """
        Функция удаления контакта
        :param contact: username контакта
        :return:
        """
        self.session.query(Contacts).filter_by(username=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """
        Функция добавления известных пользователей.
        :param users_list: Список username пользователей
        :return:
        """
        self.session.query(Users).delete()
        if users_list:
            for user in users_list:
                user_new = Users(user)
                self.session.add(user_new)
            self.session.commit()
        else:
            print(users_list)

    def save_message(self, from_user, to_user, message, date_message=datetime.datetime.now()):
        """
        Функция сохраняющяя сообщения
        :param from_user: username от какого пользователя
        :param to_user: username какому пользователю
        :param message: текст сообщения
        :param date_message: дата и время сообщения
        :return:
        """
        message_new = MessageHistory(from_user, to_user, message, date_message)
        self.session.add(message_new)
        self.session.commit()

    def get_contacts(self):
        """
        Функция возвращающяя контакты
        :return: список контактов
        """
        return [contact[0] for contact in self.session.query(Contacts.username).all()]

    def get_users(self):
        """
        Функция возвращающяя список известных пользователей
        :return: список пользователей
        """
        return [user[0] for user in self.session.query(Users.username).all()]

    def check_user(self, user):
        """
        Функция проверяющяя наличие пользователя в известных
        :param user: username пользователя
        :return: True если есть False если нет
        """
        if self.session.query(Users).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        Функция проверяющяя наличие пользователя контактах
        :param contact: username пользователя
        :return: True если есть False если нет
        """
        if self.session.query(Contacts).filter_by(username=contact).count():
            return True
        else:
            return False

    def get_history(self, from_who=None, to_who=None):
        """
        Функция возвращающая историю переписки
        :param from_who: если есть то поиск от кого
        :param to_who: если есть то поиск кому
        :return: список сообщений
        """
        query = self.session.query(MessageHistory)
        if from_who and to_who:
            query_to = query.filter_by(from_user=from_who)
            query_from = query.filter_by(to_user=to_who)
            return [
                (history_message.from_user, history_message.to_user, history_message.message,
                 history_message.date_message)
                for history_message in query_to.all()] + [
            (history_message.from_user, history_message.to_user, history_message.message, history_message.date_message)
            for history_message in query_from.all()]
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [
            (history_message.from_user, history_message.to_user, history_message.message, history_message.date_message)
            for history_message in query.all()]


if __name__ == '__main__':
    test_db = ClientStorage('client1')
    for i in ['user1', 'user2', 'user3']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('test2'))
    print(test_db.get_history(to_who='test2'))
    print(test_db.get_history('test3'))
    test_db.del_contact('test4')
    print(test_db.get_contacts())
