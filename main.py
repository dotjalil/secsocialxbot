import os
import tweepy
import time
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Twitter Credentials
api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('API_SECRET')
bearer_token = os.environ.get('BEARER_TOKEN')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

# Slack Credentials
slack_token = os.environ.get('SLACK_TOKEN')
slack_channel = os.environ.get('SLACK_CHANNEL')

# Connecting to Twitter API v2
client_v2 = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
print("Connected to Twitter API v2")

# Connecting to Slack
slack_client = WebClient(token=slack_token)
print("Connected to Slack API")

# Setting up Twitter API v1.1 for media upload
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
client_v1 = tweepy.API(auth)
print("Ready for media uploads to Twitter API v1.1")

def post_to_slack(tweet):
    try:
        message = f"New tweet found: {tweet.text} - Link: https://twitter.com/i/web/status/{tweet.id}"
        slack_client.chat_postMessage(channel=slack_channel, text=message)
    except SlackApiError as e:
        print(f"Error posting to Slack: {e}")

# Uploads media and returns media_id for use in tweet
def upload_media(filename):
    media = client_v1.media_upload(filename)
    return media.media_id

# Keywords
keywords = [
    "تشوية سمعة", "الابتزاز الالكتروني", "ساعدوني", "ابغى ابلغ", "ابغى احد يحذف",
    "اتعرض للابتزاز", "يبتزني", "يهددني", "ينشر صوري", "الجرائم الالكترونية",
    "ابتزاز الكتروني", "التشهير الالكتروني", "تشهير", "ابتزاز المقاطع", "ابتزاز الصور",
    "الابتزاز بالفيديوهات", "ابتزاز البريد", "هكر", "هكر جوالي", "نشر صورتي",
    "خلك واعي", "بصمة أمان", "بصمة أمان وهمية", "محاسبة بصمة أمان", "حذف حساب منتحل",
    "انتحال شخصية", "ينتحل شخصيتي", "منتحل شخصية", "حذف حساب", "الحماية من الابتزاز",
    "الإبلاغ عن الابتزاز", "الابتزاز الرقمي", "ابتزاز البيانات الخصية", "الابتزاز المالي", "الابتزاز العاطفي",
    "التعرض للابتزاز", "كلنا امن", "تقديم بلاغ", "كيف اشتكي", "كيف ابلغ",
    "الابتزاز السيبراني", "الابتزاز عن طريق الانترنت", "خطابة", "زواج مسيار", "قوانين الابتزاز",
    "تسريب البيانات", "تهكير رقمي", "مكافحة الابتزاز", "ارقام بلاغات الابتزاز", "ارقام مكافحة الابتزاز"
]

# Looking for tweets containing specific keywords from the last 5 minutes
while True:
    current_time = datetime.now(timezone.utc)
    start_time = current_time - timedelta(minutes=5)
    start_time_str = start_time.isoformat(timespec='seconds')

    # Creating a query string with all keywords
    query = " OR ".join(f'"{keyword}"' for keyword in keywords)
    response = client_v2.search_recent_tweets(query=query, start_time=start_time_str, max_results=10)

    if response.data is not None:
        for tweet in response.data:
            print("Tweet found:", tweet.text)
            post_to_slack(tweet)  # Send message to Slack

            # Upload GIF and reply to tweet
            media_id = upload_media("path/to/your/gif.gif")  # Replace with your GIF path
            client_v2.create_tweet(text="Your reply message here", in_reply_to_tweet_id=tweet.id, media_ids=[media_id])
            print("Replied to tweet ID:", tweet.id)

    time.sleep(300)  # Can use anything from 60 seconds up
