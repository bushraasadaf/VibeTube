from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout

class ClickableVideoWidget(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, video_id, title, channel_name, views, parent=None):
        super().__init__(parent)
        self.video_id = video_id
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor) 
        
        layout = QVBoxLayout(self)
        
        # Title and Views
        title_layout = QHBoxLayout()
        title_label = QLabel(f"**Title:** {title}")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        views_label = QLabel(f"Views: {views:,}")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(views_label)
        layout.addLayout(title_layout)
        
        # Channel
        layout.addWidget(QLabel(f"Channel: {channel_name}"))
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)


    def mousePressEvent(self, event):
        self.clicked.emit(self.video_id)
        super().mousePressEvent(event) 