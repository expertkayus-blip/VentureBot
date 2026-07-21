import os
import time
import logging
import threading
import random
from datetime import datetime
import telebot
from telebot import types

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set!")
    exit(1)

# Initialize bot with more robust settings
bot = telebot.TeleBot(TOKEN, threaded=False)

# Business ideas
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

# Store active chats
active_chats = {}
posting_threads = {}

def send_idea(chat_id):
    """Send a random business idea"""
    try:
        idea = random.choice(BUSINESS_IDEAS)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        message = f"💡 **Business Idea**\n\n{idea}\n\n---\n⏰ {timestamp}\n\n🚀 *Venture1 Bot*"
        
        bot.send_message(chat_id, message, parse_mode='Markdown')
        logger.info(f"Posted idea to chat: {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error posting to {chat_id}: {e}")
        return False

def post_ideas_loop(chat_id):
    """Loop to post ideas every 5 minutes"""
    logger.info(f"Starting post loop for chat: {chat_id}")
    while chat_id in active_chats and active_chats[chat_id]:
        try:
            send_idea(chat_id)
            # Wait 5 minutes (300 seconds)
            for _ in range(300):
                if chat_id not in active_chats or not active_chats[chat_id]:
                    break
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in post loop for {chat_id}: {e}")
            time.sleep(60)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user = message.from_user
        chat_id = message.chat.id
        logger.info(f"Start command received from chat: {chat_id}")
        
        bot.reply_to(
            message,
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
    except Exception as e:
        logger.error(f"Error in start command: {e}")

@bot.message_handler(commands=['idea'])
def send_idea_command(message):
    try:
        chat_id = message.chat.id
        idea = random.choice(BUSINESS_IDEAS)
        bot.reply_to(message, f"💡 **Business Idea**\n\n{idea}", parse_mode='Markdown')
        logger.info(f"Idea command from chat: {chat_id}")
    except Exception as e:
        logger.error(f"Error in idea command: {e}")

@bot.message_handler(commands=['start_bot'])
def start_bot_command(message):
    try:
        chat_id = message.chat.id
        logger.info(f"Start_bot command from chat: {chat_id}")
        
        if chat_id in active_chats and active_chats[chat_id]:
            bot.reply_to(message, "⚠️ Bot is already running in this chat! Use /stop_bot to stop it first.")
            return
        
        active_chats[chat_id] = True
        
        # Start posting thread
        thread = threading.Thread(target=post_ideas_loop, args=(chat_id,), daemon=True)
        thread.start()
        posting_threads[chat_id] = thread
        
        bot.reply_to(
            message,
            "✅ **Bot Started!**\n\n"
            "I'll post a new business idea every 5 minutes in this chat.\n"
            "Use /stop_bot to stop the posts.",
            parse_mode='Markdown'
        )
        logger.info(f"Bot started successfully for chat: {chat_id}")
    except Exception as e:
        logger.error(f"Error in start_bot command: {e}")
        bot.reply_to(message, "❌ Error starting bot. Please try again.")

@bot.message_handler(commands=['stop_bot'])
def stop_bot_command(message):
    try:
        chat_id = message.chat.id
        logger.info(f"Stop_bot command from chat: {chat_id}")
        
        if chat_id in active_chats and active_chats[chat_id]:
            active_chats[chat_id] = False
            if chat_id in posting_threads:
                del posting_threads[chat_id]
            bot.reply_to(
                message,
                "⏹️ **Bot Stopped!**\n\n"
                "I've stopped posting business ideas.\n"
                "Use /start_bot to restart.",
                parse_mode='Markdown'
            )
            logger.info(f"Bot stopped for chat: {chat_id}")
        else:
            bot.reply_to(
                message,
                "ℹ️ Bot is not currently running in this chat.\n"
                "Use /start_bot to start posting!"
            )
    except Exception as e:
        logger.error(f"Error in stop_bot command: {e}")

@bot.message_handler(commands=['status'])
def status_command(message):
    try:
        chat_id = message.chat.id
        logger.info(f"Status command from chat: {chat_id}")
        
        if chat_id in active_chats and active_chats[chat_id]:
            bot.reply_to(
                message,
                "🟢 **Status: Running**\n\n"
                "✅ Bot is active and posting business ideas every 5 minutes.\n"
                "📅 Last idea was posted recently.\n\n"
                "Use /stop_bot to stop the posts.",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(
                message,
                "🔴 **Status: Stopped**\n\n"
                "❌ Bot is not currently posting.\n"
                "Use /start_bot to start posting!",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in status command: {e}")

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_members(message):
    try:
        for member in message.new_chat_members:
            if member.id == bot.get_me().id:
                chat_id = message.chat.id
                chat_title = message.chat.title or "Private Chat"
                chat_type = message.chat.type
                
                logger.info(f"Bot added to chat: {chat_id} - {chat_title}")
                
                welcome = (
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
                
                bot.reply_to(message, welcome, parse_mode='Markdown')
                break
    except Exception as e:
        logger.error(f"Error in new_members handler: {e}")

# Error handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Handle any other messages"""
    try:
        chat_id = message.chat.id
        logger.info(f"Message from chat {chat_id}: {message.text}")
        # Don't reply to non-command messages to avoid spam
    except Exception as e:
        logger.error(f"Error in echo_all: {e}")

# Start the bot
if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Starting Venture1 Bot...")
    logger.info(f"Bot Token: {TOKEN[:10]}... (hidden)")
    logger.info("Bot is ready! Use /start to begin.")
    logger.info("=" * 50)
    
    # Remove webhook if exists
    try:
        bot.remove_webhook()
        logger.info("Webhook removed successfully")
    except Exception as e:
        logger.warning(f"Could not remove webhook: {e}")
    
    # Start polling with retry
    while True:
        try:
            logger.info("Starting polling...")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            logger.info("Restarting polling in 5 seconds...")
            time.sleep(5)
