from app.web import request
from app.consts.web import *
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QHBoxLayout, QErrorMessage, QMessageBox
from app.consts.data_travel import Data
from app.consts import web as web_consts
from PyQt5.QtCore import Qt
import sys


class RegistrationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.resize(300, 400)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 50, 0, 50)

        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setObjectName("login_input")

        self.email_label = QLabel("Почта:")
        self.email_input = QLineEdit()
        self.email_input.setObjectName("email_input")

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("password_input")

        self.confirm_password_label = QLabel("Подтверждение пароля:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setObjectName("confirm_password_input")

        self.submit_button = QPushButton("Регистрация")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setFixedSize(150, 30)

        self.login_input.setFixedSize(150, 30)
        self.email_input.setFixedSize(150, 30)
        self.password_input.setFixedSize(150, 30)
        self.confirm_password_input.setFixedSize(150, 30)

        layout.addWidget(self.login_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.login_input, alignment=Qt.AlignCenter)
        layout.addItem(QSpacerItem(
            0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.email_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.email_input, alignment=Qt.AlignCenter)
        layout.addItem(QSpacerItem(
            0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.password_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        layout.addItem(QSpacerItem(
            0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.confirm_password_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.confirm_password_input, alignment=Qt.AlignCenter)
        layout.addItem(QSpacerItem(
            0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def submit(self):
        if not self.password_input.text() == self.confirm_password_input.text():
            message = QErrorMessage(self)
            message.showMessage('Пароли не совпадают')
            message.exec()
            return
        login, password, mail = (self.login_input.text(
        ), self.password_input.text(), self.email_input.text())
        res = request.query_post(
            web_consts.REG, {'login': login, 'password': password, 'mail': mail})
        if res['status'] == COMPLETE:
            message = QErrorMessage(self)
            message.showMessage('Компания на введённые данные создана успешно')
            message.exec()
            self.deleteLater()
        else:
            message = QErrorMessage(self)
            message.showMessage('Логин уже используется')
            message.exec()


class AuthorizationDialog(QDialog):
    def __init__(self, window):
        super().__init__()
        self.main_window = window
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 50, 0, 50)

        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setObjectName("login_input")

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("password_input")

        self.submit_button = QPushButton("Войти")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setFixedSize(150, 30)

        self.login_input.setFixedSize(150, 30)
        self.password_input.setFixedSize(150, 30)

        layout.addWidget(self.login_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.login_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.password_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.register_button = QPushButton("Регистрация")
        self.register_button.setObjectName("register_button")
        self.register_button.clicked.connect(self.registration)
        self.register_button.setFixedSize(100, 30)
        top_layout.addWidget(self.register_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

    def submit(self):
        login, password = (self.login_input.text(), self.password_input.text())
        res = request.query_post(
            web_consts.AUTH, {'login': login, 'password': password})
        if res['status'] == COMPLETE:
            data = Data(res['role'], res['dt'], res['company'])
            print(data.premission)
            self.main_window.show(data=data)
            self.deleteLater()
        else:
            message = QErrorMessage(self)
            message.showMessage('Введённые данные не валидны')
            message.exec()

    def registration(self):
        RegistrationDialog().exec()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Вы уверены, что хотите закрыть окно?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            event.ignore()
