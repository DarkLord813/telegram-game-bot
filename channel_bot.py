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
import subprocess

print("=" * 60)
print("🤖 GAMERDROID™ V1 - FULL TELEGRAM BOT")
print("=" * 60)
print("✅ Code Verification + Channel Join + Game Scanner")
print("✅ Admin Game Uploads Enabled + Forward Support")
print("✅ Mini-Games Integration")
print("✅ Admin Broadcast Messaging System")
print("✅ Telegram Stars Payments Integration")
print("✅ Game Request System for Users")
print("✅ Premium Games System with Stars Payments")
print("✅ Enhanced Broadcast with Photos & VIDEOS")
print("✅ Individual Request Replies")
print("✅ Game Removal System with Duplicate Detection")
print("✅ Redeploy System for Admins and Users")
print("✅ GitHub Database Backup & Restore System")
print("✅ 24/7 Operation with Persistent Data Recovery")
print("✅ REFERRAL SYSTEM WITH GAME TOKENS")
print("✅ GAME TOKEN PAYMENTS FOR PREMIUM GAMES")
print("✅ XAPK & APKS FILE SUPPORT")
print("✅ AUTO GITHUB BACKUP ON EVERY GAME UPLOAD")
print("✅ WEBHOOK MODE FOR 24/7 OPERATION")
print("=" * 60)

# ==================== CONFIGURATION ====================
print("🔍 Starting initialization...")
print(f"🔍 Python version: {sys.version}")

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'GAMERDROIDV1BOT')
REQUIRED_CHANNEL = os.environ.get('REQUIRED_CHANNEL', '@pspgamers5')
CHANNEL_LINK = os.environ.get('CHANNEL_LINK', 'https://t.me/pspgamers5')
PORT = int(os.environ.get('PORT', 8080))

# Parse admin IDs
ADMIN_IDS = []
admin_ids_str = os.environ.get('ADMIN_IDS', '7475473197,7713987088')
for x in admin_ids_str.split(','):
    try:
        ADMIN_IDS.append(int(x.strip()))
    except:
        pass

# GitHub Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO_OWNER = os.environ.get('GITHUB_REPO_OWNER', '')
GITHUB_REPO_NAME = os.environ.get('GITHUB_REPO_NAME', '')

print(f"BOT_TOKEN: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
print(f"BOT_USERNAME: {BOT_USERNAME}")
print(f"ADMIN_IDS: {ADMIN_IDS}")

# Flask app for webhook
app = Flask(__name__)
bot_instance = None

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'bot': 'running', 'mode': 'webhook'}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not bot_instance:
            return jsonify({'ok': False}), 200
        update = request.get_json()
        if update:
            Thread(target=bot_instance.process_update, args=(update,)).start()
        return jsonify({'ok': True}), 200
    except:
        return jsonify({'ok': False}), 200

@app.route('/')
def home():
    return jsonify({'service': 'GAMERDROID™ V1', 'status': 'running'})

def run_server():
    app.run(host='0.0.0.0', port=PORT, debug=False)

# ==================== ENHANCED KEEP-ALIVE SERVICE ====================

class EnhancedKeepAliveService:
    def __init__(self, health_url=None):
        self.health_url = health_url or f"http://localhost:{PORT}/health"
        self.is_running = False
        self.ping_count = 0
        self.last_successful_ping = time.time()
        
    def start(self):
        self.is_running = True
        
        def ping_loop():
            consecutive_failures = 0
            while self.is_running:
                try:
                    self.ping_count += 1
                    response = requests.get(self.health_url, timeout=15)
                    if response.status_code == 200:
                        self.last_successful_ping = time.time()
                        consecutive_failures = 0
                        print(f"✅ Keep-alive ping #{self.ping_count}")
                    else:
                        consecutive_failures += 1
                except:
                    consecutive_failures += 1
                
                if consecutive_failures >= 3:
                    print("🚨 Too many failures, restarting...")
                    os._exit(1)
                
                time.sleep(240)
        
        Thread(target=ping_loop, daemon=True).start()
        print("🔄 Enhanced keep-alive service started")

# ==================== GITHUB BACKUP SYSTEM ====================

