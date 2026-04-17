from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QWidget
from db import get_connection
import pyodbc
from datetime import datetime
from PyQt6.QtCore import QDate 

class VideoDetailsPage(QWidget):
    def __init__(self, video_id, parent_window, viewer_id):
        super().__init__()
        uic.loadUi("VideoDetailsPage.ui", self) 
        self.showMaximized()
        
        self.video_id = video_id
        self.parent_window = parent_window
        self.viewer_id = viewer_id   # REAL viewer ID from login
        self.channel_id = None

        # buttons
        self.back_video.clicked.connect(self.back_to_search_results) 
        self.btnLike.clicked.connect(self.handle_like)
        self.btnSubscribe.clicked.connect(self.handle_subscribe)
        self.btnPostComment.clicked.connect(self.handle_post_comment)

        #functionalities
        self.increment_views()
        self.load_video_data()
        self.check_initial_state() 
        self.load_trending_videos() 
        self.load_comments()

    def check_initial_state(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Likes WHERE video_id = ? AND viewer_id = ?", 
                           (self.video_id, self.viewer_id))
            is_liked = cursor.fetchone()[0] > 0
            self.btnLike.setText("Unlike" if is_liked else "Like")


            if self.channel_id:
                cursor.execute("SELECT COUNT(*) FROM Subscriptions WHERE channel_id = ? AND viewer_id = ?", 
                               (self.channel_id, self.viewer_id))
                is_subscribed = cursor.fetchone()[0] > 0
                self.btnSubscribe.setText("Unsubscribe" if is_subscribed else "Subscribe")

        except Exception as e:
            print(f"Error checking initial state: {e}") 
        finally:
            if conn: conn.close()
            

    def handle_like(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Likes WHERE video_id = ? AND viewer_id = ?", 
                           (self.video_id, self.viewer_id))
            is_liked = cursor.fetchone()[0] > 0
            
            if is_liked:
                cursor.execute("DELETE FROM Likes WHERE video_id = ? AND viewer_id = ?", 
                               (self.video_id, self.viewer_id))
                cursor.execute("UPDATE Videos SET likes_count = likes_count - 1 WHERE video_id = ?", 
                               (self.video_id,))
                self.btnLike.setText("Like")
            else:
                cursor.execute("INSERT INTO Likes (video_id, viewer_id) VALUES (?, ?)", 
                               (self.video_id, self.viewer_id))
                cursor.execute("UPDATE Videos SET likes_count = likes_count + 1 WHERE video_id = ?", 
                               (self.video_id,))
                self.btnLike.setText("Unlike")
                
            conn.commit()
            #update the main video details (views,likes)
            self.load_video_data() 

            # Refresh trending on homepage 
            if hasattr(self.parent_window, 'load_trending_videos'):
               self.parent_window.load_trending_videos()

            # Update the trending list on the VideoDetailsPage itself
            self.load_trending_videos()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error handling like: {e}")
        finally:
            if conn: conn.close()


    def increment_views(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE Videos SET views = views + 1 WHERE video_id = ?", (self.video_id,))
            conn.commit()

            # refresh trending on homepage
            if hasattr(self.parent_window, 'load_trending_videos'):
                self.parent_window.load_trending_videos()
            
        except Exception as e:
            print(f"Error incrementing views: {e}")
        finally:
            if conn: conn.close()


    def handle_subscribe(self):
        if not self.channel_id:
            QMessageBox.warning(self, "Error", "Cannot subscribe: Channel ID not available.")
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Subscriptions WHERE channel_id = ? AND viewer_id = ?", 
                           (self.channel_id, self.viewer_id))
            is_subscribed = cursor.fetchone()[0] > 0
            
            if is_subscribed:
                cursor.execute("DELETE FROM Subscriptions WHERE channel_id = ? AND viewer_id = ?", 
                               (self.channel_id, self.viewer_id))
                self.btnSubscribe.setText("Subscribe")
            else:
                cursor.execute("INSERT INTO Subscriptions (channel_id, viewer_id) VALUES (?, ?)", 
                               (self.channel_id, self.viewer_id))
                self.btnSubscribe.setText("Unsubscribe")
                
            conn.commit()
            #immediately load_videos and trending videos again to show most updated version:
            self.load_video_data() 
            self.load_trending_videos()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error handling subscription: {e}")
        finally:
            if conn: conn.close()
            

    def handle_post_comment(self):
        comment_text = self.txtComment.text().strip()
        
        if not comment_text:
            QMessageBox.warning(self, "Empty Comment", "Please write a comment before posting.")
            return
            
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Comments (video_id, viewer_id, comment_text, comment_date)
                VALUES (?, ?, ?, GETDATE())
            """, (self.video_id, self.viewer_id, comment_text))
            
            cursor.execute("UPDATE Videos SET comments_count = comments_count + 1 WHERE video_id = ?", 
                           (self.video_id,))
                
            conn.commit()
            QMessageBox.information(self, "Success", "Comment posted successfully!")

            self.txtComment.clear()
            self.load_video_data() 
            self.load_comments()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error posting comment: {e}")
        finally:
            if conn: conn.close()



    def load_comments(self):
        """Fetches all comments for the current video and displays them in listComments."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    V.name, 
                    C.comment_text, 
                    C.comment_date
                FROM Comments C
                JOIN Viewers V ON C.viewer_id = V.viewer_id
                WHERE C.video_id = ?
                ORDER BY C.comment_date DESC
            """, (self.video_id,))
            
            comments = cursor.fetchall()
            self.listComments.clear()
            
            if not comments:
                self.listComments.addItem("No comments yet. Be the first to post!")
            else:
                for username, text, date in comments:
                    formatted_date = date.strftime('%Y-%m-%d %H:%M')
                    display_text = f"[{username} @ {formatted_date}]: {text}"
                    self.listComments.addItem(display_text)
                    
        except Exception as e:
            QMessageBox.critical(self, "Comment Error", f"Could not load comments: {e}")
        finally:
            if conn: conn.close()


    def load_video_data(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    V.title, V.views, G.genre_name, C.channel_name, 
                    C.channel_id, V.description, V.upload_date, V.likes_count, V.comments_count
                FROM Videos V
                JOIN Genres G ON V.genre_id = G.genre_id
                JOIN Channels C ON V.channel_id = C.channel_id
                WHERE V.video_id = ?
            """, (self.video_id,))
            
            data = cursor.fetchone()

            if data:
                title, views, genre, channel_name, channel_id, description, upload_date, likes, comments = data
                
                self.channel_id = channel_id
                
                
                self.lblTitle.setText(title)
                self.lblViews.setText(f"Views: {views:,} | Genre: {genre} | Likes: {likes:,} | Comments: {comments:,} | Uploaded: {upload_date.strftime('%Y-%m-%d')}")
                self.lblUploader.setText(f"Uploaded by: {channel_name}")
                conn.commit()

                self.check_initial_state()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not load video details: {e}")
        finally:
            if conn:
                conn.close()

    def load_trending_videos(self):
    
       # Fetches top 10 trending videos based on views and likes,
        #and displays them in the QListWidget list_trending
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT TOP 10 v.video_id, v.title, g.genre_name, c.channel_name, v.views, v.likes_count
                FROM Videos v
                JOIN Genres g ON v.genre_id = g.genre_id
                JOIN Channels c ON v.channel_id = c.channel_id
                ORDER BY v.views DESC, v.likes_count DESC
            """)

            trending_videos = cursor.fetchall() #store videos returned from query
            self.list_trending.clear() #clear any existing videos in this widget

            for video in trending_videos:
                #following line is mapping each value video_id to likes, to index in video:
                #video[0] = video_id and title = video[1] and so on     
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
                self.list_trending.addItem(display_text)

        except Exception as e:
            QMessageBox.critical(self, "Trending Videos Error", f"Could not load trending videos: {e}")
        finally:
            if conn:
                conn.close()


    def back_to_search_results(self): 
         # refresh parent search page  so that after returning from a video, 
         # SearchResultsPage shows the updated view counts.
        if hasattr(self.parent_window, 'load_videos'):
            self.parent_window.load_videos()    
        self.parent_window.show()
        self.close()