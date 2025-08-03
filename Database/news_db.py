

import sqlite3
import logging

class DatabaseNews:
    """Manages all database operations for news articles."""

    def __init__(self, db_path='database/news.db'):
        self.db_path = db_path
        # The connection is now stored as an instance variable
        self.conn = self._create_connection()
        self._create_table()

    def _create_connection(self):
        """Creates and returns a database connection."""
       
        conn = sqlite3.connect(self.db_path)
        return conn

    def _create_table(self):
        """Creates the news_articles table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            # Corrected SQL: Removed trailing comma and added UNIQUE constraint
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")

    def insert_article(self, article_data: dict):
        """
        Inserts a new article into the database.
        Ignores insertion if the URL already exists.
        Returns the ID of the new row, or None if ignored.
        """
        # The method now correctly uses `self.conn`
        sql = ''' INSERT OR IGNORE INTO news_articles(title, content, summary, url)
                  VALUES(?,?,?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                article_data['title'],
                article_data['content'],
                article_data['summary'],
                article_data['url']
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error inserting article: {e}")
            return None

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")