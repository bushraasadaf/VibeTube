from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QWidget
from role_select_window import RoleSelectWindow
from search_page import SearchResultsPage 
from db import get_connection

# viewer homepage
class ViewerHomepage(QWidget):
    def __init__(self, viewer_id, viewer_name):
        super().__init__()
        uic.loadUi("viewer_homepage.ui", self)
        self.showMaximized()
        #connect buttons
        self.btnSearch.clicked.connect(self.search_videos)
        self.btnLogout.clicked.connect(self.logout)
        self.search_results_window = None
        self.viewer_id = viewer_id
        self.viewer_name = viewer_name
        #trending videos on homepage loaded as:
        self.load_trending_videos()

        #searching functionality
    def search_videos(self):
        search_term = self.searchInput.text().strip()
        self.search_results_window = SearchResultsPage(search_term, self, self.viewer_id)
        self.search_results_window.show()
        self.hide()
    #show trending videos
    def load_trending_videos(self):
        
        #Fetches the top videos based on a trending metric (views/likes) 
        # and displays them in the QListWidget list_trending
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # SQL query to get the top 10 videos and ordering by likes and views
            cursor.execute("""
                SELECT TOP 10 
                    v.video_id,
                    v.title, 
                    g.genre_name, 
                    c.channel_name, 
                    v.views, 
                    v.likes_count
                FROM Videos v
                JOIN Genres g ON v.genre_id = g.genre_id
                JOIN Channels c ON v.channel_id = c.channel_id
                -- Order by views primarily, and likes secondarily to determine 'trending'
                ORDER BY v.views DESC, v.likes_count DESC
            """)

            trending_videos = cursor.fetchall() 
            
            #clear the widget before adding new items
            self.listTrending.clear() 

            if not trending_videos:
                self.listTrending.addItem("No trending videos found in the database.")
                return

            for video in trending_videos:
                #unpack the tuple: title, genre, channel_name, views, likes
                video_id,title, genre, channel_name, views, likes = video
                
                 # First, format the numbers with commas
                formatted_views = format(views, ',')
                formatted_likes = format(likes, ',')

                #combine all the strings using the '+' operator
                display_text = (
                    title + " | " + 
                    genre + " | " + 
                    channel_name + " | " + 
                    formatted_views + " views | " + 
                    formatted_likes + " likes"
                )
                self.listTrending.addItem(display_text)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not load trending videos: {e}")
        finally:
            if conn:
                conn.close()
    
    def logout(self):
        #Logs the viewer out and navigates back to the role selection window.
        
        # Initialize and show the previous window (RoleSelectWindow)
        self.role_window = RoleSelectWindow()
        self.role_window.show()
        
        # Close the current window
        self.close()