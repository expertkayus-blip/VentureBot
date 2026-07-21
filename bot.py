import os
import asyncio
import logging
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Business ideas list
BUSINESS_IDEAS = [
    "🚀 **AI-Powered Personal Shopping Assistant** - Create an AI that helps users find the best deals and products based on their preferences and budget.",
    
    "💡 **Remote Team Building Platform** - Develop a platform with virtual team building activities, games, and challenges for remote companies.",
    
    "📱 **Mental Health Check-in App** - Build an app that sends daily mental health check-ins and provides resources based on user responses.",
    
    "🌱 **Sustainable Product Marketplace** - Create a marketplace exclusively for eco-friendly and sustainable products with carbon footprint tracking.",
    
    "💻 **No-Code Automation Tool** - Develop a tool that allows non-technical users to automate their workflows without coding.",
    
    "📚 **Personalized Learning Platform** - Build an AI-powered platform that creates custom learning paths for users based on their goals and learning style.",
    
    "🍽️ **Meal Planning & Grocery Delivery** - Create a service that plans weekly meals, generates shopping lists, and delivers groceries.",
    
    "🏋️ **Fitness Progress Tracker** - Develop an app that uses computer vision to track workout form and progress over time.",
    
    "🎓 **Skill-Based Micro-Learning** - Build a platform offering 5-minute daily lessons on various skills with gamification.",
    
    "🏠 **Smart Home Energy Management** - Create a system that optimizes home energy usage and provides cost-saving recommendations.",
    
    "🚗 **EV Charging Station Locator** - Develop an app that shows real-time availability of EV charging stations with booking features.",
    
    "💼 **Freelancer Portfolio Builder** - Build a tool that helps freelancers create professional portfolios and find clients.",
    
    "🎮 **Educational Gaming Platform** - Create games that teach coding, languages, or other skills through interactive play.",
    
    "📊 **Social Media Analytics Tool** - Develop a comprehensive analytics tool for content creators across multiple platforms.",
    
    "🏦 **Personal Finance Coach** - Build an AI-powered app that analyzes spending habits and provides personalized financial advice."
]

# Store active jobs
active_jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"🌟 **Welcome to Venture1 Bot!** 🌟\n\n"
        f"Hello {user.first_name}! I'm here to share amazing business ideas with you.\n\n"
        f"**Commands:**\n"
        f"📌 /start - Show this message\n"
        f"▶️ /start_bot - Start posting business ideas every 5 minutes\n"
        f"⏹️ /stop_bot - Stop posting business ideas\n"
        f"💡 /idea - Get a random business idea now\n"
        f"📊 /status - Check bot status\n\n"
        f"**How to use in groups/channels:**\n"
        f"1. Add me as an admin to your group or channel\n"
        f"2. Use /start_bot to begin posting\n"
        f"3. I'll automatically detect where to post!",
        parse_mode='Markdown'
    )

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /idea command - send random business idea"""
    idea_text = random.choice(BUSINESS_IDEAS)
    await update.message.reply_text(
        f"💡 **Business Idea**\n\n{idea_text}",
        parse_mode='Markdown'
    )

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start posting business ideas every 5 minutes"""
    chat_id = update.effective_chat.id
    
    # Check if bot is already running for this chat
    if chat_id in active_jobs and active_jobs[chat_id]:
        await update.message.reply_text(
            "⚠️ Bot is already running in this chat! Use /stop_bot to stop it first."
        )
        return
    
    # Create a job for this chat
    job_queue = context.job_queue
    if job_queue:
        job = job_queue.run_repeating(
            post_idea,
            interval=300,  # 5 minutes (300 seconds)
            first=5,  # Start after 5 seconds
            chat_id=chat_id,
            name=str(chat_id)
        )
        active_jobs[chat_id] = job
        await update.message.reply_text(
            "✅ **Bot Started!**\n\n"
            "I'll post a new business idea every 5 minutes in this chat.\n"
            "Use /stop_bot to stop the posts.",
            parse_mode='Markdown'
        )
        logger.info(f"Bot started for chat: {chat_id}")
    else:
        await update.message.reply_text(
            "❌ Error starting bot. Please try again."
        )

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop posting business ideas"""
    chat_id = update.effective_chat.id
    
    if chat_id in active_jobs and active_jobs[chat_id]:
        job = active_jobs[chat_id]
        job.schedule_removal()
        del active_jobs[chat_id]
        await update.message.reply_text(
            "⏹️ **Bot Stopped!**\n\n"
            "I've stopped posting business ideas.\n"
            "Use /start_bot to restart.",
            parse_mode='Markdown'
        )
        logger.info(f"Bot stopped for chat: {chat_id}")
    else:
        await update.message.reply_text(
            "ℹ️ Bot is not currently running in this chat.\n"
            "Use /start_bot to start posting!"
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status"""
    chat_id = update.effective_chat.id
    
    if chat_id in active_jobs and active_jobs[chat_id]:
        await update.message.reply_text(
            "🟢 **Status: Running**\n\n"
            "✅ Bot is active and posting business ideas every 5 minutes.\n"
            "📅 Last idea was posted recently.\n\n"
            "Use /stop_bot to stop the posts.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🔴 **Status: Stopped**\n\n"
            "❌ Bot is not currently posting.\n"
            "Use /start_bot to start posting!",
            parse_mode='Markdown'
        )

