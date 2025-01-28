from PyQt5.QtWidgets import (
    QMainWindow, QScrollArea, QGridLayout, QWidget, QApplication,
    QVBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from app.consts.views import view
from app.structures.work_zone.appends import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.main()

    def main(self):
        self.setWindowTitle("Система")
        self.setMinimumSize(1400, 768)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(25, 25, 25, 25)
        central_widget.setLayout(grid_layout)

        vertical_scroll_area = QScrollArea()
        vertical_scroll_area.setWidgetResizable(True)
        vertical_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        vertical_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

        container1 = QWidget()
        self.options = QVBoxLayout()
        self.options.setSpacing(10)
        self.options.setContentsMargins(25, 25, 25, 25)
        self.options.setAlignment(Qt.AlignTop)
        container1.setLayout(self.options)
        vertical_scroll_area.setWidget(container1)

        horizontal_scroll_area = QScrollArea()
        horizontal_scroll_area.setWidgetResizable(True)
        horizontal_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        horizontal_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded)

        container2 = QWidget()
        self.functions = QHBoxLayout(container2)
        self.functions.setSpacing(10)
        self.functions.setContentsMargins(10, 10, 10, 10)
        container2.setLayout(self.functions)
        horizontal_scroll_area.setWidget(container2)

        self.functions.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        horizontal_scroll_area.setWidget(container2)

        self.panel = QScrollArea()
        self.panel.setWidgetResizable(True)
        self.panel.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.panel.setContentsMargins(0, 0, 0, 0)
        self.panel_wg = QWidget()
        self.panel.setWidget(self.panel_wg)

        grid_layout.addWidget(vertical_scroll_area, 0, 0, 6, 2)
        grid_layout.addWidget(horizontal_scroll_area, 0, 2, 1, 5)
        grid_layout.addWidget(self.panel, 1, 2, 6, 5)

        grid_layout.setRowStretch(1, 5)
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(2, 5)

    def show(self, data=None):
        if data is not None:
            self.update_data(data)
        super().show()

    def add_functions(self, lst):
        clear_layout(self.functions)
        for i in lst:
            i.setMinimumHeight(40)
            self.functions.addWidget(i)

    def update_data(self, data):
        self.data = data
        self.view = view[data.premission]
        foos = {
            'Проекты': Project,
            'Доски': Board,
            'Задачи': Task,
            'Работники': Worker,
            'Отчётность': Report
        }
        for i in list(self.view.keys()):
            button = QPushButton(i)
            button.setMinimumHeight(60)
            button.clicked.connect(lambda _, i=i: foos[i](self))
            self.options.addWidget(button)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            sub_layout = item.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
