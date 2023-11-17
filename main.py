import requests
import feedparser
import tweepy
import time
from datetime import datetime
import pytz

istanbul_timezone = pytz.timezone("Europe/Istanbul")

api_key = "WRITEYOURS"
api_secret = "WRITEYOURS"
access_token = "WRITE-YOURS"
access_token_secret = "WRITEYOURS"

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

rss_urls = {"Coin Telegraph": "https://cointelegraph.com/rss",
            "Coin Desk": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
            "Blockworks": "https://blockworks.co/rss",
            "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
            "Zerohedge": "http://feeds.feedburner.com/zerohedge/feed"}

def check_rss_feeds():
    for site_name, rss_url in rss_urls.items():
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            tweet_text = site_name + ": " + entry.title #+ " " + "#Bitcoin"
            tweet_link = entry.link
            published_time = datetime(*entry.published_parsed[:6])

            current_time = datetime.utcnow()
            time_difference = current_time - published_time

            with open("tweets.txt", "r") as f:
                if tweet_text not in f.read() and time_difference.total_seconds() < 1800: 
                    time.sleep(600)
                    
                    now = datetime.utcnow()
                    now = now.replace(tzinfo=pytz.utc)
                    time_of_calculation = now.astimezone(istanbul_timezone).strftime("%d-%m-%Y %H:%M:%S TSİ")
                    
                    media_ids = []
                    if 'media_content' in entry:
                        for media in entry.media_content:
                            try:
                                image_url = media['url']
                                image_content = requests.get(image_url).content
                                filename = 'temp.jpg'
                                with open(filename, 'wb') as image:
                                    image.write(image_content)
                                image_upload = api.media_upload(filename)
                                media_ids.append(image_upload.media_id)
                                print("Image shared.")
                            except tweepy.TweepyException as E:
                                print("Error occured while sharing image: " + str(E))
                    if media_ids:
                        try:
                            tweet = api.update_status(status=tweet_text, media_ids=media_ids)
                            print(tweet_text + " @" + str(time_of_calculation))
                        except tweepy.TweepyException as E:
                            print("Error occured while sharing tweet: " + str(E))
                    else:
                        try:
                            tweet = api.update_status(status=tweet_text)
                            print("Shared as text: " + tweet_text + " @" + str(time_of_calculation))
                        except tweepy.TweepyException as E:
                            print("Error occured while sharing tweet: " + str(E))

                    with open("tweets.txt", "a") as f:
                        f.write(tweet_text + "\n")

                    time.sleep(5)
                    api.update_status(status="You can check this out from here: " + entry.link,
                                      in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)
                    print("Link shared as a mention.")
                    print()
while True:
    check_rss_feeds()
    time.sleep(60)
