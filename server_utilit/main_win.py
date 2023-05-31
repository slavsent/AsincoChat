import sys

sys.path.append('../')

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QTimer
from server_utilit.history_users import StatWindow
from server_utilit.list_users import UsersWindow
from server_utilit.config_win import ConfigWindow
from server_utilit.reg_user import RegisterUser
from server_utilit.del_user import DelUserDialog


# Класс основного окна
class MainWindow(QMainWindow):
    def __init__(self, database, server, config):
        super().__init__()
        self.database = database
        self.config = config
        self.server_thread = server
        # self.initUI()

        # Кнопка выхода
        self.exitAction = QAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        # Кнопка обновить список клиентов
        self.refresh_button = QAction('Обновить список', self)

        # Кнопка настроек сервера
        self.config_btn = QAction('Настройки сервера', self)

        # Кнопка регистрации пользователя
        self.register_btn = QAction('Регистрация пользователя', self)

        # Кнопка удаления пользователя
        self.remove_btn = QAction('Удаление пользователя', self)

        # Кнопка вывести историю сообщений
        self.show_history_button = QAction('История клиентов', self)

        # Кнопка вывести список клиентов
        self.show_users_button = QAction('Список клиентов', self)

        # Статусбар
        self.statusBar()
        self.statusBar().showMessage('Server Working')

        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.register_btn)
        self.toolbar.addAction(self.remove_btn)
        self.toolbar.addAction(self.show_users_button)

        # Настройки геометрии основного окна
        self.setFixedSize(800, 400)
        self.setWindowTitle('Информационное окно сервера')

        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        # Окно со списком подключённых клиентов.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 320)

        # Таймер, обновляющий список клиентов 1 раз в секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        # Связываем кнопки с процедурами
        self.refresh_button.triggered.connect(self.create_users_model)
        self.show_history_button.triggered.connect(self.show_statistics)
        self.show_users_button.triggered.connect(self.show_list_users)
        self.config_btn.triggered.connect(self.server_config)
        self.register_btn.triggered.connect(self.reg_user)
        self.remove_btn.triggered.connect(self.rem_user)

        # Последним параметром отображаем окно.
        self.show()

    # GUI - Создание таблицы QModel, для отображения в окне программы.
    def create_users_model(self):
        list_users = self.database.active_users_list()
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
        for row in list_users:
            user, info, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time))
            time.setEditable(False)
            list.appendRow([user, ip, port, time])
        self.active_clients_table.setModel(list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()

    def show_statistics(self):
        '''Метод создающий окно со статистикой клиентов.'''
        global stat_window
        stat_window = StatWindow(self.database)
        stat_window.show()

    def show_list_users(self):
        '''Метод создающий окно со статистикой клиентов.'''
        global stat_list_users_window
        stat_list_users_window = UsersWindow(self.database)
        stat_list_users_window.show()

    def server_config(self):
        '''Метод создающий окно с настройками сервера.'''
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        '''Метод создающий окно регистрации пользователя.'''
        global reg_window
        reg_window = RegisterUser(self.database, self.server_thread)
        reg_window.show()

    def rem_user(self):
        '''Метод создающий окно удаления пользователя.'''
        global rem_window
        rem_window = DelUserDialog(self.database, self.server_thread)
        rem_window.show()
