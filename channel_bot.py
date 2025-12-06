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

print("TELEGRAM BOT - COMPLETE SYSTEM WITH STARS PAYMENTS")
print("Game Storage + Stars + Broadcast + Button Access")
print("=" * 50)

# ==================== RENDER DEBUG SECTION ====================
print("🔍 RENDER DEBUG: Starting initialization...")
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if BOT_TOKEN:
    print(f"🔍 DEBUG: Token starts with: {BOT_TOKEN[:10]}...")
else:
    print("❌ DEBUG: BOT_TOKEN is MISSING!")

# Health check server
app = Flask(__name__)

@app.route('/health')
def health_check():
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'telegram-game-bot'
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return jsonify({'service': 'Telegram Game Bot', 'status': 'running'})

def run_health_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Health server error: {e}")
        time.sleep(5)
        run_health_server()

def start_health_check():
    def health_wrapper():
        while True:
            try:
                run_health_server()
            except Exception as e:
                print(f"❌ Health server crashed: {e}")
                time.sleep(10)
    
    t = Thread(target=health_wrapper, daemon=True)
    t.start()
    print("✅ Health check server started")

# ==================== TELEGRAM STARS SYSTEM ====================

class TelegramStarsSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_stars_database()
        print("✅ Telegram Stars system initialized!")
        
    def setup_stars_database(self):
        try:
            cursor = self.bot.conn.cursor()
            
            # Stars transactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    stars_amount INTEGER,
                    usd_amount REAL,
                    description TEXT,
                    transaction_id TEXT UNIQUE,
                    payment_status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            ''')
            
            # Stars balance
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
            
            # Premium games
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE,
                    file_name TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    stars_price INTEGER DEFAULT 0,
                    description TEXT,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    download_count INTEGER DEFAULT 0
                )
            ''')
            
            # Premium purchases
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
            
            # Initialize balance
            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')
            
            self.bot.conn.commit()
            print("✅ Stars database setup complete!")
            
        except Exception as e:
            print(f"❌ Stars database error: {e}")
    
    def create_stars_invoice(self, user_id, chat_id, stars_amount, description="Donation"):
        try:
            invoice_payload = f"stars_{user_id}_{int(time.time())}"
            usd_amount = stars_amount * 0.01
            
            prices = [{"label": f"{stars_amount} Stars", "amount": stars_amount}]
            
            invoice_data = {
                "chat_id": chat_id,
                "title": "🌟 Bot Stars Donation",
                "description": description,
                "payload": invoice_payload,
                "currency": "XTR",
                "prices": json.dumps(prices),
                "start_parameter": "stars_donation",
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }
            
            url = self.bot.base_url + "sendInvoice"
            response = requests.post(url, data=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO stars_transactions 
                    (user_id, user_name, stars_amount, usd_amount, description, transaction_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    self.bot.get_user_info(user_id)['first_name'],
                    stars_amount,
                    usd_amount,
                    description,
                    invoice_payload
                ))
                
                self.bot.conn.commit()
                print(f"✅ Stars invoice created: {stars_amount} stars")
                return True, invoice_payload
            else:
                print(f"❌ Error creating invoice: {result.get('description')}")
                return False, None
            
        except Exception as e:
            print(f"❌ Stars invoice error: {e}")
            return False, None
    
    def create_premium_game_invoice(self, user_id, chat_id, stars_amount, game_name, game_id):
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
            
            url = self.bot.base_url + "sendInvoice"
            response = requests.post(url, data=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO premium_purchases 
                    (user_id, game_id, stars_paid, transaction_id, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, game_id, stars_amount, invoice_payload, 'pending'))
                
                self.bot.conn.commit()
                print(f"✅ Premium invoice created: {game_name}")
                return True, invoice_payload
            else:
                print(f"❌ Error creating premium invoice: {result.get('description')}")
                return False, None
                
        except Exception as e:
            print(f"❌ Premium invoice error: {e}")
            return False, None
    
    def get_balance(self):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT * FROM stars_balance WHERE id = 1')
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_stars_earned': result[1] or 0,
                    'total_usd_earned': result[2] or 0.0,
                    'available_stars': result[3] or 0,
                    'available_usd': result[4] or 0.0
                }
            return {'available_stars': 0, 'available_usd': 0.0}
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return {'available_stars': 0, 'available_usd': 0.0}
    
    def add_premium_game(self, file_id, file_name, file_type, file_size, stars_price, description, added_by):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_games 
                (file_id, file_name, file_type, file_size, stars_price, description, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_name, file_type, file_size, stars_price, description, added_by))
            
            self.bot.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error adding premium game: {e}")
            return False
    
    def get_premium_games(self, limit=20):
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
            print(f"❌ Error getting premium game: {e}")
            return None
    
    def has_user_purchased_game(self, user_id, game_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id FROM premium_purchases 
                WHERE user_id = ? AND game_id = ? AND status = 'completed'
            ''', (user_id, game_id))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ Error checking purchase: {e}")
            return False
    
    def handle_pre_checkout(self, pre_checkout_query_id):
        try:
            url = self.bot.base_url + "answerPreCheckoutQuery"
            data = {"pre_checkout_query_id": pre_checkout_query_id, "ok": True}
            response = requests.post(url, data=data, timeout=10)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"❌ Pre-checkout error: {e}")
            return False
    
    def handle_successful_payment(self, successful_payment):
        try:
            invoice_payload = successful_payment.get('invoice_payload', '')
            
            if invoice_payload.startswith('premium_game_'):
                return self.complete_premium_purchase(invoice_payload)
            elif invoice_payload.startswith('stars_'):
                return self.complete_stars_donation(invoice_payload)
            
            return False
        except Exception as e:
            print(f"❌ Payment processing error: {e}")
            return False
    
    def complete_premium_purchase(self, transaction_id):
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('''
                SELECT user_id, game_id, stars_paid FROM premium_purchases 
                WHERE transaction_id = ? AND status = 'pending'
            ''', (transaction_id,))
            purchase = cursor.fetchone()
            
            if not purchase:
                return False
                
            user_id, game_id, stars_paid = purchase
            
            cursor.execute('''
                UPDATE premium_purchases 
                SET status = 'completed' 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            cursor.execute('''
                UPDATE stars_balance 
                SET total_stars_earned = total_stars_earned + ?,
                    total_usd_earned = total_usd_earned + ?,
                    available_stars = available_stars + ?,
                    available_usd = available_usd + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (stars_paid, stars_paid * 0.01, stars_paid, stars_paid * 0.01))
            
            cursor.execute('''
                UPDATE stars_transactions 
                SET payment_status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Purchase completion error: {e}")
            return False
    
    def complete_stars_donation(self, transaction_id):
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('''
                UPDATE stars_transactions 
                SET payment_status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
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
            print(f"❌ Donation completion error: {e}")
            return False

# ==================== MAIN BOT CLASS ====================

class CrossPlatformBot:
    def __init__(self, token):
        if not token:
            raise ValueError("BOT_TOKEN is required")
        
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
        self.REQUIRED_CHANNEL = "@pspgamers5"
        self.ADMIN_IDS = [7475473197, 7713987088]
        
        # Session management
        self.user_sessions = {}
        self.temp_uploads = {}
        self.guess_games = {}
        self.spin_games = {}
        
        # Systems
        self.stars_system = TelegramStarsSystem(self)
        
        self.setup_database()
        print("✅ Bot system ready with all features!")
    
    def setup_database(self):
        try:
            self.conn = sqlite3.connect('game_bot_complete.db', check_same_thread=False)
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
                CREATE TABLE IF NOT EXISTS regular_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE,
                    file_name TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    category TEXT,
                    description TEXT,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER,
                    is_active INTEGER DEFAULT 1,
                    download_count INTEGER DEFAULT 0
                )
            ''')
            
            # Game requests
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    game_name TEXT,
                    platform TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Broadcast history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    message TEXT,
                    sent_to INTEGER,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize categories
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    emoji TEXT
                )
            ''')
            
            default_categories = [
                ('PSP Games', '🎮'),
                ('Android Games', '📱'),
                ('PC Games', '💻'),
                ('Emulators', '⚙️'),
                ('Tools', '🛠️')
            ]
            
            for name, emoji in default_categories:
                cursor.execute('INSERT OR IGNORE INTO categories (name, emoji) VALUES (?, ?)', (name, emoji))
            
            self.conn.commit()
            print("✅ Database setup complete!")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.setup_database()
    
    def send_message(self, chat_id, text, keyboard=None):
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
                data["reply_markup"] = json.dumps({"remove_keyboard": True})
            
            response = requests.post(url, data=data, timeout=15)
            return response.json().get('ok', False)
            
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return False
    
    def send_document(self, chat_id, file_id, caption=None):
        try:
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id,
                "caption": caption or "",
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"❌ Send document error: {result.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ Send document exception: {e}")
            return False
    
    def send_main_menu(self, chat_id, user_id, first_name):
        keyboard = [
            ["🎮 Browse Games", "💰 Premium Games"],
            ["⭐ Stars Menu", "🔍 Search Games"],
            ["📝 Request Game", "📊 Profile"],
            ["📢 Channel", "🎯 Mini Games"]
        ]
        
        if self.is_admin(user_id):
            keyboard.append(["👑 Admin Panel"])
        
        welcome_text = f"""👋 Welcome <b>{first_name}</b>!

🤖 <b>Complete Game Bot System</b>

⭐ <b>Features:</b>
• Browse & download games instantly
• Premium games with Telegram Stars
• Admin broadcasts
• Game requests
• Mini-games

Choose an option:"""
        
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def send_categories_menu(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, emoji FROM categories ORDER BY name')
        categories = cursor.fetchall()
        
        keyboard = []
        row = []
        
        for i, (name, emoji) in enumerate(categories):
            row.append(f"{emoji} {name}")
            if len(row) == 2 or i == len(categories) - 1:
                keyboard.append(row.copy())
                row = []
        
        keyboard.append(["💰 Premium Games"])
        keyboard.append(["🔙 Main Menu"])
        
        categories_text = """🎮 <b>Game Categories</b>

Browse games by category:

"""
        for name, emoji in categories:
            cursor.execute('SELECT COUNT(*) FROM regular_games WHERE category = ? AND is_active = 1', (name,))
            count = cursor.fetchone()[0]
            categories_text += f"{emoji} <b>{name}</b> - {count} games\n"
        
        categories_text += "\nSelect a category:"
        
        return self.send_message(chat_id, categories_text, keyboard)
    
    def send_games_in_category(self, chat_id, category_name, page=0):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, file_name, description, download_count 
            FROM regular_games 
            WHERE category = ? AND is_active = 1 
            ORDER BY upload_date DESC 
            LIMIT 10 OFFSET ?
        ''', (category_name, page * 10))
        
        games = cursor.fetchall()
        
        if not games:
            keyboard = [["🔙 Categories"]]
            self.send_message(chat_id, f"❌ No games found in {category_name}.", keyboard)
            return
        
        cursor.execute('SELECT COUNT(*) FROM regular_games WHERE category = ? AND is_active = 1', (category_name,))
        total_games = cursor.fetchone()[0]
        
        games_text = f"""🎮 <b>{category_name}</b>

📊 Total games: {total_games}
📄 Page {page + 1} of {(total_games + 9) // 10}

"""
        for i, (game_id, file_name, description, download_count) in enumerate(games, 1):
            games_text += f"{i}. <b>{file_name}</b>\n"
            if description:
                games_text += f"   📝 {description}\n"
            games_text += f"   📥 {download_count} downloads\n\n"
        
        keyboard = []
        row = []
        
        for i, (game_id, file_name, description, download_count) in enumerate(games, 1):
            button_text = f"📁 {i}. {file_name[:15]}{'...' if len(file_name) > 15 else ''}"
            row.append(button_text)
            if len(row) == 2 or i == len(games):
                keyboard.append(row.copy())
                row = []
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append("⬅️ Previous")
        
        if (page + 1) * 10 < total_games:
            nav_buttons.append("Next ➡️")
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append(["🔙 Categories", "🔍 Search"])
        
        self.user_sessions[chat_id] = {
            'menu': 'category_games',
            'category': category_name,
            'page': page,
            'games': games
        }
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_premium_games_menu(self, chat_id, user_id):
        premium_games = self.stars_system.get_premium_games()
        
        if not premium_games:
            keyboard = [
                ["🎮 Regular Games"],
                ["⭐ Stars Menu", "🔙 Main Menu"]
            ]
            
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games!"""
        else:
            keyboard = []
            
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
                ["🎮 Regular Games"],
                ["⭐ Stars Menu", "🔙 Main Menu"]
            ])
            
            premium_text = """💰 <b>Premium Games</b>

