from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QPushButton,
                             QVBoxLayout,
                             QHBoxLayout,
                             QLabel,
                             QFormLayout,
                             QLineEdit,
                             QTextEdit,
                             QCalendarWidget,
                             QFrame,
                             QComboBox,
                             QTableWidget,
                             QHeaderView,
                             QSpinBox)
from datetime import datetime
from app.structures.work_zone import dialogs
from PyQt5.QtCore import QDate, Qt
from app.consts.views import view


class Project():
    def __init__(self, window: QMainWindow):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Проекты']
        func_tools = {
            'Создать проект': self.create,
            'Редактировать проект': self.redact,
            'Реестр проектов': self.as_list,
            'Отобразить проект': self.as_view
        }
        buttons = []
        for i in funcs:
            button = QPushButton(i)
            button.clicked.connect(lambda _, i=i: func_tools[i]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок формы
        title = QLabel("Редактор проектов")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Макет для ввода данных проекта
        form_layout = QFormLayout()

        self.name = QLineEdit()
        date_container = QHBoxLayout()
        self.start = QCalendarWidget()
        self.start.setMaximumHeight(200)
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        self.executor = QComboBox()
        date_container.addWidget(self.start)
        date_container.addWidget(self.deadline)

        form_layout.addRow("Название проекта:", self.name)
        form_layout.addRow("Начало / Дедлайн", date_container)
        form_layout.addRow("Ответственный:", self.executor)

        layout.addLayout(form_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        create_desk = QPushButton('Создать доску')
        form_layout.addWidget(create_desk)
        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название", "Опция"])
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        form_layout.addWidget(self.desks)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def redact(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок формы
        title = QLabel("Редактор проектов")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Макет для ввода данных проекта
        form_layout = QFormLayout()

        self.name = QLineEdit()
        date_container = QHBoxLayout()
        self.start = QCalendarWidget()
        self.start.setMaximumHeight(200)
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        self.executor = QComboBox()
        date_container.addWidget(self.start)
        date_container.addWidget(self.deadline)

        form_layout.addRow("Название проекта:", self.name)
        form_layout.addRow("Начало / Дедлайн", date_container)
        form_layout.addRow("Ответственный:", self.executor)

        layout.addLayout(form_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        create_desk = QPushButton('Создать доску')
        form_layout.addWidget(create_desk)
        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название", "Опция"])
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        form_layout.addWidget(self.desks)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        delete_button = QPushButton("Удалить")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(delete_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def as_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Отображение проекта")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название", "Опция"])
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.desks)

        self.window.panel.setWidget(widget)

    def as_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр проектов")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.projects = QTableWidget()
        self.projects.setColumnCount(3)
        self.projects.setColumnHidden(2, True)
        self.projects.setHorizontalHeaderLabels(["Название", "Дедлайн"])
        header = self.projects.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.projects)

        self.window.panel.setWidget(widget)

    def req_select(self):
        pass

    def req_insert(self):
        pass

    def req_update(self):
        pass


class Board():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Доски']
        func_tools = {
            'Создать доску': self.create,
            'Редактировать доску': self.redact,
            'Реестр досок': self.as_list,
            'Отображение доски': self.as_view
        }
        buttons = []
        for i in funcs:
            button = QPushButton(i)
            button.clicked.connect(lambda _, i=i: func_tools[i]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Редактор досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desk_form = QFormLayout()
        self.name_desk = QLineEdit()
        desk_form.addRow("Название доски:", self.name_desk)
        projects = QComboBox()
        desk_form.addRow("Проект: ", projects)
        layout.addLayout(desk_form)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        form_layout = QFormLayout()
        self.name_column = QLineEdit()
        self.type = QComboBox()

        form_layout.addRow("Название колонки:", self.name_column)
        form_layout.addRow("Тип колонки:", self.type)

        layout.addLayout(form_layout)

        create_column = QPushButton('Создать колонку')
        layout.addWidget(create_column)

        column_form_layout = QFormLayout()
        column_title = QLabel('Имеющиеся колонки')
        column_title.setAlignment(Qt.AlignCenter)
        column_form_layout.addWidget(column_title)
        self.columns = QTableWidget()
        self.columns.setColumnCount(4)
        self.columns.setColumnHidden(3, True)
        self.columns.setHorizontalHeaderLabels(["Название", "Тип", "Опция"])
        header = self.columns.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        column_form_layout.addWidget(self.columns)
        layout.addLayout(column_form_layout)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def redact(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Редактор досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desk_form = QFormLayout()
        self.name_desk = QLineEdit()
        desk_form.addRow("Название доски:", self.name_desk)
        projects = QComboBox()
        desk_form.addRow("Проект: ", projects)
        layout.addLayout(desk_form)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        form_layout = QFormLayout()
        self.name_column = QLineEdit()
        self.type = QComboBox()

        form_layout.addRow("Название колонки:", self.name_column)
        form_layout.addRow("Тип колонки:", self.type)

        layout.addLayout(form_layout)

        create_column = QPushButton('Создать колонку')
        layout.addWidget(create_column)

        column_form_layout = QFormLayout()
        column_title = QLabel('Имеющиеся колонки')
        column_title.setAlignment(Qt.AlignCenter)
        column_form_layout.addWidget(column_title)
        self.columns = QTableWidget()
        self.columns.setColumnCount(4)
        self.columns.setColumnHidden(3, True)
        self.columns.setHorizontalHeaderLabels(["Название", "Тип", "Опция"])
        header = self.columns.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        column_form_layout.addWidget(self.columns)
        layout.addLayout(column_form_layout)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        delete_button = QPushButton("Удалить")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(delete_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def as_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Отображение доски")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.box_layout = QHBoxLayout()
        layout.addLayout(self.box_layout)

        self.window.panel.setWidget(widget)

    def as_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название", "Проект"])
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)

        self.window.panel.setWidget(widget)


class Task():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Задачи']
        func_tools = {
            'Создать задачу': self.create,
            'Редактировать задачу': self.redact,
            'Реестр задач': self.as_list
        }
        buttons = []
        for i in funcs:
            button = QPushButton(i)
            button.clicked.connect(lambda _, i=i: func_tools[i]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Редактор задач")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.name = QLineEdit()
        self.deadline = QCalendarWidget()
        self.priority = QComboBox()
        self.diffs = QComboBox()
        input_form.addRow("Название:", self.name)
        input_form.addRow("Дедлайн", self.deadline)
        input_form.addRow("Приоритет", self.priority)
        input_form.addRow("Сложность", self.diffs)
        layout.addLayout(input_form)

        add_executor = QPushButton('Добавить исполнителя задачи')
        layout.addWidget(add_executor)

        self.executors = QTableWidget()
        self.executors.setColumnCount(4)
        self.executors.setColumnHidden(3, True)
        self.executors.setHorizontalHeaderLabels(["Имя", "UUID", "Опции"])
        header = self.executors.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.executors)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def redact(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Редактор задач")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.name = QLineEdit()
        self.deadline = QCalendarWidget()
        self.priority = QComboBox()
        self.diffs = QComboBox()
        input_form.addRow("Название:", self.name)
        input_form.addRow("Дедлайн", self.deadline)
        input_form.addRow("Приоритет", self.priority)
        input_form.addRow("Сложность", self.diffs)
        layout.addLayout(input_form)

        add_executor = QPushButton('Добавить исполнителя задачи')
        layout.addWidget(add_executor)

        self.executors = QTableWidget()
        self.executors.setColumnCount(4)
        self.executors.setColumnHidden(3, True)
        self.executors.setHorizontalHeaderLabels(["Имя", "UUID", "Опции"])
        header = self.executors.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.executors)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        delete_button = QPushButton("Удалить")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(delete_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)
        self.window.panel.setWidget(widget)

    def as_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр задач")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.tasks = QTableWidget()
        self.tasks.setColumnCount(5)
        self.tasks.setColumnHidden(4, True)
        self.tasks.setHorizontalHeaderLabels(
            ["Дедлайн", "Приоритет", "Сложность", "Тип"])
        header = self.tasks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tasks)
        self.window.panel.setWidget(widget)


class Worker():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Работники']
        func_tools = {
            'Создать работника': self.create,
            'Редактировать работника': self.redact,
            'Реестр работников': self.as_list
        }
        buttons = []
        for i in funcs:
            button = QPushButton(i)
            button.clicked.connect(lambda _, i=i: func_tools[i]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Редактор работников")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.name = QLineEdit()
        self.job = QLineEdit()
        self.age = QSpinBox()
        self.age.setRange(1, 140)
        self.exp = QTextEdit()
        self.additional = QTextEdit()
        self.contacts = QLineEdit()

        input_form.addRow("Имя:", self.name)
        input_form.addRow("Должность:", self.job)
        input_form.addRow("Возраст:", self.age)
        input_form.addRow("Опыт:", self.exp)
        input_form.addRow("Описание:", self.additional)
        input_form.addRow("Контакты:", self.contacts)

        layout.addLayout(input_form)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        delete_button = QPushButton("Удалить")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(delete_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def redact(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Редактор работников")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.name = QLineEdit()
        self.job = QLineEdit()
        self.age = QSpinBox()
        self.age.setRange(1, 140)
        self.exp = QTextEdit()
        self.additional = QTextEdit()
        self.contacts = QLineEdit()

        input_form.addRow("Имя:", self.name)
        input_form.addRow("Должность:", self.job)
        input_form.addRow("Возраст:", self.age)
        input_form.addRow("Опыт:", self.exp)
        input_form.addRow("Описание:", self.additional)
        input_form.addRow("Контакты:", self.contacts)

        layout.addLayout(input_form)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить проект")
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def as_view(self, data):
        dialog = dialogs.WorkerView(data)
        dialog.exec_()

    def as_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр работников")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.tasks = QTableWidget()
        self.tasks.setColumnCount(6)
        self.tasks.setColumnHidden(5, True)
        self.tasks.setHorizontalHeaderLabels(
            ["ФИО", "Должность", "Возраст", "UUID", "Опции"])
        header = self.tasks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tasks)
        self.window.panel.setWidget(widget)


class Report():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Отчётность']
        func_tools = {
            'Создать отчёт': self.create
        }
        buttons = []
        for i in funcs:
            button = QPushButton(i)
            button.clicked.connect(lambda _, i=i: func_tools[i]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Создание отчёта")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.type_report = QComboBox()
        date_container = QHBoxLayout()
        self.start = QCalendarWidget()
        self.start.setMaximumHeight(200)
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        date_container.addWidget(self.start)
        date_container.addWidget(self.deadline)
        self.worker = QComboBox()

        input_form.addRow('Тип отчёта:', self.type_report)
        input_form.addRow('Начало / Дедлайн', date_container)
        input_form.addRow('Работник:', self.worker)

        layout.addLayout(input_form)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        create_button = QPushButton("Создать")
        button_container.addWidget(cancel_button)
        button_container.addWidget(create_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)
