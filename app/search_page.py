from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (QMessageBox, QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from db import get_connection 
import pyodbc 
from VideoDetailsPage import VideoDetailsPage
from clickable_widget import ClickableVideoWidget

class SearchResultsPage(QWidget):
    def __init__(self, search_term, parent_window,viewer_id):
        super().__init__()
        uic.loadUi("search_page.ui", self) 
        self.showMaximized()
        
        self.search_term = search_term
        self.parent_window = parent_window 
        self.viewer_id = viewer_id

        self.btnHome.clicked.connect(self.back_to_homepage) 

        self.label_results.setText(f"Search Results for: '{search_term}'")

        self.setup_content_area()

        self.load_videos()

    def setup_content_area(self):
        self.content_layout = self.scrollAreaWidgetContents.layout()
        
        if self.content_layout is None:
            self.content_layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        try:
            self.lblPlaceholder.setParent(None) 
        except AttributeError:
            pass

    def create_video_widget(self, title, description, channel_name, genre_name, views):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(frame)

        title_layout = QHBoxLayout()
        title_label = QLabel(f"**Title:** {title}")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        
        views_label = QLabel(f"**Views:** {views:,}")
        views_label.setStyleSheet("color: blue;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch(1) 
        title_layout.addWidget(views_label)
        layout.addLayout(title_layout)
        
        layout.addWidget(QLabel(f"**Channel:** {channel_name}"))
        layout.addWidget(QLabel(f"**Genre:** {genre_name}"))
        
        layout.addWidget(QLabel(f"**Description:** {description[:100]}..."))
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        return frame

    def load_videos(self):
        search_term = self.search_term
        conn = None

        for i in reversed(range(self.content_layout.count())): 
            widget_to_remove = self.content_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        try:
            conn = get_connection()
            if not conn: return
            
            cursor = conn.cursor()
            
            sql_query = """
                SELECT 
                    V.video_id, V.title, V.description, C.channel_name, G.genre_name, V.views
                FROM Videos V
                JOIN Channels C ON V.channel_id = C.channel_id
                JOIN Genres G ON V.genre_id = G.genre_id
            """
            params = []
            
            if search_term:
                sql_query += """
                    WHERE V.title LIKE ?
                    OR C.channel_name LIKE ?
                    OR G.genre_name LIKE ?
                """
                wildcard_term = f'%{search_term}%'
                params.extend([wildcard_term, wildcard_term, wildcard_term])

            sql_query += " ORDER BY V.views DESC"
            
            cursor.execute(sql_query, params)
            videos = cursor.fetchall()

            if not videos:
                no_results_label = QLabel("No videos found matching your search criteria.")
                no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(no_results_label)
            else:
                for row_data in videos:
                    video_id, title, description, channel_name, genre_name, views = row_data

                    video_widget = ClickableVideoWidget(
                        video_id, title, channel_name, views,
                        parent=self
                    )

                    video_widget.clicked.connect(self.open_video_details) 
                    
                    self.content_layout.addWidget(video_widget)
        
        except Exception as e:
            QMessageBox.critical(self, "Database Query Error", f"An error occurred while fetching videos: {e}")
        
        finally:
            if conn:
                conn.close()

    def open_video_details(self, video_id):
        self.hide() 
        self.video_details_window = VideoDetailsPage(video_id, self,self.viewer_id)
        self.video_details_window.show()


    def back_to_homepage(self):
        #to ensure that the most recent video details are showed on homepage:
        if hasattr(self.parent_window, 'load_trending_videos'):
            self.parent_window.load_trending_videos()
        self.parent_window.show()
        self.close()