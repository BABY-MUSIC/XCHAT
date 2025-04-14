import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatMemberUpdated
)
from motor.motor_asyncio import AsyncIOMotorClient

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# MongoDB setup
MONGO_URL = "mongodb+srv://teamdaxx123:teamdaxx123@cluster0.ysbpgcp.mongodb.net/?retryWrites=true&w=majority"
mongo_client = AsyncIOMotorClient(MONGO_URL)
word_db = mongo_client["Word"]["WordDb"]

# Bot credentials
API_ID = "16457832"
API_HASH = "3030874d0befdb5d05597deacc3e83ab"
BOT_TOKEN = "7344081617:AAFWVEyMRF2HSTEsPTuuJ7v0sHu0U2LEt6A"

# Constants
RADHIKA = Client("my_bot_radhika", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
CHANNEL_ID = "RadhikaCommunity"
MESSAGE_ID = 2357
OWNER_ID = 6657539971
SUPPORT_URL = "https://t.me/+gF7M1_0PC803ZjU9"

# ⏬ /start कमांड हैंडलर
@RADHIKA.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_mention = message.from_user.mention
    user_id = message.from_user.id
    chat_id = message.chat.id

    # MongoDB में यूजर सेव करें
    existing_user = await word_db["Users"].find_one({"user_id": user_id})
    if not existing_user:
        await word_db["Users"].insert_one({"user_id": user_id})
    
    total_users = await word_db["Users"].count_documents({})

    # Owner को notify करें
    notify_text = (
        f"👤 **New User Started Bot**\n\n"
        f"🔹 **User:** {user_mention}\n"
        f"🔹 **Chat ID:** `{chat_id}`\n"
        f"🔹 **Total Users:** `{total_users}`"
    )
    try:
        await client.send_message(OWNER_ID, notify_text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")

    # Message Forward करें
    try:
        await client.forward_messages(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_ids=MESSAGE_ID)
    except Exception as e:
        await message.reply_text("Something went wrong while forwarding the message.")

# ⏬ जब बॉट ग्रुप में ऐड हो
@RADHIKA.on_chat_member_updated()
async def on_new_group_join(client: Client, event: ChatMemberUpdated):
    try:
        # अगर बॉट ऐड हुआ है ग्रुप में
        if event.new_chat_member and event.new_chat_member.user.id == (await client.get_me()).id:
            chat = await client.get_chat(event.chat.id)
            adder = event.from_user

            # 1. MongoDB में ग्रुप सेव करें
            group_data = await word_db["Groups"].find_one({"chat_id": chat.id})
            if not group_data:
                await word_db["Groups"].insert_one({"chat_id": chat.id})

            # 2. ग्रुप में Welcome मैसेज भेजें
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("Full Open Video Call 👄", url="https://t.me/RadhikaCallBot?start=call")]
            ])
            await client.send_message(
                chat_id=chat.id,
                text=f"👋 {adder.mention} Thanks\n__Video & audio call available with zoom Come Fast 💦💦__",
                reply_markup=join_button
            )

            # 3. Owner को ग्रुप की जानकारी भेजें
            try:
                # Invite link generate करें
                if chat.username:
                    invite_link = f"https://t.me/{chat.username}"
                else:
                    try:
                        invite = await client.create_chat_invite_link(chat.id, creates_join_request=False)
                        invite_link = invite.invite_link
                    except Exception:
                        invite_link = "❌ Failed to generate invite link"

                total_groups = await word_db["Groups"].count_documents({})
                await client.send_message(
                    OWNER_ID,
                    f"📢 **Bot Added to Group**\n\n"
                    f"👤 **Added By:** {adder.mention} (`{adder.id}`)\n"
                    f"👥 **Group Name:** {chat.title}\n"
                    f"🔗 **Invite Link:** {invite_link}\n"
                    f"📊 **Total Groups:** {total_groups}"
                )
            except Exception as e:
                logger.error(f"Failed to notify OWNER: {e}")

    except Exception as e:
        logger.error(f"Error in group join handler: {e}")

# ⏬ Main run
if __name__ == "__main__":
    try:
        logger.info("Radhika started...")
        RADHIKA.run()
    except Exception as e:
        logger.error(f"Error running the bot: {e}")