Exclusive games available with Telegram Stars:

"""
            for i, game in enumerate(premium_games[:5], 1):
                game_id, file_name, file_type, file_size, stars_price, description = game
                size = self.format_file_size(file_size)
                
                premium_text += f"\n{i}. <b>{file_name}</b>"
                premium_text += f"\n   ⭐ {stars_price} Stars | 📦 {file_type} | 📏 {size}"
                premium_text += f"\n   └─ Type: <code>/premium_{game_id}</code>\n"
            
            if len(premium_games) > 5:
                premium_text += f"\n📋 ... and {len(premium_games) - 5} more"
        
        return self.send_message(chat_id, premium_text, keyboard)
    
    def send_stars_menu(self, chat_id, user_id):
        balance = self.stars_system.get_balance()
        
        keyboard = [
            ["⭐ 50 Stars", "⭐ 100 Stars"],
            ["⭐ 500 Stars", "⭐ 1000 Stars"],
            ["💫 Custom Amount", "📊 Stars Stats"],
            ["💰 Premium Games", "🔙 Main Menu"]
        ]
        
        stars_text = """⭐ <b>Telegram Stars</b>

Support our bot with Telegram Stars!

🌟 <b>Why Donate Stars?</b>
• Keep the bot running 24/7
• Support development
• Purchase premium games

