"""
Run this script ONCE locally to generate your Telethon session string.
Copy the output and add it to your .env as SESSION_STRING=...

"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH

print("Generating Telethon session string...")
print("You will be asked to enter your phone number and the code Telegram sends you.\n")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session_string = client.session.save()

print("\n" + "=" * 60)
print("YOUR SESSION STRING (copy this into your .env):")
print("=" * 60)
print(f"SESSION_STRING={session_string}")
print("=" * 60)
print("\nKeep this secret! It gives full access to your Telegram account.")
