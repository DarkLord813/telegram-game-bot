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

print("TELEGRAM BOT - CROSS PLATFORM")
print("Code Verification + Channel Join + Game Scanner")
print("Admin Game Uploads Enabled + Forward Support + Game Scanner")
print("Mini-Games Integration: Number Guess, Random Number, Lucky Spin")
print("Admin Broadcast Messaging System + Enhanced Keep-Alive Protection")
print("Telegram Stars Payments Integration")
print("Game Request System for Users")
print("Premium Games System with Stars Payments")
print("Enhanced Broadcast with Photos & VIDEOS")
print("Individual Request Replies")
print("Game Removal System with Duplicate Detection")
print("Redeploy System for Admins and Users")
print("GitHub Database Backup & Restore System")
print("24/7 Operation with Persistent Data Recovery")
print("REFERRAL SYSTEM WITH GAME TOKENS")
print("GAME TOKEN PAYMENTS FOR PREMIUM GAMES")
print("XAPK & APKS FILE SUPPORT")
print("AUTO GITHUB BACKUP ON EVERY GAME UPLOAD")
print("WEBHOOK MODE FOR 24/7 OPERATION")
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

# Test critical imports
try:
    import requests
    print("✅ DEBUG: requests import OK")
except ImportError as e:
    print(f"❌ DEBUG: requests import failed: {e}")

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
# ==================== END DEBUG SECTION ====================

# Health check server
app = Flask(__name__)

# Global bot instance for webhook
bot_instance = None

@app.route('/health')
def health_check():
    """Enhanced health check endpoint for Render monitoring"""
    try:
        bot_status = 'unknown'
        if bot_instance and hasattr(bot_instance, 'test_bot_connection'):
            bot_status = 'healthy' if bot_instance.test_bot_connection() else 'unhealthy'
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'telegram-game-bot',
            'version': '2.0.0',
            'bot_status': bot_status,
            'mode': 'webhook',
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

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint - ALWAYS RETURNS 200 OK"""
    try:
        if not bot_instance:
            print("⚠️ Webhook received but bot not ready")
            return jsonify({'ok': False, 'error': 'Bot not ready'}), 200
        
        update = request.get_json()
        if update:
            thread = Thread(target=bot_instance.process_webhook_update, args=(update,))
            thread.start()
            print(f"📨 Webhook update received")
        
        return jsonify({'ok': True}), 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 200

@app.route('/redeploy', methods=['POST'])
def redeploy_bot():
    """Redeploy endpoint for admins and users"""
    try:
        auth_token = request.headers.get('Authorization', '')
        user_id = request.json.get('user_id', '') if request.json else ''
        
        is_authorized = auth_token == os.environ.get('REDEPLOY_TOKEN', 'default_token') or user_id in ['7475473197', '7713987088']
        
        if not is_authorized:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 401
        
        print(f"🔄 Redeploy triggered by user {user_id}")
        
        def delayed_restart():
            time.sleep(2)
            os._exit(0)
        
        Thread(target=delayed_restart, daemon=True).start()
        
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

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Telegram Game Bot',
        'status': 'running',
        'version': '2.0.0',
        'mode': 'webhook',
        'endpoints': {
            'health': '/health',
            'webhook': '/webhook (POST)',
            'redeploy': '/redeploy (POST)',
            'features': ['Game Distribution', 'Mini-Games', 'Admin Uploads', 'Broadcast Messaging', 'Telegram Stars', 'Game Requests', 'Premium Games', 'Game Removal System', 'Redeploy System', '24/7 Operation', 'Referral System', 'Game Tokens', 'XAPK/APKS Support', 'Auto Backup']
        }
    })

def set_webhook():
    """Set Telegram webhook URL"""
    if not BOT_TOKEN:
        return False
    
    public_url = os.environ.get('CHOREO_URL') or os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('PUBLIC_URL')
    
    if not public_url:
        print("⚠️ No public URL found, webhook not set")
        print("⚠️ Please set CHOREO_URL environment variable")
        return False
    
    webhook_url = f"{public_url}/webhook"
    
    try:
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        delete_response = requests.post(delete_url, timeout=10)
        print(f"Delete webhook response: {delete_response.json()}")
        
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        data = {"url": webhook_url}
        response = requests.post(set_url, data=data, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Webhook set successfully: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result}")
            return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def run_webhook_server():
    """Run the Flask webhook server"""
    try:
        port = int(os.environ.get('PORT', 8080))
        print(f"🔄 Starting webhook server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {e}")
        time.sleep(10)
        os._exit(1)

def start_webhook_server():
    """Start webhook server in background"""
    t = Thread(target=run_webhook_server, daemon=True)
    t.start()
    print("✅ Webhook server started")

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
                
                if consecutive_failures >= max_consecutive_failures:
                    print("🚨 Too many consecutive failures, initiating emergency procedures...")
                    self.emergency_restart()
                    consecutive_failures = 0
                
                if time.time() - self.last_successful_ping > 600:
                    print("🚨 No successful pings for 10 minutes, emergency restart...")
                    self.emergency_restart()
                    self.last_successful_ping = time.time()
                
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

# ==================== REFERRAL SYSTEM WITH GAME TOKENS ====================

class ReferralSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_referral_database()
        print("✅ Referral system initialized!")
    
    def setup_referral_database(self):
        """Setup referral system database tables"""
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'referred_by' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT 0')
            if 'referral_code' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN referral_code TEXT UNIQUE')
            if 'game_tokens' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN game_tokens INTEGER DEFAULT 0')
            if 'total_referrals' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN total_referrals INTEGER DEFAULT 0')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    tokens_earned INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS token_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    transaction_type TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.bot.conn.commit()
            print("✅ Referral database setup complete!")
            
        except Exception as e:
            print(f"❌ Referral database setup error: {e}")
    
    def generate_referral_code(self, user_id):
        import hashlib
        code = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
        return code
    
    def register_referral(self, referrer_id, referred_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id FROM referrals WHERE referred_id = ?', (referred_id,))
            if cursor.fetchone():
                return False
            
            cursor.execute('INSERT INTO referrals (referrer_id, referred_id, tokens_earned) VALUES (?, ?, ?)', (referrer_id, referred_id, 1))
            cursor.execute('UPDATE users SET game_tokens = game_tokens + 1, total_referrals = total_referrals + 1 WHERE user_id = ?', (referrer_id,))
            cursor.execute('INSERT INTO token_transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)', (referrer_id, 1, 'referral', f'Referred user {referred_id}'))
            self.bot.conn.commit()
            print(f"✅ Referral registered: {referrer_id} -> {referred_id}")
            return True
        except Exception as e:
            print(f"❌ Referral registration error: {e}")
            return False
    
    def get_user_tokens(self, user_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT game_tokens FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def add_tokens(self, user_id, amount, description=""):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('UPDATE users SET game_tokens = game_tokens + ? WHERE user_id = ?', (amount, user_id))
            cursor.execute('INSERT INTO token_transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)', (user_id, amount, 'admin_add', description))
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Add tokens error: {e}")
            return False
    
    def deduct_tokens(self, user_id, amount, description=""):
        try:
            current = self.get_user_tokens(user_id)
            if current < amount:
                return False
            cursor = self.bot.conn.cursor()
            cursor.execute('UPDATE users SET game_tokens = game_tokens - ? WHERE user_id = ?', (amount, user_id))
            cursor.execute('INSERT INTO token_transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)', (user_id, -amount, 'purchase', description))
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Deduct tokens error: {e}")
            return False
    
    def get_referral_stats(self, user_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT total_referrals FROM users WHERE user_id = ?', (user_id,))
            total_refs = cursor.fetchone()
            total_refs = total_refs[0] if total_refs else 0
            return {
                'total_referrals': total_refs,
                'monthly_referrals': 0,
                'total_tokens_earned': total_refs,
                'current_tokens': self.get_user_tokens(user_id)
            }
        except:
            return {'total_referrals': 0, 'monthly_referrals': 0, 'total_tokens_earned': 0, 'current_tokens': 0}
    
    def get_leaderboard(self, limit=10):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT user_id, first_name, total_referrals, game_tokens FROM users WHERE total_referrals > 0 ORDER BY total_referrals DESC LIMIT ?', (limit,))
            return cursor.fetchall()
        except:
            return []
    
    def generate_referral_link(self, user_id):
        cursor = self.bot.conn.cursor()
        cursor.execute('SELECT referral_code FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        bot_username = self.bot.token.split(':')[0] if ':' in self.bot.token else 'your_bot'
        return f"https://t.me/{bot_username}?start=ref_{user_id}"

# ==================== ENHANCED BROADCAST SYSTEM WITH VIDEO ====================

class EnhancedBroadcastSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.broadcast_sessions = {}
        self.button_sessions = {}
        print("✅ Enhanced Broadcast System with Video initialized!")
    
    def create_broadcast_with_buttons(self, user_id, chat_id):
        self.broadcast_sessions[user_id] = {
            'stage': 'waiting_type',
            'type': None,
            'message': None,
            'photo': None,
            'video': None,
            'caption': None,
            'buttons': [],
            'chat_id': chat_id
        }
        
        menu_text = """📢 <b>Enhanced Broadcast System</b>

Choose what to broadcast:

📝 Text Message with formatting
🖼️ Photo with caption
🎥 Video with caption
🔘 Inline buttons support

