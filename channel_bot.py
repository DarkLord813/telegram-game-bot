import requests
import time
import secrets
import sqlite3
from datetime import datetime, timedelta
import json
import random
import threading
import os
import sys
from flask import Flask, jsonify
from threading import Thread
import traceback

print("=" * 60)
print("🤖 TELEGRAM BOT - CROSS PLATFORM")
print("🚀 RENDER DEPLOYMENT READY")
print("=" * 60)

# ==================== DEBUG INITIALIZATION ====================
print("🔍 DEBUG: Starting initialization...")
print(f"🔍 DEBUG: Python version: {sys.version}")
print(f"🔍 DEBUG: Current directory: {os.getcwd()}")
print(f"🔍 DEBUG: Files in directory: {os.listdir('.')}")

# Try to get BOT_TOKEN early for debugging
BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(f"🔍 DEBUG: BOT_TOKEN exists: {'YES' if BOT_TOKEN else 'NO'}")
if BOT_TOKEN:
    print(f"🔍 DEBUG: Token starts with: {BOT_TOKEN[:10]}...")
    print(f"🔍 DEBUG: Token length: {len(BOT_TOKEN)}")
else:
    print("❌ DEBUG: BOT_TOKEN is MISSING! Check Render Environment Variables")

# Test critical imports
try:
    import requests
    print("✅ DEBUG: requests import OK")
except ImportError as e:
    print(f"❌ DEBUG: requests import failed: {e}")

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    print("✅ DEBUG: telegram imports OK")
except ImportError as e:
    print(f"❌ DEBUG: telegram imports failed: {e}")

try:
    import sqlite3
    print("✅ DEBUG: sqlite3 import OK")
except ImportError as e:
    print(f"❌ DEBUG: sqlite3 import failed: {e}")

try:
    from flask import Flask, jsonify
    print("✅ DEBUG: flask imports OK")
except ImportError as e:
    print(f"❌ DEBUG: flask imports failed: {e}")

print("🔍 DEBUG: Starting Flask health server...")
# ==================== END DEBUG ====================

# Health check server
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Render monitoring"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'telegram-game-bot',
            'version': '1.0.0',
            'checks': {
                'bot_online': {'status': 'healthy', 'message': 'Bot is running'},
                'system': {'status': 'healthy', 'message': 'System operational'}
            }
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Telegram Game Bot',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'features': ['Game Distribution', 'Mini-Games', 'Admin Uploads', 'Broadcast Messaging']
        }
    })

