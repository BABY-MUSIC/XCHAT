import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client['telegram_bot']
posts_collection = db['posts']
sudo_users = db['sudo_users']
autopost_collection = db['autopost']
users_collection = db['users']

# Owner ID (Replace with your Telegram ID)
OWNER_ID = 123456789  # Replace with your Telegram ID

# Video Links for /start
START_VIDEO = [
    "https://www.example.com/video1.mp4",
    "https://www.example.com/video2.mp4",
    "https://www.example.com/video3.mp4"
]

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Function to send autopost to all users
def send_autopost(context: CallbackContext):
    autopost = autopost_collection.find_one()
    if autopost:
        message = autopost.get('content', None)
        if message:
            users = users_collection.find()
            for user in users:
                try:
                    context.bot.send_message(chat_id=user['user_id'], text=message)
                except Exception as e:
                    logging.error(f"Failed to send message to {user['user_id']}: {e}")

def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text("Laundo tumhare lund me pani nikal dungi\nvideo call 🤙 ke liye 10 user ko\nye link sharo karo\naudio call ke liye\n5 user ko link send karo\n\nVIDEO CALL Link 🔗:- https://t.me/girl_sexrbot?start=videocall\nAUDIO CALL Link 🔗:- https://t.me/girl_sexrbot?start=audiocall")
    
    # Save user to database if not already present
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

    # Send a random video from START_VIDEO
    if START_VIDEO:
        random_video = random.choice(START_VIDEO)
        context.bot.send_video(chat_id=user_id, video=random_video, caption="Enjoy this random video!")

def handle_message(update: Update, context: CallbackContext):
    if posts_collection.count_documents({}) > 0:
        post = posts_collection.find_one()
        update.message.reply_text(post['content'])
    else:
        update.message.reply_text("No post is set yet!")

def set_post(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if sudo_users.find_one({"user_id": user_id}):
        if len(context.args) > 0:
            post_content = ' '.join(context.args)
            posts_collection.update_one({}, {"$set": {"content": post_content}}, upsert=True)
            update.message.reply_text("Post has been set!")
        else:
            update.message.reply_text("Usage: /post <content>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def set_autopost(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if sudo_users.find_one({"user_id": user_id}):
        if len(context.args) > 0:
            message = ' '.join(context.args)
            autopost_collection.update_one({}, {"$set": {"content": message}}, upsert=True)
            update.message.reply_text("Autopost message has been set!")
        else:
            update.message.reply_text("Usage: /autopost <message>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def add_sudo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:
        if len(context.args) == 1:
            sudo_id = int(context.args[0])
            if not sudo_users.find_one({"user_id": sudo_id}):
                sudo_users.insert_one({"user_id": sudo_id})
                update.message.reply_text(f"User {sudo_id} added to sudo list!")
            else:
                update.message.reply_text("User is already a sudo user.")
        else:
            update.message.reply_text("Usage: /addsudo <user_id>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def remove_sudo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:
        if len(context.args) == 1:
            sudo_id = int(context.args[0])
            if sudo_users.find_one({"user_id": sudo_id}):
                sudo_users.delete_one({"user_id": sudo_id})
                update.message.reply_text(f"User {sudo_id} removed from sudo list!")
            else:
                update.message.reply_text("User is not a sudo user.")
        else:
            update.message.reply_text("Usage: /rm <user_id>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def main():
    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Add autopost job to scheduler
    scheduler.add_job(send_autopost, trigger=IntervalTrigger(hours=6), args=[updater.bot])

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("post", set_post, pass_args=True))
    dispatcher.add_handler(CommandHandler("autopost", set_autopost, pass_args=True))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo, pass_args=True))
    dispatcher.add_handler(CommandHandler("rm", remove_sudo, pass_args=True))

    # Message Handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
