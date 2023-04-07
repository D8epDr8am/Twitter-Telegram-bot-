import tweepy
import requests
import os
import logging
from telegram.ext import Updater, CommandHandler

# Twitter API Keys and Tokens
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_token = 'your_access_token'
access_secret = 'your_access_secret'

# Telegram Bot Token
bot_token = 'your_bot_token'

# Initialize Tweepy API with Twitter Keys and Tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# Initialize Telegram Bot
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

# Define Telegram command to send tweets
def send_tweet(update, context):
    chat_id = update.effective_chat.id
    # Extract Tweet ID from command message
    tweet_id = context.args[0]
    # Get tweet with specified ID
    tweet = api.get_status(tweet_id)
    # Extract media entities from tweet
    media = tweet.entities.get('media', [])
    if len(media) > 0:
        # If media exists, send it to Telegram chat
        for item in media:
            # Get media URL
            media_url = item['media_url_https']
            # Get media file extension
            file_extension = os.path.splitext(media_url)[1]
            # Download media file
            file_name = f'{tweet_id}_{item["id"]}{file_extension}'
            response = requests.get(media_url)
            with open(file_name, 'wb') as f:
                f.write(response.content)
            # Send media file to Telegram chat
            context.bot.send_document(chat_id=chat_id, document=open(file_name, 'rb'))
            # Delete media file from local storage
            os.remove(file_name)
    else:
        # If media does not exist, send error message
        context.bot.send_message(chat_id=chat_id, text='No media found in tweet')

# Register Telegram command handler
dispatcher.add_handler(CommandHandler('send_tweet', send_tweet))

# Start Telegram Bot
updater.start_polling()