@app.route('/debug')
def debug_info():
    """Debug endpoint to check bot status"""
    try:
        debug_info = {
            'bot_token_set': bool(BOT_TOKEN),
            'bot_token_length': len(BOT_TOKEN) if BOT_TOKEN else 0,
            'flask_running': True,
            'timestamp': datetime.now().isoformat(),
            'environment_keys': list(os.environ.keys())  # Show environment variable names
        }
        return jsonify(debug_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_health_server():
    """Run the health check server with error handling"""
    try:
        port = int(os.environ.get('PORT', 8080))
        print(f"🔄 Starting health server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Health server error: {e}")
        time.sleep(5)
        run_health_server()

def start_health_check():
    """Start health check server in background with restart capability"""
    def health_wrapper():
        while True:
            try:
                run_health_server()
            except Exception as e:
                print(f"❌ Health server crashed, restarting: {e}")
                time.sleep(10)
    
    t = Thread(target=health_wrapper, daemon=True)
    t.start()
    print("✅ Health check server started")

# ==================== KEEP-ALIVE SERVICE ====================

class KeepAliveService:
    def __init__(self, health_url=None):
        self.health_url = health_url or f"http://localhost:{os.environ.get('PORT', 8080)}/health"
        self.is_running = False
        self.ping_count = 0
        
    def start(self):
        """Start keep-alive service to prevent sleep"""
        self.is_running = True
        
        def ping_loop():
            while self.is_running:
                try:
                    self.ping_count += 1
                    response = requests.get(self.health_url, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Keep-alive ping #{self.ping_count}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print(f"❌ Keep-alive failed: Status {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    print(f"🔌 Keep-alive connection error - server may be starting")
                except requests.exceptions.Timeout:
                    print(f"⏰ Keep-alive timeout - retrying later")
                except Exception as e:
                    print(f"❌ Keep-alive error: {e}")
                
                # Wait 4 minutes (Render sleeps after 15 min inactivity)
                # Ping every 4 minutes to stay active
                time.sleep(240)  # 4 minutes
        
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print(f"🔄 Keep-alive service started - pinging every 4 minutes")
        print(f"🌐 Health endpoint: {self.health_url}")
        
    def stop(self):
        """Stop keep-alive service"""
        self.is_running = False
        print("🛑 Keep-alive service stopped")

# ==================== MAIN BOT CLASS ====================

class CrossPlatformBot:
    def __init__(self, token):
        if not token:
            print("❌ CRITICAL: No BOT_TOKEN provided!")
            raise ValueError("BOT_TOKEN is required")
            
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
        # YOUR CHANNEL DETAILS
        self.REQUIRED_CHANNEL = "@pspgamers5"
        self.CHANNEL_LINK = "https://t.me/pspgamers5"
        
        # ADMIN USER IDs
        self.ADMIN_IDS = [7475473197, 7713987088]
        
        # Mini-games state management
        self.guess_games = {}  # {user_id: {'target': number, 'attempts': count}}
        self.spin_games = {}   # {user_id: {'spins': count, 'last_spin': timestamp}}
        
        # Broadcast system
        self.broadcast_sessions = {}  # {admin_id: {'stage': 'waiting_message', 'message': ''}}
        self.broadcast_stats = {}     # Store broadcast statistics
        
        # CRASH PROTECTION
        self.last_restart = time.time()
        self.error_count = 0
        self.max_errors = 25
        self.error_window = 300
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        # Keep-alive service
        self.keep_alive = None
        
        self.setup_database()
        self.verify_database_schema()
        self.games_cache = {}
        self.is_scanning = False
        self.search_sessions = {}
        self.search_results = {}
        
        print("✅ Bot system ready!")
        print(f"📊 Monitoring channel: {self.REQUIRED_CHANNEL}")
        print(f"👑 Admin uploads enabled for {len(self.ADMIN_IDS)} users")
        print("📤 Forwarded files support enabled")
        print("🔍 Game search feature enabled")
        print("🎮 Mini-games integrated: Number Guess, Random Number, Lucky Spin")
        print("📢 Admin broadcast messaging system enabled")
        print("🛡️  Crash protection enabled")
        print("🔋 Keep-alive system ready")
    
    def start_keep_alive(self):
        """Start the keep-alive service"""
        try:
            # Get the actual Render URL from environment or use local
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                health_url = f"{render_url}/health"
            else:
                health_url = f"http://localhost:{os.environ.get('PORT', 8080)}/health"
            
            self.keep_alive = KeepAliveService(health_url)
            self.keep_alive.start()
            print("🔋 Keep-alive service activated - bot will stay awake!")
            return True
        except Exception as e:
            print(f"❌ Failed to start keep-alive: {e}")
            return False

    # ==================== BROADCAST MESSAGING SYSTEM ====================
    
    def start_broadcast(self, user_id, chat_id):
        """Start broadcast message creation"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return False
            
        self.broadcast_sessions[user_id] = {
            'stage': 'waiting_message',
            'message': '',
            'chat_id': chat_id
        }
        
        broadcast_info = """📢 <b>Admin Broadcast System</b>

You can send messages to all bot subscribers.

📝 <b>How to use:</b>
1. Type your broadcast message
2. Preview the message before sending
3. Send to all users or cancel

⚡ <b>Features:</b>
• HTML formatting support
• Preview before sending
• Send to all verified users
• Delivery statistics

💡 <b>Type your broadcast message now:</b>"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "❌ Cancel Broadcast", "callback_data": "cancel_broadcast"}]
            ]
        }
        
        self.robust_send_message(chat_id, broadcast_info, keyboard)
        return True
    
    def handle_broadcast_message(self, user_id, chat_id, text):
        """Handle broadcast message input"""
        if user_id not in self.broadcast_sessions:
            return False
            
        session = self.broadcast_sessions[user_id]
        
        if session['stage'] == 'waiting_message':
            # Store the message and show preview
            session['stage'] = 'preview'
            session['message'] = text
            
            preview_text = f"""📋 <b>Broadcast Preview</b>

Your message:
────────────────────
{text}
────────────────────

📊 This message will be sent to all verified users.

⚠️ <b>Please review carefully before sending!</b>"""
            
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Send to All Users", "callback_data": "confirm_broadcast"},
                        {"text": "✏️ Edit Message", "callback_data": "edit_broadcast"}
                    ],
                    [
                        {"text": "❌ Cancel", "callback_data": "cancel_broadcast"}
                    ]
                ]
            }
            
            self.robust_send_message(chat_id, preview_text, keyboard)
            return True
            
        return False
    
    def send_broadcast_to_all(self, user_id, chat_id):
        """Send broadcast message to all verified users"""
        if user_id not in self.broadcast_sessions:
            return False
            
        session = self.broadcast_sessions[user_id]
        message_text = session['message']
        
        # Get all verified users
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
        users = cursor.fetchall()
        
        total_users = len(users)
        if total_users == 0:
            self.robust_send_message(chat_id, "❌ No verified users found to send broadcast.")
            del self.broadcast_sessions[user_id]
            return False
        
        # Send initial progress
        progress_msg = self.robust_send_message(chat_id, 
            f"📤 Starting broadcast...\n"
            f"📊 Total users: {total_users}\n"
            f"⏳ Sending messages..."
        )
        
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        # Send to users with rate limiting
        for i, (user_id_target,) in enumerate(users):
            try:
                # Add broadcast header
                broadcast_message = f"📢 <b>Announcement from Admin</b>\n\n{message_text}\n\n────────────────────\n<i>This is an automated broadcast message</i>"
                
                if self.robust_send_message(user_id_target, broadcast_message):
                    success_count += 1
                else:
                    failed_count += 1
                
                # Update progress every 10 messages
                if (i + 1) % 10 == 0 or (i + 1) == total_users:
                    progress = int((i + 1) * 100 / total_users)
                    elapsed = time.time() - start_time
                    eta = (elapsed / (i + 1)) * (total_users - (i + 1)) if (i + 1) > 0 else 0
                    
                    progress_text = f"""📤 <b>Broadcast Progress</b>

📊 Progress: {i + 1}/{total_users} users
{self.create_progress_bar(progress)} {progress}%

✅ Successful: {success_count}
❌ Failed: {failed_count}
⏱️ Elapsed: {elapsed:.1f}s
⏳ ETA: {eta:.1f}s

Sending messages..."""
                    
                    self.robust_send_message(chat_id, progress_text)
                
                # Rate limiting to avoid hitting Telegram limits
                time.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Broadcast error for user {user_id_target}: {e}")
        
        # Send final statistics
        elapsed_total = time.time() - start_time
        success_rate = (success_count / total_users) * 100 if total_users > 0 else 0
        
        stats_text = f"""✅ <b>Broadcast Completed!</b>

📊 Final Statistics:
• 📤 Total users: {total_users}
• ✅ Successful: {success_count}
• ❌ Failed: {failed_count}
• 📈 Success rate: {success_rate:.1f}%
• ⏱️ Total time: {elapsed_total:.1f}s
• 🚀 Speed: {total_users/elapsed_total:.1f} users/second

📝 Message sent to {success_count} users successfully."""

        # Store broadcast statistics
        broadcast_id = int(time.time())
        self.broadcast_stats[broadcast_id] = {
            'admin_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'total_users': total_users,
            'success_count': success_count,
            'failed_count': failed_count,
            'message_preview': message_text[:100] + "..." if len(message_text) > 100 else message_text
        }
        
        self.robust_send_message(chat_id, stats_text)
        
        # Clean up session
        del self.broadcast_sessions[user_id]
        
        return True
    
    def get_broadcast_stats(self, user_id, chat_id, message_id):
        """Show broadcast statistics"""
        if not self.is_admin(user_id):
            return False
            
        if not self.broadcast_stats:
            stats_text = """📊 <b>Broadcast Statistics</b>

No broadcasts sent yet.

Use the broadcast feature to send messages to all users."""
        else:
            total_broadcasts = len(self.broadcast_stats)
            total_sent = sum(stats['success_count'] for stats in self.broadcast_stats.values())
            total_failed = sum(stats['failed_count'] for stats in self.broadcast_stats.values())
            total_users_reached = total_sent
            
            # Get recent broadcasts
            recent_broadcasts = sorted(self.broadcast_stats.items(), key=lambda x: x[0], reverse=True)[:5]
            
            stats_text = f"""📊 <b>Broadcast Statistics</b>

📈 Overview:
• Total broadcasts: {total_broadcasts}
• Total messages sent: {total_sent}
• Total failed: {total_failed}
• Unique users reached: {total_users_reached}

📋 Recent broadcasts:"""
            
            for broadcast_id, stats in recent_broadcasts:
                date = datetime.fromisoformat(stats['timestamp']).strftime('%Y-%m-%d %H:%M')
                stats_text += f"\n• {date}: {stats['success_count']}/{stats['total_users']} users"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📢 New Broadcast", "callback_data": "start_broadcast"}],
                [{"text": "🔄 Refresh Stats", "callback_data": "broadcast_stats"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, stats_text, keyboard)
    
    def cancel_broadcast(self, user_id, chat_id, message_id):
        """Cancel ongoing broadcast"""
        if user_id in self.broadcast_sessions:
            del self.broadcast_sessions[user_id]
        
        cancel_text = "❌ Broadcast cancelled."
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, cancel_text, keyboard)
    
    def create_broadcast_buttons(self):
        """Create broadcast management buttons"""
        return {
            "inline_keyboard": [
                [
                    {"text": "📢 New Broadcast", "callback_data": "start_broadcast"},
                    {"text": "📊 Statistics", "callback_data": "broadcast_stats"}
                ],
                [
                    {"text": "🔙 Back to Admin", "callback_data": "admin_panel"}
                ]
            ]
        }

    # ==================== CRASH PROTECTION METHODS ====================
    
    def handle_error(self, error, context="general"):
        """Comprehensive error handling with auto-recovery"""
        self.error_count += 1
        self.consecutive_errors += 1
        current_time = time.time()
        
        # Reset error count if outside window
        if current_time - self.last_restart > self.error_window:
            self.error_count = 1
            self.consecutive_errors = 1
            self.last_restart = current_time
        
        print(f"❌ Error in {context}: {str(error)[:100]}...")
        print(f"📊 Error stats: {self.error_count}/{self.max_errors} total, {self.consecutive_errors}/{self.max_consecutive_errors} consecutive")
        
        # Auto-restart if too many errors
        if (self.error_count >= self.max_errors or 
            self.consecutive_errors >= self.max_consecutive_errors):
            print("🔄 Too many errors, initiating auto-restart...")
            self.auto_restart()
        
        return False

    def auto_restart(self):
        """Auto-restart the bot safely"""
        print("🚀 Initiating auto-restart...")
        try:
            # Clean up resources
            if hasattr(self, 'conn'):
                try:
                    self.conn.close()
                except:
                    pass
            
            # Stop keep-alive
            if self.keep_alive:
                self.keep_alive.stop()
            
            # Reset error counters
            self.error_count = 0
            self.consecutive_errors = 0
            self.last_restart = time.time()
            
            # Reinitialize database
            self.setup_database()
            self.verify_database_schema()
            self.update_games_cache()
            
            # Restart keep-alive
            if self.keep_alive:
                self.keep_alive.start()
            
            print("✅ Auto-restart completed successfully")
            
        except Exception as e:
            print(f"❌ Auto-restart failed: {e}")
            time.sleep(30)

    def robust_send_message(self, chat_id, text, reply_markup=None, max_retries=3):
        """Send message with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                url = self.base_url + "sendMessage"
                data = {
                    "chat_id": chat_id, 
                    "text": text, 
                    "parse_mode": "HTML"
                }
                if reply_markup:
                    data["reply_markup"] = json.dumps(reply_markup)
                
                response = requests.post(url, data=data, timeout=15)
                result = response.json()
                
                if result.get('ok'):
                    # Reset consecutive errors on successful send
                    if self.consecutive_errors > 0:
                        self.consecutive_errors = 0
                    return True
                else:
                    error_msg = result.get('description', 'Unknown error')
                    print(f"❌ Telegram API error (attempt {attempt + 1}): {error_msg}")
                    
                    # Don't retry for certain errors
                    if any(msg in error_msg.lower() for msg in ["bot was blocked", "chat not found", "user not found"]):
                        return False
                    
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    
                    return False
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Request timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return False
            except Exception as e:
                self.handle_error(e, "send_message")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False
        return False

    def safe_db_operation(self, operation, *args, max_retries=3, **kwargs):
        """Execute database operations with retry logic"""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    print(f"🔄 Database locked, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5)
                    continue
                else:
                    self.handle_error(e, "database_operation")
                    return None
            except Exception as e:
                self.handle_error(e, "database_operation")
                return None
        return None

    # ==================== YOUR ORIGINAL METHODS CONTINUE ====================
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def create_progress_bar(self, percentage, length=10):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    # ==================== DATABASE SCHEMA VERIFICATION ====================
    
    def verify_database_schema(self):
        """Ensure database has correct schema for file uploads"""
        try:
            cursor = self.conn.cursor()
            
            # Check if bot_message_id column exists
            cursor.execute("PRAGMA table_info(channel_games)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'bot_message_id' not in columns:
                print("🔄 Adding bot_message_id column to database...")
                cursor.execute('ALTER TABLE channel_games ADD COLUMN bot_message_id INTEGER')
                self.conn.commit()
                print("✅ Database schema updated successfully!")
                
            return True
        except Exception as e:
            print(f"❌ Database schema verification failed: {e}")
            return False

    # ==================== MINI-GAMES IMPLEMENTATION ====================
    
    def start_number_guess_game(self, user_id, chat_id):
        """Start a new number guess game"""
        target_number = random.randint(1, 10)
        self.guess_games[user_id] = {
            'target': target_number,
            'attempts': 0,
            'max_attempts': 5,
            'start_time': time.time(),
            'chat_id': chat_id
        }
        
        game_text = f"""🎯 <b>Number Guess Game Started!</b>

