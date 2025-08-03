import os
import sqlite3
import random
import google.generativeai as genai
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Database.tweets_db import DatabaseTweets # Use the corrected DB class

# --- 1. SETUP ---
load_dotenv()
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()

# --- 2. DATABASE OPERATIONS ---
def fetch_latest_articles(db_path='database/news.db', limit=5):
    """Fetches the most recent articles from the news database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, summary, url FROM news_articles ORDER BY created_at DESC LIMIT ?", (limit,))
    articles = cursor.fetchall()
    conn.close()
    return [{'title': r[0], 'summary': r[1], 'url': r[2]} for r in articles]

def fetch_top_tweets(db_path='database/tweets.db', limit=5):
    """Fetches the most popular tweets from the tweets database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT text, url FROM tweets ORDER BY like_count DESC, collected_at DESC LIMIT ?", (limit,))
    tweets = cursor.fetchall()
    conn.close()
    return [{'text': r[0], 'url': r[1]} for r in tweets]

# --- 3. CONTENT GENERATION WITH GEMINI ---
def generate_post_with_gemini(source_material: dict, platform: str):
    """
    Generates a social media post using Gemini based on source material.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Define different content styles/formats
    post_formats = [
        "Opinion: Share a unique perspective on this.",
        "Analysis: Break down why this is significant.",
        "News Breakdown: Summarize this into key takeaways for a busy audience.",
        "Thought Leadership: Offer a deep, authoritative insight based on this.",
        "Short Tips: Provide quick, actionable advice related to this topic."
    ]
    chosen_format = random.choice(post_formats)

    # Tailor prompts for each platform
    if platform == "LinkedIn":
        prompt = f"""
        You are a professional social media strategist and industry thought leader.
        Your task is to create an engaging LinkedIn post based on the provided material.

        **Instructions:**
        1.  **Tone:** Professional, insightful, and conversational.
        2.  **Format:** Adopt the style of: "{chosen_format}".
        3.  **Content:** Write a compelling post that encourages discussion and engagement.
        4.  **Hashtags:** Include 3-4 relevant, professional hashtags.
        5.  **Reference:** Do NOT include the source URL in the post itself.

        **Source Material:**
        `{source_material}`

        Generate the LinkedIn post now.
        """
    elif platform == "Twitter":
        prompt = f"""
        You are a savvy and witty social media expert specializing in Twitter / X.
        Your task is to create a concise and punchy tweet.

        **Instructions:**
        1.  **Tone:** Clear, engaging, and direct. Can be slightly informal.
        2.  **Format:** Adopt the style of: "{chosen_format}".
        3.  **Content:** Write a tweet that grabs attention and is easily shareable. It MUST be under 280 characters.
        4.  **Hashtags:** Include 2-3 trending or highly relevant hashtags.
        5.  **Reference:** Do NOT include the source URL in the tweet itself.

        **Source Material:**
        `{source_material}`

        Generate the Tweet now.
        """
    else:
        return None

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return None

# --- 4. MAIN ORCHESTRATION ---
def main():
    print("🚀 Starting Viral Content Generator...")
    db_tweets = DatabaseTweets() # For writing generated posts

    # --- Generate posts from News Articles ---
    print("\n📰 Processing news articles...")
    articles = fetch_latest_articles(limit=5)
    for article in articles:
        # Generate one LinkedIn post per article
        print(f"  -> Generating LinkedIn post for article: {article['title'][:30]}...")
        linkedin_post = generate_post_with_gemini(article['summary'], "LinkedIn")
        if linkedin_post:
            db_tweets.insert_generated_post({
                'platform': 'LinkedIn',
                'content': linkedin_post,
                'source_type': 'news_article',
                'source_url': article['url']
            })
            print("     ✅ LinkedIn Post Generated and Saved.")

        # Generate one Twitter post per article
        print(f"  -> Generating Twitter post for article: {article['title'][:30]}...")
        twitter_post = generate_post_with_gemini(article['summary'], "Twitter")
        if twitter_post:
            db_tweets.insert_generated_post({
                'platform': 'Twitter',
                'content': twitter_post,
                'source_type': 'news_article',
                'source_url': article['url']
            })
            print("     ✅ Twitter Post Generated and Saved.")

    # --- Generate posts from Trending Tweets ---
    print("\n🐦 Processing trending tweets...")
    tweets = fetch_top_tweets(limit=5)
    for tweet in tweets:
        # It's often better to generate commentary rather than just reposting
        # For simplicity, we'll use the tweet text as inspiration
        print(f"  -> Generating LinkedIn post based on tweet: {tweet['text'][:40]}...")
        linkedin_post = generate_post_with_gemini(tweet['text'], "LinkedIn")
        if linkedin_post:
            db_tweets.insert_generated_post({
                'platform': 'LinkedIn',
                'content': linkedin_post,
                'source_type': 'tweet',
                'source_url': tweet['url']
            })
            print("     ✅ LinkedIn Post Generated and Saved.")
        
        print(f"  -> Generating Twitter post based on tweet: {tweet['text'][:40]}...")
        twitter_post = generate_post_with_gemini(tweet['text'], "Twitter")
        if twitter_post:
            db_tweets.insert_generated_post({
                'platform': 'Twitter',
                'content': twitter_post,
                'source_type': 'tweet',
                'source_url': tweet['url']
            })
            print("     ✅ Twitter Post Generated and Saved.")


    db_tweets.close_connection()
    print("\n🎉 Content generation complete. Posts are saved in 'database/tweets.db' in the 'generated_posts' table.")

if __name__ == "__main__":
    main()