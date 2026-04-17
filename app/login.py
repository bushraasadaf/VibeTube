from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QWidget
from db import get_connection
from creator_dashboard import CreatorDashboard
from viewer_homepage import ViewerHomepage  
import pyodbc


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)
        self.showMaximized()

        # Button connections
        self.login_button.clicked.connect(self.login_user)
        self.back_button_login.clicked.connect(self.go_back)

    def login_user(self):
        email = self.email_login.text()
        password = self.pass_login.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Enter email and password")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # CHECK VIEWER LOGIN
            cursor.execute("""
                SELECT viewer_id, name FROM Viewers
                WHERE email=? AND password=?
            """, (email, password))

            viewer = cursor.fetchone()

            if viewer:
                QMessageBox.information(self, "Success", f"Welcome Viewer {viewer[1]}!")

                # OPEN VIEWER HOMEPAGE
                self.viewer_page = ViewerHomepage(viewer_id=viewer[0], viewer_name=viewer[1])
                self.viewer_page.show()
                self.close()
                return

            #creator login
            cursor.execute("""
                SELECT creator_id, name FROM Creators
                WHERE email=? AND password=?
            """, (email, password))

            creator = cursor.fetchone()

            if creator:
                QMessageBox.information(self, "Success", f"Welcome Creator {creator[1]}!")

                # OPEN CREATOR DASHBOARD
                self.dashboard = CreatorDashboard(
                    creator_id=creator[0],
                    creator_name=creator[1]
                )
                self.dashboard.show()
                self.close()
                return

            # If neither viewer nor creator matched
            QMessageBox.warning(self, "Error", "Invalid email or password!")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", str(e))

        finally:
            conn.close()

    def go_back(self):
        from role_select_window import RoleSelectWindow
        self.role_window = RoleSelectWindow()
        self.role_window.show()
        self.close()