💰 <b>Conversion:</b> 1 Star ≈ $0.01

📊 <b>Stats:</b>"""
        
        stars_text += f"\n• Total Stars Earned: <b>{balance['total_stars_earned']} ⭐</b>"
        stars_text += f"\n• Total USD Value: <b>${balance['total_usd_earned']:.2f}</b>"
        stars_text += "\n\nThank you for supporting us! 🙏"
        
        return self.send_message(chat_id, stars_text, keyboard)
    
    def send_admin_menu(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM regular_games')
        regular_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM premium_games')
        premium_count = cursor.fetchone()[0]
        
        keyboard = [
            ["📤 Upload Game", "💰 Upload Premium"],
            ["📢 Broadcast", "🗑️ Manage Games"],
            ["📊 Statistics", "🔙 Main Menu"]
        ]
        
        admin_text = f"""👑 <b>Admin Panel</b>

📊 <b>Statistics:</b>
• Regular games: {regular_count}
• Premium games: {premium_count}

⚡ <b>Features:</b>
• Upload regular/premium games
• Broadcast to all users
• Manage games
• View statistics

Choose an option:"""
        
        return self.send_message(chat_id, admin_text, keyboard)
    
    def send_upload_menu(self, chat_id):
        keyboard = [
            ["🆓 Regular Game", "💰 Premium Game"],
            ["🔙 Admin Menu"]
        ]
        
        upload_text = """📤 <b>Upload Game</b>

