from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SESSION_STRING = os.getenv("SESSION_STRING", "")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))
