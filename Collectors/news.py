import feedparser
from newspaper import Article

RSS_URL = "https://news.google.com/rss"

def get_articles_from_rss(rss_url):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:5]:
        try:
            article = Article(entry.link)
            article.download()
            article.parse()

            articles.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link,
                "published": entry.published,
                "full_text": article.text
            })
        except Exception as e:
            print(f"Failed to parse article: {entry.link} – {e}")
    return articles

if __name__ == "__main__":
    full_articles = get_articles_from_rss(RSS_URL)
    # for a in full_articles:
    #     print(f"\n📌 {a['title']}\n➡️ {a['link']}\n📰 {a['full_text'][:5000]}...\n")
    print(f"{full_articles[0]['title']}\n {full_articles[0]['full_text']}")
    print(full_articles[0])
