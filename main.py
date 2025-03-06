import telebot
import random
import requests
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your bot token and channel details
BOT_TOKEN = "8074904664:AAGmKjpGRjtphBk91ABwT_d07l5mZkKt2RY"
CHANNEL_USERNAME = "@dar3658"  # Your Telegram Channel
CHANNEL_LINK = "https://t.me/dar3658"  # Your Channel Link
DATA_FILE = "card_count.json"

bot = telebot.TeleBot(BOT_TOKEN)

# Function to check if a user is in the channel
def is_user_in_channel(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# Load total generated card count
def load_total_count():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            return data.get("total_cards", 0)
    except FileNotFoundError:
        return 0

def save_total_count(count):
    with open(DATA_FILE, "w") as file:
        json.dump({"total_cards": count}, file)

total_cards = load_total_count()

# Function to fetch BIN details
def get_bin_info(bin_number):
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if response.status_code == 200:
            data = response.json()
            bank = data.get("bank", {}).get("name", "Unknown Bank")
            country = data.get("country", {}).get("name", "Unknown Country")
            scheme = data.get("scheme", "Unknown")  # Visa, Mastercard, etc.
            card_type = data.get("type", "Unknown")  # Credit/Debit
            
            return (f"🏦 **Bank:** {bank}\n"
                    f"🌍 **Country:** {country}\n"
                    f"💳 **Scheme:** {scheme}\n"
                    f"🛒 **Type:** {card_type}")
        else:
            return "❌ BIN info not found."
    except Exception as e:
        return f"❌ Error fetching BIN info: {e}"

# Function to generate a random credit card
def generate_card():
    global total_cards
    bin_number = str(random.randint(400000, 499999))
    card_number = bin_number + ''.join([str(random.randint(0, 9)) for _ in range(10)])
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_day = str(random.randint(1, 31)).zfill(2)
    exp_year = str(random.randint(24, 29))
    cvv = str(random.randint(100, 999))
    amount = f"${random.randint(100, 5000)}"

    total_cards += 1
    save_total_count(total_cards)

    return card_number, exp_month, exp_day, exp_year, cvv, amount, total_cards

# Card Checking Function (Simulated)
def check_card(card_number):
    if len(card_number) < 16 or not card_number.isdigit():
        return "❌ Invalid Card Format!"

    bin_number = card_number[:6]
    bin_info = get_bin_info(bin_number)

    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_day = str(random.randint(1, 31)).zfill(2)
    exp_year = str(random.randint(24, 29))
    cvv = str(random.randint(100, 999))

    approved = random.choice([True, False])

    if approved:
        return (f"✅ **Approval Card ✅**\n"
                f"💳 **Card:** `{card_number}|{exp_month}|{exp_day}|{exp_year}|{cvv}`\n"
                f"ℹ️ **Info:**\n{bin_info}\n"
                f"🤖 **Bot:** Dar-X")
    else:
        return (f"❌ **Declined Card ❌**\n"
                f"💳 **Card:** `{card_number}`\n"
                f"ℹ️ **Info:**\n{bin_info}\n"
                f"🤖 **Bot:** Dar-X")

# Start Command with Join Verification
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id

    if is_user_in_channel(user_id):
        bot.send_message(user_id, "✅ **Welcome! You now have full access to the bot.**")
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔹 Join Channel 🔹", url=CHANNEL_LINK))
        keyboard.add(InlineKeyboardButton("✅ Verify", callback_data="check_join"))

        bot.send_message(
            user_id,
            "⚠️ **Access Denied!**\n\n"
            "📌 You must join our channel to use this bot.\n\n"
            "👉 Click the button below to join, then press **Verify**.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# Check if user joined after clicking "Verify"
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_status(call):
    user_id = call.message.chat.id

    if is_user_in_channel(user_id):
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="✅ **Thank you for joining! You now have full access.**"
        )
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined yet. Please join and try again.", show_alert=True)

# Generate Card Command
@bot.message_handler(commands=['gen'])
def send_card(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        send_welcome(message)
        return

    card_number, exp_month, exp_day, exp_year, cvv, amount, total = generate_card()

    response = (f"✅ **CC Generated Successfully**\n"
                f"💳 **Card:** `{card_number}|{exp_month}|{exp_day}|{exp_year}|{cvv}`\n"
                f"💰 **Amount:** `{amount}`\n"
                f"📊 **Total Cards Generated:** `{total}`")

    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# Check Card Command
@bot.message_handler(commands=['chk'])
def check_card_command(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        send_welcome(message)
        return

    bot.send_message(message.chat.id, "✏️ **Send me a Card Number to check.**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_card_check)

def process_card_check(message):
    card_number = message.text.strip().replace(" ", "")
    result = check_card(card_number)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

# Command to check total generated cards
@bot.message_handler(commands=['total'])
def total_generated(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        send_welcome(message)
        return

    bot.send_message(message.chat.id, f"📊 **Total Cards Generated:** `{total_cards}`", parse_mode="Markdown")

# Run the bot
bot.polling()