Choose upload type:

🆓 <b>Regular Game</b>
• Free for all users
• Direct download

💰 <b>Premium Game</b>  
• Requires Stars payment
• Set your price

📁 Send the game file after choosing."""
        
        return self.send_message(chat_id, upload_text, keyboard)
    
    def send_broadcast_menu(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_verified = 1')
        user_count = cursor.fetchone()[0]
        
        keyboard = [
            ["📝 Text Broadcast", "📷 Photo Broadcast"],
            ["🔙 Admin Menu"]
        ]
        
        broadcast_text = f"""📢 <b>Broadcast System</b>

Send messages to all verified users.

📊 Total users: {user_count}

Choose broadcast type:

📝 <b>Text Broadcast</b>
• Send text messages
• HTML formatting supported

📷 <b>Photo Broadcast</b>
• Send photos with captions
• Visual announcements"""
        
        return self.send_message(chat_id, broadcast_text, keyboard)
    
    def broadcast_to_all_users(self, chat_id, admin_id, message_text, photo_file_id=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
            users = cursor.fetchall()
            
            total_users = len(users)
            if total_users == 0:
                self.send_message(chat_id, "❌ No verified users found.")
                return False
            
            self.send_message(chat_id, f"📤 Starting broadcast to {total_users} users...")
            
            success_count = 0
            failed_count = 0
            
            for i, (user_id,) in enumerate(users):
                try:
                    if photo_file_id:
                        url = self.base_url + "sendPhoto"
                        data = {
                            "chat_id": user_id,
                            "photo": photo_file_id,
                            "caption": message_text,
                            "parse_mode": "HTML"
                        }
                        response = requests.post(url, data=data, timeout=30)
                    else:
                        url = self.base_url + "sendMessage"
                        data = {
                            "chat_id": user_id,
                            "text": message_text,
                            "parse_mode": "HTML"
                        }
                        response = requests.post(url, data=data, timeout=30)
                    
                    if response.json().get('ok'):
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    if (i + 1) % 10 == 0:
                        progress = int((i + 1) * 100 / total_users)
                        self.send_message(chat_id, f"📤 Progress: {i + 1}/{total_users} ({progress}%)")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Broadcast error for user {user_id}: {e}")
            
            # Save broadcast record
            cursor.execute('''
                INSERT INTO broadcasts (admin_id, message, sent_to)
                VALUES (?, ?, ?)
            ''', (admin_id, message_text[:100], success_count))
            self.conn.commit()
            
            result_text = f"""✅ <b>Broadcast Completed!</b>