Send your content now:"""
        
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
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_text'
        self.broadcast_sessions[user_id]['type'] = 'text'
        self.bot.robust_send_message(chat_id, "📝 Send your broadcast message (HTML formatting supported):")
    
    def handle_broadcast_photo(self, user_id, chat_id):
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_photo'
        self.broadcast_sessions[user_id]['type'] = 'photo'
        self.bot.robust_send_message(chat_id, "🖼️ Send your photo (caption optional):\n\nSend 'skip' for no caption")
    
    def handle_broadcast_video(self, user_id, chat_id):
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_video'
        self.broadcast_sessions[user_id]['type'] = 'video'
        self.bot.robust_send_message(chat_id, "🎥 Send your video (caption optional):\n\nSend 'skip' for no caption")
    
    def handle_caption(self, user_id, chat_id, caption):
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        if caption.lower() != 'skip':
            session['caption'] = caption
        session['stage'] = 'preview'
        self.show_preview(user_id, chat_id)
    
    def add_buttons_to_broadcast(self, user_id, chat_id):
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        session['stage'] = 'waiting_buttons'
        self.button_sessions[user_id] = {'buttons': [], 'stage': 'collecting'}
        
        help_text = """🔘 Add Inline Buttons

Send buttons ONE BY ONE in separate messages.

Format: Button Text|type|value

Types: url, callback, game

Examples:
Join Channel|url|https://t.me/pspgamers5
Get Games|callback|games

Send 'done' when finished.
Send 'cancel' to abort."""
        
        self.bot.robust_send_message(chat_id, help_text)
    
    def process_buttons_input(self, user_id, chat_id, text):
        if user_id not in self.button_sessions:
            return
        
        if text.lower() == 'cancel':
            del self.button_sessions[user_id]
            self.bot.robust_send_message(chat_id, "❌ Button addition cancelled.")
            return
        
        if text.lower() == 'done':
            if user_id in self.broadcast_sessions:
                self.broadcast_sessions[user_id]['buttons'] = self.button_sessions[user_id]['buttons']
                self.broadcast_sessions[user_id]['stage'] = 'preview'
            del self.button_sessions[user_id]
            self.show_preview(user_id, chat_id)
            return
        
        parts = text.split('|')
        if len(parts) >= 3:
            button_text = parts[0].strip()
            button_type = parts[1].strip().lower()
            button_value = parts[2].strip()
            
            if button_type == 'url':
                button = {"text": button_text, "url": button_value}
            elif button_type == 'callback':
                button = {"text": button_text, "callback_data": button_value}
            elif button_type == 'game':
                button = {"text": button_text, "callback_game": {}}
            else:
                self.bot.robust_send_message(chat_id, "❌ Invalid type. Use: url, callback, or game")
                return
            
            self.button_sessions[user_id]['buttons'].append(button)
            self.bot.robust_send_message(chat_id, f"✅ Button added: {button_text}\n\nSend another button, 'done' to finish, or 'cancel' to abort")
        else:
            self.bot.robust_send_message(chat_id, "❌ Invalid format. Use: Text|type|value")
    
    def show_preview(self, user_id, chat_id):
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        
        preview_text = "📋 <b>Broadcast Preview</b>\n\n"
        
        if session['type'] == 'text':
            preview_text += f"📝 <b>Message:</b>\n{session['message']}\n\n"
        elif session['type'] == 'photo':
            preview_text += f"🖼️ <b>Photo</b>\n"
            if session.get('caption'):
                preview_text += f"📝 <b>Caption:</b>\n{session['caption']}\n\n"
        elif session['type'] == 'video':
            preview_text += f"🎥 <b>Video</b>\n"
            if session.get('caption'):
                preview_text += f"📝 <b>Caption:</b>\n{session['caption']}\n\n"
        
        if session['buttons']:
            preview_text += f"🔘 <b>Buttons:</b> {len(session['buttons'])}\n"
            for btn in session['buttons']:
                preview_text += f"  • {btn['text']}\n"
        
        preview_text += "\nSend this broadcast?"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "✅ Send Broadcast", "callback_data": "send_broadcast"}],
                [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
            ]
        }
        
        self.bot.robust_send_message(chat_id, preview_text, keyboard)
    
    def execute_broadcast(self, user_id, chat_id):
        if user_id not in self.broadcast_sessions:
            return
        
        session = self.broadcast_sessions[user_id]
        
        cursor = self.bot.conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
        users = cursor.fetchall()
        
        if not users:
            self.bot.robust_send_message(chat_id, "❌ No verified users found.")
            del self.broadcast_sessions[user_id]
            return
        
        total_users = len(users)
        success_count = 0
        failed_count = 0
        
        reply_markup = None
        if session['buttons']:
            button_rows = [session['buttons'][i:i+2] for i in range(0, len(session['buttons']), 2)]
            reply_markup = json.dumps({"inline_keyboard": button_rows})
        
        start_time = time.time()
        
        for user_id_target, in users:
            try:
                if session['type'] == 'text':
                    success = self.bot.robust_send_message(
                        user_id_target, 
                        session['message'], 
                        json.loads(reply_markup) if reply_markup else None
                    )
                elif session['type'] == 'photo':
                    if session.get('photo'):
                        success = self.bot.robust_send_photo(
                            user_id_target, 
                            session['photo'], 
                            session.get('caption', ''), 
                            json.loads(reply_markup) if reply_markup else None
                        )
                    else:
                        success = False
                elif session['type'] == 'video':
                    if session.get('video'):
                        success = self.bot.robust_send_video(
                            user_id_target, 
                            session['video'], 
                            session.get('caption', ''), 
                            json.loads(reply_markup) if reply_markup else None
                        )
                    else:
                        success = False
                else:
                    success = False
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    
                time.sleep(0.05)
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Broadcast error to {user_id_target}: {e}")
        
        elapsed = time.time() - start_time
        
        cursor.execute('''
            INSERT INTO broadcast_history 
            (admin_id, message_text, photo_file_id, video_file_id, inline_buttons, total_sent, total_failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session.get('message'), session.get('photo'), session.get('video'), json.dumps(session['buttons']) if session['buttons'] else None, success_count, failed_count))
        self.bot.conn.commit()
        
        stats_text = f"""✅ <b>Broadcast Completed!</b>

