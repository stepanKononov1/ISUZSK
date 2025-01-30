from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCalendarWidget,
                             QPushButton, QFormLayout, QHBoxLayout, QSpinBox)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCalendarWidget,
    QPushButton, QFormLayout, QHBoxLayout)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QDate
from app.web import request as query
from app.web.request import query_post
from app.consts import web as web_consts
from datetime import datetime


class WorkerView(QDialog):
    def __init__(self, employee_data, jwt):
        """
        employee_data: List of employee info.
        Example: [1, 'Иван Иванов', '123e4567-e89b-12d3-a456-426614174000', '5 лет в продажах', 'Описание опыта работы и должности сотрудника.', 'ivanov@mail.com']
        """
        super().__init__()
        self.jwt = jwt
        self.resize(500, 300)
        self.data = employee_data[0]  # Берём данные первого сотрудника
        self.main()

    def main(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.user_id = int(self.data[0])
        self.name = QLineEdit(f"{self.data[1]}")

        self.uuid = QLineEdit(f"{self.data[2]}")

        self.exp = QTextEdit()
        self.exp.setText(self.data[3])

        self.description = QTextEdit()
        self.description.setText(self.data[4])

        self.contacts = QLineEdit(f"{self.data[5]}")

        self.age = QSpinBox()
        self.age.setValue(int(self.data[6]))
        self.age.setRange(1, 140)

        btn_exit = QPushButton('Обновить данные')
        btn_exit.clicked.connect(self.exit_dialog)
        btn_exit.setStyleSheet("text-align: center;")
        btn_exit.setMaximumWidth(150)
        btn_exit.setMaximumHeight(60)
        btn_exit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        form.addRow('Имя:', self.name)
        form.addRow('UUID:', self.uuid)
        form.addRow('Опыт:', self.exp)
        form.addRow('Описание:', self.description)
        form.addRow('Контакты:', self.contacts)
        form.addRow('Возраст:', self.age)
        layout.addLayout(form)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

    def exit_dialog(self):
        cookies = {
            web_consts.QUERYES: {
                'worker_u_base': {web_consts.KWARGS: [self.uuid.text(), self.user_id]},
                'worker_u_appends': {web_consts.KWARGS: [
                    self.name.text(),
                    self.age.value(),
                    self.exp.toPlainText(),
                    self.contacts.text(),
                    self.description.toPlainText(),
                    self.user_id
                ]}
            },
            web_consts.TOKEN: self.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = MessageSuccess('Успех', 'Работник обновлён')
            dialog.exec_()
        else:
            dialog = MessageError('Ошибка', 'Работника обновить не удалось')
            dialog.exec_()


class ProjectSave(QMessageBox):
    def __init__(self, cookies):
        super().__init__()
        self.setWindowTitle('Редактор')
        self.setStandardButtons(QMessageBox.Ok)
        res = query.query_post(web_consts.EXECUTE, cookies)
        if res['status'] == web_consts.COMPLETE:
            self.setText('Данные сохранены')
        else:
            self.setText(f'Ошибка: {web_consts["data"]}')
        self.exec()


class TaskItem(QListWidgetItem):
    def __init__(self, task_id, name, executor, deadline, column_id):
        super().__init__(f"{name} | {deadline}")
        self.name = name
        self.executor = executor
        self.deadline = deadline
        self.task_id = task_id  # Уникальный ID задачи
        self.column_id = column_id  # Идентификатор колонки, в которой находится задача


class TaskColumn(QListWidget):
    def __init__(self, column_id, name, board, type_c):
        super().__init__()
        self.column_id = column_id
        self.board = board  # Ссылка на доску для обновления данных
        self.type_c = type_c
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        # Заголовок колонки
        self.header = QLabel(name)
        self.header.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(350)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        item = event.source().takeItem(event.source().currentRow()
                                       )  # Берём задачу из старой колонки
        self.addItem(item)  # Добавляем в новую колонку

        # Обновляем column_id у задачи
        old_column_id = item.column_id  # Сохраняем старый column_id
        item.column_id = self.column_id  # Обновляем column_id у задачи
        type_c = self.type_c

        # Логируем или отправляем в БД
        print(
            f"Задача '{item.text()}' перемещена из колонки {old_column_id} в колонку {self.column_id}")
        self.board.update_task_column(item.task_id, self.column_id, type_c)


class BoardView(QWidget):
    def __init__(self, board_data, jwt):
        print(board_data)
        super().__init__()
        layout = QVBoxLayout(self)
        self.jwt = jwt

        title = QLabel(board_data["name"])
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.columns = []
        self.task_dict = {}

        self.board_layout = QHBoxLayout()
        layout.addLayout(self.board_layout)

        for column in board_data["columns"]:
            column_widget = TaskColumn(
                column["id"], column["name"], self, column['type'])
            column_layout = QVBoxLayout()
            column_layout.addWidget(column_widget.header)
            column_layout.addWidget(column_widget)
            self.columns.append(column_widget)
            self.board_layout.addLayout(column_layout)

        for task in board_data["tasks"]:
            task_item = TaskItem(
                task["id"], task["name"], task["executor"], task["deadline"], task["column_id"]
            )
            self.task_dict[task["id"]] = task_item

            for column in self.columns:
                if column.column_id == task["column_id"]:
                    column.addItem(task_item)
                    break

    def update_task_column(self, task_id, new_column_id, type_c):
        cookies = {
            web_consts.QUERYES: {
                'task_u_b': {web_consts.KWARGS: [new_column_id, task_id]}
            },
            web_consts.TOKEN: self.jwt
        }
        if type_c == 1:
            cookies[web_consts.QUERYES].update(
                {'task_u_executed': {web_consts.KWARGS: [task_id]}})
        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = MessageSuccess('Успех', 'Задача перенесена')
            dialog.exec_()
        else:
            dialog = MessageError('Ошибка', 'Задача не перенесена')
            dialog.exec_()
        print(
            f"Обновление в БД: Задача {task_id} теперь в колонке {new_column_id}")
        # Тут можно добавить обновление в базе данных


class MessageSuccess(QMessageBox):
    def __init__(self, title, message, info_text=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Information)
        self.setText(message)
        if info_text:
            self.setInformativeText(info_text)


class MessageError(QMessageBox):
    def __init__(self, title, message, info_text=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Critical)
        self.setText(message)
        if info_text:
            self.setInformativeText(info_text)


class CreateTaskForm(QWidget):
    def __init__(self, executors, boards, jwt, parent=None):
        super().__init__(parent)
        self.jwt = jwt
        self.setWindowTitle("Создание задачи")

        layout = QVBoxLayout(self)

        # Заголовок формы
        title = QLabel("Создание задачи")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ввод данных задачи
        form_layout = QFormLayout()

        self.task_name_input = QLineEdit()
        form_layout.addRow("Название задачи:", self.task_name_input)

        self.deadline_calendar = QCalendarWidget()
        self.deadline_calendar.setGridVisible(True)
        form_layout.addRow("Дедлайн:", self.deadline_calendar)

        self.priority_combobox = QComboBox()
        self.priority_combobox.addItems(
            [str(i) for i in range(11)])  # от 0 до 10
        form_layout.addRow("Приоритет:", self.priority_combobox)

        self.difficulty_combobox = QComboBox()
        self.difficulty_combobox.addItems(
            [str(i) for i in range(11)])  # от 0 до 10
        form_layout.addRow("Сложность:", self.difficulty_combobox)

        # Список исполнителей с ID
        self.executor_combobox = QComboBox()
        self.executor_combobox.addItems(
            [executor[1] for executor in executors])  # executor[1] - имя
        self.executor_data = executors  # сохраняем полный список с ID
        form_layout.addRow("Исполнитель:", self.executor_combobox)

        # Список досок с ID
        self.board_combobox = QComboBox()
        self.board_combobox.addItems([f'{board[4]} | {board[1]}'
                                     for board in boards])  # board[1] - имя
        self.board_data = boards  # сохраняем полный список с ID досок
        form_layout.addRow("Колонка:", self.board_combobox)

        layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_action)
        buttons_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Создать задачу")
        self.save_button.clicked.connect(self.save_action)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout)

    def save_action(self):
        # Получаем ID выбранного исполнителя
        executor_name = self.executor_combobox.currentText()
        executor_id = next(
            executor[0] for executor in self.executor_data if executor[1] == executor_name)

        # Получаем ID выбранной доски
        board_name = self.board_combobox.currentText()
        board_id = next(board[0]
                        for board in self.board_data if f'{board[4]} | {board[1]}' == board_name)

        # Функция для сохранения задачи
        task_data = {
            "name": self.task_name_input.text(),
            "deadline": self.deadline_calendar.selectedDate().toString(Qt.ISODate),
            "priority": int(self.priority_combobox.currentText()),
            "difficulty": int(self.difficulty_combobox.currentText()),
            "executor_id": executor_id,  # ID исполнителя
            "column_id": board_id  # ID доски
        }
        cookies = {
            web_consts.QUERYES: {
                'task_i': {
                    web_consts.KWARGS: [
                        task_data['name'],
                        task_data['deadline'],
                        task_data['priority'],
                        task_data['difficulty'],
                        task_data['executor_id'],
                        datetime.now().isoformat()
                    ]
                },
                'task_i_company': {web_consts.KWARGS: [f'{web_consts.JWT}company', f'{web_consts.LASTIND}Tasks']},
                'task_i_column': {web_consts.KWARGS:
                                  [
                                      task_data['column_id'], f'{web_consts.LASTIND}Tasks'
                                  ]}
            },
            web_consts.TOKEN: self.jwt
        }

        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = MessageSuccess('Успех', 'Задача создана')
            dialog.exec_()
        else:
            dialog = MessageError('Провал', 'Задача не создана')
            dialog.exec_()

        print("Задача сохранена:", task_data)
        # Здесь можно добавить код для отправки данных на сервер или в базу данных

    def cancel_action(self):
        # Закрыть окно формы
        self.close()