📊 Results:
• Total users: {total_users}
• Successful: {success_count}
• Failed: {failed_count}
• Success rate: {(success_count/total_users*100):.1f}%"""

            self.send_message(chat_id, result_text)
            return True
            
        except Exception as e:
            print(f"❌ Broadcast error: {e}")
            self.send_message(chat_id, "❌ Broadcast failed.")
            return False
    
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
    
    def check_channel_membership(self, user_id):
        try:
            url = self.base_url + "getChatMember"
            data = {"chat_id": self.REQUIRED_CHANNEL, "user_id": user_id}
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
            cursor.execute('SELECT verification_code, code_expires FROM users WHERE user_id = ?', (user_id,))
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
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_user_info(self, user_id):
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
    
    def save_regular_game(self, file_id, file_name, file_type, file_size, category, description, added_by):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO regular_games 
                (file_id, file_name, file_type, file_size, category, description, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_name, file_type, file_size, category, description, added_by))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error saving regular game: {e}")
            return False
    
    def process_message(self, message):
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name}: {text}")
                
                # Save user
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name)
                    VALUES (?, ?, ?)
                ''', (user_id, message['from'].get('username', ''), first_name))
                self.conn.commit()
                
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
                        self.send_message(chat_id, "✅ Payment successful! Thank you!")
                    return success
                
                # Handle session states
                if chat_id in self.user_sessions:
                    session = self.user_sessions[chat_id]
                    
                    if session.get('state') == 'waiting_code':
                        if text.isdigit() and len(text) == 6:
                            if self.verify_code(user_id, text):
                                if self.check_channel_membership(user_id):
                                    self.mark_channel_joined(user_id)
                                    self.send_message(chat_id, "✅ Verification complete!")
                                    self.send_main_menu(chat_id, user_id, first_name)
                                else:
                                    self.send_message(chat_id, "✅ Code verified! Please join our channel @pspgamers5")
                                    keyboard = [["📢 Join Channel"], ["🔙 Main Menu"]]
                                    self.send_message(chat_id, "Join channel to continue:", keyboard)
                                del self.user_sessions[chat_id]
                            else:
                                self.send_message(chat_id, "❌ Invalid or expired code.")
                        return True
                    
                    elif session.get('state') == 'waiting_game_name':
                        self.user_sessions[chat_id] = {
                            'menu': 'request',
                            'state': 'waiting_platform',
                            'data': {'game_name': text}
                        }
                        self.send_message(chat_id, f"🎮 Game: {text}\n\nNow specify platform (PSP, Android, etc.):")
                        return True
                    
                    elif session.get('state') == 'waiting_platform':
                        game_name = session['data']['game_name']
                        platform = text
                        
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            INSERT INTO game_requests (user_id, user_name, game_name, platform)
                            VALUES (?, ?, ?, ?)
                        ''', (user_id, first_name, game_name, platform))
                        self.conn.commit()
                        
                        self.send_message(chat_id, f"✅ Game request submitted!\n\nGame: {game_name}\nPlatform: {platform}")
                        del self.user_sessions[chat_id]
                        return True
                    
                    elif session.get('state') == 'waiting_stars_amount':
                        try:
                            stars_amount = int(text)
                            if stars_amount > 0 and stars_amount <= 10000:
                                success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount)
                                if success:
                                    self.send_message(chat_id, f"✅ Stars invoice created! Check your Telegram messages.")
                                else:
                                    self.send_message(chat_id, "❌ Failed to create invoice.")
                            else:
                                self.send_message(chat_id, "❌ Enter amount 1-10000.")
                        except:
                            self.send_message(chat_id, "❌ Invalid number.")
                        del self.user_sessions[chat_id]
                        return True
                    
                    elif session.get('state') == 'waiting_premium_price':
                        try:
                            stars_price = int(text)
                            if stars_price > 0 and stars_price <= 10000:
                                self.temp_uploads[chat_id]['stars_price'] = stars_price
                                self.user_sessions[chat_id]['state'] = 'waiting_premium_description'
                                self.send_message(chat_id, f"⭐ Price set: {stars_price} Stars\n\nEnter description:")
                            else:
                                self.send_message(chat_id, "❌ Enter price 1-10000.")
                        except:
                            self.send_message(chat_id, "❌ Invalid number.")
                        return True
                    
                    elif session.get('state') == 'waiting_premium_description':
                        description = text
                        self.temp_uploads[chat_id]['description'] = description
                        self.user_sessions[chat_id]['state'] = 'waiting_premium_file'
                        self.send_message(chat_id, "✅ Description saved!\n\nNow upload the game file.")
                        return True
                    
                    elif session.get('state') == 'waiting_broadcast':
                        message_text = text
                        self.user_sessions[chat_id]['state'] = None
                        self.broadcast_to_all_users(chat_id, user_id, message_text)
                        return True
                    
                    elif session.get('state') == 'waiting_category':
                        if text.startswith(('🎮 ', '📱 ', '💻 ', '⚙️ ', '🛠️ ')):
                            category = text[2:]
                            if chat_id in self.temp_uploads:
                                self.temp_uploads[chat_id]['category'] = category
                            
                            # Complete upload
                            if chat_id in self.temp_uploads:
                                file_info = self.temp_uploads[chat_id]
                                if file_info.get('type') == 'regular':
                                    game_id = self.save_regular_game(
                                        file_info['file_id'],
                                        file_info['file_name'],
                                        file_info.get('file_type', ''),
                                        file_info.get('file_size', 0),
                                        category,
                                        file_info.get('description', ''),
                                        user_id
                                    )
                                    if game_id:
                                        self.send_message(chat_id, f"✅ Regular game saved! ID: {game_id}")
                                        self.send_main_menu(chat_id, user_id, first_name)
                                    else:
                                        self.send_message(chat_id, "❌ Failed to save game.")
                                elif file_info.get('type') == 'premium':
                                    stars_price = file_info.get('stars_price', 0)
                                    description = file_info.get('description', '')
                                    game_id = self.stars_system.add_premium_game(
                                        file_info['file_id'],
                                        file_info['file_name'],
                                        file_info.get('file_type', ''),
                                        file_info.get('file_size', 0),
                                        stars_price,
                                        description,
                                        user_id
                                    )
                                    if game_id:
                                        self.send_message(chat_id, f"✅ Premium game saved! ID: {game_id}\nPrice: {stars_price} Stars")
                                        self.send_main_menu(chat_id, user_id, first_name)
                                    else:
                                        self.send_message(chat_id, "❌ Failed to save premium game.")
                                
                                del self.temp_uploads[chat_id]
                            
                            del self.user_sessions[chat_id]
                        elif text == '📝 Custom Category':
                            self.send_message(chat_id, "📝 Enter custom category name:")
                            self.user_sessions[chat_id]['state'] = 'waiting_custom_category'
                        return True
                    
                    elif session.get('state') == 'waiting_custom_category':
                        category = text
                        if chat_id in self.temp_uploads:
                            self.temp_uploads[chat_id]['category'] = category
                        
                        # Complete upload (same as above)
                        if chat_id in self.temp_uploads:
                            file_info = self.temp_uploads[chat_id]
                            if file_info.get('type') == 'regular':
                                game_id = self.save_regular_game(
                                    file_info['file_id'],
                                    file_info['file_name'],
                                    file_info.get('file_type', ''),
                                    file_info.get('file_size', 0),
                                    category,
                                    file_info.get('description', ''),
                                    user_id
                                )
                                if game_id:
                                    self.send_message(chat_id, f"✅ Regular game saved! ID: {game_id}")
                                    self.send_main_menu(chat_id, user_id, first_name)
                                else:
                                    self.send_message(chat_id, "❌ Failed to save game.")
                            
                            del self.temp_uploads[chat_id]
                        
                        del self.user_sessions[chat_id]
                        return True
                
                # Handle premium game purchase
                if text.startswith('/premium_'):
                    try:
                        game_id = int(text.replace('/premium_', ''))
                        game = self.stars_system.get_premium_game_by_id(game_id)
                        
                        if not game:
                            self.send_message(chat_id, "❌ Premium game not found.")
                            return True
                        
                        if self.stars_system.has_user_purchased_game(user_id, game_id):
                            if game['file_id']:
                                self.send_document(chat_id, game['file_id'], f"🎮 {game['file_name']}\nEnjoy your game!")
                            else:
                                self.send_message(chat_id, "❌ Game file not available.")
                            return True
                        
                        success, invoice_id = self.stars_system.create_premium_game_invoice(
                            user_id, chat_id, game['stars_price'], game['file_name'], game_id
                        )
                        
                        if success:
                            self.send_message(chat_id, f"✅ Invoice created for {game['file_name']}!\nPrice: {game['stars_price']} Stars\n\nCheck Telegram for payment.")
                        else:
                            self.send_message(chat_id, "❌ Failed to create invoice.")
                        
                        return True
                    except:
                        self.send_message(chat_id, "❌ Invalid premium game ID.")
                        return True
                
                # Handle menu navigation
                if text == '/start' or text == '🔙 Main Menu':
                    self.send_main_menu(chat_id, user_id, first_name)
                    return True
                
                elif text == '🎮 Browse Games':
                    self.send_categories_menu(chat_id)
                    return True
                
                elif text == '🔙 Categories':
                    self.send_categories_menu(chat_id)
                    return True
                
                elif text == '💰 Premium Games':
                    self.send_premium_games_menu(chat_id, user_id)
                    return True
                
                elif text == '⭐ Stars Menu':
                    self.send_stars_menu(chat_id, user_id)
                    return True
                
                elif text == '📝 Request Game':
                    self.user_sessions[chat_id] = {'state': 'waiting_game_name'}
                    self.send_message(chat_id, "🎮 Enter the name of the game you want to request:")
                    return True
                
                elif text == '🔍 Search Games':
                    self.send_message(chat_id, "🔍 Enter search query:")
                    self.user_sessions[chat_id] = {'state': 'waiting_search'}
                    return True
                
                elif text == '📊 Profile':
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT created_at, is_verified FROM users WHERE user_id = ?', (user_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        created_at, is_verified = result
                        profile_text = f"""👤 <b>Profile</b>