📊 Final Statistics:
• Total users: {total_users}
✅ Sent: {success_count}
❌ Failed: {failed_count}
📈 Success rate: {(success_count/total_users)*100:.1f}%
⏱️ Time taken: {elapsed:.1f}s
📝 Type: {session['type'].upper()} Broadcast"""
        
        self.bot.robust_send_message(chat_id, stats_text)
        del self.broadcast_sessions[user_id]

# ==================== TELEGRAM STARS SYSTEM ====================

class TelegramStarsSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_stars_database()
        print("✅ Telegram Stars system initialized!")
        
    def setup_stars_database(self):
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stars_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    stars_amount INTEGER,
                    usd_amount REAL,
                    description TEXT,
                    telegram_star_amount INTEGER,
                    transaction_id TEXT,
                    payment_status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            ''')
            
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
            
            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')
            self.bot.conn.commit()
            print("✅ Telegram Stars database setup complete!")
        except Exception as e:
            print(f"❌ Stars database setup error: {e}")
    
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
                    'available_usd': result[4] or 0.0,
                    'last_updated': result[5]
                }
            return {'available_stars': 0, 'available_usd': 0.0}
        except:
            return {'available_stars': 0, 'available_usd': 0.0}

# ==================== GAME REQUEST SYSTEM ====================

class GameRequestSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_game_requests_database()
        print("✅ Game request system initialized!")
    
    def setup_game_requests_database(self):
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    game_name TEXT,
                    platform TEXT,
                    status TEXT DEFAULT 'pending',
                    admin_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_request_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER,
                    admin_id INTEGER,
                    reply_text TEXT,
                    photo_file_id TEXT,
                    video_file_id TEXT,
                    document_file_id TEXT,
                    reply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES game_requests (id)
                )
            ''')
            
            self.bot.conn.commit()
            print("✅ Game request system setup complete!")
        except Exception as e:
            print(f"❌ Game request database setup error: {e}")
    
    def submit_game_request(self, user_id, game_name, platform="Unknown"):
        try:
            user_info = self.bot.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Anonymous')
            
            cursor = self.bot.conn.cursor()
            cursor.execute('INSERT INTO game_requests (user_id, user_name, game_name, platform, status) VALUES (?, ?, ?, ?, ?)', (user_id, user_name, game_name, platform, 'pending'))
            self.bot.conn.commit()
            request_id = cursor.lastrowid
            
            for admin_id in self.bot.ADMIN_IDS:
                try:
                    self.bot.robust_send_message(admin_id, f"🎮 New Game Request!\n\nUser: {user_name}\nGame: {game_name}\nPlatform: {platform}\nID: #{request_id}")
                except:
                    pass
            
            return request_id
        except Exception as e:
            print(f"❌ Error submitting game request: {e}")
            return False
    
    def get_request_by_id(self, request_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id, user_id, user_name, game_name, platform, status, admin_notes, created_at FROM game_requests WHERE id = ?', (request_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'user_id': result[1],
                    'user_name': result[2],
                    'game_name': result[3],
                    'platform': result[4],
                    'status': result[5],
                    'admin_notes': result[6],
                    'created_at': result[7]
                }
            return None
        except:
            return None
    
    def update_request_status(self, request_id, status, admin_notes=""):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('UPDATE game_requests SET status = ?, admin_notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (status, admin_notes, request_id))
            self.bot.conn.commit()
            return True
        except:
            return False

# ==================== PREMIUM GAMES SYSTEM ====================

class PremiumGamesSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_premium_games_database()
        print("✅ Premium games system initialized!")
    
    def setup_premium_games_database(self):
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_games (
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
                    bot_message_id INTEGER,
                    stars_price INTEGER DEFAULT 0,
                    tokens_price INTEGER DEFAULT 10,
                    description TEXT,
                    is_premium INTEGER DEFAULT 1
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_id INTEGER,
                    payment_method TEXT,
                    stars_paid INTEGER DEFAULT 0,
                    tokens_paid INTEGER DEFAULT 0,
                    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            self.bot.conn.commit()
            print("✅ Premium games database setup complete!")
        except Exception as e:
            print(f"❌ Premium games database setup error: {e}")
    
    def get_premium_games(self, limit=50):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id, file_name, file_type, file_size, stars_price, tokens_price, description, upload_date, file_id, bot_message_id, is_uploaded FROM premium_games WHERE is_premium = 1 ORDER BY created_at DESC LIMIT ?', (limit,))
            return cursor.fetchall()
        except:
            return []
    
    def get_premium_game_by_id(self, game_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id, file_name, file_type, file_size, stars_price, tokens_price, description, file_id, bot_message_id, is_uploaded, message_id FROM premium_games WHERE id = ?', (game_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'file_name': result[1],
                    'file_type': result[2],
                    'file_size': result[3],
                    'stars_price': result[4],
                    'tokens_price': result[5],
                    'description': result[6],
                    'file_id': result[7],
                    'bot_message_id': result[8],
                    'is_uploaded': result[9],
                    'message_id': result[10]
                }
            return None
        except:
            return None
    
    def has_user_purchased_game(self, user_id, game_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT id FROM premium_purchases WHERE user_id = ? AND game_id = ? AND status = "completed"', (user_id, game_id))
            return cursor.fetchone() is not None
        except:
            return False
    
    def record_purchase(self, user_id, game_id, payment_method, stars_paid=0, tokens_paid=0, transaction_id=""):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('INSERT INTO premium_purchases (user_id, game_id, payment_method, stars_paid, tokens_paid, transaction_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, game_id, payment_method, stars_paid, tokens_paid, transaction_id, 'completed'))
            self.bot.conn.commit()
            return True
        except:
            return False

# ==================== GITHUB BACKUP SYSTEM ====================

class GitHubBackupSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_github_config()
        print("✅ GitHub Backup system initialized!")
    
    def setup_github_config(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo_owner = os.environ.get('GITHUB_REPO_OWNER', 'your-username')
        self.repo_name = os.environ.get('GITHUB_REPO_NAME', 'your-repo')
        self.backup_branch = os.environ.get('GITHUB_BACKUP_BRANCH', 'main')
        self.backup_path = os.environ.get('GITHUB_BACKUP_PATH', 'backups/telegram_bot.db')
        
        self.is_enabled = bool(self.github_token and self.repo_owner and self.repo_name)
        
        if self.is_enabled:
            print(f"✅ GitHub Backup: Enabled for {self.repo_owner}/{self.repo_name}")
        else:
            print("⚠️ GitHub Backup: Disabled - Set environment variables")
    
    def backup_database_to_github(self, commit_message="Auto backup: Database update"):
        if not self.is_enabled:
            return False
        
        try:
            db_path = self.bot.get_db_path()
            if not os.path.exists(db_path):
                return False
            
            with open(db_path, 'rb') as f:
                db_content = f.read()
            
            db_b64 = base64.b64encode(db_content).decode('utf-8')
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {'Authorization': f'token {self.github_token}', 'Accept': 'application/vnd.github.v3+json'}
            
            file_sha = None
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    file_sha = response.json().get('sha')
            except:
                pass
            
            data = {'message': commit_message, 'content': db_b64, 'branch': self.backup_branch}
            if file_sha:
                data['sha'] = file_sha
            
            response = requests.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"✅ Database backed up to GitHub")
                return True
            else:
                print(f"❌ GitHub backup failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ GitHub backup error: {e}")
            return False
    
    def get_backup_info(self):
        if not self.is_enabled:
            return {"enabled": False}
        return {"enabled": True, "last_backup": "Recently"}

# ==================== REDEPLOY SYSTEM ====================

class RedeploySystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.redeploy_requests = {}
        print("✅ Redeploy system initialized!")
    
    def show_redeploy_menu(self, user_id, chat_id, message_id):
        if not self.bot.is_admin(user_id):
            self.bot.answer_callback_query(message_id, "❌ Access denied. Admin only.", True)
            return
        
        redeploy_text = """🔄 <b>Bot Redeploy System</b>

This system allows you to restart the bot without losing any data.

⚠️ <b>Important:</b>
• Database will be preserved
• All games and user data remain safe
• Bot will be unavailable for 10-30 seconds

