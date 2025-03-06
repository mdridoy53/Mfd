import random
import requests
import datetime
from faker import Faker
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram Bot Token
TOKEN = "7685065199:AAG7zSGqItTRJCVLcP-KgGLGGBb71inB_Cs"

# Required Channel (Users must join)
CHANNEL_USERNAME = "@Ravanv4"

# Initialize Faker for generating random names
fake = Faker()

# Check if user is a channel member
def is_user_member(user_id, bot):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# Get BIN info
def get_bin_info(bin_number):
    url = f"https://lookup.binlist.net/{bin_number}"
    response = requests.get(url, headers={"Accept-Version": "3"})
    if response.status_code == 200:
        data = response.json()
        bank = data.get("bank", {}).get("name", "Unknown")
        country = data.get("country", {}).get("name", "Unknown")
        scheme = data.get("scheme", "Unknown").title()
        card_type = data.get("type", "Unknown").title()
        return f"**BIN Info:**\n🔹 **BIN:** {bin_number}\n🏦 **Bank:** {bank}\n🌍 **Country:** {country}\n💳 **Brand:** {scheme}\n🔄 **Type:** {card_type}"
    else:
        return "❌ Invalid BIN or API error!"

# Generate a Luhn-valid card number
def luhn_generate(bin_number):
    card_number = [int(digit) for digit in bin_number]
    while len(card_number) < 15:
        card_number.append(random.randint(0, 9))
    check_sum = sum((2 * d if i % 2 == 0 else d) - 9 if (2 * d) > 9 else (2 * d if i % 2 == 0 else d) for i, d in enumerate(card_number[::-1]))
    card_number.append((10 - (check_sum % 10)) % 10)
    return ''.join(map(str, card_number))

# Generate expiry date and CVV
def generate_expiry():
    return f"{random.randint(1, 12):02d}/{random.randint(datetime.datetime.now().year % 100 + 1, datetime.datetime.now().year % 100 + 5)}"

def generate_cvv():
    return str(random.randint(100, 999))

# Simulate card checking (Random Approval/Decline)
def check_card(card_number, expiry, cvv):
    return f"✅ **Approved ✅**\n🔹 **Card:** {card_number} | {expiry} | {cvv}\n💳 **Status:** Live & Working!\n🤖 **Bot:** Ravan 4.3v" if random.choice([True, False]) else f"❌ **Declined ❌**\n🔹 **Card:** {card_number} | {expiry} | {cvv}\n⚠ **Status:** Declined or Not Working!\n🤖 **Bot:** Ravan 4.3v"

# Fake payment processing function
def process_payment(amount, card_number, expiry, cvv):
    response = requests.post("https://random-payment-api.com/pay", json={"amount": amount, "card": card_number, "expiry": expiry, "cvv": cvv})
    return f"✅ **Payment Successful ✅**\n💰 **Amount:** ${amount}\n🔹 **Card:** {card_number} | {expiry} | {cvv}\n🛒 **Status:** Processed!\n🤖 **Bot:** Ravan 4.3v" if response.status_code == 200 else f"❌ **Payment Failed ❌**\n💰 **Amount:** ${amount}\n🔹 **Card:** {card_number} | {expiry} | {cvv}\n⚠ **Status:** Declined!\n🤖 **Bot:** Ravan 4.3v"

# Generate random email combos and save to Combo.txt
def generate_combo(amount):
    domains = ["gmail.com", "outlook.com", "yahoo.com"]
    combos = []

    for _ in range(amount):
        name = fake.first_name().lower() + str(random.randint(10, 99))
        email = f"{name}@{random.choice(domains)}"
        password = fake.password(length=10)
        combo = f"{email}:{password}"
        combos.append(combo)

    with open("Combo.txt", "w") as file:
        file.write("\n".join(combos))

    return combos

# Command Handlers
def bin_lookup(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /bin <BIN>")
        return
    update.message.reply_text(get_bin_info(context.args[0]), parse_mode="Markdown")

def gen_card(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /gen <BIN> [Amount] (Max 6 digits, Max 10 cards)")
        return
    bin_number, amount = context.args[0], min(int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 1, 10)
    update.message.reply_text("\n".join(f"{luhn_generate(bin_number)} | {generate_expiry()} | {generate_cvv()}" for _ in range(amount)))

def chk_card(update: Update, context: CallbackContext):
    if len(context.args) != 3:
        update.message.reply_text("Usage: /chk <Card_Number> <Expiry (MM/YY)> <CVV>")
        return
    update.message.reply_text(check_card(*context.args), parse_mode="Markdown")

def pay(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        update.message.reply_text("Usage: /pay <Amount> <Card_Number> <Expiry (MM/YY)> <CVV>")
        return
    update.message.reply_text(process_payment(*context.args), parse_mode="Markdown")

def combo(update: Update, context: CallbackContext):
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Usage: /combo <AMOUNT> (Max 50)")
        return
    amount = min(int(context.args[0]), 50)
    generate_combo(amount)
    update.message.reply_document(open("Combo.txt", "rb"), caption=f"✅ **Generated {amount} Combos**\n📂 **Saved as:** Combo.txt\n🤖 **Bot:** Ravan 4.3v")

# Main function to start the bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("bin", bin_lookup))
    dp.add_handler(CommandHandler("gen", gen_card))
    dp.add_handler(CommandHandler("chk", chk_card))
    dp.add_handler(CommandHandler("pay", pay))
    dp.add_handler(CommandHandler("combo", combo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
