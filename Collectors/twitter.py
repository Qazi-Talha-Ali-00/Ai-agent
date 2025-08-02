import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


auth = tweepy.OAuthHandler(API_KEY,API_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

client_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

try:
    api_v1.verify_credentials()
    print("Authentication successful for twitter")
except Exception as e:
    print(f"Authentication fialed : {e}")


def get_trending_topics(woeid=1, max_trends = 10):
    """
    WOEID = Where on Earth ID, WOEID = 1 for global
    """
    try:
        trends = api_v1.get_place_trends(woeid)
        trends_data = []
        for trend in trends[0]['trends'][:max_trends]:
            trends_data.append({
                "name": trend["name"],
                "tweet_volume":trend.get("tweet_volume",0),
                "timestamp": trends[0]['as_of'],
                "source_link": trend.get("url","")
            })
        return trends_data
    except Exception as e:
        print(f"Error fetching the trends data :{e}")
        return []
    


global_trends = get_trending_topics()
for trend in global_trends:
    print(f"Trend: {trend['name']},  Volume: {trend['tweet_volume']}, Time: {trend['timestamp']}")

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get("https://x.com/explore")
# time.sleep(5)  # Wait for page to load
# trends = driver.find_elements_by_css_selector("div[aria-label='Timeline: Trending now'] span")
# for trend in trends[:10]:
#     print(f"Trend: {trend.text}")
# driver.quit()