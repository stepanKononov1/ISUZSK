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
                             QSpinBox,
                             QScrollArea,
                             QListWidget,
                             QListWidgetItem,
                             QTableWidgetItem)
from datetime import datetime
from app.structures.work_zone import dialogs
from PyQt5.QtCore import QDate, Qt, QTimer
from app.consts.views import view
from app.consts import web as web_consts
from app.web.request import query_post


def get_all_items(table_widget):
    items = []
    for row in range(table_widget.rowCount()):
        row_items = []
        for col in range(table_widget.columnCount()):
            item = table_widget.item(row, col)
            if item is not None:
                row_items.append(item.text())
            else:
                row_items.append(None)  # Если ячейка пустая
        items.append(row_items)
    return items


class Project():
    def __init__(self, window: QMainWindow):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Проекты']
        self.btn_create = QPushButton('Создать проект')
        self.btn_redact = QPushButton('Редактировать проект')
        self.btn_redact.setEnabled(False)
        self.btn_list = QPushButton('Реестр проектов')
        self.btn_view = QPushButton('Отобразить проект')
        self.btn_view.setEnabled(False)
        func_tools = {
            'Создать проект': (self.create, self.btn_create),
            'Редактировать проект': (self.redact, self.btn_redact),
            'Реестр проектов': (self.as_list, self.btn_list),
            'Отобразить проект': (self.as_view, self.btn_view)
        }
        buttons = []
        for i in funcs:
            button = func_tools[i][1]
            button.clicked.connect(lambda _, i=i: func_tools[i][0]())
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
        self.start.setMinimumDate(QDate.currentDate())
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        self.deadline.setMinimumDate(QDate.currentDate().addDays(1))
        self.executor = QComboBox()
        cookies = {
            web_consts.QUERYES: {
                'worker_list': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        status = res[web_consts.STATUS]
        if status == web_consts.FAILURE:
            msg = dialogs.MessageError(
                'Ошибка', 'Сотрудники не были полученны')
            msg.exec_()
        else:
            users = res[web_consts.DATA]['worker_list0']
            for i in users:
                user_id, uuid, fullname = i
                data = f'Имя: {fullname} | Айди: {uuid}'
                self.executor.addItem(data, user_id)
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

        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(1, True)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название"])
        self.desks.setEditTriggers(QTableWidget.NoEditTriggers)
        self.desks.doubleClicked.connect(self.delete_desk)
        self.desks.setRowCount(2)
        cookies = {
            web_consts.QUERYES: {
                'desk_i': {web_consts.KWARGS: ['В ожидании', 0]},
                'lastrow': {web_consts.KWARGS: [f'Desks']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        self.desks.setItem(0, 0, QTableWidgetItem('В ожидании'))
        self.desks.setItem(0, 1, QTableWidgetItem(
            str(res_desks[web_consts.DATA]['lastrow1'][0][0])))
        self.desks.setItem(0, 2, QTableWidgetItem('0'))
        cookies = {
            web_consts.QUERYES: {
                'desk_i': {web_consts.KWARGS: ['Завершена', 0]},
                'lastrow': {web_consts.KWARGS: [f'Desks']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        self.desks.setItem(1, 0, QTableWidgetItem('Завершена'))
        self.desks.setItem(1, 1, QTableWidgetItem(
            str(res_desks[web_consts.DATA]['lastrow1'][0][0])))
        self.desks.setItem(1, 2, QTableWidgetItem('1'))
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)
        add_desk = QPushButton('Добавить доску')
        add_desk.clicked.connect(self.add_desk)

        self.desks_list = QListWidget()
        cookies = {
            web_consts.QUERYES: {
                'desk_list': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        desks = res_desks[web_consts.DATA]['desk_list0']
        for i in desks:
            desk_id, desk_name = i
            item = QListWidgetItem(f'Доска: {desk_name}')
            item.setData(Qt.UserRole, {'id': desk_id})
            self.desks_list.addItem(item)

        self.desks_list.itemDoubleClicked.connect(self.commit_desk)
        self.desks_list.setHidden(True)
        layout.addWidget(self.desks_list)

        layout.addWidget(add_desk)

        self.workers = QListWidget()
        workers = res[web_consts.DATA]['worker_list0']
        for i in workers:
            user_id, uuid, fullname = i
            item = QListWidgetItem(f'Имя: {fullname} | Айди: {uuid}')
            item.setData(Qt.UserRole, {'id': user_id})
            self.workers.addItem(item)
        self.workers.itemDoubleClicked.connect(self.commit_worker)
        self.workers.setHidden(True)
        layout.addWidget(self.workers)

        self.worker_area = QScrollArea()
        self.worker_area.setWidgetResizable(True)
        self.worker_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.worker_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.worker_area.setContentsMargins(0, 0, 0, 0)

        worker_form = QFormLayout()
        self.worker_list = QListWidget()
        self.worker_list.itemDoubleClicked.connect(self.delete_worker)
        worker_form.addWidget(self.worker_list)
        self.worker_area.setLayout(worker_form)

        layout.addWidget(self.worker_area)

        add_worker = QPushButton('Добавить работника')
        add_worker.clicked.connect(self.add_worker)
        layout.addWidget(add_worker)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.as_list)
        save_button = QPushButton("Сохранить проект")
        save_button.clicked.connect(self.save)
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def add_desk(self):
        self.desks_list.setHidden(False)
        self.desks.setHidden(True)

    def commit_desk(self):
        inx = self.desks.rowCount() - 1
        self.desks.insertRow(inx)
        self.desks.setItem(inx, 0, QTableWidgetItem(
            self.desks_list.currentItem().text()))
        self.desks.setItem(inx, 1, QTableWidgetItem(
            self.desks_list.currentItem().data(Qt.UserRole)['id']))
        self.desks_list.setHidden(True)
        self.desks.setHidden(False)

    def delete_desk(self):
        row = self.desks.currentRow()
        cnt = self.desks.rowCount()
        if not row in (cnt - 1, -1, 0):
            self.desks.removeRow(row)

    def add_worker(self):
        self.worker_area.setHidden(True)
        self.workers.setHidden(False)

    def commit_worker(self):
        add_item = self.workers.currentItem()
        ids = []
        for i in range(self.worker_list.count()):
            item = self.worker_list.item(i)
            item_id = item.data(Qt.UserRole)
            ids.append(item_id)
        if add_item.data(Qt.UserRole) not in ids:
            new_item = QListWidgetItem(add_item.text())
            new_item.setData(Qt.UserRole, add_item.data(Qt.UserRole))
            self.worker_list.addItem(new_item)
        self.worker_area.setHidden(False)
        self.workers.setHidden(True)

    def delete_worker(self):
        row = self.worker_list.currentRow()
        self.worker_list.takeItem(row)

    def save(self):
        # Проверяем наличие всех данных
        if not self.name.text():
            dialog = dialogs.MessageError(
                'Ошибка', 'Название проекта не указано')
            dialog.exec_()
            return

        if not self.executor.currentData():
            dialog = dialogs.MessageError('Ошибка', 'Исполнитель не выбран')
            dialog.exec_()
            return

        if not self.start.selectedDate().isValid() or not self.deadline.selectedDate().isValid():
            dialog = dialogs.MessageError(
                'Ошибка', 'Неверные даты начала или завершения проекта')
            dialog.exec_()
            return

        if self.worker_list.count() == 0:
            dialog = dialogs.MessageError('Ошибка', 'Не выбраны исполнители')
            dialog.exec_()
            return

        if not any(self.desks.rowCount() > 0 for i in range(self.desks.rowCount())):
            dialog = dialogs.MessageError(
                'Ошибка', 'Не добавлены рабочие места для проекта')
            dialog.exec_()
            return

        # Если все данные есть, выполняем запрос
        cookies = {
            web_consts.QUERYES: {
                'proj_i': {web_consts.KWARGS: [
                    self.name.text(),
                    self.executor.currentData(),
                    self.start.selectedDate().toPyDate().isoformat(),
                    self.deadline.selectedDate().toPyDate().isoformat(),
                ]},
                'proj_i_comp': {web_consts.KWARGS: [f'{web_consts.JWT}company', f'{web_consts.LASTIND}Projects']},
                'proj_i_exec': {web_consts.KWARGS: [[f'{web_consts.LASTIND}Projects', self.worker_list.item(i).data(Qt.UserRole)['id']] for i in range(self.worker_list.count())]},
                'proj_i_desk': {web_consts.KWARGS: [[f'{web_consts.LASTIND}Projects', int(i[1])] for i in get_all_items(self.desks)]}
            },
            web_consts.TOKEN: self.data.jwt
        }

        res = query_post(web_consts.EXECUTE, cookies)

        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Подтверждение', 'Проект создан')
            dialog.exec_()
        else:
            dialog = dialogs.MessageError('Ошибка', 'Проект не создан')
            dialog.exec_()

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
        self.start.setMinimumDate(QDate.currentDate())
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        self.deadline.setMinimumDate(QDate.currentDate().addDays(1))
        self.executor = QComboBox()
        cookies = {
            web_consts.QUERYES: {
                'worker_list': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        status = res[web_consts.STATUS]
        if status == web_consts.FAILURE:
            msg = dialogs.MessageError(
                'Ошибка', 'Сотрудники не были полученны')
            msg.exec_()
        else:
            users = res[web_consts.DATA]['worker_list0']
            for i in users:
                user_id, uuid, fullname = i
                data = f'Имя: {fullname} | Айди: {uuid}'
                self.executor.addItem(data, user_id)
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

        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(1, True)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название"])
        self.desks.setEditTriggers(QTableWidget.NoEditTriggers)
        self.desks.doubleClicked.connect(self.delete_desk)
        self.desks.setRowCount(2)
        cookies = {
            web_consts.QUERYES: {
                'desk_i': {web_consts.KWARGS: ['В ожидании', 0]},
                'lastrow': {web_consts.KWARGS: [f'Desks']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        self.desks.setItem(0, 0, QTableWidgetItem('В ожидании'))
        self.desks.setItem(0, 1, QTableWidgetItem(
            str(res_desks[web_consts.DATA]['lastrow1'][0][0])))
        self.desks.setItem(0, 2, QTableWidgetItem('0'))
        cookies = {
            web_consts.QUERYES: {
                'desk_i': {web_consts.KWARGS: ['Завершена', 0]},
                'lastrow': {web_consts.KWARGS: [f'Desks']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        self.desks.setItem(1, 0, QTableWidgetItem('Завершена'))
        self.desks.setItem(1, 1, QTableWidgetItem(
            str(res_desks[web_consts.DATA]['lastrow1'][0][0])))
        self.desks.setItem(1, 2, QTableWidgetItem('1'))
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)
        add_desk = QPushButton('Добавить доску')
        add_desk.clicked.connect(self.add_desk)

        self.desks_list = QListWidget()
        cookies = {
            web_consts.QUERYES: {
                'desk_list': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        desks = res_desks[web_consts.DATA]['desk_list0']
        for i in desks:
            desk_id, desk_name = i
            item = QListWidgetItem(f'Доска: {desk_name}')
            item.setData(Qt.UserRole, {'id': desk_id})
            self.desks_list.addItem(item)

        self.desks_list.itemDoubleClicked.connect(self.commit_desk)
        self.desks_list.setHidden(True)
        layout.addWidget(self.desks_list)

        layout.addWidget(add_desk)

        self.workers = QListWidget()
        workers = res[web_consts.DATA]['worker_list0']
        for i in workers:
            user_id, uuid, fullname = i
            item = QListWidgetItem(f'Имя: {fullname} | Айди: {uuid}')
            item.setData(Qt.UserRole, {'id': user_id})
            self.workers.addItem(item)
        self.workers.itemDoubleClicked.connect(self.commit_worker)
        self.workers.setHidden(True)
        layout.addWidget(self.workers)

        self.worker_area = QScrollArea()
        self.worker_area.setWidgetResizable(True)
        self.worker_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.worker_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.worker_area.setContentsMargins(0, 0, 0, 0)

        worker_form = QFormLayout()
        self.worker_list = QListWidget()
        self.worker_list.itemDoubleClicked.connect(self.delete_worker)
        worker_form.addWidget(self.worker_list)
        self.worker_area.setLayout(worker_form)

        layout.addWidget(self.worker_area)

        add_worker = QPushButton('Добавить работника')
        add_worker.clicked.connect(self.add_worker)
        layout.addWidget(add_worker)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.as_list)
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete)
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save)
        button_container.addWidget(cancel_button)
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
        self.projects.setEditTriggers(QTableWidget.NoEditTriggers)
        cookies = {
            web_consts.QUERYES: {
                'proj_list': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        projects = res[web_consts.DATA]['proj_list0']
        self.projects.setRowCount(len(projects))
        self.projects.setHorizontalHeaderLabels(["Название", "Дедлайн"])
        for row, project in enumerate(projects):
            self.projects.setItem(row, 0, QTableWidgetItem(project[1]))
            self.projects.setItem(row, 1, QTableWidgetItem(project[4]))
            self.projects.setItem(row, 2, QTableWidgetItem(project[0]))
        header = self.projects.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.projects)

        self.window.panel.setWidget(widget)


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
