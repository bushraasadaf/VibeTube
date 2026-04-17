from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
from db import get_connection
from role_select_window import RoleSelectWindow
import pyodbc
class RegisterPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('register_page.ui', self)
        self.showMaximized()
        self.registerBtn.clicked.connect(self.register_user)

    def register_user(self):
        name = self.usernameInput.text()
        email = self.email_line.text()
        password = self.passwordInput.text()
        role = self.roleSelect.currentText()

        if not name or not email or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        success = False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check if email already exists in either table
            cursor.execute("SELECT email FROM Viewers WHERE email = ?", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Registration Error", "This email is already registered as a Viewer!")
                return

            cursor.execute("SELECT email FROM Creators WHERE email = ?", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Registration Error", "This email is already registered as a Creator!")
                return

            #insert into viewer table
            if role == 'Viewer':
                sql_insert_viewer = "INSERT INTO Viewers (name, email, password) VALUES (?, ?, ?)"
                cursor.execute(sql_insert_viewer, (name, email, password))
                conn.commit()
                success = True
            #insert into creator table
            elif role == 'Creator':
                # Insert Creator and get creator_id
                cursor.execute("""
                    INSERT INTO Creators (name, email, password)
                    OUTPUT INSERTED.creator_id  --get the creator_id just inserted(needed for channel creation)
                    VALUES (?, ?, ?)
                """, (name, email, password))
                creator_id = cursor.fetchone()[0] #store the id of creator (needed for channel creation below)

                # Insert corresponding Channel
                channel_name = f"{name}'s Channel"
                cursor.execute("INSERT INTO Channels (creator_id, channel_name) VALUES (?, ?)",
                               (creator_id, channel_name))
                conn.commit()
                success = True
            #upon registration, show a box telling it was a success
            if success:
                QMessageBox.information(self, "Registration Success", f"{role} account created for {name}!")
                self.role_select_window = RoleSelectWindow()
                self.role_select_window.show()
                self.close()
        #to deal with identical emails:
        except pyodbc.Error as e:
                if 'UNIQUE' in str(e):
                    QMessageBox.warning(self, "Registration Error", "This email is already registered!")
                else:
                   QMessageBox.warning(self, "Database Error", f"Error: {e}")
        finally:
            if conn:
                conn.close()