🆔 ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Verified: {'Yes' if is_verified else 'No'}
📅 Joined: {created_at}"""
                    else:
                        profile_text = f"👤 Name: {first_name}\n🆔 ID: {user_id}"
                    
                    self.send_message(chat_id, profile_text)
                    return True
                
                elif text == '📢 Channel':
                    self.send_message(chat_id, "📢 Join our channel: @pspgamers5")
                    return True
                
                elif text == '🎯 Mini Games':
                    keyboard = [
                        ["🎯 Number Guess", "🎲 Random"],
                        ["🎰 Lucky Spin", "🔙 Main Menu"]
                    ]
                    self.send_message(chat_id, "🎮 <b>Mini Games</b>\n\nChoose a game:", keyboard)
                    return True
                
                elif text == '👑 Admin Panel':
                    if self.is_admin(user_id):
                        self.send_admin_menu(chat_id)
                    else:
                        self.send_message(chat_id, "❌ Admin access required.")
                    return True
                
                elif text == '📤 Upload Game' and self.is_admin(user_id):
                    self.send_upload_menu(chat_id)
                    return True
                
                elif text == '🆓 Regular Game' and self.is_admin(user_id):
                    self.send_message(chat_id, "📤 Upload regular game file.\n\nSupported: ZIP, 7Z, ISO, APK, etc.")
                    self.user_sessions[chat_id] = {'state': 'waiting_regular_file'}
                    return True
                
                elif text == '💰 Premium Game' and self.is_admin(user_id):
                    self.user_sessions[chat_id] = {'state': 'waiting_premium_price'}
                    self.send_message(chat_id, "💰 Enter price in Stars (1-10000):")
                    return True
                
                elif text == '📢 Broadcast' and self.is_admin(user_id):
                    self.send_broadcast_menu(chat_id)
                    return True
                
                elif text == '📝 Text Broadcast' and self.is_admin(user_id):
                    self.user_sessions[chat_id] = {'state': 'waiting_broadcast'}
                    self.send_message(chat_id, "📝 Enter broadcast message:")
                    return True
                
                elif text == '📷 Photo Broadcast' and self.is_admin(user_id):
                    self.send_message(chat_id, "📷 Send photo with caption for broadcast.")
                    self.user_sessions[chat_id] = {'state': 'waiting_photo_broadcast'}
                    return True
                
                elif text == '📊 Statistics' and self.is_admin(user_id):
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM regular_games')
                    regular = cursor.fetchone()[0]
                    cursor.execute('SELECT COUNT(*) FROM premium_games')
                    premium = cursor.fetchone()[0]
                    cursor.execute('SELECT COUNT(*) FROM users')
                    users = cursor.fetchone()[0]
                    
                    stats_text = f"""📊 <b>Statistics</b>