async def post_idea(context: ContextTypes.DEFAULT_TYPE):
    """Post a business idea to the chat"""
    chat_id = context.job.chat_id
    idea_text = random.choice(BUSINESS_IDEAS)
    
    # Add timestamp and footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = f"💡 **Business Idea**\n\n{idea_text}\n\n---\n⏰ {timestamp}\n\n🚀 *Venture1 Bot*"
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Posted idea to chat: {chat_id}")
    except Exception as e:
        logger.error(f"Error posting to chat {chat_id}: {e}")
        # If bot can't post, remove the job
        if chat_id in active_jobs:
            job = active_jobs[chat_id]
            job.schedule_removal()
            del active_jobs[chat_id]
            logger.info(f"Removed job for chat: {chat_id} due to error")

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when bot is added to a new group/channel"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            chat_id = update.effective_chat.id
            chat_type = update.effective_chat.type
            chat_title = update.effective_chat.title or "Private Chat"
            
            welcome_msg = (
                f"🎉 **Thanks for adding me to {chat_title}!** 🎉\n\n"
                f"📌 **Chat Type:** {chat_type}\n"
                f"🆔 **Chat ID:** `{chat_id}`\n\n"
                f"**To start posting business ideas:**\n"
                f"▶️ Use /start_bot\n\n"
                f"**Other commands:**\n"
                f"⏹️ /stop_bot - Stop posting\n"
                f"💡 /idea - Get an idea now\n"
                f"📊 /status - Check status\n\n"
                f"✨ I'll automatically detect where to post!"
            )
            
            await update.message.reply_text(
                welcome_msg,
                parse_mode='Markdown'
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any other messages - auto-detect chat ID"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title or "Private Chat"
    
    # Auto-detect and log chat info
    logger.info(f"Message from {chat_type} '{chat_title}' (ID: {chat_id})")
    
    # Don't reply to non-command messages
    # but you can add custom logic here if needed

def main():
    """Start the bot"""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables!")
        logger.info("Please set your bot token in Railway environment variables")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("idea", idea))
    application.add_handler(CommandHandler("start_bot", start_bot))
    application.add_handler(CommandHandler("stop_bot", stop_bot))
    application.add_handler(CommandHandler("status", status))
    
    # Add message handlers
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        handle_new_chat_members
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    # Start the bot
    logger.info("Starting Venture1 Bot...")
    logger.info("Bot is ready! Use /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
