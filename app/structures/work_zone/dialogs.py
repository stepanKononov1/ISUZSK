from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt
from app.web import request as query
from app.consts import web as responce


class WorkerView(QDialog):
    def __init__(self, data):
        """
        data{id, name, exp, description, contacts}
        """
        super().__init__()
        self.resize(500, 300)
        self.data = data
        self.main()

    def main(self):
        layout = QVBoxLayout()
        title = QLabel(f"Работник: {self.data['name']}")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.exp = QTextEdit()
        self.exp.setText(self.data['exp'])
        layout.addWidget(self.exp)

        self.description = QTextEdit()
        self.description.setText(self.data['description'])
        layout.addWidget(self.description)

        self.contacts = QLineEdit()
        self.contacts.setText(self.data['contacts'])
        layout.addWidget(self.contacts)

        btn_exit = QPushButton('Назад')
        btn_exit.clicked.connect(self.exit_dialog)
        btn_exit.setStyleSheet("text-align: center;")
        btn_exit.setMaximumWidth(150)
        btn_exit.setMaximumHeight(60)
        btn_exit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

    def exit_dialog(self):
        dialog = QMessageBox()
        dialog.setWindowTitle('Редактор')
        dialog.setText('Данные изменены')
        dialog.setStandardButtons(QMessageBox.Ok)
        res = query.query_post('proj_i', {
            'w_id': self.data['id'],
            'exp': self.exp.toPlainText(),
            'desc': self.description.toPlainText(),
            'con': self.contacts.text()
        })
        if res['status'] == responce.COMPLETE:
            self.setText('Данные сохранены')
        else:
            self.setText(f'Ошибка: {responce["data"]}')
        dialog.exec()


class ProjectSave(QMessageBox):
    def __init__(self, **kwargs):
        super().__init__()
        self.setWindowTitle('Редактор')
        self.setStandardButtons(QMessageBox.Ok)
        res = query.query_post('proj_i', kwargs)
        if res['status'] == responce.COMPLETE:
            self.setText('Данные сохранены')
        else:
            self.setText(f'Ошибка: {responce["data"]}')
        self.exec()
