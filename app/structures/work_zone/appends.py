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
import datetime
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
        self.btn_list = QPushButton('Реестр проектов')
        self.btn_view = QPushButton('Отобразить проект')
        self.btn_redact.setEnabled(False)
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
        self.set_activities(False)
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
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)
        add_desk = QPushButton('Добавить доску')
        add_desk.clicked.connect(self.add_desk)

        self.desks_list = QListWidget()
        cookies = {
            web_consts.QUERYES: {
                'desks_list_proj': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        desks = res_desks[web_consts.DATA]['desks_list_proj0']
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
        new_id = self.desks_list.currentItem().data(Qt.UserRole)['id']

        # Проверяем, есть ли уже такой id в таблице desks
        found = False
        for row in range(self.desks.rowCount()):
            if self.desks.item(row, 1).text() == str(new_id):
                found = True
                break

        if found:
            dialog = dialogs.MessageError(
                'Исключение', "Этот ID уже существует в таблице.")
            dialog.exec_()
        else:
            inx = self.desks.rowCount()
            self.desks.insertRow(inx)
            self.desks.setItem(inx, 0, QTableWidgetItem(
                self.desks_list.currentItem().text()))
            self.desks.setItem(inx, 1, QTableWidgetItem(str(new_id)))
        self.desks_list.setHidden(True)
        self.desks.setHidden(False)

    def delete_desk(self):
        row = self.desks.currentRow()
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

        if self.desks.rowCount() == 0:
            dialog = dialogs.MessageError('Ошибка', 'Нет не единой доски')
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
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок формы
        title = QLabel("Редактор проектов")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Макет для ввода данных проекта
        form_layout = QFormLayout()
        cookies = {
            web_consts.QUERYES: {
                'proj_s': {web_consts.KWARGS: [f'{web_consts.JWT}company', self.proj_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        project_data = query_post(web_consts.EXECUTE, cookies)
        date_object = datetime.date.fromisoformat(
            str(project_data[web_consts.DATA]['proj_s0'][0][3]))
        start = QDate(date_object.year, date_object.month, date_object.day)
        date_object = datetime.date.fromisoformat(
            str(project_data[web_consts.DATA]['proj_s0'][0][4]))
        deadline = QDate(date_object.year, date_object.month, date_object.day)
        self.name = QLineEdit()
        self.name.setText(str(project_data[web_consts.DATA]['proj_s0'][0][1]))
        date_container = QHBoxLayout()
        self.start = QCalendarWidget()
        self.start.setMaximumHeight(200)
        self.start.setSelectedDate(start)
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        self.deadline.setSelectedDate(deadline)
        self.executor = QComboBox()
        cookies = {
            web_consts.QUERYES: {
                'worker_s': {web_consts.KWARGS: [f'{web_consts.JWT}company', self.proj_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        worker_exec_data = query_post(web_consts.EXECUTE, cookies)
        print(cookies)
        print(worker_exec_data)
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
                if user_id == worker_exec_data[web_consts.DATA]['worker_s0'][0][0]:
                    self.executor.setCurrentIndex(self.executor.count() - 1)
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
        cookies = {
            web_consts.QUERYES: {
                'proj_s_desks': {web_consts.KWARGS: [f'{web_consts.JWT}company', self.proj_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        desks = query_post(web_consts.EXECUTE, cookies)
        desks = desks[web_consts.DATA]['proj_s_desks0']
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)
        add_desk = QPushButton('Добавить доску')
        add_desk.clicked.connect(self.add_desk)
        self.desks.setRowCount(len(desks))
        for row, (desk_id, name) in enumerate(desks):
            self.desks.setItem(row, 0, QTableWidgetItem(name))
            self.desks.setItem(row, 1, QTableWidgetItem(str(desk_id)))
        self.desks_list = QListWidget()
        cookies = {
            web_consts.QUERYES: {
                'desks_list_proj': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res_desks = query_post(web_consts.EXECUTE, cookies)
        desks = res_desks[web_consts.DATA]['desks_list_proj0']
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
        cookies = {
            web_consts.QUERYES:
            {
                'worker_list_proj': {web_consts.KWARGS:
                                     [f'{web_consts.JWT}company', self.proj_id]
                                     }
            },
            web_consts.TOKEN: self.data.jwt
        }
        worker_list = query_post(web_consts.EXECUTE, cookies)[
            web_consts.DATA]['worker_list_proj0']
        for i in worker_list:
            user_id, uuid, fullname = i
            new_item = QListWidgetItem(f'Имя: {fullname} | Айди: {uuid}')
            new_item.setData(Qt.UserRole, {'id': user_id})
            self.worker_list.addItem(new_item)
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
        save_button.clicked.connect(self.save_changes)
        button_container.addWidget(delete_button)
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def delete(self):
        cookies = {
            web_consts.QUERYES: {
                'proj_d': {web_consts.KWARGS: [self.proj_id]},
                'proj_d_desks': {web_consts.KWARGS: [self.proj_id]},
                'proj_d_exec': {web_consts.KWARGS: [self.proj_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Подтверждение', 'Проект удалён')
            dialog.exec_()
        else:
            dialog = dialogs.MessageError('Ошибка', 'Проект не был удалён')
            dialog.exec_()
        self.as_list()

    def save_changes(self):
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

        if self.desks.rowCount() == 0:
            dialog = dialogs.MessageError('Ошибка', 'Нет не единой доски')
            dialog.exec_()
            return

        if not self.start.selectedDate().isValid() or not self.deadline.selectedDate().isValid():
            dialog = dialogs.MessageError(
                'Ошибка', 'Неверные даты начала или завершения проекта')
            dialog.exec_()
            return
        cookies = {
            web_consts.QUERYES: {
                'proj_d_desks': {web_consts.KWARGS: [self.proj_id]},
                'proj_d_exec': {web_consts.KWARGS: [self.proj_id]},
                'proj_u': {web_consts.KWARGS: [self.name.text(),
                                               self.executor.currentData(),
                                               self.start.selectedDate().toPyDate().isoformat(),
                                               self.deadline.selectedDate().toPyDate().isoformat(),
                                               self.proj_id]},
                'proj_i_exec': {web_consts.KWARGS: [[f'{web_consts.LASTIND}Projects', self.worker_list.item(i).data(Qt.UserRole)['id']] for i in range(self.worker_list.count())]},
                'proj_i_desk': {web_consts.KWARGS: [[f'{web_consts.LASTIND}Projects', int(i[1])] for i in get_all_items(self.desks)]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)

        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Подтверждение', 'Проект обновлён')
            dialog.exec_()
        else:
            dialog = dialogs.MessageError('Ошибка', 'Проект не обновлён')
            dialog.exec_()

    def as_view(self):
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Отображение проекта")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.desks = QTableWidget()
        self.desks.setColumnCount(3)
        self.desks.setColumnHidden(1, True)
        self.desks.setColumnHidden(2, True)
        self.desks.setHorizontalHeaderLabels(["Название"])
        cookies = {
            web_consts.QUERYES: {
                'proj_s_desks': {web_consts.KWARGS: [f'{web_consts.JWT}company', self.proj_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        desks = query_post(web_consts.EXECUTE, cookies)
        desks = desks[web_consts.DATA]['proj_s_desks0']
        self.desks.setRowCount(len(desks))
        self.desks.setEditTriggers(QTableWidget.NoEditTriggers)
        for row, (desk_id, name) in enumerate(desks):
            self.desks.setItem(row, 0, QTableWidgetItem(name))
            self.desks.setItem(row, 1, QTableWidgetItem(str(desk_id)))
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.desks.itemDoubleClicked.connect(self.chose_desk)

        layout.addWidget(self.desks)

        self.window.panel.setWidget(widget)

    def as_list(self):
        self.set_activities(False)
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
        print(res)
        projects = res[web_consts.DATA]['proj_list0']
        self.projects.setRowCount(len(projects))
        self.projects.setHorizontalHeaderLabels(["Название", "Дедлайн"])
        for row, project in enumerate(projects):
            self.projects.setItem(row, 0, QTableWidgetItem(str(project[1])))
            self.projects.setItem(row, 1, QTableWidgetItem(str(project[4])))
            self.projects.setItem(row, 2, QTableWidgetItem(str(project[0])))
        self.projects.itemSelectionChanged.connect(self.chose_project)
        header = self.projects.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.projects)

        self.window.panel.setWidget(widget)

    def chose_project(self):
        self.set_activities(True)
        row = self.projects.currentRow()
        self.clear()
        self.proj_id = int(self.projects.item(row, 2).text())

    def chose_desk(self):
        row = self.desks.currentRow()
        self.clear()
        self.desk = int(self.desks.item(row, 1).text())
        print(self.desk)

    def set_activities(self, flag):
        self.btn_redact.setEnabled(flag)
        self.btn_view.setEnabled(flag)

    def clear(self):
        self.proj_id = -1
        self.desk = -1


class Board():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Доски']
        self.btn_create = QPushButton('Создать доску')
        self.btn_redact = QPushButton('Редактировать доску')
        self.btn_list = QPushButton('Реестр досок')
        self.btn_view = QPushButton('Отображение доски')
        self.btn_redact.setEnabled(False)
        self.btn_view.setEnabled(False)
        func_tools = {
            'Создать доску': (self.create, self.btn_create),
            'Редактировать доску': (self.redact, self.btn_redact),
            'Реестр досок': (self.as_list, self.btn_list),
            'Отображение доски': (self.as_view, self.btn_view)
        }
        buttons = []
        for i in funcs:
            button = func_tools[i][1]
            button.clicked.connect(lambda _, i=i: func_tools[i][0]())
            buttons.append(button)
        self.window.add_functions(buttons)
        self.set_activities(False)

    def create(self):
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Редактор досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desk_form = QFormLayout()
        self.name_desk = QLineEdit()
        desk_form.addRow("Название доски:", self.name_desk)
        layout.addLayout(desk_form)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        form_layout = QFormLayout()
        self.name_column = QLineEdit()
        self.type = QComboBox()
        self.type.addItem("Обычная", 0)
        self.type.addItem("Завершения", 1)

        form_layout.addRow("Название колонки:", self.name_column)
        form_layout.addRow("Тип колонки:", self.type)

        layout.addLayout(form_layout)

        create_column = QPushButton('Создать колонку')
        create_column.clicked.connect(self.create_column)
        layout.addWidget(create_column)

        column_form_layout = QFormLayout()
        column_title = QLabel('Имеющиеся колонки')
        column_title.setAlignment(Qt.AlignCenter)
        column_form_layout.addWidget(column_title)
        self.columns = QTableWidget()
        self.columns.setColumnCount(3)
        self.columns.setColumnHidden(2, True)
        self.columns.setHorizontalHeaderLabels(["Название", "Тип"])
        self.columns.setEditTriggers(QTableWidget.NoEditTriggers)
        self.columns.itemDoubleClicked.connect(self.delete_column)
        header = self.columns.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        column_form_layout.addWidget(self.columns)
        layout.addLayout(column_form_layout)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить доску")
        cancel_button.clicked.connect(self.as_list)
        save_button.clicked.connect(self.save_board)
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def delete_column(self):
        row = self.columns.currentRow()
        if row >= 0:
            self.columns.removeRow(row)

    def create_column(self):
        name = self.name_column.text()
        column_type = str(self.type.currentText())
        column_type_id = str(self.type.currentData(Qt.UserRole))

        if not name:
            msg = dialogs.MessageError('Ошибка', 'Название колонки не указано')
            msg.exec_()
            return

        # Проверка наличия column_type_id со значением '1' в таблице
        for row in range(self.columns.rowCount()):
            if column_type_id == '1' and self.columns.item(row, 2).text() == '1':
                msg = dialogs.MessageError(
                    'Ошибка', 'Колонка с этим типом уже добавлена')
                msg.exec_()
                return

        row_position = self.columns.rowCount()
        self.columns.insertRow(row_position)
        self.columns.setItem(row_position, 0, QTableWidgetItem(name))
        self.columns.setItem(row_position, 1, QTableWidgetItem(column_type))
        self.columns.setItem(row_position, 2, QTableWidgetItem(column_type_id))
        self.columns.itemDoubleClicked.connect(self.delete_column)

        self.name_column.clear()
        self.type.setCurrentIndex(0)  # Сброс типа

    def delete_column(self):
        row = self.columns.currentRow()
        self.columns.removeRow(row)

    def save_board(self):

        if not self.name_desk.text():
            msg = dialogs.MessageError('Ошибка', 'Название доски не указано')
            msg.exec_()
            return

        has_admin_column = False
        for row in range(self.columns.rowCount()):
            column_type_id = self.columns.item(row, 2).text()

            if column_type_id == '1':
                has_admin_column = True  # Найдена колонка с id 1

        if not has_admin_column:
            msg = dialogs.MessageError(
                'Ошибка', 'Не добавлена колонка выполнения')
            msg.exec_()
            return

        columns_data = []
        for row in range(self.columns.rowCount()):
            column_name = self.columns.item(row, 0).text()
            column_type = self.columns.item(row, 1).text()
            column_type = 0 if column_type == 'Обычная' else 1
            columns_data.append(
                [column_name, column_type, f'{web_consts.LASTIND}Desks'])

        cookies = {
            web_consts.QUERYES: {
                'desk_i': {web_consts.KWARGS: [
                    self.name_desk.text()
                ]},
                'desk_i_comp': {web_consts.KWARGS: [f'{web_consts.JWT}company', f'{web_consts.LASTIND}Desks']},
                'desk_i_column': {web_consts.KWARGS: [columns_data]}
            },
            web_consts.TOKEN: self.data.jwt
        }

        res = query_post(web_consts.EXECUTE, cookies)

        if res[web_consts.STATUS] == web_consts.COMPLETE:
            msg = dialogs.MessageSuccess(
                'Подтверждение', 'Доска успешно создана')
            msg.exec_()
        else:
            msg = dialogs.MessageError('Ошибка', 'Не удалось создать доску')
            msg.exec_()

    def redact(self):
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        cookies = {
            web_consts.QUERYES: {
                'desk_s': {web_consts.KWARGS: [self.desk_id]},
                'desk_s_columns': {web_consts.KWARGS: [self.desk_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        desk_data = res[web_consts.DATA]['desk_s0']
        columns = res[web_consts.DATA]['desk_s_columns1']

        title = QLabel("Редактор досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desk_form = QFormLayout()
        self.name_desk = QLineEdit()
        self.name_desk.setText(desk_data[0][1])
        desk_form.addRow("Название доски:", self.name_desk)
        layout.addLayout(desk_form)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        form_layout = QFormLayout()
        self.name_column = QLineEdit()
        self.type = QComboBox()
        self.type.addItem("Обычная", 0)
        self.type.addItem("Завершения", 1)

        form_layout.addRow("Название колонки:", self.name_column)
        form_layout.addRow("Тип колонки:", self.type)

        layout.addLayout(form_layout)

        create_column = QPushButton('Создать колонку')
        create_column.clicked.connect(self.create_column)
        layout.addWidget(create_column)

        column_form_layout = QFormLayout()
        column_title = QLabel('Имеющиеся колонки')
        column_title.setAlignment(Qt.AlignCenter)
        column_form_layout.addWidget(column_title)
        self.columns = QTableWidget()
        self.columns.setColumnCount(3)
        self.columns.setColumnHidden(2, True)
        self.columns.setHorizontalHeaderLabels(["Название", "Тип"])
        self.columns.setEditTriggers(QTableWidget.NoEditTriggers)
        self.columns.setRowCount(len(columns))
        self.columns.itemDoubleClicked.connect(self.delete_column)
        print(columns)
        for row, (col_id, name, typ, desk_id) in enumerate(columns):
            print(row, name, typ)
            tp = 'Обычная' if typ == 0 else 'Завершения'
            self.columns.setItem(row, 0, QTableWidgetItem(str(name)))
            self.columns.setItem(row, 1, QTableWidgetItem(str(tp)))
            self.columns.setItem(row, 2, QTableWidgetItem(str(typ)))
        header = self.columns.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        column_form_layout.addWidget(self.columns)
        layout.addLayout(column_form_layout)

        button_container = QHBoxLayout()
        delete_button = QPushButton("Удалить")
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить доску")
        delete_button.clicked.connect(self.delete_board)
        cancel_button.clicked.connect(self.as_list)
        save_button.clicked.connect(self.redact_board)
        button_container.addWidget(delete_button)
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def redact_board(self):
        if not self.name_desk.text():
            msg = dialogs.MessageError('Ошибка', 'Название доски не указано')
            msg.exec_()
            return

        has_admin_column = False
        for row in range(self.columns.rowCount()):
            column_type_id = self.columns.item(row, 2).text()

            if column_type_id == '1':
                has_admin_column = True  # Найдена колонка с id 1

        if not has_admin_column:
            msg = dialogs.MessageError(
                'Ошибка', 'Не добавлена колонка выполнения')
            msg.exec_()
            return

        columns_data = []
        for row in range(self.columns.rowCount()):
            column_name = self.columns.item(row, 0).text()
            column_type = self.columns.item(row, 1).text()
            column_type = 0 if column_type == 'Обычная' else 1
            columns_data.append(
                (column_name, column_type, f'{web_consts.LASTIND}Desks'))
        cookies = {
            web_consts.QUERYES: {
                'desk_d': {web_consts.KWARGS: [self.desk_id]},
                'desk_d_com': {web_consts.KWARGS: [self.desk_id]},
                'desk_d_col': {web_consts.KWARGS: [self.desk_id]},
                'desk_d_proj': {web_consts.KWARGS: [self.desk_id]},
                'desk_i': {web_consts.KWARGS: [
                    self.name_desk.text()
                ]},
                'desk_i_comp': {web_consts.KWARGS: [f'{web_consts.JWT}company', f'{web_consts.LASTIND}Desks']},
                'desk_i_column': {web_consts.KWARGS: [columns_data]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Подтверждение', 'Доска измененна')
            dialog.exec_()
        else:
            dialog = dialogs.MessageError('Ошибка', 'Доска не была измененна')
            dialog.exec_()

    def delete_board(self):
        cookies = {
            web_consts.QUERYES: {
                'desk_d': {web_consts.KWARGS: [self.desk_id]},
                'desk_d_col': {web_consts.KWARGS: [self.desk_id]},
                'desk_d_proj': {web_consts.KWARGS: [self.desk_id]},
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Подтверждение', 'Доска удалёна')
            dialog.exec_()
        else:
            dialog = dialogs.MessageError('Ошибка', 'Доска не была удалёна')
            dialog.exec_()

    def as_view(self):
        self.set_activities(False)
        cookies = {
            web_consts.QUERYES: {
                'desk_s_columns': {web_consts.KWARGS: [self.desk_id]},
                'desk_s_tasks': {web_consts.KWARGS: [self.desk_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        columns = res[web_consts.DATA]['desk_s_columns0']
        tasks = res[web_consts.DATA]['desk_s_tasks1']
        board_data = {
            "name": "Отображение доски",  # Имя доски можно заменить на нужное
            "columns": [
                # предполагаем, что в колонках [id, name]
                {"id": column[0], "name": column[1], "type": column[2]}
                for column in columns
            ],
            "tasks": [
                {"id": task[0], "name": task[1], "executor": task[2],
                    "deadline": task[3], "column_id": task[4]}
                for task in tasks
            ]
        }
        print(board_data)
        widget = dialogs.BoardView(board_data, self.data.jwt)
        self.window.panel.setWidget(widget)

    def as_list(self):
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр досок")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.desks = QTableWidget()
        self.desks.setColumnCount(2)
        self.desks.setColumnHidden(1, True)
        self.desks.setHorizontalHeaderLabels(["Название", "id"])
        self.desks.setEditTriggers(QTableWidget.NoEditTriggers)
        self.desks.itemClicked.connect(self.desk_edit)
        cookies = {
            web_consts.QUERYES: {
                'desk_list': {
                    web_consts.KWARGS: [
                        f'{web_consts.JWT}company'
                    ]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        desks = query_post(web_consts.EXECUTE, cookies)[
            web_consts.DATA]['desk_list0']
        self.desks.setRowCount(len(desks))
        for row, (desk_id, name) in enumerate(desks):
            self.desks.setItem(row, 0, QTableWidgetItem(name))
            self.desks.setItem(row, 1, QTableWidgetItem(str(desk_id)))
        header = self.desks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.desks)

        self.window.panel.setWidget(widget)

    def desk_edit(self):
        row = self.desks.currentRow()
        if row != -1:
            self.desk_id = int(self.desks.item(row, 1).text())
        self.set_activities(True)

    def set_activities(self, flag):
        self.btn_redact.setEnabled(flag)
        self.btn_view.setEnabled(flag)


class Task():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Задачи']
        self.btn_create = QPushButton('Создать задачу')
        self.btn_redact = QPushButton('Редактировать задачу')
        self.btn_list = QPushButton('Реестр задач')
        self.btn_redact.setEnabled(False)
        func_tools = {
            'Создать задачу': (self.create, self.btn_create),
            'Редактировать задачу': (self.redact, self.btn_redact),
            'Реестр задач': (self.as_list, self.btn_list),
        }
        buttons = []
        for i in funcs:
            button = func_tools[i][1]
            button.clicked.connect(lambda _, i=i: func_tools[i][0]())
            buttons.append(button)
        self.window.add_functions(buttons)

    def create(self):
        self.set_activities(False)
        cookies = {
            web_consts.QUERYES: {
                'column_s': {
                    web_consts.KWARGS: [web_consts.NN]
                },
                'worker_list': {
                    web_consts.KWARGS: [f'{web_consts.JWT}company']
                }
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        executors = res[web_consts.DATA]['worker_list1']
        executors = [[i[0], f'{i[2]} | {i[1]}'] for i in executors]
        boards = res[web_consts.DATA]['column_s0']
        widget = dialogs.CreateTaskForm(executors, boards, self.data.jwt)
        self.window.panel.setWidget(widget)

    def redact(self):
        self.set_activities(False)
        cookies = {
            web_consts.QUERYES: {
                'task_s': {web_consts.KWARGS: [
                    self.task_id
                ]},
                'column_s': {
                    web_consts.KWARGS: [web_consts.NN]
                },
                'worker_list': {
                    web_consts.KWARGS: [f'{web_consts.JWT}company']
                }
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        task_data = res[web_consts.DATA]['task_s0'][0]
        executors = res[web_consts.DATA]['worker_list2']
        executors = [[i[0], f'{i[2]} | {i[1]}'] for i in executors]
        boards = res[web_consts.DATA]['column_s1']
        widget = dialogs.EditTaskForm(
            task_data, executors, boards, self.data.jwt)
        self.window.panel.setWidget(widget)

    def as_list(self):
        self.set_activities(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр задач")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.tasks = QTableWidget()
        self.tasks.setColumnCount(6)
        self.tasks.setColumnHidden(5, True)
        self.tasks.setHorizontalHeaderLabels(
            ["Дедлайн", "Приоритет", "Сложность", "Имя", "Исполнитель"])

        cookies = {
            web_consts.QUERYES: {
                'task_list': {
                    web_consts.KWARGS: [f'{web_consts.JWT}company']
                }
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        tasks = res[web_consts.DATA]['task_list0']

        self.tasks.setRowCount(len(tasks))
        print(tasks)
        for row, (task_id, name, deadline, priority, storypoints, typei, executed, executor, f, g, m, r) in enumerate(tasks):
            self.tasks.setItem(row, 0, QTableWidgetItem(str(deadline)))
            self.tasks.setItem(row, 1, QTableWidgetItem(str(priority)))
            self.tasks.setItem(row, 2, QTableWidgetItem(str(storypoints)))
            self.tasks.setItem(row, 3, QTableWidgetItem(str(name)))
            self.tasks.setItem(row, 4, QTableWidgetItem(str(executor)))
            self.tasks.setItem(row, 5, QTableWidgetItem(str(task_id)))
        self.tasks.itemClicked.connect(self.set_data)
        self.tasks.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.tasks.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tasks)
        self.window.panel.setWidget(widget)

    def set_data(self):
        self.set_activities(True)
        self.task_id = int(self.tasks.item(self.tasks.currentRow(), 5).text())

    def set_activities(self, flag):
        self.btn_redact.setEnabled(flag)


class Worker():
    def __init__(self, window):
        self.data = window.data
        self.window = window
        funcs = view[self.data.premission]['Работники']
        self.btn_create = QPushButton('Создать работника')
        self.btn_list = QPushButton('Реестр работников')
        func_tools = {
            'Создать работника': (self.create, self.btn_create),
            'Реестр работников': (self.as_list, self.btn_list),
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
        title = QLabel("Редактор работников")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        input_form = QFormLayout()

        self.name = QLineEdit()
        self.age = QSpinBox()
        self.age.setRange(1, 140)
        self.exp = QTextEdit()
        self.additional = QTextEdit()
        self.contacts = QLineEdit()
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.per = QComboBox()
        self.per.addItem('Работник', 0)
        self.per.addItem('Админ', 1)

        input_form.addRow("Имя:", self.name)
        input_form.addRow("Возраст:", self.age)
        input_form.addRow("Опыт:", self.exp)
        input_form.addRow("Описание:", self.additional)
        input_form.addRow("Контакты:", self.contacts)
        input_form.addRow("Тип:", self.per)
        input_form.addRow("Логин:", self.login)
        input_form.addRow("Пароль:", self.password)

        layout.addLayout(input_form)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить работника")
        save_button.clicked.connect(self.save_worker)
        button_container.addWidget(cancel_button)
        button_container.addWidget(save_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def save_worker(self):
        errors = []

        if not self.login.text():
            errors.append("Напишите логин")
        if not self.password.text():
            errors.append("Напишите пароль")
        if not self.name.text():
            errors.append("Напишите имя")
        if not self.contacts.text():
            errors.append("Укажите контактные данные")
        if not self.exp.toPlainText():
            errors.append("Заполните опыт")
        if not self.additional.toPlainText():
            errors.append("Добавьте дополнительную информацию")
        if self.age.value() <= 0:
            errors.append("Возраст должен быть больше 0")

        if errors:
            dialog = dialogs.MessageError('Ошибка', "\n".join(errors))
            dialog.exec_()
            return

        cookies = {
            web_consts.TOKEN: self.data.jwt,
            'per': str(self.per.currentData(Qt.UserRole)),
            'login': self.login.text(),
            'password': self.password.text(),
            'age': str(self.age.value()),
            'exp': self.exp.toPlainText(),
            'add': self.additional.toPlainText(),
            'con': self.contacts.text(),
            'name': self.name.text()
        }
        print(cookies)
        res = query_post(web_consts.REGW, cookies)
        if res[web_consts.STATUS] == web_consts.COMPLETE:
            dialog = dialogs.MessageSuccess('Успех', 'Работник создан')
        else:
            dialog = dialogs.MessageError('Ошибка', 'Работник не создан')
        dialog.exec_()

    def as_view(self):
        if self.data.premission == 'w':
            return
        cookies = {
            web_consts.QUERYES: {
                'worker_s_new': {web_consts.KWARGS: [f'{web_consts.JWT}company', self.worker_id]}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        user = res[web_consts.DATA]['worker_s_new0']
        dialog = dialogs.WorkerView(user, self.data.jwt)
        dialog.exec_()

    def as_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Реестр работников")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        cookies = {
            web_consts.QUERYES: {
                'worker_list_new': {web_consts.KWARGS: [f'{web_consts.JWT}company']}
            },
            web_consts.TOKEN: self.data.jwt
        }
        res = query_post(web_consts.EXECUTE, cookies)
        workers = res[web_consts.DATA]['worker_list_new0']
        self.workers = QTableWidget()
        self.workers.setColumnCount(4)
        self.workers.setColumnHidden(3, True)
        self.workers.setHorizontalHeaderLabels(
            ["ФИО", "Возраст", "UUID"])
        self.workers.setRowCount(len(workers))
        self.workers.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.workers.itemClicked.connect(self.set_data)
        for row, (user_id, fullname, age, uuid) in enumerate(workers):
            self.workers.setItem(row, 0, QTableWidgetItem(str(fullname)))
            self.workers.setItem(row, 1, QTableWidgetItem(str(age)))
            self.workers.setItem(row, 2, QTableWidgetItem(str(uuid)))
            self.workers.setItem(row, 3, QTableWidgetItem(str(user_id)))
        header = self.workers.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.workers)
        self.window.panel.setWidget(widget)

    def set_data(self):
        self.worker_id = int(self.workers.item(
            self.workers.currentRow(), 3).text())
        self.as_view()


def format_query_result(query_result, query_type):
    try:
        if query_type == "unfinished_tasks":
            return f"Количество незавершенных задач: {query_result[0][0]}"

        elif query_type == "avg_exec_time":
            return f"Среднее время выполнения задач: {query_result[0][0]} часа"

        elif query_type == "total_hours":
            return f"Общее время работы над задачами: {query_result[0][0]} часов"

        elif query_type == "avg_complex":
            return f"Средняя сложность задач: {query_result[0][0]} балла"

        elif query_type == "completed_tasks":
            print(query_result)
            return f"Количество завершенных задач: {query_result[0][0]}"

        elif query_type == "unfinished_tasks_per_executor":
            result_text = "Количество незавершенных задач по каждому исполнителю:\n"
            for row in query_result:
                executor, count = row
                result_text += f"Исполнитель {executor}: {count} задач(и)\n"
            return result_text

        elif query_type == "avg_exec_time_per_executor":
            result_text = "Среднее время выполнения задач по каждому исполнителю:\n"
            for row in query_result:
                executor, avg_time = row
                result_text += f"Исполнитель {executor}: {avg_time} часов\n"
            return result_text

        elif query_type == "total_hours_per_executor":
            result_text = "Общее время работы по каждому исполнителю:\n"
            for row in query_result:
                executor, total_hours = row
                result_text += f"Исполнитель {executor}: {total_hours} часов\n"
            return result_text

        elif query_type == "avg_complex_per_executor":
            result_text = "Средняя сложность задач по каждому исполнителю:\n"
            for row in query_result:
                executor, avg_complex = row
                result_text += f"Исполнитель {executor}: {avg_complex} балла\n"
            return result_text

        elif query_type == "completed_tasks_per_executor":
            result_text = "Количество завершенных задач по каждому исполнителю:\n"
            for row in query_result:
                executor, count = row
                result_text += f"Исполнитель {executor}: {count} задач(и)\n"
            return result_text

    except:
        dialog = dialogs.MessageError('Ошибка', 'Недостаточно данных')
        dialog.exec_()


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
        self.type_report.addItem(
            "Количество незавершенных задач", "unfinished_tasks")
        self.type_report.addItem(
            "Среднее время выполнения задач", "avg_exec_time")
        self.type_report.addItem(
            "Общее время работы над задачами", "total_hours")
        self.type_report.addItem("Средняя сложность задач", "avg_complex")
        self.type_report.addItem("Завершенные задачи", "completed_tasks")
        self.type_report.addItem(
            "Количество незавершенных задач по исполнителю", "unfinished_tasks_per_executor")
        self.type_report.addItem(
            "Среднее время выполнения задач по исполнителю", "avg_exec_time_per_executor")
        self.type_report.addItem(
            "Общее время работы по исполнителю", "total_hours_per_executor")
        self.type_report.addItem(
            "Средняя сложность по исполнителю", "avg_complex_per_executor")
        self.type_report.addItem(
            "Завершенные задачи по исполнителю", "completed_tasks_per_executor")

        date_container = QHBoxLayout()
        self.start = QCalendarWidget()
        self.start.setMaximumHeight(200)
        self.deadline = QCalendarWidget()
        self.deadline.setMaximumHeight(200)
        date_container.addWidget(self.start)
        date_container.addWidget(self.deadline)

        input_form.addRow('Тип отчёта:', self.type_report)
        input_form.addRow('Начало / Дедлайн', date_container)

        layout.addLayout(input_form)

        button_container = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        create_button = QPushButton("Создать")
        create_button.clicked.connect(self.generate_report)
        button_container.addWidget(cancel_button)
        button_container.addWidget(create_button)
        layout.addLayout(button_container)

        self.window.panel.setWidget(widget)

    def generate_report(self):
        # Получаем выбранный тип отчета
        report_type = self.type_report.currentText()
        rep = self.type_report.currentData(Qt.UserRole)

        # Получаем выбранные даты
        start_date = self.start.selectedDate().toString('yyyy-MM-dd')
        deadline_date = self.deadline.selectedDate().toString('yyyy-MM-dd')

        cookies = {
            web_consts.QUERYES: {
                rep: {web_consts.KWARGS: [
                    f'{web_consts.JWT}company', start_date, deadline_date]}
            },
            web_consts.TOKEN: self.data.jwt
        }

        # Соответствие типов отчета с параметрами для format_query_result
        query_types = {
            "Количество незавершенных задач": "unfinished_tasks",
            "Среднее время выполнения задач": "avg_exec_time",
            "Общее время работы над задачами": "total_hours",
            "Средняя сложность задач": "avg_complex",
            "Завершенные задачи": "completed_tasks",
            "Количество незавершенных задач по исполнителю": "unfinished_tasks_per_executor",
            "Среднее время выполнения задач по исполнителю": "avg_exec_time_per_executor",
            "Общее время работы по исполнителю": "total_hours_per_executor",
            "Средняя сложность по исполнителю": "avg_complex_per_executor",
            "Завершенные задачи по исполнителю": "completed_tasks_per_executor"
        }

        if report_type in query_types:
            query_result = query_post(web_consts.EXECUTE, cookies)[
                web_consts.DATA][f'{rep}0']
            formatted_report = format_query_result(
                query_result, query_types[report_type])
            self.show_report(formatted_report)

    def show_report(self, report_text):
        # Например, выводим отчет в отдельном виджете
        report_window = QWidget()
        report_layout = QVBoxLayout(report_window)
        report_label = QLabel(report_text)
        report_layout.addWidget(report_label)
        self.window.panel.setWidget(report_window)
