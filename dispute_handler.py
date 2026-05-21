import re
import sqlite3
from datetime import datetime
from typing import Dict, Tuple, Optional
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)


class DisputeHandler:
    """Handles dispute information collection and analysis."""

    def __init__(self, db_path: str = "disputes.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disputes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                order_id TEXT NOT NULL,
                category TEXT,
                description TEXT,
                sentiment REAL,
                priority INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()

    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return True, "Email is valid."
        return False, "Please provide a valid email address (e.g., user@example.com)."

    def validate_order_id(self, order_id: str) -> Tuple[bool, str]:
        """Validate order ID format (alphanumeric, 5+ chars)."""
        order_pattern = r'^[A-Za-z0-9]{5,}$'
        if re.match(order_pattern, order_id):
            return True, "Order ID is valid."
        return False, "Please provide a valid order ID (at least 5 alphanumeric characters)."

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the description."""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    def calculate_priority(self, text: str, sentiment: float) -> int:
        """Calculate priority based on keywords and sentiment."""
        from config import PRIORITY_KEYWORDS
        
        priority = 1  # Default priority
        text_lower = text.lower()
        
        # Check for priority keywords
        for keyword, value in PRIORITY_KEYWORDS.items():
            if keyword in text_lower:
                priority = max(priority, value)
        
        # Increase priority if very negative sentiment
        if sentiment < -0.5:
            priority = max(priority, 4)
        
        return min(priority, 5)  # Cap at 5

    def classify_category(self, description: str) -> Optional[str]:
        """Classify the dispute into a category based on description."""
        from config import DISPUTE_CATEGORIES
        
        text_lower = description.lower()
        
        # Simple keyword matching for classification
        category_keywords = {
            "Item Not Received": ["not received", "didn't receive", "never arrived", "missing"],
            "Item Not as Described": ["not as described", "different from description", "doesn't match", "misleading"],
            "Quality Issue": ["poor quality", "low quality", "defective", "broken", "doesn't work"],
            "Damaged Item": ["damaged", "broken", "cracked", "shattered", "torn"],
            "Wrong Item": ["wrong item", "incorrect item", "sent wrong", "not what i ordered"],
            "Partial Shipment": ["partial", "incomplete", "missing items", "didn't send all"],
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "Other"

    def save_dispute(self, user_id: int, email: str, order_id: str, 
                    category: str, description: str) -> bool:
        """Save dispute to database."""
        try:
            sentiment = self.analyze_sentiment(description)
            priority = self.calculate_priority(description, sentiment)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO disputes 
                (user_id, email, order_id, category, description, sentiment, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, email, order_id, category, description, sentiment, priority))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Dispute saved for user {user_id}: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving dispute: {e}")
            return False

    def get_dispute_stats(self) -> Dict:
        """Get statistics about disputes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM disputes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM disputes WHERE resolved = 1")
            resolved = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(sentiment) FROM disputes")
            avg_sentiment = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(priority) FROM disputes")
            avg_priority = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total": total,
                "resolved": resolved,
                "pending": total - resolved,
                "avg_sentiment": round(avg_sentiment, 2),
                "avg_priority": round(avg_priority, 2)
            }
        except Exception as e:
            logger.error(f"Error getting dispute stats: {e}")
            return {}

    def generate_response_suggestion(self, sentiment: float, priority: int) -> str:
        """Generate a response suggestion based on sentiment and priority."""
        if sentiment < -0.5 and priority >= 4:
            return "⚠️ *High Priority* - This customer is very upset. Immediate escalation recommended."
        elif sentiment < -0.1:
            return "😟 The customer seems dissatisfied. A prompt resolution is needed."
        elif sentiment > 0.5:
            return "😊 The customer is cooperative. Standard dispute resolution should work."
        else:
            return "📋 Neutral sentiment. Proceed with standard dispute handling."
