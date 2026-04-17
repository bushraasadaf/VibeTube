from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QWidget
from db import get_connection
from role_select_window import RoleSelectWindow
from upload_video import UploadVideoForm
import pyodbc
from edit_video import EditVideoForm
#creator functional requirement
class CreatorDashboard(QWidget):
    def __init__(self, creator_id, creator_name):
        super().__init__()
        uic.loadUi("creator_dashboard.ui", self)
        self.showMaximized()
        self.creator_id = creator_id
        self.creator_name = creator_name

        # to make selected row highglghted/ bold
        self.table_videos.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #FF9AA2;
                color: white;
                font-weight: bold;
            }
        """)
        #SelectRows means clicking any cell in a row will 
        # select the entire row, not just the individual cell.
        # QAbstractItemView is an abstract base class in Qt for item views like QTableView or QTableWidget.
        self.table_videos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        
        #This tells the table how many selections are allowed at a time.
        # SingleSelection means only one row can be selected at a time.
        self.table_videos.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # Set welcome label
        self.label_dashboard.setText(f"Creator Dashboard - {self.creator_name}")

        # Connect buttons
        self.btn_upload.clicked.connect(self.upload_video)
        self.btn_edit.clicked.connect(self.edit_video)
        self.btn_delete.clicked.connect(self.delete_video)
        self.btn_logout.clicked.connect(self.logout)

        # Load creator data
        self.load_videos()
        self.load_subscriber_count()

    def load_videos(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.video_id, v.title, g.genre_name, v.upload_date, v.views, v.likes_count, v.comments_count
                FROM Videos v
                JOIN Genres g ON v.genre_id = g.genre_id
                JOIN Channels c ON v.channel_id = c.channel_id
                WHERE c.creator_id = ?
            """, (self.creator_id,))
            videos = cursor.fetchall()

            self.table_videos.setRowCount(0)
            for row_number, row_data in enumerate(videos):
                self.table_videos.insertRow(row_number)
                for col_number, data in enumerate(row_data[1:]):  # skip video_id from display
                    self.table_videos.setItem(row_number, col_number, QTableWidgetItem(str(data)))

        except Exception as e:
            QMessageBox.warning(self, "Database Error", str(e))
        finally:
            conn.close()

    def load_subscriber_count(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM Subscriptions s
                JOIN Channels c ON s.channel_id = c.channel_id
                WHERE c.creator_id = ?
            """, (self.creator_id,))
            count = cursor.fetchone()[0]
            self.label_subscriber_count.setText(f"Subscribers: {count}")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", str(e))
        finally:
            conn.close()

    def upload_video(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT channel_id FROM Channels WHERE creator_id = ?", (self.creator_id,))
        channel_id = cursor.fetchone()[0]
        conn.close()

        self.upload_form = UploadVideoForm(self.creator_id, channel_id, self)
        self.upload_form.show()

    def edit_video(self):
        selected_row = self.table_videos.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Select Video", "Please select a video to edit.")
            return

        video_title = self.table_videos.item(selected_row, 0).text()

        # Need the video_id
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT video_id 
            FROM Videos 
            WHERE title = ? 
            AND channel_id = (SELECT channel_id FROM Channels WHERE creator_id = ?)
        """, (video_title, self.creator_id))
        result = cursor.fetchone()
        conn.close()

        if not result:
            QMessageBox.warning(self, "Error", "Could not find the selected video.")
            return

        video_id = result[0]

        # Open edit form
        self.edit_form = EditVideoForm(video_id, self.creator_id, self)
        self.edit_form.show()


    def delete_video(self):
        selected_row = self.table_videos.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Select Video", "Please select a video to delete.")
            return

        video_title = self.table_videos.item(selected_row, 0).text()

        # Confirm delete
        confirm = QMessageBox.question(
            self,
            "Delete Video",
            f"Are you sure you want to delete '{video_title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Videos
            WHERE title = ?
            AND channel_id = (SELECT channel_id FROM Channels WHERE creator_id = ?)
        """, (video_title, self.creator_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Deleted", "Video deleted successfully!")
        self.load_videos()

    def logout(self):
        self.role_window = RoleSelectWindow()
        self.role_window.show()
        self.close()

