# 🚀 Quick Start Guide

## Step 1: Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt
```

## Step 2: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts to create a new bot
4. Copy the **bot token** provided

## Step 3: Configure Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and paste your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

3. (Optional) Add your Telegram user ID as `OWNER_ID` for admin commands

## Step 4: Run the Bot

```bash
python chat.py
```

You should see:
```
🤖 Order Dispute Resolution Bot started
```

## Step 5: Test the Bot

1. Search for your bot on Telegram (use the username from BotFather)
2. Click "Start" or send `/dispute`
3. Follow the conversation flow:
   - Enter email: user@example.com
   - Enter order ID: ORDER123
   - Select category
   - Describe the issue
   - Review and submit

## Common Issues

**Bot not responding?**
- Double-check your token in `.env`
- Restart the bot: `python chat.py`

**Database error?**
- Delete `disputes.db` file and restart
- Bot will recreate it automatically

## Features Overview

✅ **Email Validation** - Ensures valid email format
✅ **Order ID Validation** - Checks order ID format
✅ **Sentiment Analysis** - Understands customer emotion
✅ **Auto-Classification** - Categorizes issues automatically
✅ **Priority Calculation** - Assigns urgency levels
✅ **Data Storage** - Saves all disputes to database
✅ **Statistics** - View dispute analytics with `/stats`

## Next Steps

- Check [README.md](README.md) for detailed documentation
- Customize categories in `config.py`
- Review dispute data in `disputes.db`
- Integrate with your system for automated responses

---

**Happy resolving! 🎉**
