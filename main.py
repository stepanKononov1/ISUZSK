from app.structures.main.dialogs import AuthorizationDialog
from PyQt5.QtWidgets import QApplication
from app.structures.main.work_zone import MainWindow
import sys

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    dialog = AuthorizationDialog(window)
    dialog.exec()
    sys.exit(app.exec())
