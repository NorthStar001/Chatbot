import logging
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, DISPUTE_CATEGORIES, LOG_LEVEL
from dispute_handler import DisputeHandler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Conversation states
EMAIL, ORDER_ID, CATEGORY, DESCRIPTION, CONFIRMATION = range(5)

# Initialize dispute handler
dispute_handler = DisputeHandler()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for email."""
    user = update.effective_user
    
    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the *Order Dispute Resolution Bot*. 🤖\n\n"
        "I'm here to help you resolve order issues quickly and efficiently.\n"
        "Let's get started by collecting some information.\n\n"
        "_Please provide your email address associated with your order._"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate email."""
    email = update.message.text.strip()
    
    is_valid, message = dispute_handler.validate_email(email)
    
    if not is_valid:
        await update.message.reply_text(
            f"❌ {message}\n\n_Please try again._",
            parse_mode='Markdown'
        )
        return EMAIL
    
    context.user_data['email'] = email
    logger.info(f"Email collected from {update.effective_user.id}: {email}")
    
    await update.message.reply_text(
        f"✅ Great! Email saved: `{email}`\n\n"
        "_Now, please provide your Order ID._",
        parse_mode='Markdown'
    )
    
    return ORDER_ID


async def receive_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate order ID."""
    order_id = update.message.text.strip().upper()
    
    is_valid, message = dispute_handler.validate_order_id(order_id)
    
    if not is_valid:
        await update.message.reply_text(
            f"❌ {message}\n\n_Please try again._",
            parse_mode='Markdown'
        )
        return ORDER_ID
    
    context.user_data['order_id'] = order_id
    logger.info(f"Order ID collected from {update.effective_user.id}: {order_id}")
    
    # Show category buttons
    keyboard = [[category] for category in DISPUTE_CATEGORIES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Order ID saved: `{order_id}`\n\n"
        "_What type of issue are you facing? Select from the options below:_",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    return CATEGORY


async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive dispute category."""
    category = update.message.text.strip()
    
    if category not in DISPUTE_CATEGORIES:
        keyboard = [[cat] for cat in DISPUTE_CATEGORIES]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "❌ Please select a valid category.",
            reply_markup=reply_markup
        )
        return CATEGORY
    
    context.user_data['category'] = category
    logger.info(f"Category selected from {update.effective_user.id}: {category}")
    
    await update.message.reply_text(
        f"✅ Category selected: *{category}*\n\n"
        "_Please describe the issue in detail. Include what happened, when it happened, and any other relevant information._",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and analyze description."""
    description = update.message.text.strip()
    
    if len(description) < 10:
        await update.message.reply_text(
            "❌ Please provide more details (at least 10 characters).",
        )
        return DESCRIPTION
    
    context.user_data['description'] = description
    
    # Analyze the description
    sentiment = dispute_handler.analyze_sentiment(description)
    context.user_data['sentiment'] = sentiment
    
    # Auto-classify if not explicitly selected
    if 'category' not in context.user_data or context.user_data['category'] == "Other":
        detected_category = dispute_handler.classify_category(description)
        context.user_data['category'] = detected_category
    
    logger.info(f"Description received from {update.effective_user.id}, sentiment: {sentiment}")
    
    # Generate response suggestion
    priority = dispute_handler.calculate_priority(description, sentiment)
    suggestion = dispute_handler.generate_response_suggestion(sentiment, priority)
    
    # Show summary
    summary = (
        "*📋 Dispute Summary:*\n\n"
        f"📧 Email: `{context.user_data['email']}`\n"
        f"📦 Order ID: `{context.user_data['order_id']}`\n"
        f"🏷️ Category: *{context.user_data['category']}*\n"
        f"📝 Description: _{description}_\n\n"
        f"🔍 Analysis: {suggestion}\n\n"
        "_Is this information correct?_"
    )
    
    keyboard = [["✅ Yes, Submit"], ["❌ No, Start Over"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
    
    return CONFIRMATION


async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and save the dispute."""
    response = update.message.text.strip()
    
    if response == "❌ No, Start Over":
        context.user_data.clear()
        return await start(update, context)
    
    elif response == "✅ Yes, Submit":
        # Save to database
        success = dispute_handler.save_dispute(
            user_id=update.effective_user.id,
            email=context.user_data['email'],
            order_id=context.user_data['order_id'],
            category=context.user_data['category'],
            description=context.user_data['description']
        )
        
        if success:
            confirmation_msg = (
                "✅ *Thank you!* Your dispute has been submitted successfully.\n\n"
                "🎫 Dispute Details:\n"
                f"• Order ID: `{context.user_data['order_id']}`\n"
                f"• Category: *{context.user_data['category']}*\n"
                f"• Priority Level: 🔴 High\n\n"
                "📧 We'll send updates to your email address.\n"
                "⏱️ Expected resolution time: 3-5 business days.\n\n"
                "_Use /help for more options or /dispute for another dispute._"
            )
            
            await update.message.reply_text(
                confirmation_msg,
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
            
            logger.info(f"Dispute saved successfully for user {update.effective_user.id}")
        else:
            await update.message.reply_text(
                "❌ Error saving dispute. Please try again later.",
                reply_markup=ReplyKeyboardRemove()
            )
    
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "❌ Dispute submission cancelled.\n\n"
        "_Use /dispute to start again or /help for assistance._",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    help_text = (
        "*🤖 Order Dispute Resolution Bot - Help*\n\n"
        "*Available Commands:*\n"
        "🔹 /start - Begin a new dispute\n"
        "🔹 /dispute - Submit a new dispute\n"
        "🔹 /help - Show this help message\n"
        "🔹 /stats - View dispute statistics\n"
        "🔹 /cancel - Cancel current operation\n\n"
        "*How it works:*\n"
        "1️⃣ Provide your email address\n"
        "2️⃣ Enter your order ID\n"
        "3️⃣ Select the issue category\n"
        "4️⃣ Describe the problem in detail\n"
        "5️⃣ Review and submit\n\n"
        "_Our AI will analyze your case and prioritize it accordingly._"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show dispute statistics."""
    stats = dispute_handler.get_dispute_stats()
    
    stats_text = (
        "*📊 Dispute Statistics*\n\n"
        f"📈 Total Disputes: {stats.get('total', 0)}\n"
        f"✅ Resolved: {stats.get('resolved', 0)}\n"
        f"⏳ Pending: {stats.get('pending', 0)}\n"
        f"😊 Avg Sentiment: {stats.get('avg_sentiment', 0)}\n"
        f"🔴 Avg Priority: {stats.get('avg_priority', 0)}/5"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("dispute", start),
        ],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order_id)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_submission)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    logger.info("🤖 Order Dispute Resolution Bot started")
    
    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()
