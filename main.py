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
client = MongoClient("mongodb+srv://Yash_607:Yash_607@cluster0.r3s9sbo.mongodb.net/?retryWrites=true&w=majority")
db = client['telegram_bot']
posts_collection = db['posts']
sudo_users = db['sudo_users']
autopost_collection = db['autopost']
users_collection = db['users']

# Owner ID (Replace with your Telegram ID)
OWNER_ID = 7400383704  # Replace with your Telegram ID

# Video Links for /start
START_VIDEO = [
        "https://te.legra.ph/file/a66008b78909b431fc92b.mp4",
        "https://te.legra.ph/file/0ab82f535e1193d09c0e4.mp4",
        "https://te.legra.ph/file/1ab9cde9388117db9d26c.mp4",
        "https://te.legra.ph/file/75e49339469dbf9ad1dd2.mp4",
        "https://telegra.ph/file/9bcc076fd81dfe3feb291.mp4",
        "https://telegra.ph/file/b7a1a42429a65f64e67af.mp4",
        "https://telegra.ph/file/dc3da5a3eb77ae20fa21d.mp4",
        "https://telegra.ph/file/7b15fbca08ae1e73e559c.mp4",
        "https://telegra.ph/file/a9c1dea3f34925bb60686.mp4",
        "https://telegra.ph/file/913b4e567b7f435b7f0db.mp4",
        "https://telegra.ph/file/5a5d1a919a97af2314955.mp4",
        "https://telegra.ph/file/0f8b903669600d304cbe4.mp4",
        "https://telegra.ph/file/f3816b54c9eb7617356b6.mp4",
        "https://telegra.ph/file/516dbaa03fde1aaa70633.mp4",
        "https://telegra.ph/file/07bba6ead0f1e381b1bd1.mp4",
        "https://telegra.ph/file/0a4f7935df9b4ab8d62ed.mp4",
        "https://telegra.ph/file/40966bf68c0e4dbe18058.mp4",
        "https://telegra.ph/file/50637aa9c04d136687523.mp4",
        "https://telegra.ph/file/b81c0b0e491da73e64260.mp4",
        "https://telegra.ph/file/4ddf5f29783d92ae03804.mp4",
        "https://telegra.ph/file/4037dc2517b702cc208b1.mp4",
        "https://telegra.ph/file/33cebe2798c15d52a2547.mp4",
        "https://telegra.ph/file/4dc3c8b03616da516104a.mp4",
        "https://telegra.ph/file/6b148dace4d987fae8f3e.mp4",
        "https://telegra.ph/file/8cb081db4eeed88767635.mp4",
        "https://telegra.ph/file/98d3eb94e6f00ed56ef91.mp4",
        "https://telegra.ph/file/1fb387cf99e057b62d75d.mp4",
        "https://telegra.ph/file/6e1161f63879c07a1f213.mp4",
        "https://telegra.ph/file/0bf4defb9540d2fa6d277.mp4",
        "https://telegra.ph/file/d5f8280754d9aa5dffa6a.mp4",
        "https://telegra.ph/file/0f23807ed1930704e2bef.jpg",
        "https://telegra.ph/file/c49280b8f1dcecaf86c00.jpg",
        "https://telegra.ph/file/f483400ff141de73767ca.jpg",
        "https://telegra.ph/file/1543bbea4e3c1abb6764a.jpg",
        "https://telegra.ph/file/a0d77be0d769c7cd334ab.jpg",
        "https://telegra.ph/file/6c6e93860527d2f577df8.jpg",
        "https://telegra.ph/file/d987b0e72eb3bb4801f01.jpg",
        "https://telegra.ph/file/b434999287d3580250960.jpg",
        "https://telegra.ph/file/0729cc082bf97347988f7.jpg",
        "https://telegra.ph/file/bb96d25df82178a2892e7.jpg",
        "https://telegra.ph/file/be73515791ea33be92a7d.jpg",
        "https://telegra.ph/file/fe234d6273093282d2dcc.jpg",
        "https://telegra.ph/file/66254bb72aa8094d38250.jpg",
        "https://telegra.ph/file/44bdaf37e5f7bdfc53ac6.jpg",
        "https://telegra.ph/file/e561ee1e1ca88db7e8038.jpg",
        "https://telegra.ph/file/f1960ccfc866b29ea5ad2.jpg",
        "https://telegra.ph/file/97622cad291472fb3c4aa.jpg",
        "https://telegra.ph/file/a46e316b413e9dc43e91b.jpg",
        "https://telegra.ph/file/497580fc3bddc21e0e162.jpg",
        "https://telegra.ph/file/3e86cc6cab06a6e2bde82.jpg",
        "https://telegra.ph/file/83140e2c57ddd95f310e6.jpg",
        "https://telegra.ph/file/2b20f8509d9437e94fed5.jpg",
        "https://telegra.ph/file/571960dcee4fce56698a4.jpg",
        "https://telegra.ph/file/25929a0b49452d8946c14.mp4",
        "https://telegra.ph/file/f5c9ceded3ee6e76a5931.jpg",
        "https://telegra.ph/file/a8bf6c6df8a48e4a306ca.jpg",
        "https://telegra.ph/file/af9e3f98da0bd937adf6e.jpg",
        "https://telegra.ph/file/2fcccbc72c57b6892d23a.jpg",
        "https://telegra.ph/file/843109296a90b8a6c5f68.jpg"
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
    updater = Updater("7880735724:AAFrwbMyRP-L7rDqTQxca61H_NyFwxNZ5f8", use_context=True)
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
    