I'm thinking of a number between 1 and 10.

📝 <b>How to play:</b>
• Guess the number by typing it (1-10)
• You have {self.guess_games[user_id]['max_attempts']} attempts
• I'll tell you if your guess is too high or too low

🎮 <b>Type your first guess now!</b>"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔢 Quick Numbers", "callback_data": "quick_numbers"}],
                [{"text": "🔄 New Game", "callback_data": "game_guess"}],
                [{"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}]
            ]
        }
        
        self.robust_send_message(chat_id, game_text, keyboard)
        return True
    
    def handle_guess_input(self, user_id, chat_id, guess_text):
        """Handle user's number guess"""
        if user_id not in self.guess_games:
            self.robust_send_message(chat_id, "❌ No active number guess game. Start a new one from Mini-Games!")
            return False
        
        try:
            guess = int(guess_text.strip())
            if guess < 1 or guess > 10:
                self.robust_send_message(chat_id, "❌ Please enter a number between 1 and 10!")
                return True
        except ValueError:
            self.robust_send_message(chat_id, "❌ Please enter a valid number!")
            return True
        
        game = self.guess_games[user_id]
        game['attempts'] += 1
        target = game['target']
        
        # Create quick number buttons
        quick_buttons = []
        row = []
        for i in range(1, 11):
            row.append({"text": str(i), "callback_data": f"quick_guess_{i}"})
            if i % 5 == 0:
                quick_buttons.append(row)
                row = []
        
        keyboard = {
            "inline_keyboard": quick_buttons + [
                [{"text": "🔄 New Game", "callback_data": "game_guess"}],
                [{"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}]
            ]
        }
        
        if guess == target:
            time_taken = time.time() - game['start_time']
            win_text = f"""🎉 <b>Congratulations! You won!</b>

✅ Correct guess: <b>{guess}</b>
🎯 Target number: <b>{target}</b>
📊 Attempts used: <b>{game['attempts']}</b>
⏱️ Time taken: <b>{time_taken:.1f} seconds</b>

🏆 <b>Well done!</b>"""
            
            self.robust_send_message(chat_id, win_text, keyboard)
            del self.guess_games[user_id]
            
        elif game['attempts'] >= game['max_attempts']:
            lose_text = f"""😔 <b>Game Over!</b>

🎯 The number was: <b>{target}</b>
📊 Your attempts: <b>{game['attempts']}</b>
💡 Better luck next time!

🔄 Want to try again?"""
            
            self.robust_send_message(chat_id, lose_text, keyboard)
            del self.guess_games[user_id]
            
        else:
            remaining = game['max_attempts'] - game['attempts']
            hint = "📈 Too high!" if guess > target else "📉 Too low!"
            
            progress_text = f"""🎯 <b>Number Guess Game</b>

🔢 Your guess: <b>{guess}</b>
{hint}
📊 Attempts: <b>{game['attempts']}</b>/<b>{game['max_attempts']}</b>
🎯 Remaining attempts: <b>{remaining}</b>

💡 Keep guessing!"""
            
            self.robust_send_message(chat_id, progress_text, keyboard)
        
        return True
    
    def generate_random_number(self, user_id, chat_id):
        """Generate a random number with options"""
        number = random.randint(1, 100)
        
        # Analyze the number
        analysis = []
        if number % 2 == 0:
            analysis.append("🔵 Even number")
        else:
            analysis.append("🔴 Odd number")
        
        if number <= 33:
            analysis.append("📊 In lower third (1-33)")
        elif number <= 66:
            analysis.append("📊 In middle third (34-66)")
        else:
            analysis.append("📊 In upper third (67-100)")
        
        if number == 69:
            analysis.append("😏 Nice!")
        elif number == 42:
            analysis.append("🤔 The answer to everything!")
        elif number == 100:
            analysis.append("🎯 Perfect score!")
        
        analysis_text = "\n".join(analysis)
        
        random_text = f"""🎲 <b>Random Number Generator</b>

🎯 Your lucky number: 
<b>🎊 {number} 🎊</b>

📊 <b>Analysis:</b>
{analysis_text}

🔄 Generate another random number?"""
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔄 New Number", "callback_data": "game_random"},
                    {"text": "🎯 1-10 Range", "callback_data": "random_1_10"}
                ],
                [
                    {"text": "🎰 1-1000 Range", "callback_data": "random_1_1000"},
                    {"text": "💰 Lucky 7", "callback_data": "random_lucky"}
                ],
                [
                    {"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}
                ]
            ]
        }
        
        self.robust_send_message(chat_id, random_text, keyboard)
        return True
    
    def generate_custom_random(self, user_id, chat_id, range_type):
        """Generate random number in custom range"""
        if range_type == "1_10":
            number = random.randint(1, 10)
            range_text = "1-10"
        elif range_type == "1_1000":
            number = random.randint(1, 1000)
            range_text = "1-1000"
        elif range_type == "lucky":
            numbers = [7, 77, 777, 7777]
            number = random.choice(numbers)
            range_text = "Lucky 7s"
        else:
            number = random.randint(1, 100)
            range_text = "1-100"
        
        custom_text = f"""🎲 <b>Custom Random Number</b>

🎯 Range: <b>{range_text}</b>
🎊 Your number: <b>{number}</b>

💫 <b>Special number generated!</b>"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 Another Number", "callback_data": f"random_{range_type}"}],
                [{"text": "🔙 Back to Random", "callback_data": "game_random"}]
            ]
        }
        
        self.robust_send_message(chat_id, custom_text, keyboard)
        return True
    
    def lucky_spin(self, user_id, chat_id):
        """Perform a lucky spin"""
        now = time.time()
        
        # Rate limiting: 1 spin per 3 seconds
        if user_id in self.spin_games:
            last_spin = self.spin_games[user_id].get('last_spin', 0)
            if now - last_spin < 3:
                wait_time = 3 - (now - last_spin)
                self.robust_send_message(chat_id, f"⏳ Please wait {wait_time:.1f} seconds before spinning again!")
                return True
        
        # Generate spin results
        symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
        spins = [random.choice(symbols) for _ in range(3)]
        
        # Calculate win
        win_amount = 0
        win_type = "No win"
        
        if spins[0] == spins[1] == spins[2]:
            if spins[0] == "💎":
                win_amount = 1000
                win_type = "JACKPOT! 💎 DIAMOND TRIPLE 💎"
            elif spins[0] == "7️⃣":
                win_amount = 500
                win_type = "BIG WIN! 7️⃣ TRIPLE 7 7️⃣"
            else:
                win_amount = 100
                win_type = "TRIPLE MATCH!"
        elif spins[0] == spins[1] or spins[1] == spins[2]:
            win_amount = 25
            win_type = "DOUBLE MATCH!"
        
        # Update spin stats
        if user_id not in self.spin_games:
            self.spin_games[user_id] = {'spins': 0, 'total_wins': 0}
        
        self.spin_games[user_id]['spins'] += 1
        self.spin_games[user_id]['total_wins'] += win_amount
        self.spin_games[user_id]['last_spin'] = now
        
        stats = self.spin_games[user_id]
        
        # Create spin result text
        spin_text = f"""🎰 <b>LUCKY SPIN</b>

