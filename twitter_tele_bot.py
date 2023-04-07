import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import tweepy

# Twitter API credentials
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_key = "YOUR_ACCESS_KEY"
access_secret = "YOUR_ACCESS_SECRET"

# Authenticate Twitter API credentials
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Telegram Bot token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Send tweets from user timeline to Telegram chat
def send_user_timeline(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    username = context.args[0]
    try:
        tweets = api.user_timeline(screen_name=username, count=10, tweet_mode='extended')
    except tweepy.TweepError as e:
        context.bot.send_message(chat_id=chat_id, text=f'Error: {str(e)}')
        return

    if len(tweets) > 0:
        for tweet in tweets:
            # Check if tweet has media files
            if 'media' in tweet.entities:
                for item in tweet.extended_entities['media']:
                    media_url = item['media_url']
                    file_extension = os.path.splitext(media_url)[1]
                    # Download media file
                    file_name = f'{tweet.id}_{item["id"]}{file_extension}'
                    response = requests.get(media_url)
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    # Send media file to Telegram chat
                    context.bot.send_document(chat_id=chat_id, document=open(file_name, 'rb'))
                    # Delete media file from local storage
                    os.remove(file_name)
            else:
                # If media does not exist, send tweet text to Telegram chat
                context.bot.send_message(chat_id=chat_id, text=tweet.full_text)
    else:
        # If tweets do not exist, send error message
        context.bot.send_message(chat_id=chat_id, text=f'No tweets found from user {username}')

# Send tweets from list to Telegram chat
def send_list_timeline(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    list_owner = context.args[0]
    list_slug = context.args[1]
    try:
        tweets = api.list_timeline(owner_screen_name=list_owner, slug=list_slug, count=10, tweet_mode='extended')
    except tweepy.TweepError as e:
        context.bot.send_message(chat_id=chat_id, text=f'Error: {str(e)}')
        return

    if len(tweets) > 0:
        for tweet in tweets:
            # Check if tweet has media files
            if 'media' in tweet.entities:
                for item in tweet.extended_entities['media']:
                    media_url = item['media_url']
                    file_extension = os.path.splitext(media_url)[1]
                    # Download media file
                    file_name = f'{tweet.id}_{item["id"]}{file_extension}'
                    response = requests.get(media_url)
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    # Send media file to Telegram chat
                context.bot.send_document(chat_id=chat_id, document=open(file_name, 'rb'))
                # Delete media file from local storage
                os.remove(file_name)
        else:
            # If media does not exist, send tweet text to Telegram chat
            context.bot.send_message(chat_id=chat_id, text=tweet.full_text)
else:
    # If tweets do not exist, send error message
    context.bot.send_message(chat_id=chat_id, text=f'No tweets found from list {list_slug} by {list_owner}')

                   

Telegram command handlers
dispatcher.add_handler(CommandHandler('user_timeline', send_user_timeline))
dispatcher.add_handler(CommandHandler('list_timeline', send_list_timeline))

Start the bot
updater.start_polling()
updater.idle()