🎮 Regular Games: {regular}
💰 Premium Games: {premium}
👥 Total Users: {users}"""
                    
                    self.send_message(chat_id, stats_text)
                    return True
                
                elif text == '🗑️ Manage Games' and self.is_admin(user_id):
                    keyboard = [["🔙 Admin Menu"]]
                    self.send_message(chat_id, "🗑️ Game management coming soon...", keyboard)
                    return True
                
                elif text == '💫 Custom Amount':
                    self.user_sessions[chat_id] = {'state': 'waiting_stars_amount'}
                    self.send_message(chat_id, "💫 Enter Stars amount (1-10000):")
                    return True
                
                elif text.startswith('⭐ '):
                    stars_text = text.replace('⭐ ', '').replace(' Stars', '')
                    try:
                        stars_amount = int(stars_text)
                        success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount)
                        if success:
                            self.send_message(chat_id, f"✅ Stars invoice created! Check Telegram.")
                        else:
                            self.send_message(chat_id, "❌ Failed to create invoice.")
                    except:
                        self.send_message(chat_id, "❌ Invalid amount.")
                    return True
                
                elif text == '📊 Stars Stats' and self.is_admin(user_id):
                    balance = self.stars_system.get_balance()
                    stats_text = f"""📊 <b>Stars Statistics</b>

⭐ Total Stars Earned: {balance['total_stars_earned']}
💰 Total USD Value: ${balance['total_usd_earned']:.2f}
💎 Available Stars: {balance['available_stars']}
💵 Available USD: ${balance['available_usd']:.2f}"""
                    
                    self.send_message(chat_id, stats_text)
                    return True
                
                # Handle category selection
                elif text.startswith(('🎮 ', '📱 ', '💻 ', '⚙️ ', '🛠️ ')):
                    category_name = text[2:]
                    self.send_games_in_category(chat_id, category_name)
                    return True
                
                # Handle game selection from category
                elif chat_id in self.user_sessions and self.user_sessions[chat_id].get('menu') == 'category_games':
                    if text.startswith('📁 '):
                        try:
                            game_num = int(text.split('.')[0].replace('📁 ', '')) - 1
                            session = self.user_sessions[chat_id]
                            games = session.get('games', [])
                            
                            if 0 <= game_num < len(games):
                                game_id, file_name, description, download_count = games[game_num]
                                
                                cursor = self.conn.cursor()
                                cursor.execute('SELECT file_id FROM regular_games WHERE id = ?', (game_id,))
                                result = cursor.fetchone()
                                
                                if result:
                                    file_id = result[0]
                                    caption = f"🎮 <b>{file_name}</b>"
                                    if description:
                                        caption += f"\n\n📝 {description}"
                                    
                                    if self.send_document(chat_id, file_id, caption):
                                        cursor.execute('''
                                            UPDATE regular_games 
                                            SET download_count = download_count + 1
                                            WHERE id = ?
                                        ''', (game_id,))
                                        self.conn.commit()
                                        
                                        keyboard = [
                                            ["📁 Send Again", "🎮 Browse More"],
                                            ["🔙 Categories", "🔍 Search"]
                                        ]
                                        self.send_message(chat_id, f"✅ <b>{file_name}</b> sent!", keyboard)
                                    else:
                                        self.send_message(chat_id, "❌ Failed to send file.")
                                else:
                                    self.send_message(chat_id, "❌ File not found.")
                            else:
                                self.send_message(chat_id, "❌ Invalid selection.")
                        except:
                            self.send_message(chat_id, "❌ Error processing selection.")
                        return True
                
                # Handle pagination
                elif text in ['⬅️ Previous', 'Next ➡️']:
                    if chat_id in self.user_sessions and self.user_sessions[chat_id].get('menu') == 'category_games':
                        session = self.user_sessions[chat_id]
                        page = session.get('page', 0)
                        category = session.get('category', '')
                        
                        if text == '⬅️ Previous' and page > 0:
                            page -= 1
                        elif text == 'Next ➡️':
                            page += 1
                        
                        self.send_games_in_category(chat_id, category, page)
                        return True
                
                # Handle search
                elif chat_id in self.user_sessions and self.user_sessions[chat_id].get('state') == 'waiting_search':
                    query = text
                    del self.user_sessions[chat_id]
                    
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        SELECT id, file_name, category, description 
                        FROM regular_games 
                        WHERE file_name LIKE ? AND is_active = 1 
                        LIMIT 10
                    ''', (f'%{query}%',))
                    
                    results = cursor.fetchall()
                    
                    if not results:
                        self.send_message(chat_id, f"❌ No results for: {query}")
                        return True
                    
                    results_text = f"""🔍 <b>Search Results</b>

