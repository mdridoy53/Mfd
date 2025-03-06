import asyncio
import random
import requests
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from luhn import generate

# Replace with your actual bot token
BOT_TOKEN = "8074904664:AAGmKjpGRjtphBk91ABwT_d07l5mZkKt2RY"
OWNER_ID = 7987662357  # Replace with your Telegram ID
CHANNEL_USERNAME = "@dar3658"  # Channel to join

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Database Setup
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        bin TEXT,
        card TEXT,
        bank TEXT,
        country TEXT,
        date TEXT
    )
""")
conn.commit()

async def check_channel_membership(user_id):
    """Check if the user is a member of the channel"""
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except ChatNotFound:
        return False

async def send_join_channel_message(user_id):
    """Send a message with a button to join the channel"""
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("✅ Join Now", url=f"https://t.me/{CHANNEL_USERNAME}")
    keyboard.add(button)
    await bot.send_message(user_id, f"🚨 To use the bot, you need to join the channel first:\n\n{CHANNEL_USERNAME}", reply_markup=keyboard)

def get_bin_info(bin_number):
    """Fetch bank and country info from BIN"""
    apis = [
        f"https://bins.su/lookup/{bin_number}",
        f"https://lookup.binlist.net/{bin_number}"
    ]
    
    for url in apis:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                bank = data.get("bank", {}).get("name", "Unknown")
                country = data.get("country", {}).get("name", "Unknown")
                return bank, country
        except:
            continue
    
    return "Unknown", "Unknown"

def generate_card(bin_prefix):
    """Generate a valid CC number with expiry & CVV"""
    while len(bin_prefix) < 16:
        bin_prefix += str(random.randint(0, 9))

    cc_number = generate(bin_prefix[:15])  # Ensure Luhn valid number
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(25, 30))  # Example: 2025-2030
    cvv = str(random.randint(100, 999))

    return f"{cc_number}|{exp_month}|{exp_year}|{cvv}"

@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    """Welcome message and check if user has joined the channel"""
    user_id = message.from_user.id
    if await check_channel_membership(user_id):
        await message.reply("👋 Welcome to the CC Generator Bot! Now you can use the `/gen <BIN> <quantity>` command.")
    else:
        await send_join_channel_message(user_id)

@dp.message_handler(commands=["gen"])
async def generate_cc(message: Message):
    """Generate multiple CCs based on BIN & quantity"""
    user_id = message.from_user.id
    if not await check_channel_membership(user_id):
        await send_join_channel_message(user_id)
        return
    
    args = message.text.split()
    
    # Validate user input
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("❌ Usage: /gen <BIN> <quantity>\nExample: /gen 52185316 10")
        return

    bin_prefix = args[1]
    quantity = int(args[2]) if len(args) > 2 and args[2].isdigit() else 1

    if quantity < 1 or quantity > 20:  # Limit to 20 cards
        await message.reply("❌ You can generate between 1-20 cards at a time.")
        return

    bank, country = get_bin_info(bin_prefix)
    time_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cards = [generate_card(bin_prefix) for _ in range(quantity)]

    # Save logs to database
    for card in cards:
        cursor.execute("INSERT INTO logs (user_id, username, bin, card, bank, country, date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (message.from_user.id, message.from_user.username, bin_prefix, card, bank, country, time_generated))
    conn.commit()

    response_text = f"""𝗜𝗻𝗳𝗼 -
- 𝐁𝐚𝐧𝐤 - {bank}
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country}
- 𝐓𝐢𝐦𝐞 - {time_generated}
- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - ✅

💳 **Generated {quantity} Cards:**\n""" + "\n".join([f"`{c}`" for c in cards])

    await message.reply(response_text, parse_mode="Markdown")

@dp.message_handler(commands=["logs"])
async def show_logs(message: Message):
    """Show the last 5 generated cards (Admin Only)"""
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ You are not authorized to access logs.")
        return

    cursor.execute("SELECT user_id, username, bin, card, bank, country, date FROM logs ORDER BY id DESC LIMIT 5")
    logs = cursor.fetchall()

    if not logs:
        await message.reply("📜 No logs found.")
        return

    response = "📜 **Last 5 Logs:**\n"
    for log in logs:
        response += f"""
👤 **User:** {log[1]} (ID: {log[0]})
🔹 **BIN:** {log[2]}
💳 **Card:** `{log[3]}`
🏦 **Bank:** {log[4]}
🌍 **Country:** {log[5]}
📅 **Date:** {log[6]}
──────────────
"""
    await message.reply(response, parse_mode="Markdown")

@dp.message_handler(commands=["stats"])
async def show_stats(message: Message):
    """Show bot usage statistics"""
    cursor.execute("SELECT COUNT(*) FROM logs")
    total_generated = cursor.fetchone()[0]

    await message.reply(f"📊 **Bot Statistics:**\n🔹 **Total Cards Generated:** {total_generated}")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
