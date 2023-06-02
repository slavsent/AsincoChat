import sys
sys.path.append('../')

from PyQt5.QtWidgets import QDialog, QPushButton, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


# Класс окна с историей пользователей
class UsersWindow(QDialog):
    """
    Класс списка существующих пользователей
    """
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Информация о пользователях')
        self.setFixedSize(600, 800)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 765)
        self.close_button.clicked.connect(self.close)

        # Лист со списком
        self.users_table = QTableView(self)
        self.users_table.move(10, 10)
        self.users_table.setFixedSize(580, 740)

        self.create_list_users()

    def create_list_users(self):
        """
        Получение существующих пользователей
        :return:
        """
        # Список записей из базы
        hist_list = self.database.users_list()

        # Объект модели данных:
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Имя Клиента', 'Информация', 'Время последнего подключения'])
        for row in hist_list:
            user, info, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            # last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            time = QStandardItem(str(time))
            time.setEditable(False)
            info = QStandardItem(str(info))
            info.setEditable(False)
            list.appendRow([user, info, time])
        self.users_table.setModel(list)
        self.users_table.resizeColumnsToContents()
        self.users_table.resizeRowsToContents()