Query: <code>{query}</code>
Found: {len(results)} games

"""
                    for i, (game_id, file_name, category, description) in enumerate(results, 1):
                        results_text += f"{i}. <b>{file_name}</b>\n"
                        results_text += f"   📁 {category}\n"
                        if description:
                            results_text += f"   📝 {description[:50]}...\n"
                        results_text += f"   └─ Type: <code>/get_{game_id}</code>\n\n"
                    
                    self.send_message(chat_id, results_text)
                    return True
                
                # Handle get game command
                elif text.startswith('/get_'):
                    try:
                        game_id = int(text.replace('/get_', ''))
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT file_id, file_name, description FROM regular_games WHERE id = ?', (game_id,))
                        result = cursor.fetchone()
                        
                        if result:
                            file_id, file_name, description = result
                            caption = f"🎮 <b>{file_name}</b>"
                            if description:
                                caption += f"\n\n📝 {description}"
                            
                            if self.send_document(chat_id, file_id, caption):
                                cursor.execute('''
                                    UPDATE regular_games 
                                    SET download_count = download_count + 1
                                    WHERE id = ?
                                ''', (game_id,))
                                self.conn.commit()
                                self.send_message(chat_id, f"✅ <b>{file_name}</b> sent!")
                            else:
                                self.send_message(chat_id, "❌ Failed to send file.")
                        else:
                            self.send_message(chat_id, "❌ Game not found.")
                    except:
                        self.send_message(chat_id, "❌ Invalid game ID.")
                    return True
            
            # Handle document uploads
            if 'document' in message:
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                
                if self.is_admin(user_id):
                    return self.handle_document_upload(message, chat_id, user_id)
            
            # Handle photo uploads for broadcast
            if 'photo' in message:
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                
                if self.is_admin(user_id) and chat_id in self.user_sessions and self.user_sessions[chat_id].get('state') == 'waiting_photo_broadcast':
                    photo = message['photo'][-1]
                    photo_file_id = photo['file_id']
                    caption = message.get('caption', '📢 Announcement from Admin')
                    
                    self.user_sessions[chat_id]['state'] = None
                    self.broadcast_to_all_users(chat_id, user_id, caption, photo_file_id)
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            traceback.print_exc()
            return False
    
    def handle_document_upload(self, message, chat_id, user_id):
        try:
            doc = message['document']
            file_id = doc.get('file_id')
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            
            print(f"📥 Upload: {file_name} (ID: {file_id})")
            
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            
            self.temp_uploads[chat_id] = {
                'file_id': file_id,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': file_size,
                'type': 'regular'
            }
            
            if chat_id in self.user_sessions and self.user_sessions[chat_id].get('state') == 'waiting_premium_file':
                self.temp_uploads[chat_id]['type'] = 'premium'
                file_info = self.temp_uploads[chat_id]
                stars_price = file_info.get('stars_price', 0)
                description = file_info.get('description', '')
                
                self.send_message(chat_id, f"✅ Premium game ready!\n\nFile: {file_name}\nPrice: {stars_price} Stars\nDescription: {description}")
            
            # Ask for category
            cursor = self.conn.cursor()
            cursor.execute('SELECT name, emoji FROM categories ORDER BY name')
            categories = cursor.fetchall()
            
            keyboard = []
            row = []
            for name, emoji in categories:
                row.append(f"{emoji} {name}")
                if len(row) == 2:
                    keyboard.append(row.copy())
                    row = []
            
            if row:
                keyboard.append(row)
            
            keyboard.append(["📝 Custom Category"])
            
            categories_text = f"""✅ <b>File received!</b>

📁 File: <code>{file_name}</code>
📦 Type: {file_type}
📏 Size: {self.format_file_size(file_size)}

Select a category:"""
            
            self.user_sessions[chat_id] = {'state': 'waiting_category'}
            return self.send_message(chat_id, categories_text, keyboard)
            
        except Exception as e:
            print(f"❌ Document upload error: {e}")
            traceback.print_exc()
            return False
    
    def run(self):
        print("🤖 Complete Bot System running...")
        
        offset = 0
        
        while True:
            try:
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
                                pre_checkout = update['pre_checkout_query']
                                success = self.stars_system.handle_pre_checkout(pre_checkout['id'])
                                if success:
                                    print(f"✅ Pre-checkout handled: {pre_checkout['id']}")
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
    print("🚀 Starting Complete Telegram Bot System...")
    
    start_health_check()
    time.sleep(2)
    
    if BOT_TOKEN:
        print("🔍 Testing bot token...")
        
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_name = data['result']['first_name']
                print(f"✅ Bot connected: {bot_name}")
                
                bot = CrossPlatformBot(BOT_TOKEN)
                bot.run()
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    else:
        print("❌ ERROR: BOT_TOKEN not set!")
        
        while True:
            time.sleep(60)
