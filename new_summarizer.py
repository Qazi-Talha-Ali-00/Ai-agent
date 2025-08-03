import os
import time
import requests
import feedparser
import google.generativeai as genai
from newspaper import Article, Config, ArticleException
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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
def resolve_final_url_with_playwright(gnews_url):
    """
    Uses a real browser via Playwright to navigate through JavaScript redirects
    and find the final destination URL.
    """
    final_url = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # Navigate to the Google News URL, wait for the page to start loading
            page.goto(gnews_url, timeout=20000, wait_until='domcontentloaded')
            # Give the page a moment to execute JavaScript if needed
            page.wait_for_timeout(3000)
            # The final URL after JavaScript redirects
            final_url = page.url
            browser.close()
    except PlaywrightTimeoutError:
        return None
    except Exception as e:
        return None
    return final_url

# The rest of the functions remain the same
def get_article_content_from_url(url):
    """Downloads and parses a news article to extract its main text content."""
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except (ArticleException, IOError) as e:
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
    articles_to_process = 12

    for entry in news_feed.entries[:articles_to_process]:
        title = entry.title
        google_news_link = entry.link
        final_url = resolve_final_url_with_playwright(google_news_link)

        if not final_url or "news.google.com" in final_url:
            continue
        
        article_content = get_article_content_from_url(final_url)

        if article_content:
            summary = summarize_with_gemini(article_content, title)
            if summary:
                print("\n" + "="*50)
                print(f"Title: {title}")
                print(f"\nSummary:\n{summary}")
                print(f"\nSource: {final_url}")
                print("="*50 + "\n")
        else:
            continue
if __name__ == "__main__":
    main()