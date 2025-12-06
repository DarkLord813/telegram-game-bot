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
from flask import Flask, jsonify, request
from threading import Thread
import traceback
import base64
from io import BytesIO
import hashlib
import hmac

print("TELEGRAM BOT - CROSS PLATFORM (NO INLINE KEYBOARDS)")
print("Using Regular Keyboards Only")
print("=" * 50)

# ==================== RENDER DEBUG SECTION ====================
print("🔍 RENDER DEBUG: Starting initialization...")
print(f"🔍 DEBUG: Python version: {sys.version}")
print(f"🔍 DEBUG: Current directory: {os.getcwd()}")
print(f"🔍 DEBUG: Files in directory: {os.listdir('.')}")

BOT_TOKEN = os.environ.get('BOT_TOKEN')

print(f"🔍 DEBUG: BOT_TOKEN exists: {'YES' if BOT_TOKEN else 'NO'}")

if BOT_TOKEN:
    print(f"🔍 DEBUG: Token starts with: {BOT_TOKEN[:10]}...")
    print(f"🔍 DEBUG: Token length: {len(BOT_TOKEN)}")
else:
    print("❌ DEBUG: BOT_TOKEN is MISSING! Check Render Environment Variables")

# Health check server
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Enhanced health check endpoint for Render monitoring"""
    try:
        bot_status = 'unknown'
        if 'bot' in globals() and hasattr(bot, 'test_bot_connection'):
            bot_status = 'healthy' if bot.test_bot_connection() else 'unhealthy'
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'telegram-game-bot',
            'version': '1.0.0',
            'bot_status': bot_status,
            'checks': {
                'bot_online': {'status': bot_status, 'message': f'Bot is {bot_status}'},
                'system': {'status': 'healthy', 'message': 'System operational'},
                'database': {'status': 'healthy', 'message': 'Database connected'}
            }
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time(),
            'bot_status': 'error'
        }), 500

@app.route('/redeploy', methods=['POST'])
def redeploy_bot():
    """Redeploy endpoint for admins and users"""
    try:
        # Get authorization from request
        auth_token = request.headers.get('Authorization', '')
        user_id = request.json.get('user_id', '') if request.json else ''
        
        # Simple authorization check
        is_authorized = auth_token == os.environ.get('REDEPLOY_TOKEN', 'default_token') or user_id in ['7475473197', '7713987088']
        
        if not is_authorized:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 401
        
        print(f"🔄 Redeploy triggered by user {user_id}")
        
        # Trigger redeploy logic
        trigger_redeploy()
        
        return jsonify({
            'status': 'success',
            'message': 'Redeploy initiated successfully',
            'redeploy_id': int(time.time()),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

def trigger_redeploy():
    """Trigger a redeploy of the bot"""
    try:
        print("🚀 Initiating bot redeploy...")
        
        # Schedule a graceful restart
        def delayed_restart():
            time.sleep(5)
            os._exit(0)
        
        restart_thread = threading.Thread(target=delayed_restart, daemon=True)
        restart_thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Redeploy error: {e}")
        return False

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Telegram Game Bot',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'redeploy': '/redeploy (POST)',
            'features': ['Game Distribution', 'Mini-Games', 'Admin Uploads', 'Broadcast Messaging', 'Telegram Stars', 'Game Requests', 'Premium Games', 'Game Removal System', 'Redeploy System', '24/7 Operation']
        }
    })

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
    print("✅ Health check server started on port 8080")

# ==================== ENHANCED KEEP-ALIVE SERVICE ====================

class EnhancedKeepAliveService:
    def __init__(self, health_url=None):
        self.health_url = health_url or f"http://localhost:{os.environ.get('PORT', 8080)}/health"
        self.is_running = False
        self.ping_count = 0
        self.last_successful_ping = time.time()
        
    def start(self):
        """Start enhanced keep-alive service with better monitoring"""
        self.is_running = True
        
        def ping_loop():
            consecutive_failures = 0
            max_consecutive_failures = 3
            
            while self.is_running:
                try:
                    self.ping_count += 1
                    response = requests.get(self.health_url, timeout=15)
                    
                    if response.status_code == 200:
                        self.last_successful_ping = time.time()
                        consecutive_failures = 0
                        print(f"✅ Keep-alive ping #{self.ping_count}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        consecutive_failures += 1
                        print(f"❌ Keep-alive failed: Status {response.status_code} (Failures: {consecutive_failures})")
                        
                except requests.exceptions.ConnectionError:
                    consecutive_failures += 1
                    print(f"🔌 Keep-alive connection error (Failures: {consecutive_failures})")
                except requests.exceptions.Timeout:
                    consecutive_failures += 1
                    print(f"⏰ Keep-alive timeout (Failures: {consecutive_failures})")
                except Exception as e:
                    consecutive_failures += 1
                    print(f"❌ Keep-alive error: {e} (Failures: {consecutive_failures})")
                
                # Emergency restart if too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    print("🚨 Too many consecutive failures, initiating emergency procedures...")
                    self.emergency_restart()
                    consecutive_failures = 0
                
                # Check if last successful ping was too long ago
                if time.time() - self.last_successful_ping > 600:  # 10 minutes
                    print("🚨 No successful pings for 10 minutes, emergency restart...")
                    self.emergency_restart()
                    self.last_successful_ping = time.time()
                
                # Dynamic ping interval
                if consecutive_failures > 0:
                    sleep_time = 60
                else:
                    sleep_time = 240
                
                time.sleep(sleep_time)
        
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print(f"🔄 Enhanced keep-alive service started")
        print(f"🌐 Health endpoint: {self.health_url}")
        
    def emergency_restart(self):
        """Emergency restart procedure"""
        print("🔄 Initiating emergency restart...")
        os._exit(1)
        
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
        
        # Session management
        self.user_sessions = {}  # {user_id: {'menu': 'main', 'state': 'waiting_input', 'data': {}}}
        self.guess_games = {}
        self.spin_games = {}
        self.broadcast_sessions = {}
        self.stars_sessions = {}
        self.request_sessions = {}
        self.upload_sessions = {}
        self.reply_sessions = {}
        self.search_sessions = {}
        self.search_results = {}
        
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
        self.games_cache = {}
        self.is_scanning = False
        
        print("✅ Bot system ready!")
        print(f"📊 Monitoring channel: {self.REQUIRED_CHANNEL}")
        print("📤 Forwarded files support enabled")
        print("🔍 Game search feature enabled")
        print("🎮 Mini-games integrated")
        print("📢 Admin broadcast messaging system enabled")
    
    def setup_database(self):
        try:
            self.conn = sqlite3.connect('telegram_bot.db', check_same_thread=False)
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
            
            # Games table
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
    
    def send_message(self, chat_id, text, keyboard=None):
        """Send message with optional keyboard"""
        try:
            url = self.base_url + "sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            if keyboard:
                data["reply_markup"] = json.dumps({
                    "keyboard": keyboard,
                    "resize_keyboard": True,
                    "one_time_keyboard": False
                })
            else:
                # Remove keyboard if None
                data["reply_markup"] = json.dumps({"remove_keyboard": True})
            
            response = requests.post(url, data=data, timeout=15)
            return response.json().get('ok', False)
            
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return False
    
    def send_main_menu(self, chat_id, user_id, first_name):
        """Send main menu"""
        keyboard = [
            ["📊 Profile", "🕒 Time"],
            ["📢 Channel", "🎮 Games"],
            ["🔍 Search Games", "📝 Request Game"],
            ["⭐ Donate Stars", "🎯 Mini Games"]
        ]
        
        # Add admin menu for admins
        if self.is_admin(user_id):
            keyboard.append(["👑 Admin Panel"])
        
        welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>GAMERDROID™ V1</b>

Choose an option below:"""
        
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def send_games_menu(self, chat_id):
        """Send games menu"""
        stats = self.get_channel_stats()
        keyboard = [
            ["📁 Game Files", "💰 Premium Games"],
            ["🎯 Mini Games", "🔍 Search Games"],
            ["📝 Request Game", "⭐ Donate Stars"],
            ["🔙 Back to Main Menu"]
        ]
        
        games_text = f"""🎮 <b>Games Section</b>

📊 Total Games: {stats['total_games']}
• 🆓 Regular: {stats['total_games']}
• 💰 Premium: 0

Choose an option:"""
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_game_files_menu(self, chat_id):
        """Send game files menu"""
        keyboard = [
            ["📦 ZIP Files", "🗜️ 7Z Files"],
            ["💿 ISO Files", "📱 APK Files"],
            ["🎮 PSP Games", "📋 All Files"],
            ["🔍 Search Games", "🔙 Back to Games"]
        ]
        
        files_text = """📁 <b>Game Files Browser</b>

Browse games by file type:

• 📦 ZIP Files - Compressed game archives
• 🗜️ 7Z Files - 7-Zip compressed archives  
• 💿 ISO Files - Disc image files
• 📱 APK Files - Android applications
• 🎮 PSP Games - PSP specific formats
• 📋 All Files - Complete game list

Choose an option:"""
        
        return self.send_message(chat_id, files_text, keyboard)
    
    def send_mini_games_menu(self, chat_id):
        """Send mini-games menu"""
        keyboard = [
            ["🎯 Number Guess", "🎲 Random Number"],
            ["🎰 Lucky Spin", "📊 My Stats"],
            ["🔙 Back to Games"]
        ]
        
        games_text = """🎮 <b>Mini Games</b>

Choose a game to play:

• 🎯 Number Guess - Guess the random number (1-10)
• 🎲 Random Number - Generate random numbers with analysis
• 🎰 Lucky Spin - Spin for lucky symbols and coins
• 📊 My Stats - View your gaming statistics

Have fun! 🎉"""
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_admin_menu(self, chat_id):
        """Send admin menu"""
        keyboard = [
            ["📤 Upload Games", "🗑️ Remove Games"],
            ["📢 Broadcast", "📊 Upload Stats"],
            ["🔄 Update Cache", "🔍 Scan Games"],
            ["🔙 Back to Main Menu"]
        ]
        
        admin_text = """👑 <b>Admin Panel</b>

Admin Features:
• 📤 Upload regular games
• 🗑️ Remove games  
• 📢 Broadcast messages
• 📊 View statistics
• 🔄 Update cache
• 🔍 Scan for games

Choose an option:"""
        
        return self.send_message(chat_id, admin_text, keyboard)
    
    def send_search_menu(self, chat_id):
        """Send search menu"""
        keyboard = [
            ["🔍 Search Again"],
            ["📁 Browse All", "🎮 Games Menu"],
            ["🔙 Main Menu"]
        ]
        
        search_text = """🔍 <b>Game Search</b>

To search for games, simply type the game name.

Examples:
• "GTA"
• "God of War"
• "FIFA"
• "Minecraft"

Type your game name now!"""
        
        return self.send_message(chat_id, search_text, keyboard)
    
    def send_verification_menu(self, chat_id):
        """Send verification menu"""
        keyboard = [
            ["✅ Verify Code"],
            ["📢 Join Channel"],
            ["🔄 Start Over"]
        ]
        
        verify_text = """🔐 <b>Verification Required</b>

Please complete verification to access games:

1. Join our channel: @pspgamers5
2. Get verification code with /start
3. Enter the code

Choose an option:"""
        
        return self.send_message(chat_id, verify_text, keyboard)
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def is_user_verified(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result and result[0] == 1
        except:
            return False
    
    def is_user_completed(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result and result[0] == 1 and result[1] == 1
        except:
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
                return status in ['member', 'administrator', 'creator']
            
        except Exception as e:
            print(f"❌ Channel check error: {e}")
        
        return False
    
    def mark_channel_joined(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET joined_channel = 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error marking channel: {e}")
            return False
    
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
                return False
                
            stored_code, expires_str = result
            expires = datetime.fromisoformat(expires_str)
            
            if datetime.now() > expires:
                return False
                
            if stored_code == code:
                cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
                self.conn.commit()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    def get_channel_stats(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games = cursor.fetchone()[0]
            return {'total_games': total_games, 'premium_games': 0}
        except:
            return {'total_games': 0, 'premium_games': 0}
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def update_games_cache(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT file_name, file_type, file_size, upload_date, category, is_uploaded FROM channel_games')
            games = cursor.fetchall()
            
            self.games_cache = {
                'zip': [], '7z': [], 'iso': [], 'apk': [], 'rar': [], 
                'pkg': [], 'cso': [], 'pbp': [], 'recent': [], 'all': []
            }
            
            for game in games:
                file_name, file_type, file_size, upload_date, category, is_uploaded = game
                game_info = {
                    'file_name': file_name,
                    'file_type': file_type,
                    'file_size': file_size,
                    'upload_date': upload_date,
                    'category': category,
                    'is_uploaded': is_uploaded
                }
                
                file_type_lower = file_type.lower()
                if file_type_lower in self.games_cache:
                    self.games_cache[file_type_lower].append(game_info)
                
                self.games_cache['all'].append(game_info)
            
            print(f"🔄 Cache updated: {len(self.games_cache['all'])} games")
            
        except Exception as e:
            print(f"Cache error: {e}")
    
    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Handle session states first
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]
                    
                    if session['state'] == 'waiting_code':
                        if text.isdigit() and len(text) == 6:
                            if self.verify_code(user_id, text):
                                if self.check_channel_membership(user_id):
                                    self.mark_channel_joined(user_id)
                                    self.send_message(chat_id, "✅ Verification complete! Welcome!")
                                    self.send_main_menu(chat_id, user_id, first_name)
                                else:
                                    self.send_message(chat_id, "✅ Code verified! Please join our channel @pspgamers5 and then click 'Join Channel' in the menu.")
                                    keyboard = [["📢 Join Channel"], ["🔙 Main Menu"]]
                                    self.send_message(chat_id, "Join our channel to continue:", keyboard)
                                del self.user_sessions[user_id]
                            else:
                                self.send_message(chat_id, "❌ Invalid or expired code. Try again or use /start")
                        return True
                    
                    elif session['state'] == 'waiting_game_name':
                        self.user_sessions[user_id] = {
                            'menu': 'request',
                            'state': 'waiting_platform',
                            'data': {'game_name': text}
                        }
                        self.send_message(chat_id, f"🎮 Game: {text}\n\nNow please specify the platform (PSP, Android, etc.):")
                        return True
                    
                    elif session['state'] == 'waiting_platform':
                        game_name = session['data']['game_name']
                        platform = text
                        
                        # Save request to database
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            INSERT INTO game_requests (user_id, user_name, game_name, platform, status)
                            VALUES (?, ?, ?, ?, 'pending')
                        ''', (user_id, first_name, game_name, platform))
                        self.conn.commit()
                        
                        self.send_message(chat_id, f"✅ Game request submitted!\n\nGame: {game_name}\nPlatform: {platform}\n\nWe'll notify you when it's available.")
                        del self.user_sessions[user_id]
                        return True
                    
                    elif session['state'] == 'waiting_search':
                        self.handle_game_search(chat_id, user_id, text)
                        del self.user_sessions[user_id]
                        return True
                    
                    elif session['state'] == 'waiting_stars_amount':
                        try:
                            stars_amount = int(text)
                            if stars_amount > 0:
                                self.send_message(chat_id, f"⭐ {stars_amount} Stars selected. Payment system would be integrated here.")
                                del self.user_sessions[user_id]
                            else:
                                self.send_message(chat_id, "❌ Please enter a positive number.")
                        except:
                            self.send_message(chat_id, "❌ Please enter a valid number.")
                        return True
                
                # Handle number guess game
                if user_id in self.guess_games:
                    if text.strip().isdigit():
                        guess = int(text.strip())
                        return self.handle_guess_input(chat_id, user_id, guess)
                
                # Handle commands and menu options
                if text == '/start':
                    return self.handle_start(chat_id, user_id, first_name)
                
                elif text == '/menu':
                    if self.is_user_completed(user_id):
                        self.send_main_menu(chat_id, user_id, first_name)
                    else:
                        self.send_verification_menu(chat_id)
                    return True
                
                elif text == '🔙 Back to Main Menu':
                    self.send_main_menu(chat_id, user_id, first_name)
                    return True
                
                elif text == '🔙 Back to Games':
                    self.send_games_menu(chat_id)
                    return True
                
                elif text == '🎮 Games':
                    if self.is_user_completed(user_id):
                        self.send_games_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '📁 Game Files':
                    if self.is_user_completed(user_id):
                        self.send_game_files_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '🎯 Mini Games':
                    if self.is_user_completed(user_id):
                        self.send_mini_games_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '🔍 Search Games':
                    if self.is_user_completed(user_id):
                        self.user_sessions[user_id] = {
                            'menu': 'search',
                            'state': 'waiting_search',
                            'data': {}
                        }
                        self.send_search_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '📝 Request Game':
                    if self.is_user_completed(user_id):
                        self.user_sessions[user_id] = {
                            'menu': 'request',
                            'state': 'waiting_game_name',
                            'data': {}
                        }
                        self.send_message(chat_id, "🎮 Please enter the name of the game you want to request:")
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '⭐ Donate Stars':
                    if self.is_user_completed(user_id):
                        keyboard = [
                            ["⭐ 50 Stars", "⭐ 100 Stars"],
                            ["⭐ 500 Stars", "⭐ 1000 Stars"],
                            ["💫 Custom Amount", "🔙 Back to Games"]
                        ]
                        self.send_message(chat_id, "⭐ Support our bot with Telegram Stars!\n\nChoose an amount:", keyboard)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '💫 Custom Amount':
                    self.user_sessions[user_id] = {
                        'menu': 'stars',
                        'state': 'waiting_stars_amount',
                        'data': {}
                    }
                    self.send_message(chat_id, "💫 Enter the number of Stars you'd like to donate:")
                    return True
                
                elif text.startswith('⭐ '):
                    stars_text = text.replace('⭐ ', '').replace(' Stars', '')
                    try:
                        stars_amount = int(stars_text)
                        self.send_message(chat_id, f"⭐ {stars_amount} Stars selected. Payment system would be integrated here.")
                    except:
                        self.send_message(chat_id, "❌ Invalid stars amount.")
                    return True
                
                elif text == '📊 Profile':
                    self.handle_profile(chat_id, user_id, first_name)
                    return True
                
                elif text == '🕒 Time':
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.send_message(chat_id, f"🕒 Current Time: {current_time}")
                    return True
                
                elif text == '📢 Channel':
                    channel_text = f"""📢 <b>Channel Information</b>

🏷️ Channel: @pspgamers5
🔗 Link: https://t.me/pspgamers5
📝 Description: PSP Games & More!

Join our channel to access games!"""
                    self.send_message(chat_id, channel_text)
                    return True
                
                elif text == '📢 Join Channel':
                    if self.check_channel_membership(user_id):
                        self.mark_channel_joined(user_id)
                        if self.is_user_verified(user_id):
                            self.send_message(chat_id, "✅ Channel verified! Welcome!")
                            self.send_main_menu(chat_id, user_id, first_name)
                        else:
                            self.send_message(chat_id, "✅ Channel joined! Now verify your code with /start")
                    else:
                        self.send_message(chat_id, "❌ You haven't joined the channel yet. Please join @pspgamers5 first.")
                    return True
                
                elif text == '✅ Verify Code':
                    self.send_message(chat_id, "🔐 Please enter your 6-digit verification code:")
                    self.user_sessions[user_id] = {
                        'menu': 'verify',
                        'state': 'waiting_code',
                        'data': {}
                    }
                    return True
                
                elif text == '👑 Admin Panel':
                    if self.is_admin(user_id):
                        self.send_admin_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                elif text == '📤 Upload Games' and self.is_admin(user_id):
                    self.send_message(chat_id, "📤 To upload a game, simply send the game file to this bot.\n\nSupported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP")
                    return True
                
                elif text == '🗑️ Remove Games' and self.is_admin(user_id):
                    keyboard = [["🔍 Search & Remove"], ["📋 View Recent"], ["🔙 Admin Menu"]]
                    self.send_message(chat_id, "🗑️ Game Removal System\n\nChoose an option:", keyboard)
                    return True
                
                elif text == '📢 Broadcast' and self.is_admin(user_id):
                    self.send_message(chat_id, "📢 Broadcast System\n\nType your broadcast message:")
                    self.user_sessions[user_id] = {
                        'menu': 'broadcast',
                        'state': 'waiting_message',
                        'data': {}
                    }
                    return True
                
                elif text == '📊 Upload Stats' and self.is_admin(user_id):
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
                    uploads = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_forwarded = 1')
                    forwards = cursor.fetchone()[0]
                    
                    stats_text = f"""📊 Upload Statistics

Total uploads: {uploads}
Forwarded files: {forwards}
Total games: {len(self.games_cache.get('all', []))}

Use 'Upload Games' to add more files."""
                    self.send_message(chat_id, stats_text)
                    return True
                
                elif text == '🔄 Update Cache' and self.is_admin(user_id):
                    self.update_games_cache()
                    self.send_message(chat_id, "✅ Games cache updated!")
                    return True
                
                elif text == '🔍 Scan Games' and self.is_admin(user_id):
                    self.send_message(chat_id, "🔍 Scanning for games...")
                    self.scan_channel_for_games()
                    self.send_message(chat_id, "✅ Game scan complete!")
                    return True
                
                elif text == '🔙 Admin Menu':
                    self.send_admin_menu(chat_id)
                    return True
                
                elif text == '🎯 Number Guess':
                    if self.is_user_completed(user_id):
                        self.start_number_guess_game(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '🎲 Random Number':
                    if self.is_user_completed(user_id):
                        self.generate_random_number(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '🎰 Lucky Spin':
                    if self.is_user_completed(user_id):
                        self.lucky_spin(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '📊 My Stats':
                    if self.is_user_completed(user_id):
                        self.show_mini_games_stats(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text in ['📦 ZIP Files', '🗜️ 7Z Files', '💿 ISO Files', '📱 APK Files', '🎮 PSP Games', '📋 All Files']:
                    if self.is_user_completed(user_id):
                        file_type_map = {
                            '📦 ZIP Files': 'zip',
                            '🗜️ 7Z Files': '7z',
                            '💿 ISO Files': 'iso',
                            '📱 APK Files': 'apk',
                            '🎮 PSP Games': 'psp',
                            '📋 All Files': 'all'
                        }
                        
                        file_type = file_type_map.get(text, 'all')
                        
                        if file_type == 'psp':
                            games = self.games_cache.get('cso', []) + self.games_cache.get('pbp', [])
                        elif file_type == 'all':
                            games = self.games_cache.get('all', [])
                        else:
                            games = self.games_cache.get(file_type, [])
                        
                        if not games:
                            self.send_message(chat_id, f"❌ No {text} found.")
                            return True
                        
                        # Show first 10 games
                        games_text = f"📁 {text}\n\n"
                        for i, game in enumerate(games[:10], 1):
                            size = self.format_file_size(game['file_size'])
                            games_text += f"{i}. {game['file_name']}\n"
                            games_text += f"   📦 {game['file_type']} | 📏 {size}\n\n"
                        
                        if len(games) > 10:
                            games_text += f"📋 ... and {len(games) - 10} more files\n\n"
                        
                        games_text += "To download a game, use the search feature or ask admin."
                        
                        self.send_message(chat_id, games_text)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '🔍 Search Again':
                    self.user_sessions[user_id] = {
                        'menu': 'search',
                        'state': 'waiting_search',
                        'data': {}
                    }
                    self.send_search_menu(chat_id)
                    return True
                
                elif text == '📁 Browse All':
                    self.send_game_files_menu(chat_id)
                    return True
                
                elif text == '🎮 Games Menu':
                    self.send_games_menu(chat_id)
                    return True
                
                # Handle document uploads from admins
                if 'document' in message and self.is_admin(user_id):
                    return self.handle_document_upload(message)
                
                # Handle forwarded messages from admins
                if 'forward_origin' in message and self.is_admin(user_id):
                    return self.handle_forwarded_message(message)
                
                # If no command matched, check if it's a search query
                if self.is_user_completed(user_id) and len(text) > 2:
                    self.handle_game_search(chat_id, user_id, text)
                    return True
            
            # Handle photo messages
            if 'photo' in message:
                user_id = message['from']['id']
                chat_id = message['chat']['id']
                
                # Check if this is a broadcast photo from admin
                if user_id in self.user_sessions and self.user_sessions[user_id]['state'] == 'waiting_message' and self.is_admin(user_id):
                    photo = message['photo'][-1]
                    caption = message.get('caption', 'Broadcast Message')
                    self.send_message(chat_id, "📷 Photo broadcast would be sent here.")
                    del self.user_sessions[user_id]
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            return False
    
    def handle_start(self, chat_id, user_id, first_name):
        """Handle /start command"""
        try:
            username = ""
            
            # Check if user is already completed
            if self.is_user_completed(user_id):
                self.send_main_menu(chat_id, user_id, first_name)
                return True
            
            # Check if user is verified but not joined channel
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                keyboard = [["📢 Join Channel"], ["✅ Verify Code"]]
                self.send_message(chat_id, "✅ Code verified! Please join our channel @pspgamers5", keyboard)
                return True
            
            # Generate verification code
            code = self.generate_code()
            if self.save_verification_code(user_id, username, first_name, code):
                self.user_sessions[user_id] = {
                    'menu': 'verify',
                    'state': 'waiting_code',
                    'data': {}
                }
                
                welcome_text = f"""🔐 <b>Welcome to PSP Gamers Bot!</b>

👋 Hello {first_name}!

Your verification code: 
<code>{code}</code>

📝 Reply with this code to verify.

⏰ Code expires in 10 minutes.

After verification, join our channel: @pspgamers5"""
                
                self.send_message(chat_id, welcome_text)
                return True
            else:
                self.send_message(chat_id, "❌ Error generating verification code. Please try again.")
                return False
            
        except Exception as e:
            print(f"❌ Start handler error: {e}")
            self.send_message(chat_id, "❌ Error starting bot. Please try again.")
            return False
    
    def handle_profile(self, chat_id, user_id, first_name):
        """Handle profile command"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT created_at, is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                created_at, is_verified, joined_channel = result
                profile_text = f"""👤 <b>User Profile</b>

🆔 User ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Verified: {'Yes' if is_verified else 'No'}
📢 Channel Joined: {'Yes' if joined_channel else 'No'}
📅 Member Since: {created_at}"""
            else:
                profile_text = f"""👤 <b>User Profile</b>

🆔 User ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Verified: No
📢 Channel Joined: No

Use /start to begin verification."""

            self.send_message(chat_id, profile_text)
            
        except Exception as e:
            print(f"❌ Profile error: {e}")
    
    def handle_game_search(self, chat_id, user_id, search_term):
        """Handle game search"""
        try:
            if not search_term or len(search_term) < 2:
                self.send_message(chat_id, "❌ Please enter at least 2 characters to search.")
                return False
            
            print(f"🔍 User {user_id} searching for: '{search_term}'")
            
            # Search in database
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT file_name, file_type, file_size, upload_date, category, is_uploaded
                FROM channel_games 
                WHERE LOWER(file_name) LIKE ? 
                ORDER BY file_name
                LIMIT 20
            ''', (f'%{search_term.lower()}%',))
            
            results = cursor.fetchall()
            
            if not results:
                self.send_message(chat_id, f"❌ No games found for: {search_term}")
                return True
            
            results_text = f"🔍 Search Results for: {search_term}\n\n"
            results_text += f"📊 Found: {len(results)} games\n\n"
            
            for i, game in enumerate(results[:10], 1):
                file_name, file_type, file_size, upload_date, category, is_uploaded = game
                size = self.format_file_size(file_size)
                source = "🤖 Bot" if is_uploaded == 1 else "📢 Channel"
                
                results_text += f"{i}. {file_name}\n"
                results_text += f"   📦 {file_type} | 📏 {size} | {source}\n\n"
            
            if len(results) > 10:
                results_text += f"📋 ... and {len(results) - 10} more games\n\n"
            
            results_text += "To request a game not listed, use 'Request Game' in the menu."
            
            self.send_message(chat_id, results_text)
            return True
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            self.send_message(chat_id, "❌ Error searching for games. Please try again.")
            return False
    
    def handle_document_upload(self, message):
        """Handle document upload from admin"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            if not self.is_admin(user_id):
                return False
            
            if 'document' not in message:
                return False
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            bot_message_id = message['message_id']
            
            print(f"📥 Admin {user_id} uploading: {file_name}")
            
            # Check if it's a supported game file
            game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
            if not any(file_name.lower().endswith(ext) for ext in game_extensions):
                self.send_message(chat_id, f"❌ File type not supported: {file_name}")
                return False
            
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine if this is a forwarded file
            is_forwarded = 'forward_origin' in message
            
            # Generate unique message ID for storage
            storage_message_id = int(time.time() * 1000) + random.randint(1000, 9999)
            
            # Prepare game info
            game_info = {
                'message_id': storage_message_id,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': file_size,
                'upload_date': upload_date,
                'category': self.determine_file_category(file_name),
                'added_by': user_id,
                'is_uploaded': 1,
                'is_forwarded': 1 if is_forwarded else 0,
                'file_id': file_id,
                'bot_message_id': bot_message_id
            }
            
            # Store in database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO channel_games 
                (message_id, file_name, file_type, file_size, upload_date, category, 
                 added_by, is_uploaded, is_forwarded, file_id, bot_message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_info['message_id'],
                game_info['file_name'],
                game_info['file_type'],
                game_info['file_size'],
                game_info['upload_date'],
                game_info['category'],
                game_info['added_by'],
                game_info['is_uploaded'],
                game_info['is_forwarded'],
                game_info['file_id'],
                game_info['bot_message_id']
            ))
            self.conn.commit()
            
            # Update cache
            self.update_games_cache()
            
            # Send confirmation
            size = self.format_file_size(file_size)
            confirm_text = f"""✅ Game file added successfully!

📁 File: {file_name}
📦 Type: {file_type}
📏 Size: {size}
🗂️ Category: {game_info['category']}
🕒 Added: {upload_date}

The file is now available in the games browser!"""
            
            self.send_message(chat_id, confirm_text)
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def handle_forwarded_message(self, message):
        """Handle forwarded messages from admin"""
        # Similar to document upload but for forwarded messages
        return self.handle_document_upload(message)
    
    def determine_file_category(self, filename):
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.apk'):
            return 'Android Games'
        elif filename_lower.endswith('.iso'):
            if 'psp' in filename_lower:
                return 'PSP Games'
            elif 'ps2' in filename_lower:
                return 'PS2 Games'
            elif 'ps1' in filename_lower or 'psx' in filename_lower:
                return 'PS1 Games'
            else:
                return 'ISO Games'
        elif filename_lower.endswith('.zip'):
            if 'psp' in filename_lower:
                return 'PSP Games'
            else:
                return 'ZIP Games'
        elif filename_lower.endswith('.7z'):
            return '7Z Games'
        elif filename_lower.endswith('.pkg'):
            return 'PS Vita Games'
        elif filename_lower.endswith('.cso') or filename_lower.endswith('.pbp'):
            return 'PSP Games'
        else:
            return 'Other Games'
    
    # ==================== MINI-GAMES METHODS ====================
    
    def start_number_guess_game(self, chat_id, user_id):
        """Start a new number guess game"""
        target_number = random.randint(1, 10)
        self.guess_games[user_id] = {
            'target': target_number,
            'attempts': 0,
            'max_attempts': 5,
            'start_time': time.time()
        }
        
        game_text = f"""🎯 <b>Number Guess Game Started!</b>

I'm thinking of a number between 1 and 10.

📝 <b>How to play:</b>
• Guess the number by typing it (1-10)
• You have 5 attempts
• I'll tell you if your guess is too high or too low

🎮 <b>Type your first guess now!</b>"""
        
        self.send_message(chat_id, game_text)
        return True
    
    def handle_guess_input(self, chat_id, user_id, guess):
        """Handle user's number guess"""
        if user_id not in self.guess_games:
            self.send_message(chat_id, "❌ No active number guess game. Start a new one from Mini-Games!")
            return False
        
        game = self.guess_games[user_id]
        game['attempts'] += 1
        target = game['target']
        
        if guess == target:
            time_taken = time.time() - game['start_time']
            win_text = f"""🎉 <b>Congratulations! You won!</b>

✅ Correct guess: {guess}
🎯 Target number: {target}
📊 Attempts used: {game['attempts']}
⏱️ Time taken: {time_taken:.1f} seconds

🏆 <b>Well done!</b>"""
            
            self.send_message(chat_id, win_text)
            del self.guess_games[user_id]
            
        elif game['attempts'] >= game['max_attempts']:
            lose_text = f"""😔 <b>Game Over!</b>

🎯 The number was: {target}
📊 Your attempts: {game['attempts']}
💡 Better luck next time!"""
            
            self.send_message(chat_id, lose_text)
            del self.guess_games[user_id]
            
        else:
            remaining = game['max_attempts'] - game['attempts']
            hint = "📈 Too high!" if guess > target else "📉 Too low!"
            
            progress_text = f"""🎯 <b>Number Guess Game</b>

🔢 Your guess: {guess}
{hint}
📊 Attempts: {game['attempts']}/5
🎯 Remaining attempts: {remaining}

💡 Keep guessing!"""
            
            self.send_message(chat_id, progress_text)
        
        return True
    
    def generate_random_number(self, chat_id, user_id):
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
        
        analysis_text = "\n".join(analysis)
        
        random_text = f"""🎲 <b>Random Number Generator</b>

🎯 Your lucky number: 
<b>🎊 {number} 🎊</b>

📊 <b>Analysis:</b>
{analysis_text}"""
        
        self.send_message(chat_id, random_text)
        return True
    
    def lucky_spin(self, chat_id, user_id):
        """Perform a lucky spin"""
        now = time.time()
        
        # Rate limiting: 1 spin per 3 seconds
        if user_id in self.spin_games:
            last_spin = self.spin_games[user_id].get('last_spin', 0)
            if now - last_spin < 3:
                wait_time = 3 - (now - last_spin)
                self.send_message(chat_id, f"⏳ Please wait {wait_time:.1f} seconds before spinning again!")
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
• Total Winnings: {stats['total_wins']} coins"""
        
        self.send_message(chat_id, spin_text)
        return True
    
    def show_mini_games_stats(self, chat_id, user_id):
        """Show user's mini-games statistics"""
        guess_stats = "No games played" if user_id not in self.guess_games else f"Active game: {self.guess_games[user_id]['attempts']} attempts"
        spin_stats = "No spins yet" if user_id not in self.spin_games else f"{self.spin_games[user_id]['spins']} spins, {self.spin_games[user_id]['total_wins']} coins won"
        
        stats_text = f"""📊 <b>Mini-Games Statistics</b>

🎯 <b>Number Guess:</b>
{guess_stats}

🎰 <b>Lucky Spin:</b>
{spin_stats}

🎲 <b>Random Number:</b>
Always available!"""
        
        self.send_message(chat_id, stats_text)
    
    # ==================== GAME SCANNING METHODS ====================
    
    def scan_channel_for_games(self):
        """Scan channel for game files"""
        if self.is_scanning:
            return 0
        
        self.is_scanning = True
        try:
            print(f"🔍 Scanning {self.REQUIRED_CHANNEL} for games...")
            
            # Get channel messages
            url = self.base_url + "getChatHistory"
            data = {
                "chat_id": self.REQUIRED_CHANNEL,
                "limit": 50
            }
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            games_found = 0
            
            if result.get('ok'):
                messages = result.get('result', [])
                
                for message in messages:
                    if 'document' in message:
                        doc = message['document']
                        file_name = doc.get('file_name', '').lower()
                        
                        game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
                        if any(file_name.endswith(ext) for ext in game_extensions):
                            
                            # Check if already in database
                            cursor = self.conn.cursor()
                            cursor.execute('SELECT message_id FROM channel_games WHERE message_id = ?', (message['message_id'],))
                            existing = cursor.fetchone()
                            
                            if not existing:
                                # Add to database
                                file_type = file_name.split('.')[-1].upper()
                                file_size = doc.get('file_size', 0)
                                file_id = doc.get('file_id', '')
                                upload_date = datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
                                
                                cursor.execute('''
                                    INSERT OR IGNORE INTO channel_games 
                                    (message_id, file_name, file_type, file_size, upload_date, category, added_by, is_uploaded, is_forwarded, file_id, bot_message_id)
                                    VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, ?, NULL)
                                ''', (
                                    message['message_id'],
                                    doc.get('file_name', 'Unknown'),
                                    file_type,
                                    file_size,
                                    upload_date,
                                    self.determine_file_category(file_name),
                                    file_id
                                ))
                                
                                self.conn.commit()
                                games_found += 1
            
            self.update_games_cache()
            print(f"✅ Found {games_found} new games")
            
            self.is_scanning = False
            return games_found
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            self.is_scanning = False
            return 0
    
    def robust_send_message(self, chat_id, text, keyboard=None):
        """Send message with retry logic"""
        for attempt in range(3):
            try:
                return self.send_message(chat_id, text, keyboard)
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)
                    continue
                print(f"❌ Failed to send message after 3 attempts: {e}")
                return False
        return False
    
    # ==================== ENHANCED RUN METHOD ====================

    def run(self):
        """Main bot loop"""
        print("🤖 Bot is running...")
        
        offset = 0
        
        while True:
            try:
                # Get updates from Telegram
                url = self.base_url + "getUpdates"
                params = {"timeout": 100, "offset": offset}
                response = requests.get(url, params=params, timeout=110)
                data = response.json()
                
                if data.get('ok'):
                    updates = data.get('result', [])
                    
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        try:
                            if 'message' in update:
                                self.process_message(update['message'])
                        except Exception as e:
                            print(f"❌ Update processing error: {e}")
                            continue
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
                
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)

# ==================== START THE BOT ====================

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot...")
    
    # Start health check server
    start_health_check()
    
    # Wait for health server to start
    time.sleep(2)
    
    if BOT_TOKEN:
        print("🔍 Testing bot token...")
        
        # Test connection
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_name = data['result']['first_name']
                print(f"✅ Bot connected: {bot_name}")
                
                # Start the bot
                bot = CrossPlatformBot(BOT_TOKEN)
                bot.run()
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    else:
        print("❌ ERROR: BOT_TOKEN environment variable not set!")
        print("💡 Health server will continue running for monitoring")
        
        # Keep the health server running
        while True:
            time.sleep(60)
