from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from db import get_connection
from PyQt6.QtCore import QDate

class UploadVideoForm(QWidget):
    def __init__(self, creator_id, channel_id, parent_dashboard):
        super().__init__()
        uic.loadUi("upload_video.ui", self)
        self.showMaximized()

        self.creator_id = creator_id
        self.channel_id = channel_id
        self.parent_dashboard = parent_dashboard
        #set the upload date to current date:
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit.setCalendarPopup(True)
        #submit button connection
        self.btn_submit.clicked.connect(self.submit_video)
        self.pushButton.clicked.connect(self.go_back)

    def submit_video(self):
        title = self.input_title.text()
        description = self.input_description.toPlainText()
        genre_name = self.dropdown_category.currentText()
        upload_date = self.dateEdit.date().toString("yyyy-MM-dd")

        if not title.strip():
            QMessageBox.warning(self, "Missing Title", "Please enter a video title.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Convert genre name to genre_id
            cursor.execute("SELECT genre_id FROM Genres WHERE genre_name = ?", (genre_name,))
            genre_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO Videos (channel_id, genre_id, title, description, upload_date, views, likes_count, comments_count)
                VALUES (?, ?, ?, ?, ?, 0, 0, 0)
            """, (self.channel_id, genre_id, title, description, upload_date))

            conn.commit()
            QMessageBox.information(self, "Success", "Video uploaded successfully!")
            self.parent_dashboard.load_videos()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        finally:
            conn.close()

    def go_back(self):
        self.close()
