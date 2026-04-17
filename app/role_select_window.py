from PyQt6 import QtWidgets, uic

class RoleSelectWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        #default screen:
        uic.loadUi("role_select.ui", self) 
        self.showMaximized()
        # Connect buttons
        self.loginviewer_btn.clicked.connect(self.open_login)
        self.logincreator_btn.clicked.connect(self.open_login)
        self.regiser.clicked.connect(self.open_register)
    #for viewer/creator login:
    def open_login(self):
        from login import LoginPage
        self.login_page = LoginPage()
        self.login_page.show()
        self.close()
    #for registration:
    def open_register(self):
        from register import RegisterPage
        self.register_page = RegisterPage()
        self.register_page.show()
        self.close()