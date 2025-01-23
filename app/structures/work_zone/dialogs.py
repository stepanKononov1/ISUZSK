from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt


class WorkerView(QDialog):
    def __init__(self, data):
        """
        data{name, exp, description, contacts}
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

        exp = QTextEdit()
        exp.setText(self.data['exp'])
        layout.addWidget(exp)

        description = QTextEdit()
        description.setText(self.data['description'])
        layout.addWidget(description)

        contacts = QLineEdit()
        contacts.setText(self.data['contacts'])
        layout.addWidget(contacts)

        btn_exit = QPushButton('Назад')
        btn_exit.clicked.connect(self.exit)
        btn_exit.setStyleSheet("text-align: center;")
        btn_exit.setMaximumWidth(150)
        btn_exit.setMaximumHeight(60)
        btn_exit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

    def exit(self):
        """
        Purpose: 
        """

    # end def