class EditTaskForm(QWidget):
    def __init__(self, task_data, executors, boards, jwt, parent=None):
        super().__init__(parent)
        self.jwt = jwt
        self.setWindowTitle("Редактирование задачи")

        # Сохранение данных задачи для редактирования (task_data - список)
        self.task_data = task_data
        # task_data[1] - название задачи
        print(task_data)
        self.setWindowTitle(f"Редактирование задачи: {task_data[1]}")

        layout = QVBoxLayout(self)

        # Заголовок формы
        title = QLabel("Редактирование задачи")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ввод данных задачи
        form_layout = QFormLayout()

        self.task_name_input = QLineEdit(
            task_data[1])  # task_data[1] - имя задачи
        form_layout.addRow("Название задачи:", self.task_name_input)

        self.deadline_calendar = QCalendarWidget()
        self.deadline_calendar.setGridVisible(True)
        self.deadline_calendar.setSelectedDate(QDate.fromString(
            task_data[2], Qt.ISODate))  # task_data[2] - deadline
        form_layout.addRow("Дедлайн:", self.deadline_calendar)

        self.priority_combobox = QComboBox()
        self.priority_combobox.addItems(
            [str(i) for i in range(11)])  # от 0 до 10
        self.priority_combobox.setCurrentText(
            str(task_data[3]))  # task_data[3] - priority
        form_layout.addRow("Приоритет:", self.priority_combobox)

        self.difficulty_combobox = QComboBox()
        self.difficulty_combobox.addItems(
            [str(i) for i in range(11)])  # от 0 до 10
        self.difficulty_combobox.setCurrentText(
            str(task_data[4]))  # task_data[4] - difficulty
        form_layout.addRow("Сложность:", self.difficulty_combobox)

        # Список исполнителей с ID
        self.executor_combobox = QComboBox()
        self.executor_combobox.addItems(
            [executor[1] for executor in executors])  # executor[1] - имя
        self.executor_data = executors  # сохраняем полный список с ID
        try:
            self.executor_combobox.setCurrentText(next(
                executor[1] for executor in executors if executor[0] == task_data[5]))  # task_data[5] - executor_id
        except StopIteration:
            dialog = MessageError(
                'Ошибка', 'После редактирования доски удалён исполнитель')
            dialog.exec_()
        form_layout.addRow("Исполнитель:", self.executor_combobox)

        # Список досок с ID
        self.board_combobox = QComboBox()
        self.board_combobox.addItems([board[1]
                                     for board in boards])  # board[1] - имя
        self.board_data = boards  # сохраняем полный список с ID досок
        try:
            self.board_combobox.setCurrentText(next(
                board[1] for board in boards if board[0] == task_data[6]))  # task_data[6] - column_id
        except StopIteration:
            dialog = MessageError(
                'Ошибка', 'После редактирования доски задача не имеет колонку')
            dialog.exec_()
        form_layout.addRow("Колонка:", self.board_combobox)

        layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_action)
        buttons_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.save_action)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout)

    def save_action(self):
        # Получаем ID выбранного исполнителя
        executor_name = self.executor_combobox.currentText()
        executor_id = next(
            executor[0] for executor in self.executor_data if executor[1] == executor_name)

        # Получаем ID выбранной доски
        board_name = self.board_combobox.currentText()
        board_id = next(board[0]
                        for board in self.board_data if board[1] == board_name)

        # Обновление данных задачи
        updated_task_data = [
            self.task_data[0],  # task_id
            self.task_name_input.text(),  # name
            self.deadline_calendar.selectedDate().toString(Qt.ISODate),  # deadline
            int(self.priority_combobox.currentText()),  # priority
            int(self.difficulty_combobox.currentText()),  # difficulty
            executor_id,  # executor_id
            board_id  # column_id
        ]

        cookies = {
            web_consts.QUERYES: {
                'task_u': {
                    web_consts.KWARGS: [
                        updated_task_data[1],
                        updated_task_data[2],
                        updated_task_data[3],
                        updated_task_data[4],
                        updated_task_data[5],
                        updated_task_data[0]
                    ]
                },
                'task_d_column': {
                    web_consts.KWARGS: [updated_task_data[0]]
                },
                'task_i_column': {web_consts.KWARGS:
                                  [
                                      updated_task_data[6], updated_task_data[0]
                                  ]}
            },
            web_consts.TOKEN: self.jwt
        }

        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = MessageSuccess('Успех', 'Задача обновлена')
            dialog.exec_()
        else:
            dialog = MessageError('Провал', 'Не удалось обновить задачу')
            dialog.exec_()

        print("Задача обновлена:", updated_task_data)
        # Здесь можно добавить код для отправки данных на сервер или в базу данных

    def cancel_action(self):
        # Закрыть окно формы
        self.close()