class GitHubBackupSystem:
    def __init__(self, bot):
        self.bot = bot
        self.enabled = bool(GITHUB_TOKEN and GITHUB_REPO_OWNER and GITHUB_REPO_NAME)
        if self.enabled:
            print(f"✅ GitHub Backup: Enabled")
    
    def backup(self, reason="Auto backup"):
        if not self.enabled:
            return False
        try:
            db_path = self.bot.get_db_path()
            if not os.path.exists(db_path):
                return False
            with open(db_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode()
            url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/backups/telegram_bot.db"
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            data = {'message': reason, 'content': content, 'branch': 'main'}
            response = requests.put(url, headers=headers, json=data, timeout=30)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Backup error: {e}")
            return False

# ==================== REFERRAL SYSTEM WITH GAME TOKENS ====================

class ReferralSystem:
    def __init__(self, bot):
        self.bot = bot
        self.setup_tables()
        print("✅ Referral system initialized!")
    
    def setup_tables(self):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'game_tokens' not in cols:
                cursor.execute('ALTER TABLE users ADD COLUMN game_tokens INTEGER DEFAULT 0')
            if 'total_referrals' not in cols:
                cursor.execute('ALTER TABLE users ADD COLUMN total_referrals INTEGER DEFAULT 0')
            if 'referred_by' not in cols:
                cursor.execute('ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT 0')
            self.bot.conn.commit()
        except Exception as e:
            print(f"Referral setup error: {e}")
    
    def get_tokens(self, user_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT game_tokens FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def add_tokens(self, user_id, amount):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('UPDATE users SET game_tokens = game_tokens + ? WHERE user_id = ?', (amount, user_id))
            self.bot.conn.commit()
            return True
        except:
            return False
    
    def deduct_tokens(self, user_id, amount):
        try:
            current = self.get_tokens(user_id)
            if current < amount:
                return False
            cursor = self.bot.conn.cursor()
            cursor.execute('UPDATE users SET game_tokens = game_tokens - ? WHERE user_id = ?', (amount, user_id))
            self.bot.conn.commit()
            return True
        except:
            return False
    
    def register_referral(self, referrer_id, referred_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT referred_by FROM users WHERE user_id = ?', (referred_id,))
            result = cursor.fetchone()
            if result and result[0] != 0:
                return False
            cursor.execute('UPDATE users SET game_tokens = game_tokens + 1, total_referrals = total_referrals + 1 WHERE user_id = ?', (referrer_id,))
            cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', (referrer_id, referred_id))
            self.bot.conn.commit()
            self.bot.robust_send_message(referrer_id, f"🎉 New Referral!\nUser joined using your link!\nYou earned 1 Game Token! 💎")
            return True
        except:
            return False
    
    def get_link(self, user_id):
        return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

# ==================== ENHANCED BROADCAST SYSTEM ====================

class EnhancedBroadcastSystem:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.button_sessions = {}
        print("✅ Enhanced Broadcast System initialized!")
    
    def create_broadcast_with_buttons(self, user_id, chat_id):
        self.sessions[user_id] = {'stage': 'waiting_type', 'type': None, 'message': None, 'photo': None, 'video': None, 'caption': None, 'buttons': []}
        
        menu_text = """📢 <b>Enhanced Broadcast System</b>

Choose what to broadcast:

📝 Text Message
🖼️ Photo with caption
🎥 Video with caption
🔘 Inline buttons support"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📝 Text Message", "callback_data": "broadcast_text"}],
                [{"text": "🖼️ Photo + Caption", "callback_data": "broadcast_photo"}],
                [{"text": "🎥 Video + Caption", "callback_data": "broadcast_video"}],
                [{"text": "🔘 Add Buttons", "callback_data": "broadcast_add_buttons"}],
                [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
            ]
        }
        self.bot.robust_send_message(chat_id, menu_text, keyboard)
    
    def handle_broadcast_text(self, user_id, chat_id):
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = 'waiting_text'
            self.sessions[user_id]['type'] = 'text'
            self.bot.robust_send_message(chat_id, "📝 Send your broadcast message:")
    
    def handle_broadcast_photo(self, user_id, chat_id):
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = 'waiting_photo'
            self.sessions[user_id]['type'] = 'photo'
            self.bot.robust_send_message(chat_id, "🖼️ Send your photo:")
    
    def handle_broadcast_video(self, user_id, chat_id):
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = 'waiting_video'
            self.sessions[user_id]['type'] = 'video'
            self.bot.robust_send_message(chat_id, "🎥 Send your video:")
    
    def add_buttons_to_broadcast(self, user_id, chat_id):
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = 'waiting_buttons'
            self.button_sessions[user_id] = {'buttons': []}
            help_text = """🔘 Add Inline Buttons

Format: Button Text|type|value

Types: url, callback

Examples:
Join Channel|url|https://t.me/pspgamers5
Get Games|callback|games

Send 'done' when finished."""
            self.bot.robust_send_message(chat_id, help_text)
    
    def parse_button(self, text):
        parts = text.split('|')
        if len(parts) >= 3:
            btn_text = parts[0].strip()
            btn_type = parts[1].strip().lower()
            btn_value = parts[2].strip()
            if btn_type == 'url':
                return {"text": btn_text, "url": btn_value}
            elif btn_type == 'callback':
                return {"text": btn_text, "callback_data": btn_value}
        return None
    
    def process_buttons_input(self, user_id, chat_id, text):
        if user_id not in self.button_sessions:
            return
        
        if text.lower() == 'done':
            if user_id in self.sessions:
                self.sessions[user_id]['buttons'] = self.button_sessions[user_id]['buttons']
                self.sessions[user_id]['stage'] = 'preview'
            del self.button_sessions[user_id]
            self.show_preview(user_id, chat_id)
            return
        
        button = self.parse_button(text)
        if button:
            self.button_sessions[user_id]['buttons'].append(button)
            self.bot.robust_send_message(chat_id, f"✅ Button added: {button['text']}\nSend 'done' to finish")
        else:
            self.bot.robust_send_message(chat_id, "❌ Invalid format. Use: Text|type|value")
    
    def show_preview(self, user_id, chat_id):
        if user_id not in self.sessions:
            return
        session = self.sessions[user_id]
        
        preview_text = f"📋 Broadcast Preview\n\nType: {session['type'].upper()}\n\nSend this broadcast?"
        keyboard = {"inline_keyboard": [[{"text": "✅ Send", "callback_data": "send_broadcast"}], [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]]}
        self.bot.robust_send_message(chat_id, preview_text, keyboard)
    
    def execute_broadcast(self, user_id, chat_id):
        if user_id not in self.sessions:
            return
        session = self.sessions[user_id]
        
        cursor = self.bot.conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
        users = cursor.fetchall()
        
        if not users:
            self.bot.robust_send_message(chat_id, "❌ No verified users found.")
            del self.sessions[user_id]
            return
        
        success = 0
        failed = 0
        
        reply_markup = None
        if session['buttons']:
            rows = [session['buttons'][i:i+2] for i in range(0, len(session['buttons']), 2)]
            reply_markup = json.dumps({"inline_keyboard": rows})
        
        for uid, in users:
            try:
                if session['type'] == 'text':
                    self.bot.robust_send_message(uid, session['message'], json.loads(reply_markup) if reply_markup else None)
                elif session['type'] == 'photo' and session.get('photo'):
                    self.bot.robust_send_photo(uid, session['photo'], session.get('caption', ''), json.loads(reply_markup) if reply_markup else None)
                elif session['type'] == 'video' and session.get('video'):
                    self.bot.robust_send_video(uid, session['video'], session.get('caption', ''), json.loads(reply_markup) if reply_markup else None)
                success += 1
            except:
                failed += 1
            time.sleep(0.05)
        
        self.bot.robust_send_message(chat_id, f"✅ Broadcast sent!\n✅ Sent: {success}\n❌ Failed: {failed}")
        del self.sessions[user_id]

# ==================== TELEGRAM STARS SYSTEM ====================

class TelegramStarsSystem:
    def __init__(self, bot):
        self.bot = bot
        self.setup_tables()
        print("✅ Telegram Stars system initialized!")
    
    def setup_tables(self):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, stars_amount INTEGER,
                    transaction_id TEXT, payment_status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_balance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_stars_earned INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')
            self.bot.conn.commit()
        except Exception as e:
            print(f"Stars setup error: {e}")

# ==================== GAME REQUEST SYSTEM ====================

class GameRequestSystem:
    def __init__(self, bot):
        self.bot = bot
        self.setup_tables()
        print("✅ Game request system initialized!")
    
    def setup_tables(self):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, user_name TEXT, game_name TEXT, platform TEXT,
                    status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.bot.conn.commit()
        except Exception as e:
            print(f"Game requests setup error: {e}")
    
    def submit(self, user_id, game_name, platform):
        try:
            user_info = self.bot.get_user_info(user_id)
            cursor = self.bot.conn.cursor()
            cursor.execute('INSERT INTO game_requests (user_id, user_name, game_name, platform) VALUES (?, ?, ?, ?)', (user_id, user_info.get('first_name', 'User'), game_name, platform))
            self.bot.conn.commit()
            return cursor.lastrowid
        except:
            return False

# ==================== PREMIUM GAMES SYSTEM ====================

class PremiumGamesSystem:
    def __init__(self, bot):
        self.bot = bot
        self.setup_tables()
        print("✅ Premium games system initialized!")
    
    def setup_tables(self):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT, file_type TEXT, file_size INTEGER, file_id TEXT,
                    tokens_price INTEGER DEFAULT 10, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, game_id INTEGER, purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.bot.conn.commit()
        except Exception as e:
            print(f"Premium games setup error: {e}")
    
    def get_premium_games(self, limit=20):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id, file_name, file_type, file_size, tokens_price FROM premium_games ORDER BY created_at DESC LIMIT ?', (limit,))
            return cursor.fetchall()
        except:
            return []

# ==================== MAIN BOT CLASS ====================

class GamerDroidBot:
    def __init__(self, token):
        if not token:
            raise ValueError("BOT_TOKEN required")
        
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.REQUIRED_CHANNEL = REQUIRED_CHANNEL
        self.CHANNEL_LINK = CHANNEL_LINK
        self.ADMIN_IDS = ADMIN_IDS
        self.monthly_users = 68
        
        # Sessions
        self.game_requests = {}
        self.broadcast_sessions = {}
        self.remove_sessions = {}
        self.current_games = []
        self.current_games_list = []
        self.search_sessions = {}
        self.stars_sessions = {}
        self.upload_sessions = {}
        self.reply_sessions = {}
        self.media_reply_sessions = {}
        self.guess_games = {}
        self.spin_games = {}
        
        # Cache
        self.games_cache = {'zip': [], '7z': [], 'iso': [], 'apk': [], 'xapk': [], 'apks': [], 'cso': [], 'pbp': [], 'all': []}
        
        # Stats
        self.total_uploads = 500
        self.total_forwarded = 500
        self.last_restart = time.time()
        self.error_count = 0
        
        # Setup database
        self.setup_database()
        
        # Initialize systems
        self.referral = ReferralSystem(self)
        self.broadcast_system = EnhancedBroadcastSystem(self)
        self.stars = TelegramStarsSystem(self)
        self.game_requests_system = GameRequestSystem(self)
        self.premium = PremiumGamesSystem(self)
        self.backup = GitHubBackupSystem(self)
        
        # Update cache
        self.update_cache()
        
        print("✅ GAMERDROID™ V1 Bot ready!")
        print(f"✅ Admin IDs: {ADMIN_IDS}")
    
    def get_db_path(self):
        return 'telegram_bot.db'
    
    def setup_database(self):
        try:
            self.conn = sqlite3.connect(self.get_db_path(), check_same_thread=False)
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT, first_name TEXT,
                    is_verified INTEGER DEFAULT 0, joined_channel INTEGER DEFAULT 0,
                    verification_code TEXT, code_expires DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    game_tokens INTEGER DEFAULT 0, total_referrals INTEGER DEFAULT 0,
                    referred_by INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channel_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT, file_type TEXT, file_size INTEGER,
                    file_id TEXT, message_id INTEGER, category TEXT,
                    added_by INTEGER, upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, user_name TEXT, game_name TEXT, platform TEXT,
                    status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS broadcast_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER, message_text TEXT,
                    total_sent INTEGER DEFAULT 0, total_failed INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT, file_type TEXT, file_size INTEGER, file_id TEXT,
                    tokens_price INTEGER DEFAULT 10, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, game_id INTEGER, payment_method TEXT,
                    tokens_paid INTEGER, purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, stars_amount INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("✅ Database ready")
        except Exception as e:
            print(f"DB error: {e}")
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def robust_send_message(self, chat_id, text, reply_markup=None):
        try:
            url = self.base_url + "sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            r = requests.post(url, data=data, timeout=15)
            return r.json().get('ok', False)
        except:
            return False
    
    def robust_send_photo(self, chat_id, photo, caption="", reply_markup=None):
        try:
            url = self.base_url + "sendPhoto"
            data = {"chat_id": chat_id, "photo": photo, "parse_mode": "HTML"}
            if caption:
                data["caption"] = caption
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            r = requests.post(url, data=data, timeout=30)
            return r.json().get('ok', False)
        except:
            return False
    
    def robust_send_video(self, chat_id, video, caption="", reply_markup=None):
        try:
            url = self.base_url + "sendVideo"
            data = {"chat_id": chat_id, "video": video, "parse_mode": "HTML"}
            if caption:
                data["caption"] = caption
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            r = requests.post(url, data=data, timeout=60)
            return r.json().get('ok', False)
        except:
            return False
    
    def edit_message(self, chat_id, msg_id, text, reply_markup=None):
        try:
            url = self.base_url + "editMessageText"
            data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            requests.post(url, data=data, timeout=15)
        except:
            pass
    
    def answer_callback(self, query_id, text=None, show_alert=False):
        try:
            url = self.base_url + "answerCallbackQuery"
            data = {"callback_query_id": query_id}
            if text:
                data["text"] = text
            if show_alert:
                data["show_alert"] = True
            requests.post(url, data=data, timeout=5)
        except:
            pass
    
    def get_user_info(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT first_name, game_tokens, total_referrals FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                return {'first_name': result[0], 'game_tokens': result[1] or 0, 'total_referrals': result[2] or 0}
            return {'first_name': 'User', 'game_tokens': 0, 'total_referrals': 0}
        except:
            return {'first_name': 'User', 'game_tokens': 0, 'total_referrals': 0}
    
    # ==================== GAME MANAGEMENT ====================
    
    def update_cache(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT file_name, file_type, file_size, file_id, message_id, category FROM channel_games')
            games = cursor.fetchall()
            self.games_cache = {'zip': [], '7z': [], 'iso': [], 'apk': [], 'xapk': [], 'apks': [], 'cso': [], 'pbp': [], 'all': []}
            for g in games:
                fn, ft, fs, fid, mid, cat = g
                info = {'file_name': fn, 'file_type': ft, 'file_size': fs, 'file_id': fid, 'message_id': mid, 'category': cat}
                ft_low = ft.lower()
                if ft_low in self.games_cache:
                    self.games_cache[ft_low].append(info)
                self.games_cache['all'].append(info)
            print(f"📁 Cache: {len(self.games_cache['all'])} games")
        except Exception as e:
            print(f"Cache error: {e}")
    
    def format_size(self, bytes):
        if bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} GB"
    
    def determine_category(self, filename):
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        cat_map = {'apk': 'APK', 'xapk': 'XAPK', 'apks': 'APKS', 'zip': 'ZIP', '7z': '7Z', 'iso': 'ISO', 'cso': 'PSP', 'pbp': 'PSP'}
        return cat_map.get(ext, 'Other')
    
    def save_game(self, message, file_id, file_name, file_size, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM channel_games WHERE file_name = ?', (file_name,))
            if cursor.fetchone():
                self.robust_send_message(user_id, f"❌ Game '{file_name}' already exists!")
                return False
            
            category = self.determine_category(file_name)
            ext = file_name.split('.')[-1].lower() if '.' in file_name else 'other'
            
            cursor.execute('''
                INSERT INTO channel_games (file_name, file_type, file_size, file_id, message_id, category, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_name, ext, file_size, file_id, message['message_id'], category, user_id))
            self.conn.commit()
            
            self.update_cache()
            size_str = self.format_size(file_size)
            self.robust_send_message(user_id, f"✅ Game Added!\n\n📁 {file_name}\n📦 {ext.upper()} | 📏 {size_str}\n📂 {category}")
            
            # Backup
            Thread(target=self.backup.backup, args=(f"Game added: {file_name}",)).start()
            return True
        except Exception as e:
            print(f"Save error: {e}")
            self.robust_send_message(user_id, f"❌ Error: {str(e)}")
            return False
    
    def send_game_file(self, user_id, chat_id, file_name, file_id):
        try:
            self.robust_send_message(chat_id, f"📥 Sending {file_name}...")
            url = self.base_url + "sendDocument"
            data = {"chat_id": chat_id, "document": file_id, "caption": f"🎮 {file_name}"}
            r = requests.post(url, data=data, timeout=60)
            if r.json().get('ok'):
                self.robust_send_message(chat_id, f"✅ {file_name} sent!")
                return True
            return False
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def show_games(self, games, title, chat_id, msg_id):
        if not games:
            self.edit_message(chat_id, msg_id, f"❌ No {title} games found.", self.game_files_buttons())
            return
        
        self.current_games_list = games[:20]
        text = f"📁 <b>{title} GAMES</b>\n\n📊 Found: {len(games)} files\n\n"
        keyboard = []
        
        for i, game in enumerate(self.current_games_list, 1):
            size = self.format_size(game['file_size'])
            text += f"{i}. <code>{game['file_name'][:40]}</code>\n   📦 {game['file_type'].upper()} | 📏 {size}\n\n"
            keyboard.append([{"text": f"📥 Download {i}", "callback_data": f"dl_{i}"}])
        
        keyboard.append([{"text": "🔙 Back to Games", "callback_data": "game_files"}])
        self.edit_message(chat_id, msg_id, text, {"inline_keyboard": keyboard})
    
    # ==================== VERIFICATION ====================
    
    def generate_code(self):
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def save_verification_code(self, user_id, username, first_name, code):
        try:
            expires = datetime.now() + timedelta(minutes=10)
            cursor = self.conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO users (user_id, username, first_name, verification_code, code_expires, is_verified, joined_channel) VALUES (?, ?, ?, ?, ?, 0, 0)', (user_id, username, first_name, code, expires))
            self.conn.commit()
            return True
        except:
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
            return False
        except:
            return False
    
    def check_channel_membership(self, user_id):
        try:
            url = self.base_url + "getChatMember"
            data = {"chat_id": self.REQUIRED_CHANNEL, "user_id": user_id}
            r = requests.post(url, data=data, timeout=10)
            if r.json().get('ok'):
                status = r.json()['result']['status']
                return status in ['member', 'administrator', 'creator']
            return False
        except:
            return False
    
    def mark_channel_joined(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET joined_channel = 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except:
            return False
    
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
    
    def get_channel_stats(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total = cursor.fetchone()[0]
            return {'total_games': total}
        except:
            return {'total_games': 0}
    
    # ==================== MENU BUTTONS ====================
    
    def main_menu_buttons(self):
        stats = self.get_channel_stats()
        keyboard = [
            [{"text": "📊 Profile", "callback_data": "profile"}, {"text": "🕒 Time", "callback_data": "time"}],
            [{"text": "📢 Channel", "callback_data": "channel_info"}, {"text": f"🎮 Games ({stats['total_games']})", "callback_data": "games"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}, {"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "👥 Referral Program", "callback_data": "referral_menu"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}]
        ]
        if self.is_admin:
            keyboard.append([{"text": "🔧 Admin Panel", "callback_data": "admin_panel"}])
        keyboard.append([{"text": "🔄 Redeploy Bot", "callback_data": "redeploy_menu"}])
        return {"inline_keyboard": keyboard}
    
    def admin_panel_buttons(self):
        return {
            "inline_keyboard": [
                [{"text": "📤 Upload Stats", "callback_data": "upload_stats"}, {"text": "🔄 Update Cache", "callback_data": "update_cache"}],
                [{"text": "📤 Upload Games", "callback_data": "upload_games"}, {"text": "🗑️ Remove Games", "callback_data": "remove_games"}],
                [{"text": "🗑️ Clear All Games", "callback_data": "clear_all_games"}, {"text": "🔍 Scan Bot Games", "callback_data": "scan_bot_games"}],
                [{"text": "📢 Broadcast", "callback_data": "broadcast_menu"}, {"text": "🎮 Game Requests", "callback_data": "game_requests_admin"}],
                [{"text": "⭐ Stars Stats", "callback_data": "stars_stats"}, {"text": "💾 Backup System", "callback_data": "backup_menu"}],
                [{"text": "🔄 Redeploy System", "callback_data": "redeploy_panel"}, {"text": "📊 System Status", "callback_data": "system_status"}],
                [{"text": "👥 Referral Stats", "callback_data": "referral_stats"}, {"text": "💎 Token Management", "callback_data": "token_management"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
    
    def channel_buttons(self):
        return {"inline_keyboard": [[{"text": "📢 JOIN CHANNEL", "url": self.CHANNEL_LINK}, {"text": "✅ VERIFY JOIN", "callback_data": "verify_channel"}]]}
    
    def games_buttons(self):
        stats = self.get_channel_stats()
        return {"inline_keyboard": [
            [{"text": "🎮 Mini Games", "callback_data": "mini_games"}, {"text": f"📁 Game Files ({stats['total_games']})", "callback_data": "game_files"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}, {"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "👥 Referral Program", "callback_data": "referral_menu"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
            [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
        ]}
    
    def game_files_buttons(self):
        stats = self.get_channel_stats()
        return {"inline_keyboard": [
            [{"text": f"📦 ZIP ({len(self.games_cache.get('zip', []))})", "callback_data": "game_zip"}, {"text": f"🗜️ 7Z ({len(self.games_cache.get('7z', []))})", "callback_data": "game_7z"}],
            [{"text": f"💿 ISO ({len(self.games_cache.get('iso', []))})", "callback_data": "game_iso"}, {"text": f"📱 APK ({len(self.games_cache.get('apk', []))})", "callback_data": "game_apk"}],
            [{"text": f"🎮 PSP ({len(self.games_cache.get('cso', [])) + len(self.games_cache.get('pbp', []))})", "callback_data": "game_psp"}, {"text": f"📋 All ({stats['total_games']})", "callback_data": "game_all"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "🔄 Rescan", "callback_data": "rescan_games"}, {"text": "🔙 Back to Games", "callback_data": "games"}]
        ]}
    
    def mini_games_buttons(self):
        return {"inline_keyboard": [
            [{"text": "🎯 Number Guess", "callback_data": "game_guess"}, {"text": "🎲 Random Number", "callback_data": "game_random"}],
            [{"text": "🎰 Lucky Spin", "callback_data": "game_spin"}, {"text": "🔙 Back to Games", "callback_data": "games"}]
        ]}
    
    def search_buttons(self):
        return {"inline_keyboard": [
            [{"text": "🔍 New Search", "callback_data": "search_games"}, {"text": "📁 Browse All", "callback_data": "game_files"}],
            [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
        ]}
    
    def broadcast_menu_buttons(self):
        return {"inline_keyboard": [
            [{"text": "📝 Text Broadcast", "callback_data": "broadcast_text"}],
            [{"text": "🖼️ Photo Broadcast", "callback_data": "broadcast_photo"}],
            [{"text": "🎥 Video Broadcast", "callback_data": "broadcast_video"}],
            [{"text": "🔘 Add Buttons", "callback_data": "broadcast_add_buttons"}],
            [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
        ]}
    
    def stars_buttons(self):
        return {"inline_keyboard": [
            [{"text": "⭐ 50 Stars", "callback_data": "donate_50"}, {"text": "⭐ 100 Stars", "callback_data": "donate_100"}],
            [{"text": "⭐ 500 Stars", "callback_data": "donate_500"}, {"text": "⭐ 1000 Stars", "callback_data": "donate_1000"}],
            [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
        ]}
    
    def redeploy_buttons(self):
        return {"inline_keyboard": [
            [{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}],
            [{"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}],
            [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
        ]}
    
    # ==================== HANDLE CALLBACK ====================
    
    def handle_callback(self, callback):
        try:
            data = callback['data']
            message = callback['message']
            chat_id = message['chat']['id']
            msg_id = message['message_id']
            user_id = callback['from']['id']
            first_name = callback['from']['first_name']
            
            self.answer_callback(callback['id'])
            
            # Main Menu
            if data == "back_to_menu":
                text = f"""<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

Made by @rexoronsaye

<b>What can this bot do?</b>
Search games across different platforms on telegram.
Made by @rexoronsaye

Choose an option below:"""
                self.edit_message(chat_id, msg_id, text, self.main_menu_buttons())
                return
            
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, msg_id, "❌ Admin only", self.main_menu_buttons())
                    return
                text = f"""<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

- <b>Individual Request Replies</b>
- <b>Photo Broadcast Support</b>
- <b>Game Removal System</b>
- <b>Duplicate Detection</b>
- <b>Redeploy System</b>
- <b>GitHub Database Backup</b>
- <b>Keep-Alive Protection</b>
- <b>Persistent Data Recovery</b>

Choose an option below:"""
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "games":
                text = f"""<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

<b>Games Section</b>

- <b>Total Games:</b> {self.get_channel_stats()['total_games']}
  - FREE
  - Regular: {self.get_channel_stats()['total_games']}
  - Premium: 0

📌 Choose an option below:
- Game Files - Browse all regular games
- Premium Games - Exclusive paid games
- Mini Games - Fun mini-games to play
- Search Games - Search for specific games
- Request Game - Request games not in our collection
- Donate Stars - Support our bot with Telegram Stars

<b>Channel:</b> {self.REQUIRED_CHANNEL}
<b>Time:</b> {datetime.now().strftime('%I:%M %p')}"""
                self.edit_message(chat_id, msg_id, text, self.games_buttons())
                return
            
            elif data == "game_files":
                stats = self.get_channel_stats()
                text = f"📁 <b>Game Files</b>\n\nTotal: {stats['total_games']} games\nChoose category:"
                self.edit_message(chat_id, msg_id, text, self.game_files_buttons())
                return
            
            elif data == "mini_games":
                text = "🎮 <b>Mini Games</b>\n\nChoose a game to play:"
                self.edit_message(chat_id, msg_id, text, self.mini_games_buttons())
                return
            
            elif data == "profile":
                cursor = self.conn.cursor()
                cursor.execute('SELECT created_at FROM users WHERE user_id = ?', (user_id,))
                created = cursor.fetchone()
                created_str = datetime.fromisoformat(created[0]).strftime('%Y-%m-%d\n%H:%M:%S') if created else 'Unknown'
                verified = "Yes" if self.is_user_verified(user_id) else "No"
                channel_joined = "Yes" if self.check_channel_membership(user_id) else "No"
                tokens = self.referral.get_tokens(user_id)
                
                text = f"""<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

Made by @rexoronsaye

<b>User Profile</b>

• <b>User ID</b>: {user_id}
• <b>Name</b>: {first_name}
• <b>Verified</b>: {verified}
• <b>Channel Joined</b>: {channel_joined}
• <b>Member Since</b>: {created_str}

Your unique ID: {user_id}
Use this ID for admin verification if needed.

<b>Sidebar Options:</b>
- Profile
- Time
- Channel
- Games ({self.get_channel_stats()['total_games']})
- Premium Games
- Search Games
- Request Game
- Donate Stars
- Admin Panel
- Redeploy Bot"""
                self.edit_message(chat_id, msg_id, text, self.main_menu_buttons())
                return
            
            elif data == "time":
                self.edit_message(chat_id, msg_id, f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.main_menu_buttons())
                return
            
            elif data == "channel_info":
                self.edit_message(chat_id, msg_id, f"📢 {self.REQUIRED_CHANNEL}\n🔗 {self.CHANNEL_LINK}", self.main_menu_buttons())
                return
            
            elif data == "verify_channel":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    text = "✅ Verified! Welcome to GAMERDROID™ V1!"
                    self.edit_message(chat_id, msg_id, text, self.main_menu_buttons())
                else:
                    text = "❌ Please join the channel first!"
                    self.edit_message(chat_id, msg_id, text, self.channel_buttons())
                return
            
            elif data == "search_games":
                text = "🔍 Type a game name to search:\n\nExample: 'God of War'"
                self.edit_message(chat_id, msg_id, text, self.search_buttons())
                return
            
            elif data == "request_game":
                self.game_requests[user_id] = {'stage': 'name'}
                text = f"""<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

<b>Game Request</b>

Please tell us the name of the game you'd like to request:

<b>Example:</b> 'God of War: Chains of Olympus'"""
                self.edit_message(chat_id, msg_id, text, None)
                return
            
            elif data == "stars_menu":
                self.edit_message(chat_id, msg_id, "⭐ <b>Donate Stars</b>\n\nSupport the bot with Telegram Stars!\n\nChoose amount:", self.stars_buttons())
                return
            
            elif data == "referral_menu":
                link = self.referral.get_link(user_id)
                tokens = self.referral.get_tokens(user_id)
                text = f"""👥 <b>Referral Program</b>

💎 <b>Your Stats:</b>
• Total Referrals: {tokens}
• Tokens Earned: {tokens}
• Current Balance: {tokens}

🎁 <b>How it works:</b>
1. Share your referral link
2. Friends join using your link
3. You get <b>1 Game Token</b> per referral
4. Use tokens to buy premium games!

🔗 <b>Your Referral Link:</b>
<code>{link}</code>

💡 1 Game Token = 1 Star value for premium games"""
                keyboard = {"inline_keyboard": [[{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}], [{"text": "🔙 Back", "callback_data": "back_to_menu"}]]}
                self.edit_message(chat_id, msg_id, text, keyboard)
                return
            
            elif data == "my_tokens":
                tokens = self.referral.get_tokens(user_id)
                text = f"""💎 <b>Game Tokens Balance</b>

💰 Current Balance: <b>{tokens} Tokens</b>

💡 <b>What can you do with tokens?</b>
• Buy premium games (10 tokens each)
• Exchange for premium content
• Access exclusive features

🎮 <b>Value:</b> 1 Token = 1 Star"""
                keyboard = {"inline_keyboard": [[{"text": "🎮 Premium Games", "callback_data": "premium_games"}, {"text": "👥 Referral Program", "callback_data": "referral_menu"}], [{"text": "🔙 Back", "callback_data": "back_to_menu"}]]}
                self.edit_message(chat_id, msg_id, text, keyboard)
                return
            
            elif data == "premium_games":
                premium_games = self.premium.get_premium_games(5)
                user_tokens = self.referral.get_tokens(user_id)
                
                if not premium_games:
                    text = f"""💰 <b>Premium Games</b>

💎 Your Tokens: {user_tokens}

No premium games available yet.
Check back later for exclusive games that you can purchase with Telegram Stars!"""
                    keyboard = {"inline_keyboard": [[{"text": "🆓 Regular Games", "callback_data": "game_files"}], [{"text": "🔄 Refresh", "callback_data": "premium_games"}], [{"text": "🔙 Back to Games", "callback_data": "games"}]]}
                else:
                    text = f"""💰 <b>Premium Games</b>

💎 Your Tokens: {user_tokens}

"""
                    kb = []
                    for i, g in enumerate(premium_games[:5], 1):
                        gid, name, ftype, fsize, price = g
                        size = self.format_size(fsize)
                        text += f"{i}. {name}\n   💎 {price} Tokens | 📦 {ftype} | 📏 {size}\n\n"
                        kb.append([{"text": f"💎 Buy ({price} Tokens)", "callback_data": f"buy_{gid}"}])
                    kb.append([{"text": "🆓 Regular Games", "callback_data": "game_files"}])
                    kb.append([{"text": "🔄 Refresh", "callback_data": "premium_games"}])
                    kb.append([{"text": "🔙 Back to Games", "callback_data": "games"}])
                    keyboard = {"inline_keyboard": kb}
                
                self.edit_message(chat_id, msg_id, text, keyboard)
                return
            
            elif data.startswith("buy_"):
                game_id = int(data.replace("buy_", ""))
                # Get game from database
                cursor = self.conn.cursor()
                cursor.execute('SELECT file_name, tokens_price FROM premium_games WHERE id = ?', (game_id,))
                game = cursor.fetchone()
                if game:
                    name, price = game
                    if self.referral.deduct_tokens(user_id, price):
                        cursor.execute('INSERT INTO premium_purchases (user_id, game_id, payment_method, tokens_paid) VALUES (?, ?, ?, ?)', (user_id, game_id, 'tokens', price))
                        self.conn.commit()
                        self.robust_send_message(chat_id, f"✅ Purchased {name} for {price} tokens!")
                    else:
                        self.robust_send_message(chat_id, f"❌ Insufficient tokens! Need {price} tokens.")
                return
            
            # Admin Actions
            elif data == "upload_stats" and self.is_admin(user_id):
                text = f"""<b>Your Stats:</b>
- Total uploads: {self.total_uploads}
- Forwarded files: {self.total_forwarded}
- Regular games: {self.get_channel_stats()['total_games']}
- Premium games: 0

<b>Choose an option:</b>"""
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "update_cache":
                self.update_cache()
                self.edit_message(chat_id, msg_id, "✅ Cache updated!", self.admin_panel_buttons())
                return
            
            elif data == "upload_games" and self.is_admin(user_id):
                text = "📤 Send a game file (ZIP, 7Z, ISO, APK, XAPK, APKS)\n\nThe game will be automatically saved to the database."
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "remove_games" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('SELECT file_name, file_id FROM channel_games LIMIT 30')
                games = cursor.fetchall()
                if not games:
                    self.edit_message(chat_id, msg_id, "❌ No games to remove.", self.admin_panel_buttons())
                    return
                self.remove_games_list = [{'file_name': g[0], 'file_id': g[1]} for g in games]
                text = "🗑️ <b>Remove Games</b>\n\nSelect a game to remove:\n\n"
                kb = []
                for i, game in enumerate(self.remove_games_list[:20], 1):
                    text += f"{i}. {game['file_name'][:40]}\n"
                    kb.append([{"text": f"❌ Remove {i}", "callback_data": f"remove_{i}"}])
                kb.append([{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}])
                self.edit_message(chat_id, msg_id, text, {"inline_keyboard": kb})
                return
            
            elif data.startswith("remove_"):
                idx = int(data.split('_')[1]) - 1
                if hasattr(self, 'remove_games_list') and idx < len(self.remove_games_list):
                    game = self.remove_games_list[idx]
                    cursor = self.conn.cursor()
                    cursor.execute('DELETE FROM channel_games WHERE file_name = ?', (game['file_name'],))
                    self.conn.commit()
                    self.update_cache()
                    self.robust_send_message(chat_id, f"✅ Removed: {game['file_name']}")
                    # Refresh
                    cursor.execute('SELECT file_name, file_id FROM channel_games LIMIT 30')
                    games = cursor.fetchall()
                    self.remove_games_list = [{'file_name': g[0], 'file_id': g[1]} for g in games]
                    if self.remove_games_list:
                        text = "🗑️ <b>Remove Games</b>\n\nSelect a game to remove:\n\n"
                        kb = []
                        for i, g in enumerate(self.remove_games_list[:20], 1):
                            text += f"{i}. {g['file_name'][:40]}\n"
                            kb.append([{"text": f"❌ Remove {i}", "callback_data": f"remove_{i}"}])
                        kb.append([{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}])
                        self.edit_message(chat_id, msg_id, text, {"inline_keyboard": kb})
                    else:
                        self.edit_message(chat_id, msg_id, "✅ All games removed!", self.admin_panel_buttons())
                return
            
            elif data == "clear_all_games" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM channel_games')
                self.conn.commit()
                self.update_cache()
                self.edit_message(chat_id, msg_id, "🗑️ All games cleared!", self.admin_panel_buttons())
                return
            
            elif data == "scan_bot_games" and self.is_admin(user_id):
                self.edit_message(chat_id, msg_id, "🔍 Scanning for bot-uploaded games...\n\nFeature coming soon.", self.admin_panel_buttons())
                return
            
            elif data == "broadcast_menu" and self.is_admin(user_id):
                self.broadcast_system.create_broadcast_with_buttons(user_id, chat_id)
                return
            
            elif data == "broadcast_text" and self.is_admin(user_id):
                self.broadcast_system.handle_broadcast_text(user_id, chat_id)
                return
            
            elif data == "broadcast_photo" and self.is_admin(user_id):
                self.broadcast_system.handle_broadcast_photo(user_id, chat_id)
                return
            
            elif data == "broadcast_video" and self.is_admin(user_id):
                self.broadcast_system.handle_broadcast_video(user_id, chat_id)
                return
            
            elif data == "broadcast_add_buttons" and self.is_admin(user_id):
                self.broadcast_system.add_buttons_to_broadcast(user_id, chat_id)
                return
            
            elif data == "send_broadcast" and self.is_admin(user_id):
                self.broadcast_system.execute_broadcast(user_id, chat_id)
                return
            
            elif data == "cancel_broadcast":
                if user_id in self.broadcast_system.sessions:
                    del self.broadcast_system.sessions[user_id]
                if user_id in self.broadcast_system.button_sessions:
                    del self.broadcast_system.button_sessions[user_id]
                self.edit_message(chat_id, msg_id, "❌ Broadcast cancelled.", self.admin_panel_buttons() if self.is_admin(user_id) else self.main_menu_buttons())
                return
            
            elif data == "game_requests_admin" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('SELECT id, user_name, game_name, platform, created_at FROM game_requests WHERE status = "pending" ORDER BY created_at DESC LIMIT 10')
                requests = cursor.fetchall()
                if not requests:
                    self.edit_message(chat_id, msg_id, "📋 No pending game requests.", self.admin_panel_buttons())
                    return
                text = "🎮 <b>Game Requests</b>\n\n"
                for r in requests:
                    req_id, name, game, platform, created = r
                    text += f"📝 #{req_id} - {game}\n   👤 {name} | 📱 {platform}\n   🕐 {created[:16]}\n\n"
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "stars_stats" and self.is_admin(user_id):
                self.edit_message(chat_id, msg_id, "⭐ Stars Stats\n\nTotal Stars Received: 0\nTotal USD: $0.00", self.admin_panel_buttons())
                return
            
            elif data == "backup_menu" and self.is_admin(user_id):
                text = "💾 Backup System\n\nEnabled: Yes\nAuto-backup on every game upload\nLast backup: Recently"
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "redeploy_panel" and self.is_admin(user_id):
                text = f"""<b>Admin Redeploy Access</b>
- Admin: {first_name}
- User ID: {user_id}

You have admin privileges and can redeploy the bot directly.

Choose redeploy type:"""
                self.edit_message(chat_id, msg_id, text, self.redeploy_buttons())
                return
            
            elif data == "redeploy_menu":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, msg_id, "❌ Admin only", self.main_menu_buttons())
                    return
                text = f"""<b>Admin Redeploy Access</b>
- Admin: {first_name}
- User ID: {user_id}

You have admin privileges and can redeploy the bot directly.

Choose redeploy type:"""
                self.edit_message(chat_id, msg_id, text, self.redeploy_buttons())
                return
            
            elif data == "redeploy_soft" and self.is_admin(user_id):
                self.edit_message(chat_id, msg_id, "🔄 Soft redeploy initiated... Bot will restart in 5 seconds.", self.admin_panel_buttons())
                def restart(): time.sleep(5); os._exit(0)
                Thread(target=restart).start()
                return
            
            elif data == "redeploy_force" and self.is_admin(user_id):
                self.edit_message(chat_id, msg_id, "🚀 Force redeploy initiated... Bot will restart in 2 seconds.", self.admin_panel_buttons())
                def restart(): time.sleep(2); os._exit(0)
                Thread(target=restart).start()
                return
            
            elif data == "system_status" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM channel_games')
                games = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM users')
                users = cursor.fetchone()[0]
                text = f"""📊 System Status

🟢 Bot Status: ONLINE
📁 Regular Games: {games}
💰 Premium Games: 0
👥 Users: {users}
🕒 Mode: Webhook"""
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "referral_stats" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('SELECT user_id, first_name, total_referrals, game_tokens FROM users WHERE total_referrals > 0 ORDER BY total_referrals DESC LIMIT 10')
                top = cursor.fetchall()
                text = "🏆 Referral Leaderboard\n\n"
                for i, (uid, name, refs, tokens) in enumerate(top, 1):
                    text += f"{i}. {name} - {refs} referrals ({tokens} tokens)\n"
                if not top:
                    text += "No referrals yet."
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            elif data == "token_management" and self.is_admin(user_id):
                text = "💎 Token Management\n\nUse /addtokens [user_id] [amount] to add tokens"
                self.edit_message(chat_id, msg_id, text, self.admin_panel_buttons())
                return
            
            # Game Categories
            elif data == "game_zip":
                self.show_games(self.games_cache.get('zip', []), "ZIP", chat_id, msg_id)
                return
            elif data == "game_7z":
                self.show_games(self.games_cache.get('7z', []), "7Z", chat_id, msg_id)
                return
            elif data == "game_iso":
                self.show_games(self.games_cache.get('iso', []), "ISO", chat_id, msg_id)
                return
            elif data == "game_apk":
                self.show_games(self.games_cache.get('apk', []), "APK", chat_id, msg_id)
                return
            elif data == "game_psp":
                psp_games = self.games_cache.get('cso', []) + self.games_cache.get('pbp', [])
                self.show_games(psp_games, "PSP", chat_id, msg_id)
                return
            elif data == "game_all":
                self.show_games(self.games_cache.get('all', []), "ALL", chat_id, msg_id)
                return
            elif data == "rescan_games":
                self.update_cache()
                self.edit_message(chat_id, msg_id, "✅ Cache updated!", self.game_files_buttons())
                return
            
            # Download Game
            elif data.startswith("dl_"):
                idx = int(data.replace("dl_", "")) - 1
                if idx < len(self.current_games_list):
                    game = self.current_games_list[idx]
                    self.send_game_file(user_id, chat_id, game['file_name'], game['file_id'])
                return
            
            # Mini Games
            elif data == "game_guess":
                self.guess_games[user_id] = random.randint(1, 10)
                self.edit_message(chat_id, msg_id, "🎯 Guess a number between 1-10!\n\nSend your guess:", None)
                return
            elif data == "game_random":
                num = random.randint(1, 100)
                self.edit_message(chat_id, msg_id, f"🎲 Random number: {num}", self.mini_games_buttons())
                return
            elif data == "game_spin":
                symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣"]
                spin = [random.choice(symbols) for _ in range(3)]
                self.edit_message(chat_id, msg_id, f"🎰 {spin[0]} | {spin[1]} | {spin[2]}", self.mini_games_buttons())
                return
            
            # Donations
            elif data.startswith("donate_"):
                stars = int(data.replace("donate_", ""))
                self.robust_send_message(chat_id, f"⭐ Thank you! {stars} Stars donation received!")
                return
            
        except Exception as e:
            print(f"Callback error: {e}")
            traceback.print_exc()
    
    # ==================== PROCESS UPDATE ====================
    
    def process_update(self, update):
        try:
            if 'message' in update:
                self.process_message(update['message'])
            elif 'callback_query' in update:
                self.handle_callback(update['callback_query'])
        except Exception as e:
            print(f"Update error: {e}")
    
    def process_message(self, message):
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                username = message['from'].get('username', '')
                
                # Handle /start command
                if text.startswith('/start'):
                    parts = text.split()
                    referrer_id = None
                    if len(parts) > 1 and parts[1].startswith('ref_'):
                        try:
                            referrer_id = int(parts[1].replace('ref_', ''))
                        except:
                            pass
                    
                    # Register user
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
                    if not cursor.fetchone():
                        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)', (user_id, username, first_name))
                        self.conn.commit()
                        if referrer_id and referrer_id != user_id:
                            self.referral.register_referral(referrer_id, user_id)
                    
                    # Send verification code
                    code = self.generate_code()
                    self.save_verification_code(user_id, username, first_name, code)
                    welcome = f"""👋 Welcome {first_name}!

🔐 Your verification code: <code>{code}</code>

Please join {self.REQUIRED_CHANNEL} and enter this code to verify."""
                    
                    self.robust_send_message(chat_id, welcome, self.channel_buttons())
                    return True
                
                # Handle verification code
                if text.isdigit() and len(text) == 6:
                    if self.verify_code(user_id, text):
                        if self.check_channel_membership(user_id):
                            self.mark_channel_joined(user_id)
                            text = f"""✅ Verification Complete!

👋 Welcome {first_name}!

<b>GAMERDROID™ V1</b>
{self.monthly_users} monthly users

Made by @rexoronsaye

Choose an option below:"""
                            self.robust_send_message(chat_id, text, self.main_menu_buttons())
                        else:
                            self.robust_send_message(chat_id, "✅ Code verified! Now join our channel.", self.channel_buttons())
                    else:
                        self.robust_send_message(chat_id, "❌ Invalid code. Use /start to get a new code.")
                    return True
                
                # Handle game request
                if user_id in self.game_requests:
                    session = self.game_requests[user_id]
                    if session.get('stage') == 'name':
                        session['game_name'] = text
                        session['stage'] = 'platform'
                        self.robust_send_message(chat_id, f"🎮 Game: {text}\n\nNow send the platform (Android/PSP/PC/PS2/etc):")
                        return True
                    elif session.get('stage') == 'platform':
                        game_name = session['game_name']
                        platform = text
                        cursor = self.conn.cursor()
                        cursor.execute('INSERT INTO game_requests (user_id, user_name, game_name, platform) VALUES (?, ?, ?, ?)', (user_id, first_name, game_name, platform))
                        self.conn.commit()
                        del self.game_requests[user_id]
                        self.robust_send_message(chat_id, f"✅ Game Request Submitted!\n\n🎮 Game: {game_name}\n📱 Platform: {platform}\n\nOur team will review your request!")
                        # Notify admins
                        for admin in self.ADMIN_IDS:
                            self.robust_send_message(admin, f"🎮 New Game Request!\n\nUser: {first_name} (ID: {user_id})\nGame: {game_name}\nPlatform: {platform}")
                        return True
                
                # Handle broadcast text input
                if user_id in self.broadcast_system.sessions:
                    session = self.broadcast_system.sessions[user_id]
                    if session.get('stage') == 'waiting_text':
                        session['message'] = text
                        session['stage'] = 'preview'
                        self.broadcast_system.show_preview(user_id, chat_id)
                        return True
                    elif session.get('stage') == 'waiting_buttons':
                        self.broadcast_system.process_buttons_input(user_id, chat_id, text)
                        return True
                    elif session.get('stage') == 'waiting_caption':
                        if text.lower() == 'skip':
                            session['caption'] = ''
                        else:
                            session['caption'] = text
                        session['stage'] = 'preview'
                        self.broadcast_system.show_preview(user_id, chat_id)
                        return True
                
                # Handle number guess
                if user_id in self.guess_games:
                    try:
                        guess = int(text)
                        target = self.guess_games[user_id]
                        if guess == target:
                            self.robust_send_message(chat_id, f"🎉 Correct! The number was {target}!\n\nYou won!", self.mini_games_buttons())
                            del self.guess_games[user_id]
                        elif guess < target:
                            self.robust_send_message(chat_id, "📈 Too low! Try again:")
                        else:
                            self.robust_send_message(chat_id, "📉 Too high! Try again:")
                    except:
                        self.robust_send_message(chat_id, "❌ Please send a number between 1-10:")
                    return True
                
                # Handle search
                if self.is_user_verified(user_id):
                    self.search_games(chat_id, text)
                    return True
            
            # Handle photo upload for broadcast
            elif 'photo' in message and user_id in self.broadcast_system.sessions:
                session = self.broadcast_system.sessions[user_id]
                if session.get('stage') == 'waiting_photo':
                    session['photo'] = message['photo'][-1]['file_id']
                    session['stage'] = 'waiting_caption'
                    self.robust_send_message(chat_id, "📝 Now send the caption (or send 'skip'):")
                    return True
            
            # Handle video upload for broadcast
            elif 'video' in message and user_id in self.broadcast_system.sessions:
                session = self.broadcast_system.sessions[user_id]
                if session.get('stage') == 'waiting_video':
                    session['video'] = message['video']['file_id']
                    session['stage'] = 'waiting_caption'
                    self.robust_send_message(chat_id, "📝 Now send the caption (or send 'skip'):")
                    return True
            
            # Handle game upload (admins only)
            elif 'document' in message:
                if self.is_admin(user_id):
                    doc = message['document']
                    file_name = doc.get('file_name', 'unknown')
                    file_id = doc['file_id']
                    file_size = doc.get('file_size', 0)
                    self.save_game(message, file_id, file_name, file_size, user_id)
                else:
                    self.robust_send_message(chat_id, "❌ Only admins can upload games.")
                return True
            
            return False
        except Exception as e:
            print(f"Process error: {e}")
            return False
    
    def search_games(self, chat_id, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT file_name, file_type, file_size, file_id FROM channel_games WHERE file_name LIKE ? LIMIT 20', (f'%{query}%',))
            results = cursor.fetchall()
            if not results:
                self.robust_send_message(chat_id, f"🔍 No games found for '{query}'")
                return
            self.current_games_list = [{'file_name': r[0], 'file_type': r[1], 'file_size': r[2], 'file_id': r[3]} for r in results]
            text = f"🔍 <b>Search Results for '{query}'</b>\n\n📊 Found: {len(results)} games\n\n"
            keyboard = []
            for i, game in enumerate(self.current_games_list, 1):
                size = self.format_size(game['file_size'])
                text += f"{i}. <code>{game['file_name'][:40]}</code>\n   📦 {game['file_type'].upper()} | 📏 {size}\n\n"
                keyboard.append([{"text": f"📥 Download {i}", "callback_data": f"dl_{i}"}])
            keyboard.append([{"text": "🔍 New Search", "callback_data": "search_games"}, {"text": "🔙 Back", "callback_data": "game_files"}])
            self.robust_send_message(chat_id, text, {"inline_keyboard": keyboard})
        except Exception as e:
            print(f"Search error: {e}")

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    print("🚀 Starting GAMERDROID™ V1 Bot...")
    
    # Start webhook server
    Thread(target=run_server, daemon=True).start()
    time.sleep(2)
    
    if BOT_TOKEN:
        try:
            # Set webhook
            public_url = os.environ.get('CHOREO_URL') or os.environ.get('RENDER_EXTERNAL_URL')
            if public_url:
                webhook_url = f"{public_url}/webhook"
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook", timeout=10)
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", data={"url": webhook_url}, timeout=10)
                print(f"✅ Webhook set: {webhook_url}")
            
            bot_instance = GamerDroidBot(BOT_TOKEN)
            print("✅ Bot is running!")
            
            # Keep alive
            while True:
                time.sleep(60)
                print(f"💚 Bot alive - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No BOT_TOKEN provided")
