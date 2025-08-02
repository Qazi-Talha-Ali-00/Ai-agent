import feedparser
from newspaper import Article

rss_url = "https://news.google.com/rss"

feed = feedparser.parse(rss_url)

for entry in feed.entries[:5]:  # Top 5 articles
    print(f"\nFetching: {entry.title}")
    url = entry.link
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        print(f"Title: {article.title}")
        print(f"Summary: {article.summary}")
    except Exception as e:
        print(f"Failed to process article: {e}")
