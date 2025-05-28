import os
import logging
import time
from flask import Flask, request, jsonify
from telegram import Bot, Update, ChatPermissions
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

from database import MongoDB
from utils import is_admin, format_duration, mute_user

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
db = MongoDB(MONGO_URI)
start_time = time.time()

# --- Command Handlers ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Bot is online! Use /help for commands.")

def help_command(update: Update, context: CallbackContext):
    help_text = """
📚 **Commands:**
/broadcast_all - Send to all users & groups
/stats - Show bot statistics
/uptime - Check bot uptime
"""
    update.message.reply_text(help_text)

def broadcast_all(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("❌ Owner only!")
        return
    
    message = " ".join(context.args)
    if not message:
        update.message.reply_text("⚠️ Usage: /broadcast_all <message>")
        return
    
    # Send to all groups and users (implement in database.py)
    success = db.broadcast_message(bot, message)
    update.message.reply_text(f"📢 Broadcast sent to {success} chats.")

# --- Web Endpoints ---
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify(status="ok")

@app.route('/')
def home():
    return jsonify(
        status="running",
        uptime=format_duration(time.time() - start_time),
        stats=db.get_stats()
    )

# --- Initialization ---
def setup_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("broadcast_all", broadcast_all))

if __name__ == "__main__":
    setup_handlers(dispatcher)
    db.init_db()
    
    if WEBHOOK_URL:
        bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        app.run(host="0.0.0.0", port=PORT)
    else:
        from telegram.ext import Updater
        updater = Updater(bot=bot, use_context=True)
        updater.start_polling()
        updater.idle()
