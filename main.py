import telebot
import requests

# Replace with your bot token and channel username
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "@dar3658"  # Your channel username
CHANNEL_LINK = "https://t.me/dar3658"  # Your channel link

bot = telebot.TeleBot(BOT_TOKEN)

# Function to check if a user is in the channel
def is_user_in_channel(user_id):
    try:
        response = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if response.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception as e:
        return False

# Start Command with Membership Check
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if is_user_in_channel(user_id):
        bot.send_message(user_id, "✅ **Welcome! You have access to the bot.**")
    else:
        bot.send_message(
            user_id,
            f"⚠️ **Access Denied!**\n\n"
            f"📌 You must join our channel first: [Join Now]({CHANNEL_LINK})\n"
            f"Then, press /start again.",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

# Run the bot
bot.polling()
