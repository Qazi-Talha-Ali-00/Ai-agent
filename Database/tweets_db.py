import sqlite3
import logging

class DatabaseTweets:
    """Manages all database operations for Twitter trends and tweets."""

    def __init__(self, db_path='database/tweets.db'):
        self.db_path = db_path
        self.conn = self._create_connection()
        self._create_tables()

    def _create_connection(self):
        """Creates and returns a database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            return None

    def _create_tables(self):
        """Creates the required tables if they don't exist."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            # Table for trending topics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trending_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                tweet_volume INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Table for individual tweets
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tweets (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                author TEXT,
                url TEXT NOT NULL UNIQUE,
                reply_count INTEGER,
                like_count INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Table for our generated content
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT,
                source_url TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")

    def insert_trend(self, trend_data: dict):
        """Inserts a new trending topic, ignoring if it already exists."""
        sql = ''' INSERT OR IGNORE INTO trending_topics(topic, tweet_volume)
                  VALUES(?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (trend_data['topic'], trend_data['tweet_volume']))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error inserting trend: {e}")
            return None

    def insert_tweet(self, tweet_data: dict):
        """Inserts a new tweet, ignoring if its URL already exists."""
        sql = ''' INSERT OR IGNORE INTO tweets(id, text, author, url, reply_count, like_count)
                  VALUES(?,?,?,?,?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                tweet_data['id'],
                tweet_data['text'],
                tweet_data['author'],
                tweet_data['url'],
                tweet_data['replyCount'],
                tweet_data['likeCount']
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error inserting tweet: {e}")
            return None
            
    def insert_generated_post(self, post_data: dict):
        """Inserts a generated social media post into the database."""
        sql = ''' INSERT INTO generated_posts(platform, content, source_type, source_url)
                  VALUES(?,?,?,?) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                post_data['platform'],
                post_data['content'],
                post_data['source_type'],
                post_data['source_url']
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error inserting generated post: {e}")
            return None

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")