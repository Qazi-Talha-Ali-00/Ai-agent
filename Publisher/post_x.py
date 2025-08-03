import os
import sqlite3
import tweepy
import time # Import the time module
from dotenv import load_dotenv

def get_post_from_db(db_path='database/tweets.db'):
    """Fetches one unpublished Twitter post from the database and deletes it."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, content FROM generated_posts WHERE platform = 'Twitter' ORDER BY generated_at ASC LIMIT 1"
    )
    post = cursor.fetchone()
    
    if post:
        post_id, post_content = post
        cursor.execute("DELETE FROM generated_posts WHERE id = ?", (post_id,))
        conn.commit()

    conn.close()
    return post_content if post else None

def main(tweets_to_post=10):
    """Authenticates with the X API and posts multiple tweets in a loop."""
    # --- 1. Load Credentials & Authenticate Once ---
    load_dotenv()
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Error: Missing X API credentials in .env file.")
        return

    try:
        print("Authenticating with X API...")
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # --- 2. Loop to Fetch and Post Tweets ---
    for i in range(tweets_to_post):
        print(f"\n--- Attempting to post tweet {i + 1}/{tweets_to_post} ---")
        
        tweet_text = get_post_from_db()

        if not tweet_text:
            print("✅ No more posts for Twitter in the queue. All done!")
            break # Exit the loop if the database is empty

        try:
            print(f"🚀 Posting tweet:\n---\n{tweet_text}\n---")
            response = client.create_tweet(text=tweet_text)
            print(f"✅ Successfully posted! Tweet ID: {response.data['id']}")
            
            # Wait for 15 seconds before posting the next tweet
            if i < tweets_to_post - 1:
                 print("...waiting 15 seconds before next post...")
                 time.sleep(15)

        except tweepy.errors.TweepyException as e:
            print(f"❌ An error occurred with the X API: {e}")
            break # Stop if there's an API error
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            break


if __name__ == "__main__":
    # Call the main function to start the process
    main()