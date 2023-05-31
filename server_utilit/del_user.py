from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DelUserDialog(QDialog):
    '''
    Класс - диалог выбора контакта для удаления.
    '''

    def __init__(self, database, server):
        super().__init__()
        self.database = database
        self.server = server

        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel(
            'Выберите пользователя для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_ok.clicked.connect(self.remove_user)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.all_users_fill()

    def all_users_fill(self):
        """
        Метод заполняющий список пользователей.
        :return:
        """
        self.selector.addItems([item[0]
                                for item in self.database.users_list()])

    def remove_user(self):
        """
        Метод - обработчик удаления пользователя.
        :return:
        """
        self.database.user_delete(self.selector.currentText())
        self.messages.information(
            self, 'Успех', 'Пользователь успешно удален.')
        if self.selector.currentText() in self.server.username:
            sock = self.server.username[self.selector.currentText()]
            del self.server.username[self.selector.currentText()]
            self.server.remove_client(sock)
        # Рассылаем клиентам сообщение о необходимости обновить справочники
        self.server.service_update_lists()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    dial = DelUserDialog(None, None)
    app.exec_()