Choose an option:"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}],
                [{"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}],
                [{"text": "📊 System Status", "callback_data": "system_status"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.bot.edit_message(chat_id, message_id, redeploy_text, keyboard)
    
    def initiate_redeploy(self, user_id, chat_id, redeploy_type="soft"):
        try:
            user_info = self.bot.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Unknown')
            
            print(f"🔄 {redeploy_type.upper()} redeploy initiated by {user_name} ({user_id})")
            
            confirm_text = f"""🔄 <b>{redeploy_type.upper()} Redeploy Initiated</b>

👤 Initiated by: {user_name}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ The bot will restart shortly..."""
            
            self.bot.robust_send_message(chat_id, confirm_text)
            
            restart_delay = 5 if redeploy_type == "soft" else 2
            
            def delayed_restart():
                time.sleep(restart_delay)
                print(f"🔄 Executing {redeploy_type} redeploy...")
                os._exit(0)
            
            restart_thread = threading.Thread(target=delayed_restart, daemon=True)
            restart_thread.start()
            
            return True
        except Exception as e:
            print(f"❌ Redeploy initiation error: {e}")
            self.bot.robust_send_message(chat_id, f"❌ Redeploy failed: {str(e)}")
            return False
    
    def show_system_status(self, user_id, chat_id, message_id):
        try:
            bot_online = self.bot.test_bot_connection()
            
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            game_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM premium_games')
            premium_count = cursor.fetchone()[0]
            
            uptime_seconds = time.time() - self.bot.last_restart
            uptime_str = self.format_uptime(uptime_seconds)
            
            status_text = f"""📊 <b>System Status</b>

🤖 <b>Bot Status:</b> {'🟢 ONLINE' if bot_online else '🔴 OFFLINE'}
📁 <b>Regular Games:</b> {game_count}
💰 <b>Premium Games:</b> {premium_count}
👥 <b>Users:</b> {user_count}
🕒 <b>Uptime:</b> {uptime_str}
🔄 <b>Last Restart:</b> {datetime.fromtimestamp(self.bot.last_restart).strftime('%Y-%m-%d %H:%M:%S')}"""

            keyboard = {
                "inline_keyboard": [
                    [{"text": "🔄 Refresh", "callback_data": "system_status"}],
                    [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
                ]
            }
            
            self.bot.edit_message(chat_id, message_id, status_text, keyboard)
        except Exception as e:
            print(f"❌ System status error: {e}")
    
    def format_uptime(self, seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if days > 0:
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"

# ==================== MAIN BOT CLASS ====================

class CrossPlatformBot:
    def __init__(self, token):
        if not token:
            print("❌ CRITICAL: No BOT_TOKEN provided!")
            raise ValueError("BOT_TOKEN is required")
        
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
        self.REQUIRED_CHANNEL = "@pspgamers5"
        self.CHANNEL_LINK = "https://t.me/pspgamers5"
        self.ADMIN_IDS = [7475473197, 7713987088]
        
        # Session management
        self.stars_sessions = {}
        self.request_sessions = {}
        self.upload_sessions = {}
        self.reply_sessions = {}
        self.media_reply_sessions = {}
        self.guess_games = {}
        self.spin_games = {}
        self.broadcast_sessions = {}
        self.broadcast_stats = {}
        
        self.games_cache = {}
        self.current_games_list = []  # Store current games for download
        self.search_results = {}
        self.search_sessions = {}
        
        # Crash protection
        self.last_restart = time.time()
        self.error_count = 0
        self.max_errors = 25
        self.error_window = 300
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.is_scanning = False
        self.keep_alive = None
        
        # Setup database FIRST
        self.setup_database()
        self.verify_database_schema()
        
        # THEN initialize systems
        self.referral_system = ReferralSystem(self)
        self.broadcast_system = EnhancedBroadcastSystem(self)
        self.stars_system = TelegramStarsSystem(self)
        self.game_request_system = GameRequestSystem(self)
        self.premium_games_system = PremiumGamesSystem(self)
        self.redeploy_system = RedeploySystem(self)
        self.github_backup = GitHubBackupSystem(self)
        
        print("✅ Bot system ready!")
        print("👥 Referral System Active - 1 Game Token per referral")
        print("💎 Game Tokens can be used to purchase premium games")
        print("📹 Video Broadcast System Enabled")
        print("📝 Individual Game Request Replies with Media Support")
        print("💾 GitHub Auto-Backup on Every Game Upload")
        print("🌐 Webhook Mode - 24/7 Operation")
    
    def get_db_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_bot.db')
    
    def setup_database(self):
        try:
            db_path = self.get_db_path()
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_verified INTEGER DEFAULT 0,
                    joined_channel INTEGER DEFAULT 0,
                    verification_code TEXT,
                    code_expires DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    referred_by INTEGER DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    game_tokens INTEGER DEFAULT 0,
                    total_referrals INTEGER DEFAULT 0
                )
            ''')
            
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS broadcast_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    message_text TEXT,
                    photo_file_id TEXT,
                    video_file_id TEXT,
                    inline_buttons TEXT,
                    total_sent INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("✅ Database setup successful!")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    def verify_database_schema(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(channel_games)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'bot_message_id' not in columns:
                cursor.execute('ALTER TABLE channel_games ADD COLUMN bot_message_id INTEGER')
                self.conn.commit()
        except Exception as e:
            print(f"Schema verification error: {e}")
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def test_bot_connection(self):
        try:
            url = self.base_url + "getMe"
            response = requests.get(url, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def robust_send_message(self, chat_id, text, reply_markup=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                url = self.base_url + "sendMessage"
                data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
                if reply_markup:
                    data["reply_markup"] = json.dumps(reply_markup)
                response = requests.post(url, data=data, timeout=15)
                if response.json().get('ok'):
                    return True
                time.sleep(1)
            except:
                time.sleep(1)
        return False
    
    def robust_send_photo(self, chat_id, photo, caption="", reply_markup=None):
        try:
            url = self.base_url + "sendPhoto"
            data = {"chat_id": chat_id, "photo": photo, "parse_mode": "HTML"}
            if caption:
                data["caption"] = caption
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            response = requests.post(url, data=data, timeout=30)
            return response.json().get('ok', False)
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
            response = requests.post(url, data=data, timeout=60)
            return response.json().get('ok', False)
        except:
            return False
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        try:
            url = self.base_url + "editMessageText"
            data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            response = requests.post(url, data=data, timeout=15)
            return response.json().get('ok', False)
        except:
            return False
    
    def answer_callback_query(self, query_id, text=None, show_alert=False):
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
            cursor.execute('SELECT user_id, username, first_name, game_tokens, total_referrals FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'user_id': result[0], 
                    'username': result[1], 
                    'first_name': result[2], 
                    'game_tokens': result[3] or 0, 
                    'total_referrals': result[4] or 0
                }
            return {'first_name': 'User', 'game_tokens': 0, 'total_referrals': 0}
        except:
            return {'first_name': 'User', 'game_tokens': 0, 'total_referrals': 0}
    
    def register_user(self, user_id, username, first_name, referred_by=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            if cursor.fetchone():
                return True
            
            referral_code = self.referral_system.generate_referral_code(user_id)
            cursor.execute('INSERT INTO users (user_id, username, first_name, referral_code, referred_by, game_tokens) VALUES (?, ?, ?, ?, ?, ?)', (user_id, username, first_name, referral_code, referred_by or 0, 0))
            self.conn.commit()
            
            if referred_by and referred_by != user_id:
                self.referral_system.register_referral(referred_by, user_id)
                self.robust_send_message(referred_by, f"🎉 New Referral!\n@{username or first_name} joined!\nYou earned 1 Game Token 💎")
            
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def get_channel_stats(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM premium_games')
            premium_games = cursor.fetchone()[0]
            return {'total_games': total_games, 'premium_games': premium_games}
        except:
            return {'total_games': 0, 'premium_games': 0}
    
    def get_upload_stats(self, user_id=None):
        try:
            cursor = self.conn.cursor()
            if user_id:
                cursor.execute('SELECT COUNT(*) FROM channel_games WHERE added_by = ? AND is_uploaded = 1', (user_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
            return cursor.fetchone()[0]
        except:
            return 0
    
    def get_forward_stats(self, user_id=None):
        try:
            cursor = self.conn.cursor()
            if user_id:
                cursor.execute('SELECT COUNT(*) FROM channel_games WHERE added_by = ? AND is_uploaded = 1 AND is_forwarded = 1', (user_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1 AND is_forwarded = 1')
            return cursor.fetchone()[0]
        except:
            return 0
    
    def update_games_cache(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT file_name, file_type, file_size, upload_date, category, is_uploaded, file_id, message_id, bot_message_id FROM channel_games')
            games = cursor.fetchall()
            self.games_cache = {'zip': [], '7z': [], 'iso': [], 'apk': [], 'xapk': [], 'apks': [], 'cso': [], 'pbp': [], 'all': []}
            for game in games:
                file_name, file_type, file_size, upload_date, category, is_uploaded, file_id, msg_id, bot_msg_id = game
                game_info = {
                    'file_name': file_name, 
                    'file_type': file_type, 
                    'file_size': file_size, 
                    'upload_date': upload_date, 
                    'category': category, 
                    'is_uploaded': is_uploaded,
                    'file_id': file_id,
                    'message_id': msg_id,
                    'bot_message_id': bot_msg_id
                }
                file_type_lower = file_type.lower()
                if file_type_lower in self.games_cache:
                    self.games_cache[file_type_lower].append(game_info)
                self.games_cache['all'].append(game_info)
            print(f"🔄 Cache updated: {len(self.games_cache['all'])} games")
        except Exception as e:
            print(f"Cache error: {e}")
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def determine_file_category(self, filename):
        filename_lower = filename.lower()
        if filename_lower.endswith('.apk'):
            return 'Android APK Games'
        elif filename_lower.endswith('.xapk'):
            return 'Android XAPK Games'
        elif filename_lower.endswith('.apks'):
            return 'Android APKS Bundle'
        elif filename_lower.endswith('.iso'):
            return 'ISO Games'
        elif filename_lower.endswith('.zip'):
            return 'ZIP Games'
        elif filename_lower.endswith('.7z'):
            return '7Z Games'
        elif filename_lower.endswith('.cso') or filename_lower.endswith('.pbp'):
            return 'PSP Games'
        else:
            return 'Other Games'
    
    # ==================== GAME UPLOAD HANDLER ====================
    
    def save_game_to_database(self, message, file_id, file_name, file_size, file_type, user_id):
        """Save uploaded game to database and respond to user"""
        try:
            cursor = self.conn.cursor()
            
            # Check if game already exists
            cursor.execute('SELECT id FROM channel_games WHERE file_name = ?', (file_name,))
            existing = cursor.fetchone()
            
            if existing:
                self.robust_send_message(user_id, f"❌ Game '{file_name}' already exists in database!")
                return False
            
            # Insert game into database
            category = self.determine_file_category(file_name)
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO channel_games (message_id, file_name, file_type, file_size, upload_date, category, added_by, is_uploaded, file_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (message['message_id'], file_name, file_type, file_size, upload_date, category, user_id, 1, file_id))
            
            self.conn.commit()
            
            # Update cache
            self.update_games_cache()
            
            # Send success message to user
            size_str = self.format_file_size(file_size)
            success_text = f"""✅ <b>Game Successfully Added to Database!</b>

📁 <b>File Name:</b> {file_name}
📦 <b>Type:</b> {file_type.upper()}
📏 <b>Size:</b> {size_str}
📂 <b>Category:</b> {category}
🆔 <b>Added by:</b> {user_id}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The game is now available in the Games section!"""
            
            self.robust_send_message(user_id, success_text)
            
            # Trigger GitHub backup
            self.trigger_auto_backup(file_name)
            
            # Notify admins
            for admin_id in self.ADMIN_IDS:
                if admin_id != user_id:
                    self.robust_send_message(admin_id, f"📢 New game uploaded by user {user_id}!\n\n{file_name}\nSize: {size_str}")
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.robust_send_message(user_id, f"❌ Error saving game: {str(e)}")
            return False
    
    # ==================== GAME SENDING FUNCTION ====================
    
    def send_game_file(self, user_id, chat_id, file_name, file_id, message_id):
        """Send the actual game file to user"""
        try:
            self.robust_send_message(chat_id, f"📥 Sending <b>{file_name}</b>... Please wait.")
            
            # Send document/file to user
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id,
                "caption": f"🎮 <b>{file_name}</b>\n\n✅ Game sent successfully!\n📥 Enjoy your download!"
            }
            response = requests.post(url, data=data, timeout=60)
            
            if response.json().get('ok'):
                self.robust_send_message(chat_id, f"✅ <b>{file_name}</b> has been sent to you!")
                return True
            else:
                # Try forwarding as fallback
                url = self.base_url + "forwardMessage"
                data = {
                    "chat_id": chat_id,
                    "from_chat_id": self.REQUIRED_CHANNEL,
                    "message_id": message_id
                }
                response = requests.post(url, data=data, timeout=30)
                if response.json().get('ok'):
                    self.robust_send_message(chat_id, f"✅ <b>{file_name}</b> has been sent to you!")
                    return True
                else:
                    self.robust_send_message(chat_id, f"❌ Failed to send {file_name}. Please contact admin.")
                    return False
        except Exception as e:
            print(f"Error sending file: {e}")
            self.robust_send_message(chat_id, f"❌ Error sending file: {str(e)}")
            return False
    
    # ==================== FORMAT GAMES LIST WITH BUTTONS ====================
    
    def format_games_list(self, games, category, chat_id, message_id):
        """Format games list with inline buttons to send files"""
        if not games:
            self.edit_message(chat_id, message_id, f"❌ No {category} games found.", self.create_game_files_buttons())
            return
        
        # Store games in current list for callback
        self.current_games_list = games[:20]
        
        text = f"📁 <b>{category} GAMES</b>\n\n📊 Found: {len(games)} files\n\n"
        
        # Create buttons for each game (max 10 per page to avoid message too long)
        keyboard_buttons = []
        for i, game in enumerate(self.current_games_list, 1):
            file_name = game['file_name']
            file_type = game['file_type']
            size = self.format_file_size(game['file_size'])
            
            text += f"{i}. <b>{file_name[:40]}</b>\n   📦 {file_type.upper()} | 📏 {size}\n\n"
            
            # Create button for this game
            keyboard_buttons.append([{
                "text": f"📥 Download {i}",
                "callback_data": f"download_game_{i}"
            }])
        
        keyboard_buttons.append([{"text": "🔙 Back to Games", "callback_data": "game_files"}])
        
        self.edit_message(chat_id, message_id, text, {"inline_keyboard": keyboard_buttons})
    
    def trigger_auto_backup(self, file_name=""):
        if self.github_backup.is_enabled:
            thread = Thread(target=self.github_backup.backup_database_to_github, args=(f"Auto-backup: Game '{file_name}' uploaded",))
            thread.start()
            print(f"💾 Auto-backup triggered for: {file_name}")
    
    # ==================== VERIFICATION CODE FUNCTIONS ====================
    
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
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            if result.get('ok'):
                status = result['result']['status']
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
    
    # ==================== MENU BUTTONS ====================
    
    def create_main_menu_buttons(self):
        stats = self.get_channel_stats()
        keyboard = [
            [{"text": "📊 Profile", "callback_data": "profile"}, {"text": "🕒 Time", "callback_data": "time"}],
            [{"text": "📢 Channel", "callback_data": "channel_info"}, {"text": f"🎮 Games ({stats['total_games'] + stats['premium_games']})", "callback_data": "games"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}, {"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "👥 Referral Program", "callback_data": "referral_menu"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}]
        ]
        if self.is_admin:
            keyboard.append([{"text": "🔧 Admin Panel", "callback_data": "admin_panel"}])
        keyboard.append([{"text": "🔄 Redeploy Bot", "callback_data": "user_redeploy"}])
        return {"inline_keyboard": keyboard}
    
    def create_admin_buttons(self):
        return {
            "inline_keyboard": [
                [{"text": "📤 Upload Stats", "callback_data": "upload_stats"}, {"text": "🔄 Update Cache", "callback_data": "update_cache"}],
                [{"text": "📤 Upload Games", "callback_data": "upload_options"}, {"text": "🗑️ Remove Games", "callback_data": "remove_games"}],
                [{"text": "🗑️ Clear All Games", "callback_data": "clear_all_games"}, {"text": "🔍 Scan Bot Games", "callback_data": "scan_bot_games"}],
                [{"text": "📢 Broadcast", "callback_data": "broadcast_panel"}, {"text": "🎮 Game Requests", "callback_data": "admin_requests_panel"}],
                [{"text": "⭐ Stars Stats", "callback_data": "stars_stats"}, {"text": "💾 Backup System", "callback_data": "backup_menu"}],
                [{"text": "🔄 Redeploy System", "callback_data": "redeploy_panel"}, {"text": "📊 System Status", "callback_data": "system_status"}],
                [{"text": "👥 Referral Stats", "callback_data": "referral_stats"}, {"text": "💎 Token Management", "callback_data": "token_management"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
    
    def create_channel_buttons(self):
        return {"inline_keyboard": [[{"text": "📢 JOIN CHANNEL", "url": self.CHANNEL_LINK}, {"text": "✅ VERIFY JOIN", "callback_data": "verify_channel"}]]}
    
    def create_games_buttons(self):
        stats = self.get_channel_stats()
        return {"inline_keyboard": [
            [{"text": "🎮 Mini Games", "callback_data": "mini_games"}, {"text": f"📁 Game Files ({stats['total_games']})", "callback_data": "game_files"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}, {"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "👥 Referral Program", "callback_data": "referral_menu"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
            [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
        ]}
    
    def create_game_files_buttons(self):
        stats = self.get_channel_stats()
        return {"inline_keyboard": [
            [{"text": f"📦 ZIP ({len(self.games_cache.get('zip', []))})", "callback_data": "game_zip"}, {"text": f"🗜️ 7Z ({len(self.games_cache.get('7z', []))})", "callback_data": "game_7z"}],
            [{"text": f"💿 ISO ({len(self.games_cache.get('iso', []))})", "callback_data": "game_iso"}, {"text": f"📱 APK ({len(self.games_cache.get('apk', []))})", "callback_data": "game_apk"}],
            [{"text": f"🎮 PSP ({len(self.games_cache.get('cso', [])) + len(self.games_cache.get('pbp', []))})", "callback_data": "game_psp"}, {"text": f"📋 All ({stats['total_games']})", "callback_data": "game_all"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "🔄 Rescan", "callback_data": "rescan_games"}],
            [{"text": "🔙 Back to Games", "callback_data": "games"}]
        ]}
    
    def create_mini_games_buttons(self):
        return {"inline_keyboard": [
            [{"text": "🎯 Number Guess", "callback_data": "game_guess"}, {"text": "🎲 Random Number", "callback_data": "game_random"}],
            [{"text": "🎰 Lucky Spin", "callback_data": "game_spin"}, {"text": "📊 My Stats", "callback_data": "mini_stats"}],
            [{"text": "🔙 Back to Games", "callback_data": "games"}]
        ]}
    
    def create_search_buttons(self):
        return {"inline_keyboard": [
            [{"text": "🔍 New Search", "callback_data": "search_games"}, {"text": "📁 Browse All", "callback_data": "game_files"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}, {"text": "📝 Request Game", "callback_data": "request_game"}],
            [{"text": "👥 Referral Program", "callback_data": "referral_menu"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
            [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
        ]}
    
    # ==================== REFERRAL SYSTEM UI ====================
    
    def show_referral_menu(self, user_id, chat_id, message_id):
        stats = self.referral_system.get_referral_stats(user_id)
        referral_link = self.referral_system.generate_referral_link(user_id)
        leaderboard = self.referral_system.get_leaderboard(5)
        
        text = f"""👥 <b>Referral Program</b>

💎 <b>Your Stats:</b>
• Total Referrals: {stats['total_referrals']}
• Tokens Earned: {stats['total_tokens_earned']}
• Current Balance: {stats['current_tokens']}

🎁 <b>How it works:</b>
1. Share your referral link
2. Friends join using your link
3. You get <b>1 Game Token</b> per referral
4. Use tokens to buy premium games!

🔗 <b>Your Referral Link:</b>
<code>{referral_link}</code>

"""
        
        if leaderboard:
            text += "🏆 <b>Top Referrers:</b>\n"
            for i, (uid, name, refs, tokens) in enumerate(leaderboard, 1):
                text += f"{i}. {name} - {refs} referrals ({tokens} tokens)\n"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "💰 Browse Premium Games", "callback_data": "premium_games"}, {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def show_token_balance(self, user_id, chat_id, message_id):
        tokens = self.referral_system.get_user_tokens(user_id)
        text = f"💎 <b>Game Tokens Balance</b>\n\n💰 Current Balance: <b>{tokens} Tokens</b>\n\n💡 Use tokens to buy premium games!"
        keyboard = {"inline_keyboard": [[{"text": "🎮 Premium Games", "callback_data": "premium_games"}, {"text": "👥 Referral Program", "callback_data": "referral_menu"}], [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]]}
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def show_referral_stats_admin(self, user_id, chat_id, message_id):
        leaderboard = self.referral_system.get_leaderboard(20)
        text = "🏆 <b>Referral Leaderboard</b>\n\n"
        for i, (uid, name, refs, tokens) in enumerate(leaderboard, 1):
            text += f"{i}. {name} - {refs} referrals ({tokens} tokens)\n"
        self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
    
    def show_token_management(self, user_id, chat_id, message_id):
        text = """💎 <b>Token Management</b>

Commands for admins:
/addtokens [user_id] [amount] - Add tokens to user
/removetokens [user_id] [amount] - Remove tokens
/tokenbalance [user_id] - Check user balance"""
        self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
    
    # ==================== PREMIUM GAMES ====================
    
    def show_premium_games_menu(self, user_id, chat_id, message_id=None):
        premium_games = self.premium_games_system.get_premium_games(20)
        user_tokens = self.referral_system.get_user_tokens(user_id)
        
        if not premium_games:
            premium_text = f"""💰 <b>Premium Games</b>

💎 Your Tokens: {user_tokens}

No premium games available yet."""
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🆓 Regular Games", "callback_data": "game_files"}],
                    [{"text": "🔄 Refresh", "callback_data": "premium_games"}],
                    [{"text": "🔙 Back to Games", "callback_data": "games"}]
                ]
            }
        else:
            premium_text = f"""💰 <b>Premium Games Collection</b>

💎 Your Tokens: {user_tokens}

Purchase with <b>Stars ⭐</b> or <b>Tokens 💎</b>

"""
            keyboard_buttons = []
            
            for i, game in enumerate(premium_games[:10], 1):
                game_id, file_name, file_type, file_size, stars_price, tokens_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
                size = self.format_file_size(file_size)
                display_name = file_name[:30] + "..." if len(file_name) > 30 else file_name
                
                premium_text += f"{i}. <b>{display_name}</b>\n"
                premium_text += f"   📦 {file_type} | 📏 {size}\n"
                premium_text += f"   ⭐ {stars_price} Stars OR 💎 {tokens_price} Tokens\n\n"
                
                keyboard_buttons.append([
                    {"text": f"⭐ Buy ({stars_price} Stars)", "callback_data": f"buy_with_stars_{game_id}"},
                    {"text": f"💎 Buy ({tokens_price} Tokens)", "callback_data": f"buy_with_tokens_{game_id}"}
                ])
            
            keyboard_buttons.extend([
                [{"text": "🆓 Regular Games", "callback_data": "game_files"}],
                [{"text": "👥 Referral Program", "callback_data": "referral_menu"}],
                [{"text": "💎 My Tokens", "callback_data": "my_tokens"}],
                [{"text": "🔄 Refresh", "callback_data": "premium_games"}],
                [{"text": "🔙 Back to Games", "callback_data": "games"}]
            ])
            
            keyboard = {"inline_keyboard": keyboard_buttons}
        
        if message_id:
            self.edit_message(chat_id, message_id, premium_text, keyboard)
        else:
            self.robust_send_message(chat_id, premium_text, keyboard)
    
    def purchase_with_tokens(self, user_id, chat_id, game_id):
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        if not game:
            self.robust_send_message(chat_id, "❌ Game not found")
            return
        
        if self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id, f"✅ You already own {game['file_name']}!")
            return
        
        if self.referral_system.deduct_tokens(user_id, game['tokens_price'], f"Purchased {game['file_name']}"):
            self.premium_games_system.record_purchase(user_id, game_id, 'tokens', 0, game['tokens_price'])
            self.robust_send_message(chat_id, f"✅ Purchase Successful!\n\n🎮 {game['file_name']}\n💎 Paid: {game['tokens_price']} Tokens")
            keyboard = {"inline_keyboard": [[{"text": "📥 Download Now", "callback_data": f"download_premium_{game_id}"}]]}
            self.robust_send_message(chat_id, "🎮 Your game is ready!", keyboard)
        else:
            self.robust_send_message(chat_id, f"❌ Insufficient Tokens! Need {game['tokens_price']} Tokens")
    
    def purchase_with_stars(self, user_id, chat_id, game_id):
        self.robust_send_message(chat_id, "⭐ Stars payment feature - Coming soon!")
    
    def send_premium_game(self, user_id, chat_id, game_id):
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        if not game:
            self.robust_send_message(chat_id, "❌ Game not found")
            return
        
        if not self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id, f"❌ You haven't purchased {game['file_name']} yet!")
            return
        
        self.robust_send_message(chat_id, f"📥 Sending {game['file_name']}...")
        
        if game['is_uploaded'] and game['bot_message_id']:
            url = self.base_url + "sendDocument"
            data = {"chat_id": chat_id, "document": game['file_id'] if game['file_id'] else game['bot_message_id']}
            response = requests.post(url, data=data, timeout=30)
            success = response.json().get('ok', False)
        else:
            url = self.base_url + "forwardMessage"
            data = {"chat_id": chat_id, "from_chat_id": self.REQUIRED_CHANNEL, "message_id": game['message_id']}
            response = requests.post(url, data=data, timeout=30)
            success = response.json().get('ok', False)
        
        if success:
            self.robust_send_message(chat_id, f"✅ Enjoy your game: {game['file_name']}!")
        else:
            self.robust_send_message(chat_id, "❌ Failed to send game.")
    
    # ==================== GAME REQUESTS ====================
    
    def start_game_request(self, user_id, chat_id):
        self.request_sessions[user_id] = {'stage': 'waiting_game_name'}
        self.robust_send_message(chat_id, "🎮 <b>Game Request</b>\n\nPlease tell us the name of the game you'd like to request:\n\nExample: 'God of War: Chains of Olympus'")
    
    def handle_game_request(self, user_id, chat_id, game_name):
        self.request_sessions[user_id] = {'stage': 'waiting_platform', 'game_name': game_name}
        self.robust_send_message(chat_id, f"🎮 <b>Game Request</b>\n\nGame: {game_name}\n\nNow, please specify the platform:")
        return True
    
    def complete_game_request(self, user_id, chat_id, platform):
        if user_id not in self.request_sessions:
            return False
        session = self.request_sessions[user_id]
        if session.get('stage') != 'waiting_platform':
            return False
        
        game_name = session['game_name']
        request_id = self.game_request_system.submit_game_request(user_id, game_name, platform)
        
        if request_id:
            del self.request_sessions[user_id]
            self.robust_send_message(chat_id, f"✅ Game Request Submitted!\n\n🎮 Game: {game_name}\n📱 Platform: {platform}\n🆔 Request ID: {request_id}")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Sorry, there was an error.")
            return False
    
    def start_request_reply_with_media(self, user_id, chat_id, request_id):
        if not self.is_admin(user_id):
            return False
        
        request = self.game_request_system.get_request_by_id(request_id)
        if not request:
            self.robust_send_message(chat_id, "❌ Request not found")
            return False
        
        self.media_reply_sessions[user_id] = {'stage': 'waiting_text', 'request_id': request_id, 'user_id': request['user_id'], 'game_name': request['game_name']}
        self.robust_send_message(chat_id, f"📝 Reply to Game Request #{request_id}\n\nGame: {request['game_name']}\n\nSend your text reply:")
        return True
    
    def show_admin_requests_panel(self, user_id, chat_id, message_id):
        if not self.is_admin(user_id):
            return
        text = "👑 Game Request Management\n\nNo pending requests."
        self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
    
    def start_broadcast(self, user_id, chat_id):
        if self.is_admin(user_id):
            self.broadcast_system.create_broadcast_with_buttons(user_id, chat_id)
    
    def show_stars_menu(self, user_id, chat_id, message_id=None):
        balance = self.stars_system.get_balance()
        text = f"⭐ Support with Telegram Stars\n\n💫 Star Packages: 50, 100, 500, 1000 Stars\n\n📊 Total Received: {balance['total_stars_earned']} ⭐"
        keyboard = {"inline_keyboard": [[{"text": "⭐ 50 Stars", "callback_data": "donate_50"}, {"text": "⭐ 100 Stars", "callback_data": "donate_100"}], [{"text": "⭐ 500 Stars", "callback_data": "donate_500"}, {"text": "⭐ 1000 Stars", "callback_data": "donate_1000"}], [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]]}
        if message_id:
            self.edit_message(chat_id, message_id, text, keyboard)
        else:
            self.robust_send_message(chat_id, text, keyboard)
    
    def process_stars_donation(self, user_id, chat_id, stars_amount):
        self.robust_send_message(chat_id, f"⭐ Thank you! {stars_amount} Stars donation.")
    
    def show_stars_stats(self, user_id, chat_id, message_id):
        balance = self.stars_system.get_balance()
        self.edit_message(chat_id, message_id, f"⭐ Stars Stats\n\nTotal Stars: {balance['total_stars_earned']}", self.create_admin_buttons())
    
    def start_number_guess_game(self, user_id, chat_id):
        target = random.randint(1, 10)
        self.guess_games[user_id] = {'target': target, 'attempts': 0}
        self.robust_send_message(chat_id, "🎯 Guess a number between 1-10!")
    
    def generate_random_number(self, user_id, chat_id):
        number = random.randint(1, 100)
        self.robust_send_message(chat_id, f"🎲 Random number: {number}")
    
    def lucky_spin(self, user_id, chat_id):
        symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
        spins = [random.choice(symbols) for _ in range(3)]
        self.robust_send_message(chat_id, f"🎰 {spins[0]} | {spins[1]} | {spins[2]}")
    
    def show_mini_games_stats(self, user_id, chat_id, message_id):
        self.edit_message(chat_id, message_id, "📊 Mini Games Stats", self.create_mini_games_buttons())
    
    # ==================== HANDLE CALLBACK ====================
    
    def handle_callback_query(self, callback_query):
        try:
            data = callback_query['data']
            message = callback_query['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            user_id = callback_query['from']['id']
            first_name = callback_query['from']['first_name']
            
            self.answer_callback_query(callback_query['id'])
            
            # Referral System
            if data == "referral_menu":
                self.show_referral_menu(user_id, chat_id, message_id)
                return
            elif data == "my_tokens":
                self.show_token_balance(user_id, chat_id, message_id)
                return
            elif data == "referral_stats" and self.is_admin(user_id):
                self.show_referral_stats_admin(user_id, chat_id, message_id)
                return
            elif data == "token_management" and self.is_admin(user_id):
                self.show_token_management(user_id, chat_id, message_id)
                return
            
            # Premium Games
            elif data == "premium_games":
                self.show_premium_games_menu(user_id, chat_id, message_id)
                return
            elif data.startswith("buy_with_tokens_"):
                game_id = int(data.replace("buy_with_tokens_", ""))
                self.purchase_with_tokens(user_id, chat_id, game_id)
                return
            elif data.startswith("buy_with_stars_"):
                game_id = int(data.replace("buy_with_stars_", ""))
                self.purchase_with_stars(user_id, chat_id, game_id)
                return
            elif data.startswith("download_premium_"):
                game_id = int(data.replace("download_premium_", ""))
                self.send_premium_game(user_id, chat_id, game_id)
                return
            
            # Handle game download requests
            elif data.startswith("download_game_"):
                try:
                    # Extract index from callback data
                    index = int(data.replace("download_game_", "")) - 1  # Convert to 0-based index
                    if hasattr(self, 'current_games_list') and index < len(self.current_games_list):
                        game = self.current_games_list[index]
                        file_name = game['file_name']
                        file_id = game.get('file_id', '')
                        msg_id = game.get('message_id', 0)
                        
                        if file_id:
                            # Send the file
                            self.send_game_file(user_id, chat_id, file_name, file_id, msg_id)
                        else:
                            self.robust_send_message(chat_id, f"❌ File ID not found for {file_name}")
                    else:
                        self.robust_send_message(chat_id, "❌ Game not found. Please refresh the list.")
                except Exception as e:
                    print(f"Download error: {e}")
                    self.robust_send_message(chat_id, f"❌ Error: {str(e)}")
                return
            
            # Broadcast System
            elif data == "broadcast_panel":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.create_broadcast_with_buttons(user_id, chat_id)
                return
            elif data == "broadcast_text":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.handle_broadcast_text(user_id, chat_id)
                return
            elif data == "broadcast_photo":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.handle_broadcast_photo(user_id, chat_id)
                return
            elif data == "broadcast_video":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.handle_broadcast_video(user_id, chat_id)
                return
            elif data == "broadcast_add_buttons":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.add_buttons_to_broadcast(user_id, chat_id)
                return
            elif data == "send_broadcast":
                if not self.is_admin(user_id):
                    return
                self.broadcast_system.execute_broadcast(user_id, chat_id)
                return
            elif data == "cancel_broadcast":
                if user_id in self.broadcast_system.broadcast_sessions:
                    del self.broadcast_system.broadcast_sessions[user_id]
                if user_id in self.broadcast_system.button_sessions:
                    del self.broadcast_system.button_sessions[user_id]
                self.edit_message(chat_id, message_id, "❌ Broadcast cancelled.", self.create_admin_buttons() if self.is_admin(user_id) else self.create_main_menu_buttons())
                return
            elif data == "start_broadcast":
                self.start_broadcast(user_id, chat_id)
                return
            elif data == "broadcast_stats":
                self.edit_message(chat_id, message_id, "📊 Broadcast stats", self.create_admin_buttons())
                return
            
            # Game Requests
            elif data == "request_game":
                self.start_game_request(user_id, chat_id)
                return
            elif data == "admin_requests_panel":
                self.show_admin_requests_panel(user_id, chat_id, message_id)
                return
            elif data.startswith("reply_media_"):
                request_id = int(data.replace("reply_media_", ""))
                self.start_request_reply_with_media(user_id, chat_id, request_id)
                return
            elif data == "cancel_reply":
                if user_id in self.media_reply_sessions:
                    del self.media_reply_sessions[user_id]
                self.robust_send_message(chat_id, "❌ Reply cancelled.")
                return
            
            # Stars System
            elif data == "stars_menu":
                self.show_stars_menu(user_id, chat_id, message_id)
                return
            elif data.startswith("donate_"):
                stars_amount = int(data.replace("donate_", ""))
                self.process_stars_donation(user_id, chat_id, stars_amount)
                return
            elif data == "stars_stats" and self.is_admin(user_id):
                self.show_stars_stats(user_id, chat_id, message_id)
                return
            
            # Admin Panel and Navigation
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Admin only", self.create_main_menu_buttons())
                    return
                self.edit_message(chat_id, message_id, "👑 Admin Panel", self.create_admin_buttons())
                return
            elif data == "back_to_menu":
                self.edit_message(chat_id, message_id, f"👋 Welcome {first_name}!", self.create_main_menu_buttons())
                return
            elif data == "games":
                self.edit_message(chat_id, message_id, "🎮 Games Section", self.create_games_buttons())
                return
            elif data == "game_files":
                self.edit_message(chat_id, message_id, "📁 Game Files", self.create_game_files_buttons())
                return
            elif data == "mini_games":
                self.edit_message(chat_id, message_id, "🎮 Mini Games", self.create_mini_games_buttons())
                return
            elif data == "search_games":
                self.edit_message(chat_id, message_id, "🔍 Type a game name to search:", self.create_search_buttons())
                return
            elif data == "profile":
                tokens = self.referral_system.get_user_tokens(user_id)
                user_info = self.get_user_info(user_id)
                cursor = self.conn.cursor()
                cursor.execute('SELECT created_at FROM users WHERE user_id = ?', (user_id,))
                created_at = cursor.fetchone()
                created_str = datetime.fromisoformat(created_at[0]).strftime('%Y-%m-%d\n%H:%M:%S') if created_at else 'Unknown'
                verification_status = "Yes" if self.is_user_verified(user_id) else "No"
                channel_status = "Yes" if self.check_channel_membership(user_id) else "No"
                
                text = f"""<b>User Profile</b>

• <b>User ID</b>: {user_id}
• <b>Name</b>: {first_name}
• <b>Verified</b>: {verification_status}
• <b>Channel Joined</b>: {channel_status}
• <b>Member Since</b>: {created_str}

Your unique ID: {user_id}
Use this ID for admin verification if needed."""
                
                self.edit_message(chat_id, message_id, text, self.create_main_menu_buttons())
                return
            elif data == "time":
                self.edit_message(chat_id, message_id, f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.create_main_menu_buttons())
                return
            elif data == "channel_info":
                self.edit_message(chat_id, message_id, f"📢 {self.REQUIRED_CHANNEL}\n🔗 {self.CHANNEL_LINK}", self.create_main_menu_buttons())
                return
            elif data == "verify_channel":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    self.edit_message(chat_id, message_id, "✅ Verified!", self.create_main_menu_buttons())
                else:
                    self.edit_message(chat_id, message_id, "❌ Please join the channel first!", self.create_channel_buttons())
                return
            
            # Game Categories
            elif data == "game_zip":
                games = self.games_cache.get('zip', [])
                self.format_games_list(games, "ZIP", chat_id, message_id)
                return
            elif data == "game_7z":
                games = self.games_cache.get('7z', [])
                self.format_games_list(games, "7Z", chat_id, message_id)
                return
            elif data == "game_iso":
                games = self.games_cache.get('iso', [])
                self.format_games_list(games, "ISO", chat_id, message_id)
                return
            elif data == "game_apk":
                games = self.games_cache.get('apk', [])
                self.format_games_list(games, "APK", chat_id, message_id)
                return
            elif data == "game_psp":
                games = self.games_cache.get('cso', []) + self.games_cache.get('pbp', [])
                self.format_games_list(games, "PSP", chat_id, message_id)
                return
            elif data == "game_all":
                games = self.games_cache.get('all', [])
                self.format_games_list(games, "ALL", chat_id, message_id)
                return
            elif data == "rescan_games":
                self.update_games_cache()
                self.edit_message(chat_id, message_id, "✅ Cache updated!", self.create_game_files_buttons())
                return
            
            # Admin Actions
            elif data == "upload_stats" and self.is_admin(user_id):
                uploads = self.get_upload_stats()
                forwards = self.get_forward_stats()
                stats = self.get_channel_stats()
                text = f"""<b>Your Stats:</b>
- Total uploads: {uploads}
- Forwarded files: {forwards}
- Regular games: {stats['total_games']}
- Premium games: {stats['premium_games']}"""
                self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
                return
            elif data == "update_cache" and self.is_admin(user_id):
                self.update_games_cache()
                self.edit_message(chat_id, message_id, "✅ Cache updated!", self.create_admin_buttons())
                return
            elif data == "upload_options" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "📤 Send a game file", self.create_admin_buttons())
                return
            elif data == "remove_games" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "🗑️ Use /removegames", self.create_admin_buttons())
                return
            elif data == "clear_all_games" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM channel_games')
                cursor.execute('DELETE FROM premium_games')
                self.conn.commit()
                self.update_games_cache()
                self.edit_message(chat_id, message_id, "🗑️ All games cleared", self.create_admin_buttons())
                return
            elif data == "scan_bot_games" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "🔍 Scanning...", self.create_admin_buttons())
                return
            elif data == "backup_menu" and self.is_admin(user_id):
                info = self.github_backup.get_backup_info()
                text = f"💾 Backup System\n\nEnabled: {info.get('enabled', False)}\nAuto-backup on every game upload"
                self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
                return
            elif data == "redeploy_panel" and self.is_admin(user_id):
                text = f"""🔄 <b>Bot Redeploy System</b>

This system allows you to restart the bot without losing any data.

⚠️ <b>Important:</b>
• Database will be preserved
• All games and user data remain safe
• Bot will be unavailable for 10-30 seconds

Choose an option:"""
                keyboard = {"inline_keyboard": [[{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}], [{"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}], [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return
            elif data == "redeploy_soft" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "🔄 Soft redeploy initiated...", self.create_admin_buttons())
                def restart(): time.sleep(2); os._exit(0)
                Thread(target=restart, daemon=True).start()
                return
            elif data == "redeploy_force" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "🚀 Force redeploy initiated...", self.create_admin_buttons())
                def restart(): time.sleep(1); os._exit(0)
                Thread(target=restart, daemon=True).start()
                return
            elif data == "system_status" and self.is_admin(user_id):
                cursor = self.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM channel_games')
                game_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
                text = f"📊 System Status\n\nGames: {game_count}\nUsers: {user_count}\nMode: Webhook"
                self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
                return
            elif data == "user_redeploy":
                text = f"""<b>Admin Redeploy Access</b>
- Admin: {first_name}
- User ID: {user_id}

You have admin privileges and can redeploy the bot directly.

Choose redeploy type:"""
                keyboard = {"inline_keyboard": [[{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}], [{"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}], [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return
            
            # Mini Games
            elif data == "game_guess":
                self.start_number_guess_game(user_id, chat_id)
                return
            elif data == "game_random":
                self.generate_random_number(user_id, chat_id)
                return
            elif data == "game_spin":
                self.lucky_spin(user_id, chat_id)
                return
            elif data == "mini_stats":
                self.edit_message(chat_id, message_id, "📊 Play mini games to have fun!", self.create_mini_games_buttons())
                return
                
        except Exception as e:
            print(f"Callback error: {e}")
            traceback.print_exc()
    
    # ==================== WEBHOOK UPDATE PROCESSING ====================
    
    def process_webhook_update(self, update):
        try:
            if 'message' in update:
                self.process_message(update['message'])
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
        except Exception as e:
            print(f"Process webhook update error: {e}")
    
    def process_message(self, message):
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                username = message['from'].get('username', '')
                
                if text.startswith('/start'):
                    parts = text.split()
                    if len(parts) > 1 and parts[1].startswith('ref_'):
                        referral_value = parts[1].replace('ref_', '')
                        referrer_id = None
                        try:
                            referrer_id = int(referral_value)
                        except ValueError:
                            cursor = self.conn.cursor()
                            cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_value,))
                            result = cursor.fetchone()
                            if result:
                                referrer_id = result[0]
                        
                        if referrer_id and referrer_id != user_id:
                            self.register_user(user_id, username, first_name, referrer_id)
                        else:
                            self.register_user(user_id, username, first_name, None)
                    else:
                        self.register_user(user_id, username, first_name, None)
                    
                    code = self.generate_code()
                    self.save_verification_code(user_id, username, first_name, code)
                    welcome = f"""👋 Welcome {first_name}!

🔐 Your verification code: <code>{code}</code>

Please join {self.REQUIRED_CHANNEL} and enter this code to verify."""
                    
                    self.robust_send_message(chat_id, welcome, self.create_channel_buttons())
                    return True
                
                if text.isdigit() and len(text) == 6:
                    if self.verify_code(user_id, text):
                        if self.check_channel_membership(user_id):
                            self.mark_channel_joined(user_id)
                            welcome = f"✅ Verification Complete!\n\n👋 Welcome {first_name}!"
                            self.robust_send_message(chat_id, welcome, self.create_main_menu_buttons())
                        else:
                            self.robust_send_message(chat_id, "✅ Code verified! Now join our channel.", self.create_channel_buttons())
                    else:
                        self.robust_send_message(chat_id, "❌ Invalid code. Use /start to get a new code.")
                    return True
                
                if self.is_user_completed(user_id):
                    if text.startswith('/menu'):
                        self.robust_send_message(chat_id, "🏠 Main Menu", self.create_main_menu_buttons())
                        return True
                    
                    # Handle game request flow
                    if user_id in self.request_sessions:
                        session = self.request_sessions[user_id]
                        if session.get('stage') == 'waiting_game_name':
                            self.handle_game_request(user_id, chat_id, text)
                            return True
                        elif session.get('stage') == 'waiting_platform':
                            self.complete_game_request(user_id, chat_id, text)
                            return True
                    
                    # Handle broadcast content input
                    if user_id in self.broadcast_system.broadcast_sessions:
                        session = self.broadcast_system.broadcast_sessions[user_id]
                        
                        if session.get('stage') == 'waiting_text':
                            session['message'] = text
                            session['stage'] = 'preview'
                            self.broadcast_system.show_preview(user_id, chat_id)
                            return True
                        
                        elif session.get('stage') == 'waiting_caption':
                            if text.lower() == 'skip':
                                session['caption'] = ''
                            else:
                                session['caption'] = text
                            session['stage'] = 'preview'
                            self.broadcast_system.show_preview(user_id, chat_id)
                            return True
                    
                    # Handle broadcast buttons input
                    if user_id in self.broadcast_system.button_sessions:
                        self.broadcast_system.process_buttons_input(user_id, chat_id, text)
                        return True
                    
                    # Handle media reply text
                    if user_id in self.media_reply_sessions:
                        session = self.media_reply_sessions[user_id]
                        if session.get('stage') == 'waiting_text':
                            self.robust_send_message(session['user_id'], f"📨 Admin Reply to your game request '{session['game_name']}':\n\n{text}")
                            self.robust_send_message(chat_id, "✅ Reply sent to user!")
                            del self.media_reply_sessions[user_id]
                            return True
                    
                    # Handle search
                    if text.startswith('/search'):
                        search_term = text.replace('/search', '').strip()
                        if search_term:
                            self.search_games(chat_id, search_term, message_id)
                        return True
            
            # Handle photo uploads for broadcast
            elif 'photo' in message and user_id in self.broadcast_system.broadcast_sessions:
                session = self.broadcast_system.broadcast_sessions[user_id]
                if session.get('stage') == 'waiting_photo':
                    session['photo'] = message['photo'][-1]['file_id']
                    self.robust_send_message(chat_id, "📝 Now send the caption (or send 'skip'):")
                    session['stage'] = 'waiting_caption'
                    return True
            
            # Handle video uploads for broadcast
            elif 'video' in message and user_id in self.broadcast_system.broadcast_sessions:
                session = self.broadcast_system.broadcast_sessions[user_id]
                if session.get('stage') == 'waiting_video':
                    session['video'] = message['video']['file_id']
                    self.robust_send_message(chat_id, "📝 Now send the caption (or send 'skip'):")
                    session['stage'] = 'waiting_caption'
                    return True
            
            # Handle document uploads (game files) - SAVE TO DATABASE
            elif 'document' in message:
                if self.is_admin(user_id):
                    document = message['document']
                    file_name = document.get('file_name', 'Unknown')
                    file_id = document['file_id']
                    file_size = document.get('file_size', 0)
                    file_type = file_name.split('.')[-1] if '.' in file_name else 'unknown'
                    
                    print(f"📁 Game file uploaded: {file_name} by user {user_id}")
                    
                    # Save game to database
                    self.save_game_to_database(message, file_id, file_name, file_size, file_type, user_id)
                else:
                    self.robust_send_message(chat_id, "❌ Only admins can upload games.")
                return True
            
            return False
        except Exception as e:
            print(f"Process message error: {e}")
            return False
    
    def search_games(self, chat_id, search_term, message_id):
        """Search for games by name"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT file_name, file_type, file_size, file_id, message_id FROM channel_games WHERE file_name LIKE ?', (f'%{search_term}%',))
            results = cursor.fetchall()
            
            if not results:
                self.robust_send_message(chat_id, f"🔍 No games found matching '{search_term}'")
                return
            
            text = f"🔍 <b>Search Results for '{search_term}'</b>\n\n📊 Found: {len(results)} games\n\n"
            self.current_games_list = []
            keyboard_buttons = []
            
            for i, (file_name, file_type, file_size, file_id, msg_id) in enumerate(results[:10], 1):
                size = self.format_file_size(file_size)
                text += f"{i}. <b>{file_name[:40]}</b>\n   📦 {file_type.upper()} | 📏 {size}\n\n"
                self.current_games_list.append({'file_name': file_name, 'file_id': file_id, 'message_id': msg_id, 'file_type': file_type, 'file_size': file_size})
                keyboard_buttons.append([{"text": f"📥 Download {i}", "callback_data": f"download_game_{i}"}])
            
            keyboard_buttons.append([{"text": "🔙 Back to Games", "callback_data": "game_files"}])
            
            self.robust_send_message(chat_id, text, {"inline_keyboard": keyboard_buttons})
        except Exception as e:
            print(f"Search error: {e}")
            self.robust_send_message(chat_id, f"❌ Search error: {str(e)}")

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    print("🚀 Starting Enhanced Telegram Bot with Webhook Mode...")
    print("💾 GitHub Auto-Backup will trigger on every game upload")
    print("🌐 Webhook mode enabled for 24/7 operation")
    
    start_webhook_server()
    time.sleep(2)
    
    if BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            if response.json().get('ok'):
                print("✅ Bot token is valid")
                
                set_webhook()
                
                bot_instance = CrossPlatformBot(BOT_TOKEN)
                
                keep_alive = EnhancedKeepAliveService()
                keep_alive.start()
                
                while True:
                    time.sleep(60)
                    print(f"💚 Bot alive - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("❌ Invalid bot token")
        except Exception as e:
            print(f"❌ Connection error: {e}")
    else:
        print("❌ No BOT_TOKEN provided")
    
    print("🔴 Bot service ended")
