import os
import time
import requests
import feedparser
import google.generativeai as genai
from newspaper import Article, Config, ArticleException
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Database.news_db import DatabaseNews

# --- 1. SETUP ---
# Load environment variables and configure APIs as before
load_dotenv()
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()

# Configure newspaper3k with a browser user-agent
config = Config()
config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
config.request_timeout = 20

# --- NEW FUNCTION: Using Playwright to resolve the redirect ---
def resolve_final_url(page, gnews_url):
    """Uses an existing Playwright page to resolve a redirect URL."""
    try:
        page.goto(gnews_url, timeout=20000, wait_until='domcontentloaded')
        page.wait_for_timeout(2000) # Wait for JS redirects
        final_url = page.url
        if "news.google.com" in final_url:
            return None
        return final_url
    except PlaywrightTimeoutError:
        print(f"Timeout resolving URL: {gnews_url}")
        return None
    except Exception as e:
        print(f"Error resolving URL {gnews_url}: {e}")
        return None


# The rest of the functions remain the same
def get_article_content_from_url(url):
    """Downloads and parses a news article to extract its main text content."""
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except (ArticleException, IOError) as e:
        print(f"Failed to get content from {url}: {e}")
        return None

def summarize_with_gemini(content, title):
    """Uses the Gemini LLM to summarize a single article."""
    if not content or len(content.strip()) < 150:
        return None

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    You are an expert news analyst. Summarize the following news article in 3-4 clear and concise bullet points.
    Focus on the key takeaways and essential information.
    ARTICLE TITLE: "{title}"
    ARTICLE CONTENT: "{content[:4000]}"
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None

def main():
    news_feed = feedparser.parse("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en")
    articles_to_process = 15
    db = DatabaseNews()

    # for entry in news_feed.entries[:articles_to_process]:
    #     title = entry.title
    #     google_news_link = entry.link
    #     final_url = resolve_final_url_with_playwright(google_news_link)

    #     if not final_url or "news.google.com" in final_url:
    #         continue
        
    #     article_content = get_article_content_from_url(final_url)

    #     if article_content:
    #         summary = summarize_with_gemini(article_content, title)
    #         article = {
    #             'title': title,
    #             'content': article_content,
    #             'summary': summary,
    #             'url': final_url
    #         }
    #         article_id = db.insert_article(article)
    #         print(f"Inserted article with ID {article_id} into the database.")

    #     else:
    #         continue
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print(f"Processing up to {articles_to_process} articles...")

        for entry in news_feed.entries[:articles_to_process]:
            title = entry.title
            google_news_link = entry.link
            final_url = resolve_final_url(page,google_news_link)
            if not final_url or "news.google.com" in final_url:
                continue
            article_content = get_article_content_from_url(final_url)
            if article_content:
                summary = summarize_with_gemini(article_content, title)
                article = {
                    'title': title,
                    'content': article_content,
                    'summary': summary,
                    'url': final_url
                    }
                article_id = db.insert_article(article)
                print(f"Inserted article with ID {article_id} into the database.")

            else:
                continue
        browser.close()
    db.close_connection()
if __name__ == "__main__":
    main()