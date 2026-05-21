import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = os.getenv("OWNER_ID", None)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database
DB_PATH = os.getenv("DB_PATH", "disputes.db")

# Dispute Categories
DISPUTE_CATEGORIES = [
    "Item Not Received",
    "Item Not as Described",
    "Quality Issue",
    "Damaged Item",
    "Wrong Item",
    "Partial Shipment",
    "Other"
]

# Priority Levels (Based on urgency keywords)
PRIORITY_KEYWORDS = {
    "urgent": 5,
    "asap": 5,
    "immediately": 5,
    "critical": 4,
    "important": 3,
    "soon": 2,
}

# Sentiment thresholds
SENTIMENT_POSITIVE = 0.1
SENTIMENT_NEGATIVE = -0.1
