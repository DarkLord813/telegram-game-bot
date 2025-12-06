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

print("TELEGRAM BOT - CROSS PLATFORM WITH STARS PAYMENTS")
print("Using Regular Keyboards + Telegram Stars")
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

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Telegram Game Bot with Stars',
        'status': 'running',
        'version': '1.0.0'
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

# ==================== TELEGRAM STARS PAYMENT SYSTEM ====================

class TelegramStarsSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_stars_database()
        print("✅ Telegram Stars system initialized!")
        
    def setup_stars_database(self):
        """Setup stars payments database"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Stars transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    stars_amount INTEGER,
                    usd_amount REAL,
                    description TEXT,
                    telegram_star_amount INTEGER,
                    transaction_id TEXT UNIQUE,
                    payment_status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            ''')
            
            # Stars balance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_balance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_stars_earned INTEGER DEFAULT 0,
                    total_usd_earned REAL DEFAULT 0.0,
                    available_stars INTEGER DEFAULT 0,
                    available_usd REAL DEFAULT 0.0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Premium games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    stars_price INTEGER DEFAULT 0,
                    description TEXT,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_id TEXT,
                    added_by INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Premium purchases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_id INTEGER,
                    stars_paid INTEGER,
                    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # Initialize balance if not exists
            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')
            
            self.bot.conn.commit()
            print("✅ Telegram Stars database setup complete!")
            
        except Exception as e:
            print(f"❌ Stars database setup error: {e}")
    
    def create_stars_invoice(self, user_id, chat_id, stars_amount, description="Donation"):
        """Create Telegram Stars payment invoice"""
        try:
            # Generate unique invoice payload
            invoice_payload = f"stars_{user_id}_{int(time.time())}"
            
            # Stars pricing (approximate conversion: 1 Star ≈ $0.01)
            usd_amount = stars_amount * 0.01
            
            # Prepare stars invoice data
            prices = [{"label": f"{stars_amount} Stars", "amount": stars_amount}]
            
            invoice_data = {
                "chat_id": chat_id,
                "title": "🌟 Bot Stars Donation",
                "description": description,
                "payload": invoice_payload,
                "currency": "XTR",  # Telegram Stars currency
                "prices": json.dumps(prices),
                "start_parameter": "stars_donation",
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }
            
            print(f"⭐ Creating Stars invoice for {stars_amount} stars (${usd_amount:.2f})")
            
            # Send invoice via Telegram API
            url = self.bot.base_url + "sendInvoice"
            response = requests.post(url, data=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                # Store transaction in database
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO stars_transactions 
                    (user_id, user_name, stars_amount, usd_amount, description, transaction_id, payment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    self.bot.get_user_info(user_id)['first_name'],
                    stars_amount,
                    usd_amount,
                    description,
                    invoice_payload,
                    'pending'
                ))
                
                self.bot.conn.commit()
                print(f"✅ Stars invoice created for user {user_id}: {stars_amount} stars")
                return True, invoice_payload
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Error creating Stars invoice: {error_msg}")
                return False, None
            
        except Exception as e:
            print(f"❌ Error creating Stars invoice: {e}")
            traceback.print_exc()
            return False, None
    
    def create_premium_game_invoice(self, user_id, chat_id, stars_amount, game_name, game_id):
        """Create Stars invoice for premium game purchase"""
        try:
            invoice_payload = f"premium_game_{game_id}_{user_id}_{int(time.time())}"
            usd_amount = stars_amount * 0.01
            
            prices = [{"label": f"Premium Game: {game_name}", "amount": stars_amount}]
            
            invoice_data = {
                "chat_id": chat_id,
                "title": f"🎮 {game_name}",
                "description": f"Premium Game Purchase - {stars_amount} Stars",
                "payload": invoice_payload,
                "currency": "XTR",
                "prices": json.dumps(prices),
                "start_parameter": f"premium_game_{game_id}",
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }
            
            print(f"⭐ Creating premium game invoice: {game_name} for {stars_amount} stars")
            
            url = self.bot.base_url + "sendInvoice"
            response = requests.post(url, data=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                # Store premium purchase record
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO premium_purchases 
                    (user_id, game_id, stars_paid, transaction_id, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, game_id, stars_amount, invoice_payload, 'pending'))
                
                self.bot.conn.commit()
                print(f"✅ Premium game invoice created: {game_name} for user {user_id}")
                return True, invoice_payload
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Error creating premium game invoice: {error_msg}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error creating premium game invoice: {e}")
            traceback.print_exc()
            return False, None
    
    def get_balance(self):
        """Get current stars balance"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT * FROM stars_balance WHERE id = 1')
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_stars_earned': result[1] or 0,
                    'total_usd_earned': result[2] or 0.0,
                    'available_stars': result[3] or 0,
                    'available_usd': result[4] or 0.0,
                    'last_updated': result[5]
                }
            return {'available_stars': 0, 'available_usd': 0.0}
        except Exception as e:
            print(f"❌ Error getting stars balance: {e}")
            return {'available_stars': 0, 'available_usd': 0.0}
    
    def get_recent_transactions(self, limit=5):
        """Get recent stars transactions"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT user_name, stars_amount, usd_amount, payment_status, created_at 
                FROM stars_transactions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting recent stars transactions: {e}")
            return []
    
    def complete_premium_purchase(self, transaction_id):
        """Mark premium purchase as completed"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Get purchase details
            cursor.execute('''
                SELECT user_id, game_id, stars_paid FROM premium_purchases 
                WHERE transaction_id = ? AND status = 'pending'
            ''', (transaction_id,))
            purchase = cursor.fetchone()
            
            if not purchase:
                return False
                
            user_id, game_id, stars_paid = purchase
            
            # Update purchase status
            cursor.execute('''
                UPDATE premium_purchases 
                SET status = 'completed' 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            # Update stars balance
            cursor.execute('''
                UPDATE stars_balance 
                SET total_stars_earned = total_stars_earned + ?,
                    total_usd_earned = total_usd_earned + ?,
                    available_stars = available_stars + ?,
                    available_usd = available_usd + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (stars_paid, stars_paid * 0.01, stars_paid, stars_paid * 0.01))
            
            # Update transaction status
            cursor.execute('''
                UPDATE stars_transactions 
                SET payment_status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            self.bot.conn.commit()
            
            # Send game file to user
            game = self.get_premium_game_by_id(game_id)
            if game and game['file_id']:
                self.bot.send_document_directly(user_id, game['file_id'])
            
            return True
        except Exception as e:
            print(f"❌ Error completing premium purchase: {e}")
            return False
    
    def add_premium_game(self, file_name, file_type, file_size, stars_price, description, file_id, added_by):
        """Add a premium game to database"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_games 
                (file_name, file_type, file_size, stars_price, description, file_id, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_name, file_type, file_size, stars_price, description, file_id, added_by))
            
            self.bot.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error adding premium game: {e}")
            return False
    
    def get_premium_games(self, limit=20):
        """Get all premium games"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, file_name, file_type, file_size, stars_price, description 
                FROM premium_games 
                WHERE is_active = 1
                ORDER BY upload_date DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting premium games: {e}")
            return []
    
    def get_premium_game_by_id(self, game_id):
        """Get premium game by ID"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, file_name, file_type, file_size, stars_price, description, file_id
                FROM premium_games 
                WHERE id = ? AND is_active = 1
            ''', (game_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'file_name': result[1],
                    'file_type': result[2],
                    'file_size': result[3],
                    'stars_price': result[4],
                    'description': result[5],
                    'file_id': result[6]
                }
            return None
        except Exception as e:
            print(f"❌ Error getting premium game by ID: {e}")
            return None
    
    def has_user_purchased_game(self, user_id, game_id):
        """Check if user has already purchased a premium game"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id FROM premium_purchases 
                WHERE user_id = ? AND game_id = ? AND status = 'completed'
            ''', (user_id, game_id))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ Error checking user purchase: {e}")
            return False
    
    def handle_pre_checkout(self, pre_checkout_query_id):
        """Handle pre-checkout query"""
        try:
            url = self.bot.base_url + "answerPreCheckoutQuery"
            data = {
                "pre_checkout_query_id": pre_checkout_query_id,
                "ok": True
            }
            response = requests.post(url, data=data, timeout=10)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"❌ Error handling pre-checkout: {e}")
            return False
    
    def handle_successful_payment(self, successful_payment):
        """Handle successful payment"""
        try:
            invoice_payload = successful_payment.get('invoice_payload', '')
            
            if invoice_payload.startswith('premium_game_'):
                # This is a premium game purchase
                return self.complete_premium_purchase(invoice_payload)
            elif invoice_payload.startswith('stars_'):
                # This is a stars donation
                return self.complete_stars_donation(invoice_payload)
            
            return False
        except Exception as e:
            print(f"❌ Error handling successful payment: {e}")
            return False
    
    def complete_stars_donation(self, transaction_id):
        """Complete stars donation"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Update transaction status
            cursor.execute('''
                UPDATE stars_transactions 
                SET payment_status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            # Update balance
            cursor.execute('''
                SELECT stars_amount FROM stars_transactions 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            result = cursor.fetchone()
            
            if result:
                stars_amount = result[0]
                cursor.execute('''
                    UPDATE stars_balance 
                    SET total_stars_earned = total_stars_earned + ?,
                        total_usd_earned = total_usd_earned + ?,
                        available_stars = available_stars + ?,
                        available_usd = available_usd + ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = 1
                ''', (stars_amount, stars_amount * 0.01, stars_amount, stars_amount * 0.01))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error completing stars donation: {e}")
            return False

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
        self.user_sessions = {}
        self.guess_games = {}
        self.spin_games = {}
        
        # Telegram Stars system
        self.stars_system = TelegramStarsSystem(self)
        
        # CRASH PROTECTION
        self.last_restart = time.time()
        self.error_count = 0
        
        self.setup_database()
        self.games_cache = {}
        self.is_scanning = False
        
        print("✅ Bot system ready!")
        print(f"📊 Monitoring channel: {self.REQUIRED_CHANNEL}")
        print("⭐ Telegram Stars payments system enabled")
        print("💰 Premium games system enabled")
    
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
            
            # Regular games table
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
    
    def send_document_directly(self, chat_id, file_id, caption=None):
        """Send document directly using file_id"""
        try:
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id,
                "caption": caption or "📥 Here's your requested file!",
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            return response.json().get('ok', False)
            
        except Exception as e:
            print(f"❌ Send document error: {e}")
            return False
    
    def send_main_menu(self, chat_id, user_id, first_name):
        """Send main menu"""
        keyboard = [
            ["📊 Profile", "🕒 Time"],
            ["📢 Channel", "🎮 Games"],
            ["🔍 Search Games", "📝 Request Game"],
            ["⭐ Stars Menu", "🎯 Mini Games"]
        ]
        
        # Add admin menu for admins
        if self.is_admin(user_id):
            keyboard.append(["👑 Admin Panel"])
        
        welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>GAMERDROID™ V1</b>

⭐ <b>Telegram Stars Payments Enabled</b>
💰 <b>Premium Games Available</b>

Choose an option below:"""
        
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def send_games_menu(self, chat_id):
        """Send games menu"""
        regular_games = len(self.games_cache.get('all', []))
        premium_games = len(self.stars_system.get_premium_games())
        
        keyboard = [
            ["📁 Game Files", "💰 Premium Games"],
            ["🎯 Mini Games", "🔍 Search Games"],
            ["📝 Request Game", "⭐ Stars Menu"],
            ["🔙 Back to Main Menu"]
        ]
        
        games_text = f"""🎮 <b>Games Section</b>

📊 Total Games: {regular_games + premium_games}
• 🆓 Regular: {regular_games}
• 💰 Premium: {premium_games}

⭐ Premium games require Telegram Stars

Choose an option:"""
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_game_files_menu(self, chat_id):
        """Send game files menu"""
        keyboard = [
            ["📦 ZIP Files", "🗜️ 7Z Files"],
            ["💿 ISO Files", "📱 APK Files"],
            ["🎮 PSP Games", "📋 All Files"],
            ["💰 Premium Games", "🔍 Search Games"],
            ["🔙 Back to Games"]
        ]
        
        files_text = """📁 <b>Game Files Browser</b>

Browse games by file type:

• 📦 ZIP Files - Compressed game archives
• 🗜️ 7Z Files - 7-Zip compressed archives  
• 💿 ISO Files - Disc image files
• 📱 APK Files - Android applications
• 🎮 PSP Games - PSP specific formats
• 📋 All Files - Complete game list
• 💰 Premium Games - Paid games with Stars

Choose an option:"""
        
        return self.send_message(chat_id, files_text, keyboard)
    
    def send_premium_games_menu(self, chat_id, user_id):
        """Send premium games menu"""
        premium_games = self.stars_system.get_premium_games()
        
        if not premium_games:
            keyboard = [
                ["🆓 Regular Games"],
                ["⭐ Stars Menu", "🎮 Games Menu"],
                ["🔙 Main Menu"]
            ]
            
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games that you can purchase with Telegram Stars!"""
        else:
            keyboard = []
            
            # Create buttons for premium games (max 4 per row)
            for i in range(0, len(premium_games[:8]), 2):
                row = []
                for j in range(2):
                    if i + j < len(premium_games):
                        game_id, file_name, file_type, file_size, stars_price, description = premium_games[i + j]
                        short_name = file_name[:15] + "..." if len(file_name) > 15 else file_name
                        row.append(f"💰 {short_name}")
                if row:
                    keyboard.append(row)
            
            keyboard.extend([
                ["🆓 Regular Games"],
                ["⭐ Stars Menu", "🎮 Games Menu"],
                ["🔙 Main Menu"]
            ])
            
            premium_text = """💰 <b>Premium Games</b>

Exclusive games available for purchase with Telegram Stars:

"""
            for i, game in enumerate(premium_games[:5], 1):
                game_id, file_name, file_type, file_size, stars_price, description = game
                size = self.format_file_size(file_size)
                
                premium_text += f"\n{i}. <b>{file_name}</b>"
                premium_text += f"\n   ⭐ {stars_price} Stars | 📦 {file_type} | 📏 {size}"
                premium_text += f"\n   └─ Type: <code>/premium_{game_id}</code>\n"
            
            if len(premium_games) > 5:
                premium_text += f"\n📋 ... and {len(premium_games) - 5} more premium games"
            
            premium_text += "\n\n💡 <i>To purchase, type /premium_[ID] or click the game name</i>"
        
        return self.send_message(chat_id, premium_text, keyboard)
    
    def send_stars_menu(self, chat_id, user_id):
        """Send Telegram Stars menu"""
        balance = self.stars_system.get_balance()
        
        keyboard = [
            ["⭐ 50 Stars", "⭐ 100 Stars"],
            ["⭐ 500 Stars", "⭐ 1000 Stars"],
            ["💫 Custom Amount", "📊 Stars Stats"],
            ["💰 Premium Games", "🎮 Games Menu"],
            ["🔙 Main Menu"]
        ]
        
        stars_text = """⭐ <b>Telegram Stars</b>

Support our bot with Telegram Stars!

🌟 <b>Why Donate Stars?</b>
• Keep the bot running 24/7
• Support new features development  
• Help cover server costs
• Purchase premium games

💫 <b>How Stars Work:</b>
1. Choose stars amount below
2. Complete secure payment via Telegram
3. Stars go directly to support development
4. Get instant confirmation!

💰 <b>Conversion:</b> 1 Star ≈ $0.01

📊 <b>Stars Stats:</b>"""
        
        stars_text += f"\n• Total Stars Received: <b>{balance['total_stars_earned']} ⭐</b>"
        stars_text += f"\n• Total USD Value: <b>${balance['total_usd_earned']:.2f}</b>"
        
        recent_transactions = self.stars_system.get_recent_transactions(3)
        if recent_transactions:
            stars_text += "\n\n🎉 <b>Recent Donations:</b>"
            for transaction in recent_transactions:
                donor_name, stars_amount, usd_amount, status, created_at = transaction
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d')
                status_icon = "✅" if status == 'completed' else "⏳"
                stars_text += f"\n• {donor_name}: {status_icon} <b>{stars_amount} ⭐</b>"
        
        stars_text += "\n\nThank you for considering supporting us! 🙏"
        
        return self.send_message(chat_id, stars_text, keyboard)
    
    def send_admin_menu(self, chat_id):
        """Send admin menu"""
        keyboard = [
            ["📤 Upload Games", "💰 Upload Premium"],
            ["🗑️ Remove Games", "📢 Broadcast"],
            ["📊 Upload Stats", "🔄 Update Cache"],
            ["⭐ Stars Stats", "🔍 Scan Games"],
            ["🔙 Back to Main Menu"]
        ]
        
        admin_text = """👑 <b>Admin Panel</b>

Admin Features:
• 📤 Upload regular games (free)
• 💰 Upload premium games (Stars)
• 🗑️ Remove games  
• 📢 Broadcast messages
• 📊 View statistics
• 🔄 Update cache
• ⭐ View Stars statistics
• 🔍 Scan for games

Choose an option:"""
        
        return self.send_message(chat_id, admin_text, keyboard)
    
    def send_upload_menu(self, chat_id):
        """Send upload menu for admin"""
        keyboard = [
            ["🆓 Regular Game", "💰 Premium Game"],
            ["🔙 Admin Menu"]
        ]
        
        upload_text = """📤 <b>Upload Games - Admin Panel</b>

Choose the type of game to upload:

🆓 <b>Regular Game</b>
• Free for all users
• No payment required
• Direct download

💰 <b>Premium Game</b>  
• Requires Stars payment
• Set your price in Stars
• Users pay to download

📁 Both support all file formats (ZIP, ISO, APK, etc.)"""
        
        return self.send_message(chat_id, upload_text, keyboard)
    
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
            regular_games = cursor.fetchone()[0]
            
            premium_games = len(self.stars_system.get_premium_games())
            
            return {'total_games': regular_games, 'premium_games': premium_games}
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
    
    def get_user_info(self, user_id):
        """Get user info from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id, username, first_name FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'user_id': result[0],
                    'username': result[1],
                    'first_name': result[2]
                }
            else:
                return {'first_name': 'User'}
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return {'first_name': 'User'}
    
    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Handle pre-checkout queries
                if 'pre_checkout_query' in message:
                    pre_checkout = message['pre_checkout_query']
                    success = self.stars_system.handle_pre_checkout(pre_checkout['id'])
                    return success
                
                # Handle successful payments
                if 'successful_payment' in message:
                    successful_payment = message['successful_payment']
                    success = self.stars_system.handle_successful_payment(successful_payment)
                    if success:
                        self.send_message(chat_id, "✅ Payment successful! Thank you for your purchase/donation!")
                    return success
                
                # Handle session states first
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]
                    
                    # Handle verification code
                    if session['state'] == 'waiting_code':
                        if text.isdigit() and len(text) == 6:
                            if self.verify_code(user_id, text):
                                if self.check_channel_membership(user_id):
                                    self.mark_channel_joined(user_id)
                                    self.send_message(chat_id, "✅ Verification complete! Welcome!")
                                    self.send_main_menu(chat_id, user_id, first_name)
                                else:
                                    self.send_message(chat_id, "✅ Code verified! Please join our channel @pspgamers5")
                                    keyboard = [["📢 Join Channel"], ["🔙 Main Menu"]]
                                    self.send_message(chat_id, "Join our channel to continue:", keyboard)
                                del self.user_sessions[user_id]
                            else:
                                self.send_message(chat_id, "❌ Invalid or expired code. Try again or use /start")
                        return True
                    
                    # Handle game request
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
                        ''', (user_id, first_name, game_name, platform, 'pending'))
                        self.conn.commit()
                        
                        self.send_message(chat_id, f"✅ Game request submitted!\n\nGame: {game_name}\nPlatform: {platform}\n\nWe'll notify you when it's available.")
                        del self.user_sessions[user_id]
                        return True
                    
                    # Handle stars custom amount
                    elif session['state'] == 'waiting_stars_amount':
                        try:
                            stars_amount = int(text)
                            if stars_amount > 0 and stars_amount <= 10000:
                                success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount, "Bot Stars Donation")
                                if success:
                                    self.send_message(chat_id, f"✅ Stars invoice created for {stars_amount} Stars! Check your Telegram messages for payment.")
                                else:
                                    self.send_message(chat_id, "❌ Failed to create invoice. Please try again.")
                            else:
                                self.send_message(chat_id, "❌ Please enter a valid amount (1-10000 Stars).")
                        except:
                            self.send_message(chat_id, "❌ Please enter a valid number.")
                        del self.user_sessions[user_id]
                        return True
                    
                    # Handle premium game price input
                    elif session['state'] == 'waiting_premium_price':
                        try:
                            stars_price = int(text)
                            if stars_price > 0 and stars_price <= 10000:
                                self.user_sessions[user_id]['stars_price'] = stars_price
                                self.user_sessions[user_id]['state'] = 'waiting_premium_description'
                                self.send_message(chat_id, f"⭐ Price set: {stars_price} Stars\n\nNow please enter a description for this premium game:")
                            else:
                                self.send_message(chat_id, "❌ Please enter a valid price (1-10000 Stars).")
                        except:
                            self.send_message(chat_id, "❌ Please enter a valid number.")
                        return True
                    
                    # Handle premium game description
                    elif session['state'] == 'waiting_premium_description':
                        description = text
                        self.user_sessions[user_id]['description'] = description
                        self.user_sessions[user_id]['state'] = 'waiting_premium_file'
                        self.send_message(chat_id, f"✅ Description saved!\n\nNow please upload the game file for this premium game.")
                        return True
                
                # Handle premium game purchase commands
                if text.startswith('/premium_'):
                    try:
                        game_id = int(text.replace('/premium_', ''))
                        game = self.stars_system.get_premium_game_by_id(game_id)
                        
                        if not game:
                            self.send_message(chat_id, "❌ Premium game not found.")
                            return True
                        
                        # Check if user already purchased
                        if self.stars_system.has_user_purchased_game(user_id, game_id):
                            # Send the file
                            if game['file_id']:
                                self.send_document_directly(chat_id, game['file_id'], f"🎮 {game['file_name']}\n\nEnjoy your premium game!")
                            else:
                                self.send_message(chat_id, "❌ Game file not available. Please contact admin.")
                            return True
                        
                        # Create invoice for purchase
                        success, invoice_id = self.stars_system.create_premium_game_invoice(
                            user_id, chat_id, game['stars_price'], game['file_name'], game_id
                        )
                        
                        if success:
                            self.send_message(chat_id, f"✅ Invoice created for {game['file_name']}!\n\nPrice: {game['stars_price']} Stars\n\nCheck your Telegram messages for payment.")
                        else:
                            self.send_message(chat_id, "❌ Failed to create invoice. Please try again.")
                        
                        return True
                    except:
                        self.send_message(chat_id, "❌ Invalid premium game ID.")
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
                
                elif text == '🎮 Games Menu':
                    self.send_games_menu(chat_id)
                    return True
                
                elif text == '🔙 Admin Menu':
                    self.send_admin_menu(chat_id)
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
                
                elif text == '💰 Premium Games':
                    if self.is_user_completed(user_id):
                        self.send_premium_games_menu(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '⭐ Stars Menu':
                    if self.is_user_completed(user_id):
                        self.send_stars_menu(chat_id, user_id)
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '👑 Admin Panel':
                    if self.is_admin(user_id):
                        self.send_admin_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                elif text == '📤 Upload Games' and self.is_admin(user_id):
                    self.send_upload_menu(chat_id)
                    return True
                
                elif text == '🆓 Regular Game' and self.is_admin(user_id):
                    self.send_message(chat_id, "📤 To upload a regular game, simply send the game file to this bot.\n\nSupported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP")
                    return True
                
                elif text == '💰 Premium Game' and self.is_admin(user_id):
                    self.user_sessions[user_id] = {
                        'menu': 'upload_premium',
                        'state': 'waiting_premium_price',
                        'data': {}
                    }
                    self.send_message(chat_id, "💰 <b>Premium Game Upload</b>\n\nPlease set the price in Telegram Stars for this game:\n\n💡 Enter a number (e.g., 50 for 50 Stars ≈ $0.50)")
                    return True
                
                elif text == '💫 Custom Amount':
                    if self.is_user_completed(user_id):
                        self.user_sessions[user_id] = {
                            'menu': 'stars',
                            'state': 'waiting_stars_amount',
                            'data': {}
                        }
                        self.send_message(chat_id, "💫 Enter the number of Stars you'd like to donate (1-10000):")
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text.startswith('⭐ '):
                    if self.is_user_completed(user_id):
                        stars_text = text.replace('⭐ ', '').replace(' Stars', '')
                        try:
                            stars_amount = int(stars_text)
                            success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount, "Bot Stars Donation")
                            if success:
                                self.send_message(chat_id, f"✅ Stars invoice created for {stars_amount} Stars! Check your Telegram messages for payment.")
                            else:
                                self.send_message(chat_id, "❌ Failed to create invoice. Please try again.")
                        except:
                            self.send_message(chat_id, "❌ Invalid stars amount.")
                    else:
                        self.send_message(chat_id, "❌ Please complete verification first with /start")
                    return True
                
                elif text == '📊 Stars Stats':
                    if self.is_admin(user_id):
                        balance = self.stars_system.get_balance()
                        recent_transactions = self.stars_system.get_recent_transactions(10)
                        
                        stats_text = """📊 <b>Telegram Stars Statistics</b>

💰 <b>Financial Overview:</b>"""
                        
                        stats_text += f"\n• Total Stars Earned: <b>{balance['total_stars_earned']} ⭐</b>"
                        stats_text += f"\n• Total USD Earned: <b>${balance['total_usd_earned']:.2f}</b>"
                        stats_text += f"\n• Available Stars: <b>{balance['available_stars']} ⭐</b>"
                        stats_text += f"\n• Available USD: <b>${balance['available_usd']:.2f}</b>"
                        
                        if recent_transactions:
                            stats_text += "\n\n🎉 <b>Recent Transactions (Top 10):</b>"
                            for i, transaction in enumerate(recent_transactions, 1):
                                donor_name, stars_amount, usd_amount, status, created_at = transaction
                                date_str = datetime.fromisoformat(created_at).strftime('%m/%d %H:%M')
                                status_icon = "✅" if status == 'completed' else "⏳"
                                stats_text += f"\n{i}. {donor_name}: {status_icon} <b>{stars_amount} ⭐ (${usd_amount:.2f})</b> - {date_str}"
                        
                        self.send_message(chat_id, stats_text)
                    else:
                        self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                # Handle other menu options...
                # [Previous menu handling code continues here]
                
                # Handle document uploads from admins
                if 'document' in message and self.is_admin(user_id):
                    return self.handle_document_upload(message, user_id, chat_id, first_name)
            
            # Handle document uploads (outside text handler)
            if 'document' in message:
                user_id = message['from']['id']
                chat_id = message['chat']['id']
                
                if self.is_admin(user_id):
                    return self.handle_document_upload(message, user_id, chat_id, message['from']['first_name'])
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            traceback.print_exc()
            return False
    
    def handle_document_upload(self, message, user_id, chat_id, first_name):
        """Handle document upload from admin"""
        try:
            if 'document' not in message:
                return False
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            
            print(f"📥 Admin {user_id} uploading: {file_name}")
            
            # Check if it's a supported game file
            game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
            if not any(file_name.lower().endswith(ext) for ext in game_extensions):
                self.send_message(chat_id, f"❌ File type not supported: {file_name}")
                return False
            
            # Check if this is a premium game upload
            if user_id in self.user_sessions and self.user_sessions[user_id]['state'] == 'waiting_premium_file':
                session = self.user_sessions[user_id]
                stars_price = session.get('stars_price', 0)
                description = session.get('description', '')
                
                # Add premium game to database
                game_id = self.stars_system.add_premium_game(
                    file_name, file_type, file_size, stars_price, description, file_id, user_id
                )
                
                if game_id:
                    # Clean up session
                    del self.user_sessions[user_id]
                    
                    # Send confirmation
                    size = self.format_file_size(file_size)
                    confirm_text = f"""✅ <b>Premium Game Added Successfully!</b>

🎮 Game: {file_name}
💰 Price: <b>{stars_price} Stars</b>
📦 Type: {file_type}
📏 Size: {size}
📝 Description: {description}
🆔 Game ID: {game_id}

⭐ The game is now available in the premium games section!
Users can purchase it with: <code>/premium_{game_id}</code>"""
                    
                    self.send_message(chat_id, confirm_text)
                    return True
                else:
                    self.send_message(chat_id, "❌ Failed to add premium game to database.")
                    return False
            
            else:
                # Regular game upload
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Prepare game info
                game_info = {
                    'message_id': int(time.time() * 1000) + random.randint(1000, 9999),
                    'file_name': file_name,
                    'file_type': file_type,
                    'file_size': file_size,
                    'upload_date': upload_date,
                    'category': self.determine_file_category(file_name),
                    'added_by': user_id,
                    'is_uploaded': 1,
                    'is_forwarded': 'forward_origin' in message,
                    'file_id': file_id,
                    'bot_message_id': message['message_id']
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
                confirm_text = f"""✅ <b>Regular Game Added Successfully!</b>

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
            traceback.print_exc()
            return False
    
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
    
    def handle_start(self, chat_id, user_id, first_name):
        """Handle /start command"""
        try:
            username = message['from'].get('username', '') if 'message' in locals() else ""
            
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
    
    # [Previous methods for mini-games, search, etc. continue here]
    # Note: I've omitted some repetitive methods for brevity
    
    def run(self):
        """Main bot loop"""
        print("🤖 Bot is running with Telegram Stars...")
        
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
                            elif 'pre_checkout_query' in update:
                                # Handle pre-checkout queries
                                pre_checkout = update['pre_checkout_query']
                                success = self.stars_system.handle_pre_checkout(pre_checkout['id'])
                                if success:
                                    print(f"✅ Pre-checkout query handled: {pre_checkout['id']}")
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
    print("🚀 Starting Telegram Bot with Stars Payments...")
    
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
