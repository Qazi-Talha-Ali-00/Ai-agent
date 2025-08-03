import os
from dotenv import load_dotenv
from apify_client import ApifyClient
import re

load_dotenv()
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
APIFY_API_KEY_TRENDS = os.getenv("APIFY_API_KEY_TRENDS")

if not APIFY_API_KEY:
    raise ValueError("APIFY_API_KEY not found. Please set it in your .env file.")




def get_tweet_volume(volume_str: str | None) -> int:
    """
    Parses tweet_volume strings like "254.8k", "16.1k", "Under 10k",
    or "123M" into integer counts, or returns 0 if parsing fails.
    """

    if not volume_str or not isinstance(volume_str, str):
        return 0

    s = volume_str.strip()
    # Try to match "123.4k", "2M", "16.1k", etc.
    m = re.match(r"^([\d\.]+)\s*([kKmMbB])$", s)
    if m:
        num, suffix = m.groups()
        try:
            n = float(num)
        except ValueError:
            return 0
        return int(n * {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suffix.lower()])

    # Handle "Under Xk" or "Under Xm"
    m2 = re.match(r"^[Uu]nder\s*([\d\.]+)\s*([kKmMm])$", s)
    if m2:
        num, suffix = m2.groups()
        try:
            n = float(num)
        except ValueError:
            return 0
        # e.g. 'Under 10k' → treat as 9.999k, or just 10k
        return int(n * {"k": 1_000, "m": 1_000_000}[suffix.lower()])

    # If it's just a plain number (no suffix), parse directly
    m3 = re.match(r"^(\d+)$", s)
    if m3:
        return int(m3.group(1))

    # Fallback
    return 0

def fetch_trending_topics():


# Initialize the ApifyClient with your API token
    client = ApifyClient(APIFY_API_KEY_TRENDS)

# Prepare the Actor input
    run_input = { "country": "india" }

# Run the Actor and wait for it to finish
    run = client.actor("buk0BEIinZ6vfMEq1").call(run_input=run_input)
    trending_topics = []

# Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        trending_topics.append({"topic": item.get("topic", "Unknown Topic"),
                                "tweet_volume": get_tweet_volume(item.get("tweet_volume", None))})
    
    return trending_topics

        




def fetch_twitter_trends(trends, max_trend_items = 20,max_tweet_items=50):
    client = ApifyClient(APIFY_API_KEY)

    actor_id = "apidojo/tweet-scraper"

    # Manually provide trending topics as searchTerms
    run_input = {
        "searchTerms": trends[:max_trend_items],  # Replace with actual trending topics
        "maxItems": max_tweet_items
    }

    actor_run = client.actor(actor_id).call(run_input=run_input)
    dataset_items = []

    for item in client.dataset(actor_run['defaultDatasetId']).iterate_items():
        dataset_items.append(item)

    return dataset_items

def main():

    trending_topics = fetch_trending_topics()
    print(trending_topics)
    # print("trending topics")
    # print("="*50)
    # print(trending_topics[0])
    # print("="*50)
    # print(trending_topics)
    # trends = fetch_twitter_trends()
    # print(trends[0])
    # if trends:
    #     print("Fetched tweets:")
    #     for tweet in trends:
    #         tweet_text = tweet.get('text', 'Unknown Tweet')
    #         likes = tweet.get('favorite_count', 0)
    #         retweets = tweet.get('retweet_count', 0)
    #         replies = tweet.get('reply_count', 0)
    #         created_at = tweet.get('created_at', 'Unknown Time')
    #         print(f"Tweet: {tweet_text}")
    #         print(f"Likes: {likes}, Retweets: {retweets}, Replies: {replies}")
    #         print(f"Created at: {created_at}")
    #         print("-" * 50)
    # else:
    #     print("No tweets fetched.")
if __name__ == "__main__":
    main()