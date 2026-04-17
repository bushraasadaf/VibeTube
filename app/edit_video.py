from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from db import get_connection

class EditVideoForm(QWidget):
    def __init__(self, video_id, creator_id, parent_dashboard):
        super().__init__()
        uic.loadUi("edit_video.ui", self)
        self.showMaximized()

        self.video_id = video_id
        self.creator_id = creator_id
        self.parent_dashboard = parent_dashboard

       #button connectiosn
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_cancel.clicked.connect(self.close)

        self.load_video_data() # Load existing video data into the form (pre filled form is opened with old data)

    def load_video_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT V.title, V.description, G.genre_name
            FROM Videos V
            JOIN Genres G ON V.genre_id = G.genre_id
            WHERE V.video_id = ?
        """, (self.video_id,))
        data = cursor.fetchone()
        conn.close()

        if data: #filling the title, description, and genre fields with old data
            self.input_title.setText(data[0])
            self.input_description.setPlainText(data[1])

            # Set dropdown to the correct genre (bec when the edit video form is loaded, it starts from genre 0)
            index = self.dropdown_genre.findText(data[2])
            if index >= 0:
                self.dropdown_genre.setCurrentIndex(index)

    def save_changes(self):
        title = self.input_title.text().strip()
        description = self.input_description.toPlainText().strip()
        genre_name = self.dropdown_genre.currentText()

        if not title:
            QMessageBox.warning(self, "Missing Data", "Title cannot be empty.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        # Get genre_id (bec for updating videos query, we need genre_id not genre_name)
        cursor.execute("SELECT genre_id FROM Genres WHERE genre_name = ?", (genre_name,))
        genre_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE Videos
            SET title = ?, description = ?, genre_id = ?
            WHERE video_id = ?
            AND channel_id = (SELECT channel_id FROM Channels WHERE creator_id = ?)
        """, (title, description, genre_id, self.video_id, self.creator_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Video updated successfully!")
        
        #refresh dashboard
        self.parent_dashboard.load_videos()
        self.close()
