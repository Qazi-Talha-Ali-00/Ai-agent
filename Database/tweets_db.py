import sqlite3
import logging

class DatabaseTweets:
    """Manages all database operations for Twitter data."""

    def __init__(self, db_path='database/tweets.db'):
        self.db_path = db_path
        self.conn = self._create_connection()
        self._create_table()

    def _create_connection(self):
        """Creates and returns a database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            logging.critical(f"Database connection error: {e}")
            raise

    def _create_table(self):
        """Creates the database tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            
            # **FIXED**: Removed trailing comma
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tweets(
                           tweet_id TEXT PRIMARY KEY,
                           trend_topic TEXT NOT NULL,
                           text TEXT,
                           user_handle TEXT,
                           url TEXT NOT NULL UNIQUE,
                           reply_count INTEGER DEFAULT 0,
                           like_count INTEGER DEFAULT 0,
                           collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # **FIXED**: Removed extra comma and added tweet_volume
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS twitter_trends(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           topic TEXT NOT NULL UNIQUE,
                           tweet_volume INTEGER DEFAULT 0,
                           collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
        
    def insert_tweet(self, tweet_data: dict, trend_topic: str):
        """
        Inserts a single tweet into the database.
        The 'collected_at' timestamp is added automatically by the database.
        """
        sql = ''' INSERT OR IGNORE INTO tweets(tweet_id, trend_topic, text, user_handle, url, reply_count, like_count)
                  VALUES(?,?,?,?,?,?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                tweet_data.get('id'),
                trend_topic,
                tweet_data.get('text'),
                tweet_data.get('author', {}).get('userName'),
                tweet_data.get('url'),
                tweet_data.get('replyCount', 0),
                tweet_data.get('likeCount', 0)
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting tweet: {e}")

    def insert_trend(self, trend_data: dict):
        """
        Inserts a single trend into the database.
        The 'collected_at' timestamp is added automatically by the database.
        """
        sql = ''' INSERT OR IGNORE INTO twitter_trends(topic, tweet_volume)
                  VALUES(?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                trend_data.get('topic'),
                trend_data.get('tweet_volume', 0)
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting trend: {e}")

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()