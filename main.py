from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb+srv://Yash_607:Yash_607@cluster0.r3s9sbo.mongodb.net/?retryWrites=true&w=majority")
db = client['telegram_bot']
collection = db['posts']
sudo_users = db['sudo_users']

# Owner ID (Replace with your Telegram ID)
OWNER_ID = 7400383704  # Replace with your Telegram ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello 👋")

def handle_message(update: Update, context: CallbackContext):
    if collection.count_documents({}) > 0:
        post = collection.find_one()
        update.message.reply_text(post['content'])
    else:
        update.message.reply_text("No post is set yet!")

def set_post(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if sudo_users.find_one({"user_id": user_id}):
        if len(context.args) > 0:
            post_content = ' '.join(context.args)
            collection.update_one({}, {"$set": {"content": post_content}}, upsert=True)
            update.message.reply_text("Post has been set!")
        else:
            update.message.reply_text("Usage: /post <content>")
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

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("post", set_post, pass_args=True))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo, pass_args=True))
    dispatcher.add_handler(CommandHandler("rm", remove_sudo, pass_args=True))

    # Message Handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

