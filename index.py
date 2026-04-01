import sys
import os
import threading
import time
from flask import Flask, jsonify, request

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your bot class from channel_bot.py
from channel_bot import CrossPlatformBot, BOT_TOKEN

app = Flask(__name__)

# Store bot thread
bot_thread = None

def run_bot():
    """Run your original bot in background thread"""
    try:
        if BOT_TOKEN:
            print(f"Starting bot with token: {BOT_TOKEN[:10]}...")
            bot = CrossPlatformBot(BOT_TOKEN)
            bot.run()  # Your original run method with long polling
        else:
            print("No BOT_TOKEN found! Check environment variables.")
            print("Available env vars:", list(os.environ.keys()))
    except Exception as e:
        print(f"Bot error: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'telegram-game-bot',
        'version': '1.0.0',
        'bot_status': 'active' if bot_thread and bot_thread.is_alive() else 'starting',
        'message': 'Bot is running on Vercel'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if bot_thread and bot_thread.is_alive() else 'degraded',
        'timestamp': time.time(),
        'bot_alive': bot_thread and bot_thread.is_alive() if bot_thread else False,
        'bot_thread_id': bot_thread.ident if bot_thread and bot_thread.is_alive() else None
    })

@app.route('/keepalive')
def keepalive():
    """Keep-alive endpoint to prevent bot from stopping"""
    return jsonify({
        'status': 'pong',
        'timestamp': time.time(),
        'bot_alive': bot_thread and bot_thread.is_alive() if bot_thread else False
    })

# Start bot in background when app loads
def start_background_bot():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        print("Starting bot thread...")
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("✅ Bot thread started")
        time.sleep(2)
        print(f"Bot thread alive: {bot_thread.is_alive()}")

# This runs when the module loads
start_background_bot()
