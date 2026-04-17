import sys
from PyQt6.QtWidgets import QApplication
from role_select_window import RoleSelectWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoleSelectWindow()
    window.show()
    sys.exit(app.exec())




