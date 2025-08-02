import feedparser
import requests
from newspaper import Article

RSS_URL = "https://news.google.com/rss"

def resolve_actual_url(google_news_url):
    try:
        res = requests.get(google_news_url, timeout=5, allow_redirects=True)
        return res.url
    except Exception as e:
        print(f"Failed to resolve real URL: {e}")
        return None

def get_articles_from_rss(rss_url):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:5]:
        try:
            real_url = resolve_actual_url(entry.link)
            if not real_url:
                continue

            article = Article(real_url)
            article.download()
            article.parse()

            articles.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": real_url,
                "published": entry.published,
                "full_text": article.text
            })
        except Exception as e:
            print(f"❌ Failed to parse article: {entry.link} – {e}")
    return articles

if __name__ == "__main__":
    full_articles = get_articles_from_rss(RSS_URL)
    if full_articles:
        print(f"✅ {full_articles[0]['title']}\n\n📰 {full_articles[0]['full_text'][:800]}...")
        print(full_articles[0])
    else:
        print("No articles found.")