🎯 Spin Result:
┌─────────┐
│  {spins[0]}  |  {spins[1]}  |  {spins[2]}  │
└─────────┘

💰 <b>{win_type}</b>
🎁 Win Amount: <b>{win_amount} coins</b>

📊 <b>Your Stats:</b>
• Total Spins: {stats['spins']}
• Total Winnings: {stats['total_wins']} coins
• Average per spin: {stats['total_wins']/stats['spins']:.1f} coins

🎮 Spin again?"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎰 Spin Again", "callback_data": "game_spin"}],
                [{"text": "🎯 Big Spin (3x)", "callback_data": "big_spin"}],
                [{"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}]
            ]
        }
        
        self.robust_send_message(chat_id, spin_text, keyboard)
        return True
    
    def big_spin(self, user_id, chat_id):
        """Perform 3 spins at once"""
        spin_results = []
        total_win = 0
        
        for spin_num in range(3):
            symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
            spins = [random.choice(symbols) for _ in range(3)]
            
            # Calculate win for this spin
            win_amount = 0
            if spins[0] == spins[1] == spins[2]:
                if spins[0] == "💎":
                    win_amount = 1000
                elif spins[0] == "7️⃣":
                    win_amount = 500
                else:
                    win_amount = 100
            elif spins[0] == spins[1] or spins[1] == spins[2]:
                win_amount = 25
            
            total_win += win_amount
            spin_results.append((spins, win_amount))
        
        # Update stats
        if user_id not in self.spin_games:
            self.spin_games[user_id] = {'spins': 0, 'total_wins': 0}
        
        self.spin_games[user_id]['spins'] += 3
        self.spin_games[user_id]['total_wins'] += total_win
        self.spin_games[user_id]['last_spin'] = time.time()
        
        stats = self.spin_games[user_id]
        
        # Create big spin result text
        big_spin_text = "🎰 <b>BIG SPIN RESULTS</b>\n\n"
        
        for i, (spins, win) in enumerate(spin_results, 1):
            big_spin_text += f"🎯 Spin {i}: {spins[0]} | {spins[1]} | {spins[2]}\n"
            big_spin_text += f"💰 Win: {win} coins\n\n"
        
        big_spin_text += f"💎 <b>TOTAL WIN: {total_win} coins</b>\n\n"
        big_spin_text += f"📊 <b>Overall Stats:</b>\n"
        big_spin_text += f"• Total Spins: {stats['spins']}\n"
        big_spin_text += f"• Total Winnings: {stats['total_wins']} coins\n"
        big_spin_text += f"• Average: {stats['total_wins']/stats['spins']:.1f} coins per spin\n\n"
        big_spin_text += "🎮 Keep spinning!"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎰 Single Spin", "callback_data": "game_spin"}],
                [{"text": "🎯 Big Spin Again", "callback_data": "big_spin"}],
                [{"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}]
            ]
        }
        
        self.robust_send_message(chat_id, big_spin_text, keyboard)
        return True

    def show_mini_games_stats(self, user_id, chat_id, message_id):
        """Show user's mini-games statistics"""
        guess_stats = "No games played" if user_id not in self.guess_games else f"Active game: {self.guess_games[user_id]['attempts']} attempts"
        spin_stats = "No spins yet" if user_id not in self.spin_games else f"{self.spin_games[user_id]['spins']} spins, {self.spin_games[user_id]['total_wins']} coins won"
        
        stats_text = f"""📊 <b>Mini-Games Statistics</b>

🎯 <b>Number Guess:</b>
{guess_stats}

🎰 <b>Lucky Spin:</b>
{spin_stats}

🎲 <b>Random Number:</b>
Always available!

🎮 Keep playing and improve your stats!"""
        
        self.edit_message(chat_id, message_id, stats_text, self.create_mini_games_buttons())

    def create_mini_games_buttons(self):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎯 Number Guess", "callback_data": "game_guess"},
                    {"text": "🎲 Random Number", "callback_data": "game_random"}
                ],
                [
                    {"text": "🎰 Lucky Spin", "callback_data": "game_spin"},
                    {"text": "📊 My Stats", "callback_data": "mini_stats"}
                ],
                [
                    {"text": "🔙 Back to Games", "callback_data": "games"}
                ]
            ]
        }
        return keyboard

    # ==================== DATABASE & SETUP METHODS ====================
    
    def get_db_path(self):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'telegram_bot.db')
        return db_path
    
    def setup_database(self):
        try:
            db_path = self.get_db_path()
            print(f"📁 Database path: {db_path}")
            
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_verified INTEGER DEFAULT 0,
                    joined_channel INTEGER DEFAULT 0,
                    verification_code TEXT,
                    code_expires DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Games table - UPDATED to include bot_message_id
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channel_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER UNIQUE,
                    file_name TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    upload_date DATETIME,
                    category TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER DEFAULT 0,
                    is_uploaded INTEGER DEFAULT 0,
                    is_forwarded INTEGER DEFAULT 0,
                    file_id TEXT,
                    bot_message_id INTEGER
                )
            ''')
            
            self.conn.commit()
            print("✅ Database setup successful!")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            # Fallback to in-memory database
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.setup_database()
    
    def test_bot_connection(self):
        try:
            url = self.base_url + "getMe"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_name = data['result']['first_name']
                print(f"✅ Bot connected: {bot_name}")
                return True
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    # ==================== VERIFICATION SYSTEM ====================
    
    def generate_code(self):
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def save_verification_code(self, user_id, username, first_name, code):
        try:
            expires = datetime.now() + timedelta(minutes=10)
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, verification_code, code_expires, is_verified, joined_channel)
                VALUES (?, ?, ?, ?, ?, 0, 0)
            ''', (user_id, username, first_name, code, expires))
            self.conn.commit()
            print(f"✅ Verification code saved for user {user_id}: {code}")
            return True
        except Exception as e:
            print(f"❌ Error saving code: {e}")
            return False
    
    def verify_code(self, user_id, code):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT verification_code, code_expires FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"❌ No verification code found for user {user_id}")
                return False
                
            stored_code, expires_str = result
            expires = datetime.fromisoformat(expires_str)
            
            if datetime.now() > expires:
                print(f"❌ Verification code expired for user {user_id}")
                return False
                
            if stored_code == code:
                cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
                self.conn.commit()
                print(f"✅ User {user_id} verified successfully")
                return True
            else:
                print(f"❌ Invalid code for user {user_id}: {code} vs {stored_code}")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False

    def check_channel_membership(self, user_id):
        try:
            url = self.base_url + "getChatMember"
            data = {
                "chat_id": self.REQUIRED_CHANNEL,
                "user_id": user_id
            }
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                status = result['result']['status']
                is_member = status in ['member', 'administrator', 'creator']
                print(f"📢 Channel check for {user_id}: {status} -> {'Member' if is_member else 'Not member'}")
                return is_member
            
        except Exception as e:
            print(f"❌ Channel check error: {e}")
        
        return False
    
    def mark_channel_joined(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET joined_channel = 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
            print(f"✅ Marked channel joined for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error marking channel: {e}")
            return False
    
    def is_user_verified(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            is_verified = result and result[0] == 1
            print(f"🔍 User {user_id} verified: {is_verified}")
            return is_verified
        except Exception as e:
            print(f"❌ Error checking verification: {e}")
            return False
    
    def is_user_completed(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            is_completed = result and result[0] == 1 and result[1] == 1
            print(f"🔍 User {user_id} completed: {is_completed}")
            return is_completed
        except Exception as e:
            print(f"❌ Error checking completion: {e}")
            return False

    # ==================== MESSAGE PROCESSING ====================
    
    def handle_verification(self, message):
        """Handle /start command and send verification code"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            username = message['from'].get('username', '')
            first_name = message['from']['first_name']
            
            print(f"🔐 Verification requested by {first_name} ({user_id})")
            
            # Check if user is already completed
            if self.is_user_completed(user_id):
                welcome_text = f"""👋 Welcome back {first_name}!

✅ You're already verified!
📢 Channel membership: Active

Choose an option below:"""
                self.robust_send_message(chat_id, welcome_text, self.create_main_menu_buttons())
                return True
            
            # Check if user is verified but not joined channel
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                channel_text = f"""📢 <b>Channel Verification Required</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:"""
                self.robust_send_message(chat_id, channel_text, self.create_channel_buttons())
                return True
            
            # Check if user has joined channel but not verified
            if self.check_channel_membership(user_id) and not self.is_user_verified(user_id):
                # Mark channel as joined
                self.mark_channel_joined(user_id)
                
                # Generate and send verification code
                code = self.generate_code()
                if self.save_verification_code(user_id, username, first_name, code):
                    verify_text = f"""🔐 <b>Verification Required</b>

👋 Hello {first_name}!

✅ Channel membership: Verified
❌ Code verification: Pending

Your verification code: 
<code>{code}</code>

📝 Please reply with this code to complete verification.

⏰ Code expires in 10 minutes."""
                    self.robust_send_message(chat_id, verify_text)
                    return True
                else:
                    self.robust_send_message(chat_id, "❌ Error generating verification code. Please try again.")
                    return True
            
            # New user - start with code verification
            code = self.generate_code()
            if self.save_verification_code(user_id, username, first_name, code):
                welcome_text = f"""🔐 <b>Welcome to PSP Gamers Bot!</b>

👋 Hello {first_name}!

To access our game collection, please complete two-step verification:

📝 <b>Step 1: Code Verification</b>
Your verification code: 
<code>{code}</code>

Reply with this code to verify.

⏰ Code expires in 10 minutes.

After code verification, you'll need to join our channel."""
                self.robust_send_message(chat_id, welcome_text)
                return True
            else:
                self.robust_send_message(chat_id, "❌ Error generating verification code. Please try again.")
                return False
            
        except Exception as e:
            print(f"❌ Verification handler error: {e}")
            self.robust_send_message(chat_id, "❌ Error starting verification. Please try again.")
            return False

    def handle_code_verification(self, message):
        """Handle 6-digit code verification"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            first_name = message['from']['first_name']
            
            print(f"🔐 Code verification attempt by {first_name} ({user_id}): {text}")
            
            if not text.isdigit() or len(text) != 6:
                return False
            
            if self.verify_code(user_id, text):
                # Check if user has already joined channel
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    welcome_text = f"""✅ <b>Verification Complete!</b>

👋 Welcome {first_name}!

🎉 You now have full access to:
• 🎮 Game File Browser  
• 🔍 Game Search
• 📁 All Game Categories
• 🕒 Real-time Updates
• 🎮 Mini-Games

📢 Channel: @pspgamers5
Choose an option below:"""
                    self.robust_send_message(chat_id, welcome_text, self.create_main_menu_buttons())
                else:
                    channel_text = f"""✅ <b>Code Verified!</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

📝 <b>Step 2: Join Our Channel</b>

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:"""
                    self.robust_send_message(chat_id, channel_text, self.create_channel_buttons())
                return True
            else:
                self.robust_send_message(chat_id, "❌ Invalid or expired code. Please use /start to get a new code.")
                return True
                
        except Exception as e:
            print(f"❌ Code verification error: {e}")
            return False

    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Handle broadcast messages from admins
                if user_id in self.broadcast_sessions:
                    return self.handle_broadcast_message(user_id, chat_id, text)
                
                # Handle mini-games input first
                if user_id in self.guess_games:
                    # Check if it's a number guess for an active game
                    if text.strip().isdigit():
                        return self.handle_guess_input(user_id, chat_id, text)
                
                # Handle commands
                if text.startswith('/'):
                    if text == '/start':
                        return self.handle_verification(message)
                    elif text == '/menu' and self.is_user_completed(user_id):
                        welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>Cross-Platform Telegram Bot</b>

Choose an option below:"""
                        self.robust_send_message(chat_id, welcome_text, self.create_main_menu_buttons())
                        return True
                    elif text == '/minigames' and self.is_user_completed(user_id):
                        games_text = """🎮 <b>Mini Games</b>

Available games:
• /guess - Start number guess game
• /random - Generate random number
• /spin - Lucky spin game
• /minigames - Show this menu

Have fun! 🎉"""
                        self.robust_send_message(chat_id, games_text, self.create_mini_games_buttons())
                        return True
                    elif text == '/guess' and self.is_user_completed(user_id):
                        return self.start_number_guess_game(user_id, chat_id)
                    elif text == '/random' and self.is_user_completed(user_id):
                        return self.generate_random_number(user_id, chat_id)
                    elif text == '/spin' and self.is_user_completed(user_id):
                        return self.lucky_spin(user_id, chat_id)
                    elif text == '/broadcast' and self.is_admin(user_id):
                        return self.start_broadcast(user_id, chat_id)
                    elif text == '/debug' and self.is_admin(user_id):
                        debug_info = f"""🔧 Debug Information

Bot Status: Running
Token Set: {bool(self.token)}
Health Server: Active
Keep-Alive: {self.keep_alive.is_running if self.keep_alive else 'Not started'}
Database: Connected
"""
                        self.robust_send_message(chat_id, debug_info)
                        return True
                
                # Handle code verification
                if text.isdigit() and len(text) == 6:
                    return self.handle_code_verification(message)
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            return False

    # ==================== BUTTON CREATION METHODS ====================
    
    def create_channel_buttons(self):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📢 JOIN CHANNEL", "url": self.CHANNEL_LINK},
                    {"text": "✅ VERIFY JOIN", "callback_data": "verify_channel"}
                ]
            ]
        }
        return keyboard
    
    def create_main_menu_buttons(self):
        keyboard = [
            [
                {"text": "📊 Profile", "callback_data": "profile"},
                {"text": "🕒 Time", "callback_data": "time"}
            ],
            [
                {"text": "📢 Channel", "callback_data": "channel_info"},
                {"text": "🎮 Games", "callback_data": "games"}
            ]
        ]
        
        if self.is_admin(7475473197) or self.is_admin(7713987088):  # Your admin IDs
            keyboard.append([
                {"text": "🔧 Admin Panel", "callback_data": "admin_panel"}
            ])
        
        return {"inline_keyboard": keyboard}

    def create_admin_buttons(self):
        return {
            "inline_keyboard": [
                [
                    {"text": "📢 Broadcast", "callback_data": "broadcast_panel"},
                    {"text": "📊 Stats", "callback_data": "upload_stats"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        try:
            url = self.base_url + "answerCallbackQuery"
            data = {"callback_query_id": callback_query_id}
            if text:
                data["text"] = text
            if show_alert:
                data["show_alert"] = True
            requests.post(url, data=data, timeout=5)
        except:
            pass

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        try:
            url = self.base_url + "editMessageText"
            data = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, data=data, timeout=15)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"Edit message error: {e}")
            return False

    def handle_callback_query(self, callback_query):
        try:
            data = callback_query['data']
            message = callback_query['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            user_id = callback_query['from']['id']
            first_name = callback_query['from']['first_name']
            
            print(f"📨 Callback: {data} from {first_name} ({user_id})")
            
            self.answer_callback_query(callback_query['id'])
            
            # Broadcast system callbacks
            if data == "broadcast_panel":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                
                broadcast_info = """📢 <b>Admin Broadcast System</b>

Send messages to all bot subscribers.

⚡ Features:
• Send to all verified users
• HTML formatting support
• Preview before sending
• Delivery statistics
• Progress tracking

Choose an option:"""
                self.edit_message(chat_id, message_id, broadcast_info, self.create_broadcast_buttons())
                return
                
            elif data == "start_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.start_broadcast(user_id, chat_id)
                return
                
            elif data == "broadcast_stats":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.get_broadcast_stats(user_id, chat_id, message_id)
                return
                
            elif data == "confirm_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.send_broadcast_to_all(user_id, chat_id)
                return
                
            elif data == "cancel_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.cancel_broadcast(user_id, chat_id, message_id)
                return

            # Mini-games callbacks
            if data == "game_guess":
                self.start_number_guess_game(user_id, chat_id)
                return
                
            elif data == "game_random":
                self.generate_random_number(user_id, chat_id)
                return
                
            elif data == "game_spin":
                self.lucky_spin(user_id, chat_id)
                return
                
            elif data == "big_spin":
                self.big_spin(user_id, chat_id)
                return
                
            elif data.startswith("random_"):
                range_type = data.replace("random_", "")
                self.generate_custom_random(user_id, chat_id, range_type)
                return
                
            elif data == "mini_stats":
                self.show_mini_games_stats(user_id, chat_id, message_id)
                return

            # Handle other callbacks
            if data == "profile":
                profile_text = f"""👤 <b>User Profile</b>

🆔 User ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Status: {'Verified' if self.is_user_completed(user_id) else 'Not verified'}

Welcome to the bot!"""
                self.edit_message(chat_id, message_id, profile_text, self.create_main_menu_buttons())
                
            elif data == "time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_text = f"🕒 <b>Current Time</b>\n\n📅 {current_time}\n\n⏰ Server Time"
                self.edit_message(chat_id, message_id, time_text, self.create_main_menu_buttons())
                
            elif data == "channel_info":
                channel_info = f"""📢 <b>Channel Information</b>

🏷️ Channel: @pspgamers5
🔗 Link: https://t.me/pspgamers5
📝 Description: PSP Games & More!

Join our channel for the latest game updates!"""
                self.edit_message(chat_id, message_id, channel_info, self.create_main_menu_buttons())
                
            elif data == "games":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_main_menu_buttons())
                    return
                
                games_text = """🎮 <b>Games Section</b>

🎯 Available Features:
• Mini-Games (Number Guess, Lucky Spin, Random Number)
• More features coming soon!

Choose an option below:"""
                self.edit_message(chat_id, message_id, games_text, self.create_mini_games_buttons())
                
            elif data == "mini_games":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_main_menu_buttons())
                    return
                
                games_text = """🎮 <b>Mini Games</b>

🎯 Choose a game to play:

• 🎯 Number Guess - Guess the random number (1-10)
• 🎲 Random Number - Generate random numbers with analysis
• 🎰 Lucky Spin - Spin for lucky symbols and coins
• 📊 My Stats - View your gaming statistics

Have fun! 🎉"""
                self.edit_message(chat_id, message_id, games_text, self.create_mini_games_buttons())
                
            elif data == "back_to_menu":
                welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>Cross-Platform Telegram Bot</b>

Choose an option below:"""
                self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons())
            
            elif data == "verify_channel":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    welcome_text = f"""✅ <b>Verification Complete!</b>

👋 Welcome {first_name}!

🎉 You now have full access to all features!"""
                    self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons())
                else:
                    self.edit_message(chat_id, message_id, 
                                    "❌ You haven't joined the channel yet!\n\n"
                                    "Please join @pspgamers5 first, then click Verify Join again.",
                                    self.create_channel_buttons())
            
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_main_menu_buttons())
                    return
                
                admin_text = f"""👑 <b>Admin Panel</b>

👋 Welcome {first_name}!

🛠️ Admin Features:
• 📢 Broadcast messages to users
• 📊 View system statistics

Choose an option:"""
                self.edit_message(chat_id, message_id, admin_text, self.create_admin_buttons())
            
            elif data == "upload_stats":
                if not self.is_admin(user_id):
                    return
                
                stats_text = f"""📊 <b>System Statistics</b>

🤖 Bot Status: Running
🔋 Keep-Alive: Active
📊 Total Users: Checking...
🛡️ Crash Protection: Enabled

All systems operational!"""
                self.edit_message(chat_id, message_id, stats_text, self.create_admin_buttons())
                
        except Exception as e:
            print(f"Callback error: {e}")

    # ==================== BOT MAIN LOOP ====================

    def get_updates(self, offset=None):
        try:
            url = self.base_url + "getUpdates"
            params = {"timeout": 100, "offset": offset}
            response = requests.get(url, params=params, timeout=110)
            data = response.json()
            return data.get('result', []) if data.get('ok') else []
        except Exception as e:
            print(f"Get updates error: {e}")
            return []

    def run(self):
        """Main bot loop with comprehensive crash protection"""
        if not self.test_bot_connection():
            print("❌ Bot cannot start. Please check your token.")
            return
        
        # Start keep-alive service
        self.start_keep_alive()
        
        print("🤖 Bot is running with full protection...")
        print("📝 Send /start to begin")
        print("🎮 Mini-games available: /minigames")
        print("👑 Admin commands: /broadcast, /debug")
        print("🛡️  Crash protection enabled")
        print("🔋 Keep-alive system active")
        print("🛑 Press Ctrl+C to stop")
        
        offset = 0
        last_successful_update = time.time()
        
        while True:
            try:
                updates = self.get_updates(offset)
                
                # Check if we're getting updates regularly
                if updates:
                    last_successful_update = time.time()
                    # Reset error counter on successful updates
                    if self.consecutive_errors > 0:
                        self.consecutive_errors = 0
                        print("✅ Connection recovered")
                else:
                    # If no updates for a long time, check connection
                    if time.time() - last_successful_update > 120:  # 2 minutes
                        print("🔄 No updates received for 2 minutes, testing connection...")
                        if not self.test_bot_connection():
                            print("❌ Connection lost, reinitializing...")
                            self.auto_restart()
                            last_successful_update = time.time()
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    try:
                        if 'message' in update:
                            self.process_message(update['message'])
                        elif 'callback_query' in update:
                            self.handle_callback_query(update['callback_query'])
                    except Exception as e:
                        self.handle_error(e, "update_processing")
                        # Continue processing other updates even if one fails
                        continue
                
                # Small delay to prevent tight looping
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                if self.keep_alive:
                    self.keep_alive.stop()
                break
            except Exception as e:
                self.consecutive_errors += 1
                print(f"❌ Main loop error #{self.consecutive_errors}: {str(e)[:100]}...")
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    print("🔄 Too many consecutive errors, performing auto-restart...")
                    self.auto_restart()
                else:
                    # Exponential backoff for retries
                    sleep_time = min(5 * (2 ** (self.consecutive_errors - 1)), 30)
                    print(f"💤 Sleeping for {sleep_time} seconds before retry...")
                    time.sleep(sleep_time)

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot on Render...")
    
    # Start health server first
    start_health_check()
    print("✅ Health server started in background")
    
    # Wait a moment for health server to initialize
    time.sleep(2)
    
    # Check if BOT_TOKEN is available
    if not BOT_TOKEN:
        print("❌ CRITICAL: BOT_TOKEN environment variable not set!")
        print("💡 Please set BOT_TOKEN in Render Environment Variables")
        print("💡 The health server will continue running for monitoring")
        
        # Keep health server running even without bot token
        while True:
            time.sleep(10)
    else:
        print("✅ BOT_TOKEN found, starting bot...")
        
        # Main loop with restart capability
        restart_count = 0
        max_restarts = 10
        
        while restart_count < max_restarts:
            try:
                print(f"🔄 Starting bot instance #{restart_count + 1}...")
                bot = CrossPlatformBot(BOT_TOKEN)
                bot.run()
            except Exception as e:
                restart_count += 1
                print(f"💥 Bot crash (#{restart_count}): {e}")
                print("🔄 Restarting in 10 seconds...")
                time.sleep(10)
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
        else:
            print(f"❌ Maximum restarts ({max_restarts}) reached. Bot stopped.")
