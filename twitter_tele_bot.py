import tweepy
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import re

# Twitter API credentials
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_key = "YOUR_ACCESS_KEY"
access_secret = "YOUR_ACCESS_SECRET"

# Telegram bot token
telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"

# Telegram chat IDs to send messages to
chat_ids = [123456789, 987654321]

# Twitter user IDs to follow
user_ids = ["elonmusk", "nasa", "spacex"]

# Regular expression to match media URLs
media_regex = r"(https?://(?:www\.)?(?:mobile\.)?twitter\.com/.*/status/\d+)(?:\s|$)"

# Initialize Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
twitter_api = tweepy.API(auth)

# Initialize Telegram bot
telegram_bot = telegram.Bot(token=telegram_token)

def start(update, context):
    """Send a welcome message when the command /start is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there, I'm your Twitter bot!")

def send_tweet_to_telegram(tweet):
    """Send a tweet to Telegram chat."""
    # Get tweet text
    text = tweet.full_text

    # Replace t.co URLs with expanded URLs
    for url in tweet.entities["urls"]:
        text = text.replace(url["url"], url["expanded_url"])

    # Find and replace media URLs with links to the original tweet
    media_urls = []
    for media in tweet.entities.get("media", []):
        media_urls.append(media["url"])
        text = text.replace(media["url"], "")

    text = re.sub(media_regex, r"[\1](\1)", text)

    # Construct the message text with a link to the original tweet
    message_text = f"<b>New tweet from @{tweet.author.screen_name}:</b>\n\n{text}\n\n<a href='https://twitter.com/{tweet.author.screen_name}/status/{tweet.id}'>Link to tweet</a>"

    # Check for media attachments and add them to the message
    media_attachments = []
    for media_url in media_urls:
        if "video" in media_url or "photo" in media_url or "animated_gif" in media_url:
            media_attachments.append(media_url)

    if media_attachments:
        media_attachments.reverse()
        media_buttons = [InlineKeyboardButton("Media", url=media_url) for media_url in media_attachments]
        media_keyboard = [media_buttons]
        media_markup = InlineKeyboardMarkup(media_keyboard)
        telegram_bot.send_message(chat_id=chat_ids[0], text=message_text, parse_mode=telegram.ParseMode.HTML, reply_markup=media_markup)
    else:
        telegram_bot.send_message(chat_id=chat_ids[0], text=message_text, parse_mode=telegram.ParseMode.HTML)

def send_tweets_to_telegram():
    """Send tweets to Telegram chat."""
    # Get the latest tweets from the users
    latest_tweets = {}
    for user_id in user_ids:
        user_tweets = twitter_api.user_timeline(user_id, count=5)
        latest_tweets[user_id] = user_tweets[0].id

    # Loop indefinitely to get new tweets and send them to Telegram chat
    while True:
        try:
            for user_id in user_ids:
                user_tweets = twitter_api.user_timeline(user_id, count=5)
               
