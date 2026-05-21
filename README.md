# 🤖 Order Dispute Resolution Chatbot

An intelligent Telegram chatbot designed to help resolve order disputes efficiently and intelligently.

## Features

✨ **Intelligent Features:**
- 🧠 **NLP-based Sentiment Analysis** - Understands customer emotions
- 🎯 **Auto-Classification** - Categorizes disputes based on description
- 📊 **Priority Calculation** - Automatically assigns priority levels
- 💾 **Data Storage** - Stores all disputes in SQLite for analysis
- 🔍 **Email & Order Validation** - Ensures data integrity
- 📈 **Statistics & Analytics** - View dispute trends and metrics

## Supported Dispute Categories

- Item Not Received
- Item Not as Described
- Quality Issue
- Damaged Item
- Wrong Item
- Partial Shipment
- Other

## Requirements

- Python 3.8+
- Telegram Bot Token
- Dependencies (see requirements.txt)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd chatbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy language model (optional, for enhanced NLP):**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Create a .env file:**
   ```bash
   cp .env.example .env
   ```

5. **Configure your .env file:**
   - Get a bot token from [BotFather](https://t.me/botfather) on Telegram
   - Add your token to the `TELEGRAM_BOT_TOKEN` variable
   - Optionally, add your Telegram user ID as `OWNER_ID`

## Usage

### Starting the Bot

```bash
python chat.py
```

### Telegram Commands

- `/start` or `/dispute` - Begin submitting a new dispute
- `/help` - Show available commands and instructions
- `/stats` - View dispute statistics
- `/cancel` - Cancel current operation

### User Flow

1. User starts the bot with `/dispute`
2. Bot asks for email address (validated)
3. Bot asks for order ID (validated)
4. User selects dispute category from preset options
5. User provides detailed description
6. Bot analyzes sentiment and auto-classifies if needed
7. Bot shows summary for confirmation
8. User confirms or starts over
9. Dispute is saved to database
10. Confirmation sent to user

## How the AI Makes It Intelligent

### Sentiment Analysis
Uses TextBlob to analyze the emotional tone of the dispute description:
- **Positive**: Customer is cooperative
- **Negative**: Customer is upset (may need escalation)
- Sentiment score influences priority

### Priority Calculation
Based on:
- Urgency keywords (urgent, asap, critical, etc.)
- Sentiment score
- Automatically assigned 1-5 priority level

### Auto-Classification
Analyzes description text to identify dispute category:
- "not received" → Item Not Received
- "damaged" → Damaged Item
- "broken" → Quality Issue
- Etc.

### Data Validation
- Email format validation (RFC 5322)
- Order ID format validation (5+ alphanumeric characters)
- Description length validation

## Database Schema

### disputes table
```sql
CREATE TABLE disputes (
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
```

## Configuration

Edit `config.py` to customize:
- Dispute categories
- Priority keywords
- Sentiment thresholds
- Database path
- Logging level

## Project Structure

```
chatbot/
├── chat.py              # Main bot application
├── config.py            # Configuration settings
├── dispute_handler.py   # Dispute analysis & storage
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Example Scenarios

### Scenario 1: Item Not Received
```
User: I ordered something but never got it
Bot: [Analyzes sentiment: Slightly negative]
Bot: [Detects category: Item Not Received]
Bot: [Assigns priority: 3/5]
```

### Scenario 2: Angry Customer
```
User: This is urgent! I ordered a phone 2 weeks ago and received a broken device!
Bot: [Analyzes sentiment: Very negative]
Bot: [Detects category: Damaged Item]
Bot: [Detects keywords: "urgent"]
Bot: [Assigns priority: 5/5 - High Priority]
```

## Tips for Best Results

1. **Provide Detailed Information** - More details help the bot classify and analyze better
2. **Use Natural Language** - Write as you normally would
3. **Include Dates** - Mention when you ordered or when the issue occurred
4. **Be Specific** - Describe exactly what's wrong with the item

## Troubleshooting

**Bot not responding:**
- Check if TELEGRAM_BOT_TOKEN is set correctly in .env
- Verify internet connection
- Check bot logs for errors

**Database errors:**
- Delete `disputes.db` to reset
- Check file permissions

**NLP not working:**
- Ensure spaCy/TextBlob are installed
- Try: `pip install --upgrade spacy textblob`

## Future Enhancements

- 🔗 Integration with order management systems
- 📧 Automated email notifications
- 🤖 Machine learning for better classification
- 👥 Multi-language support
- 📱 Image/document upload for proof
- ⚙️ Admin dashboard for dispute management

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, create an issue or contact the developer.

---

**Created with ❤️ for efficient dispute resolution**
#chatbot
