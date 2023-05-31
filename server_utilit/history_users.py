from PyQt5.QtWidgets import QDialog, QPushButton, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import sys
sys.path.append('../')


class StatWindow(QDialog):
    '''
    Класс - окно со статистикой пользователей
    '''

    def __init__(self, database):
        super().__init__()

        self.database = database
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('История подклчения пользователей')
        self.setFixedSize(600, 800)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 765)
        self.close_button.clicked.connect(self.close)

        # Лист с собственно историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 740)

        self.create_stat_model()

    def create_stat_model(self):
        '''Метод реализующий заполнение таблицы статистикой сообщений.'''
        # Список записей из базы
        hist_list = self.database.login_history()

        # Объект модели данных:
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Имя Клиента', 'Адрес', 'Порт', 'Время подключения'])
        for row in hist_list:
            user, address_ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            # last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            time = QStandardItem(str(time))
            time.setEditable(False)
            address_ip = QStandardItem(str(address_ip))
            address_ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            list.appendRow([user, address_ip, port, time])
        self.history_table.setModel(list)
        self.history_table.resizeColumnsToContents()
        self.history_table.resizeRowsToContents()