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
print("Enhanced Broadcast with Photos & VIDEOS")  # UPDATED
print("Individual Request Replies")
print("Game Removal System with Duplicate Detection")
print("Redeploy System for Admins and Users")
print("GitHub Database Backup & Restore System")
print("24/7 Operation with Persistent Data Recovery")
print("REFERRAL SYSTEM WITH GAME TOKENS")  # NEW
print("GAME TOKEN PAYMENTS FOR PREMIUM GAMES")  # NEW
print("XAPK & APKS FILE SUPPORT")  # NEW
print("AUTO GITHUB BACKUP ON EVERY GAME UPLOAD")  # NEW
print("WEBHOOK MODE FOR 24/7 OPERATION")  # NEW
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
    """Telegram webhook endpoint for 24/7 operation"""
    try:
        if not bot_instance:
            return jsonify({'ok': False, 'error': 'Bot not ready'}), 503
        
        update = request.get_json()
        if update:
            # Process in background thread for fast response
            thread = Thread(target=bot_instance.process_webhook_update, args=(update,))
            thread.start()
        
        return jsonify({'ok': True}), 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

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
    
    # Auto-detect public URL
    public_url = os.environ.get('CHOREO_URL') or os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('PUBLIC_URL')
    
    if not public_url:
        print("⚠️ No public URL found, webhook not set")
        print("⚠️ Please set CHOREO_URL environment variable")
        return False
    
    webhook_url = f"{public_url}/webhook"
    
    try:
        # Delete old webhook
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        requests.post(delete_url, timeout=10)
        
        # Set new webhook
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
            
            # Add referral columns to users table if not exist
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
            
            # Create referrals table
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
            
            # Create token transactions table
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
        """Generate unique referral code for user"""
        import hashlib
        code = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
        return code
    
    def register_referral(self, referrer_id, referred_id):
        """Register a new referral and award tokens"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Check if already referred
            cursor.execute('SELECT id FROM referrals WHERE referred_id = ?', (referred_id,))
            if cursor.fetchone():
                return False
            
            # Award 1 token to referrer
            cursor.execute('''
                INSERT INTO referrals (referrer_id, referred_id, tokens_earned) 
                VALUES (?, ?, ?)
            ''', (referrer_id, referred_id, 1))
            
            # Update referrer's token balance
            cursor.execute('''
                UPDATE users 
                SET game_tokens = game_tokens + 1, total_referrals = total_referrals + 1 
                WHERE user_id = ?
            ''', (referrer_id,))
            
            # Log transaction
            cursor.execute('''
                INSERT INTO token_transactions (user_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?)
            ''', (referrer_id, 1, 'referral', f'Referred user {referred_id}'))
            
            self.bot.conn.commit()
            print(f"✅ Referral registered: {referrer_id} -> {referred_id}")
            return True
            
        except Exception as e:
            print(f"❌ Referral registration error: {e}")
            return False
    
    def get_user_tokens(self, user_id):
        """Get user's game token balance"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT game_tokens FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def add_tokens(self, user_id, amount, description=""):
        """Add tokens to user's balance"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                UPDATE users SET game_tokens = game_tokens + ? WHERE user_id = ?
            ''', (amount, user_id))
            
            cursor.execute('''
                INSERT INTO token_transactions (user_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, 'admin_add', description))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Add tokens error: {e}")
            return False
    
    def deduct_tokens(self, user_id, amount, description=""):
        """Deduct tokens from user's balance"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Check sufficient balance
            current = self.get_user_tokens(user_id)
            if current < amount:
                return False
            
            cursor.execute('''
                UPDATE users SET game_tokens = game_tokens - ? WHERE user_id = ?
            ''', (amount, user_id))
            
            cursor.execute('''
                INSERT INTO token_transactions (user_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, -amount, 'purchase', description))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Deduct tokens error: {e}")
            return False
    
    def get_referral_stats(self, user_id):
        """Get user's referral statistics"""
        try:
            cursor = self.bot.conn.cursor()
            
            cursor.execute('SELECT total_referrals FROM users WHERE user_id = ?', (user_id,))
            total_refs = cursor.fetchone()
            total_refs = total_refs[0] if total_refs else 0
            
            cursor.execute('''
                SELECT COUNT(*) FROM referrals 
                WHERE referrer_id = ? AND created_at >= date('now', '-30 days')
            ''', (user_id,))
            monthly_refs = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT SUM(tokens_earned) FROM referrals WHERE referrer_id = ?
            ''', (user_id,))
            total_tokens = cursor.fetchone()[0] or 0
            
            return {
                'total_referrals': total_refs,
                'monthly_referrals': monthly_refs,
                'total_tokens_earned': total_tokens,
                'current_tokens': self.get_user_tokens(user_id)
            }
        except:
            return {'total_referrals': 0, 'monthly_referrals': 0, 'total_tokens_earned': 0, 'current_tokens': 0}
    
    def get_leaderboard(self, limit=10):
        """Get top referrers leaderboard"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT user_id, first_name, total_referrals, game_tokens 
                FROM users 
                WHERE total_referrals > 0 
                ORDER BY total_referrals DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except:
            return []
    
    def generate_referral_link(self, user_id):
        """Generate referral link for user"""
        cursor = self.bot.conn.cursor()
        cursor.execute('SELECT referral_code FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            bot_username = self.bot.token.split(':')[0] if ':' in self.bot.token else 'your_bot'
            return f"https://t.me/{bot_username}?start=ref_{result[0]}"
        return None

# ==================== ENHANCED BROADCAST SYSTEM WITH VIDEO ====================

class EnhancedBroadcastSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.broadcast_sessions = {}
        print("✅ Enhanced Broadcast System with Video initialized!")
    
    def create_broadcast_with_buttons(self, user_id, chat_id):
        """Show broadcast type selection menu"""
        self.broadcast_sessions[user_id] = {
            'stage': 'waiting_content',
            'type': None,
            'message': None,
            'photo': None,
            'video': None,
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
        """Handle text broadcast selection"""
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_text'
        self.broadcast_sessions[user_id]['type'] = 'text'
        self.bot.robust_send_message(chat_id, "📝 Send your broadcast message (HTML formatting supported):")
    
    def handle_broadcast_photo(self, user_id, chat_id):
        """Handle photo broadcast selection"""
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_photo'
        self.broadcast_sessions[user_id]['type'] = 'photo'
        self.bot.robust_send_message(chat_id, "🖼️ Send your photo (caption optional):")
    
    def handle_broadcast_video(self, user_id, chat_id):
        """Handle video broadcast selection"""
        if user_id not in self.broadcast_sessions:
            return
        self.broadcast_sessions[user_id]['stage'] = 'waiting_video'
        self.broadcast_sessions[user_id]['type'] = 'video'
        self.bot.robust_send_message(chat_id, "🎥 Send your video (caption optional):")
    
    def handle_caption(self, user_id, chat_id, caption):
        """Handle caption input"""
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        if caption.lower() != 'skip':
            session['message'] = caption
        session['stage'] = 'preview'
        self.show_preview(user_id, chat_id)
    
    def add_buttons_to_broadcast(self, user_id, chat_id):
        """Start button addition process"""
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        session['stage'] = 'waiting_buttons'
        
        help_text = """🔘 Add Inline Buttons

Format: Button Text|type|value

Types: url, callback, game

Examples:
Join Channel|url|https://t.me/pspgamers5
Get Games|callback|games

Send 'done' when finished."""
        
        self.bot.robust_send_message(chat_id, help_text)
    
    def parse_button(self, button_text):
        """Parse button text into button object"""
        parts = button_text.split('|')
        if len(parts) >= 3:
            text = parts[0].strip()
            button_type = parts[1].strip().lower()
            value = parts[2].strip()
            if button_type == 'url':
                return {"text": text, "url": value}
            elif button_type == 'callback':
                return {"text": text, "callback_data": value}
            elif button_type == 'game':
                return {"text": text, "callback_game": {}}
        return None
    
    def process_buttons_input(self, user_id, chat_id, text):
        """Process button addition input"""
        if user_id not in self.broadcast_sessions:
            return
        session = self.broadcast_sessions[user_id]
        
        if text.lower() == 'done':
            session['stage'] = 'preview'
            self.show_preview(user_id, chat_id)
            return
        
        button = self.parse_button(text)
        if button:
            session['buttons'].append(button)
            self.bot.robust_send_message(chat_id, f"✅ Button added: {button['text']}\nSend 'done' to finish")
        else:
            self.bot.robust_send_message(chat_id, "❌ Invalid format. Use: Text|type|value")
    
    def show_preview(self, user_id, chat_id):
        """Show broadcast preview"""
        session = self.broadcast_sessions[user_id]
        
        preview_text = "📋 Broadcast Preview\n\n"
        if session['type'] == 'text':
            preview_text += f"Message:\n{session['message']}\n\n"
        elif session['type'] == 'photo':
            preview_text += f"Photo Caption:\n{session.get('message', 'No caption')}\n\n"
        elif session['type'] == 'video':
            preview_text += f"Video Caption:\n{session.get('message', 'No caption')}\n\n"
        
        if session['buttons']:
            preview_text += f"Buttons: {len(session['buttons'])}\n"
        
        preview_text += "\nSend this broadcast?"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "✅ Send", "callback_data": "send_broadcast"}],
                [{"text": "✏️ Edit", "callback_data": "broadcast_panel"}],
                [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
            ]
        }
        
        if session['type'] == 'photo' and session.get('photo'):
            self.bot.robust_send_photo(chat_id, session['photo'], preview_text, keyboard)
        elif session['type'] == 'video' and session.get('video'):
            self.bot.robust_send_video(chat_id, session['video'], preview_text, keyboard)
        else:
            self.bot.robust_send_message(chat_id, preview_text, keyboard)
    
    def execute_broadcast(self, user_id, chat_id):
        """Execute the broadcast to all users"""
        if user_id not in self.broadcast_sessions:
            return
        
        session = self.broadcast_sessions[user_id]
        
        cursor = self.bot.conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
        users = cursor.fetchall()
        
        if not users:
            self.bot.robust_send_message(chat_id, "❌ No verified users found.")
            return
        
        total_users = len(users)
        success_count = 0
        failed_count = 0
        
        # Create reply markup if buttons exist
        reply_markup = None
        if session['buttons']:
            # Arrange buttons in rows of 2
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
                    success = self.bot.robust_send_photo(
                        user_id_target, 
                        session['photo'], 
                        session.get('message', ''), 
                        json.loads(reply_markup) if reply_markup else None
                    )
                elif session['type'] == 'video':
                    success = self.bot.robust_send_video(
                        user_id_target, 
                        session['video'], 
                        session.get('message', ''), 
                        json.loads(reply_markup) if reply_markup else None
                    )
                else:
                    success = False
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    
                time.sleep(0.05)  # Rate limiting
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Broadcast error to {user_id_target}: {e}")
        
        elapsed = time.time() - start_time
        
        # Save broadcast history
        cursor.execute('''
            INSERT INTO broadcast_history 
            (admin_id, message_text, photo_file_id, video_file_id, inline_buttons, total_sent, total_failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            session.get('message'), 
            session.get('photo'), 
            session.get('video'), 
            json.dumps(session['buttons']) if session['buttons'] else None, 
            success_count, 
            failed_count
        ))
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

# ==================== TELEGRAM STARS SYSTEM (UPDATED WITH TOKENS) ====================

class TelegramStarsSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_stars_database()
        print("✅ Telegram Stars system initialized!")
        
    def setup_stars_database(self):
        """Setup stars payments database"""
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
    
    def create_stars_invoice(self, user_id, chat_id, stars_amount, description="Donation"):
        """Create Telegram Stars payment invoice"""
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
                "start_parameter": "stars_donation"
            }
            
            print(f"⭐ Creating Stars invoice for {stars_amount} stars (${usd_amount:.2f})")
            
            url = self.bot.base_url + "sendInvoice"
            response = requests.post(url, data=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
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
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Error creating Stars invoice: {error_msg}")
                return False
            
        except Exception as e:
            print(f"❌ Error creating Stars invoice: {e}")
            traceback.print_exc()
            return False
    
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
                "start_parameter": f"premium_game_{game_id}"
            }
            
            print(f"⭐ Creating premium game invoice: {game_name} for {stars_amount} stars")
            
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
                print(f"✅ Premium game invoice created: {game_name} for user {user_id}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Error creating premium game invoice: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating premium game invoice: {e}")
            traceback.print_exc()
            return False
    
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
            cursor.execute('''
                UPDATE premium_purchases 
                SET status = 'completed' 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            cursor.execute('''
                UPDATE stars_balance 
                SET total_stars_earned = total_stars_earned + (
                    SELECT stars_paid FROM premium_purchases WHERE transaction_id = ?
                ),
                total_usd_earned = total_usd_earned + (
                    SELECT stars_paid * 0.01 FROM premium_purchases WHERE transaction_id = ?
                ),
                available_stars = available_stars + (
                    SELECT stars_paid FROM premium_purchases WHERE transaction_id = ?
                ),
                available_usd = available_usd + (
                    SELECT stars_paid * 0.01 FROM premium_purchases WHERE transaction_id = ?
                ),
                last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (transaction_id, transaction_id, transaction_id, transaction_id))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error completing premium purchase: {e}")
            return False

# ==================== GAME REQUEST SYSTEM WITH INDIVIDUAL REPLIES ====================

class GameRequestSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_game_requests_database()
        print("✅ Game request system initialized!")
        
    def setup_game_requests_database(self):
        """Setup game requests database"""
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
        """Submit a new game request"""
        try:
            user_info = self.bot.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Anonymous')
            
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO game_requests 
                (user_id, user_name, game_name, platform, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user_name, game_name, platform, 'pending'))
            
            self.bot.conn.commit()
            request_id = cursor.lastrowid
            
            # Notify all admins
            self.notify_admins_about_request(user_id, user_name, game_name, platform, request_id)
            
            return request_id
        except Exception as e:
            print(f"❌ Error submitting game request: {e}")
            return False
    
    def get_pending_requests(self, limit=10):
        """Get pending game requests"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, user_id, user_name, game_name, platform, created_at 
                FROM game_requests 
                WHERE status = 'pending' 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting pending requests: {e}")
            return []
    
    def get_all_requests(self, limit=20):
        """Get all game requests"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, user_id, user_name, game_name, platform, status, created_at 
                FROM game_requests 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting all requests: {e}")
            return []
    
    def get_user_requests(self, user_id, limit=5):
        """Get game requests by a specific user"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, game_name, platform, status, created_at 
                FROM game_requests 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting user requests: {e}")
            return []
    
    def get_request_by_id(self, request_id):
        """Get specific game request by ID"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, user_id, user_name, game_name, platform, status, admin_notes, created_at
                FROM game_requests 
                WHERE id = ?
            ''', (request_id,))
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
        except Exception as e:
            print(f"❌ Error getting request by ID: {e}")
            return None
    
    def update_request_status(self, request_id, status, admin_notes=""):
        """Update game request status"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                UPDATE game_requests 
                SET status = ?, admin_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, admin_notes, request_id))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error updating request status: {e}")
            return False
    
    def add_request_reply(self, request_id, admin_id, reply_text, photo_file_id=None, video_file_id=None, document_file_id=None):
        """Add a reply to a game request (supports text, photo, video, document)"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO game_request_replies 
                (request_id, admin_id, reply_text, photo_file_id, video_file_id, document_file_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, admin_id, reply_text, photo_file_id, video_file_id, document_file_id))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error adding request reply: {e}")
            return False
    
    def get_request_replies(self, request_id):
        """Get all replies for a game request"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT admin_id, reply_text, photo_file_id, video_file_id, document_file_id, reply_date
                FROM game_request_replies 
                WHERE request_id = ?
                ORDER BY reply_date ASC
            ''', (request_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting request replies: {e}")
            return []
    
    def notify_admins_about_request(self, user_id, user_name, game_name, platform, request_id):
        """Notify all admins about new game request"""
        notification_text = f"""🎮 <b>New Game Request</b>

👤 User: {user_name} (ID: {user_id})
🎯 Game: {game_name}
📱 Platform: {platform}
🆔 Request ID: {request_id}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 Use the buttons below to reply."""

        for admin_id in self.bot.ADMIN_IDS:
            try:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📝 Reply with Text", "callback_data": f"reply_request_{request_id}"},
                            {"text": "📎 Reply with Media", "callback_data": f"reply_media_{request_id}"}
                        ],
                        [
                            {"text": "✅ Mark Completed", "callback_data": f"complete_request_{request_id}"},
                            {"text": "❌ Reject", "callback_data": f"reject_request_{request_id}"}
                        ]
                    ]
                }
                self.bot.robust_send_message(admin_id, notification_text, keyboard)
            except Exception as e:
                print(f"❌ Failed to notify admin {admin_id}: {e}")
    
    def send_reply_to_user(self, user_id, request_data, reply_text, media_type=None, media_file_id=None):
        """Send reply to user with optional media"""
        try:
            if media_type == 'photo' and media_file_id:
                caption = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request_data['game_name']}</b>
👤 Admin Response

💬 <b>Message:</b>
{reply_text}

Thank you for using our service! 🙏"""
                
                return self.bot.robust_send_photo(user_id, media_file_id, caption)
                
            elif media_type == 'video' and media_file_id:
                caption = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request_data['game_name']}</b>
👤 Admin Response

💬 <b>Message:</b>
{reply_text}

Thank you for using our service! 🙏"""
                
                return self.bot.robust_send_video(user_id, media_file_id, caption)
                
            elif media_type == 'document' and media_file_id:
                caption = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request_data['game_name']}</b>
👤 Admin Response

💬 <b>Message:</b>
{reply_text}

Thank you for using our service! 🙏"""
                
                url = self.bot.base_url + "sendDocument"
                data = {
                    "chat_id": user_id,
                    "document": media_file_id,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, data=data, timeout=30)
                return response.json().get('ok', False)
                
            else:
                user_notification = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request_data['game_name']}</b>
👤 Admin: {self.bot.get_user_info(user_id)['first_name']}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 <b>Message:</b>
{reply_text}

Thank you for using our service! 🙏"""
                
                return self.bot.robust_send_message(user_id, user_notification)
                
        except Exception as e:
            print(f"❌ Error sending reply to user: {e}")
            return False

# ==================== PREMIUM GAMES SYSTEM (UPDATED WITH TOKENS) ====================

class PremiumGamesSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_premium_games_database()
        print("✅ Premium games system initialized!")
        
    def setup_premium_games_database(self):
        """Setup premium games database"""
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
                    status TEXT DEFAULT 'completed',
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (game_id) REFERENCES premium_games (id)
                )
            ''')
            
            self.bot.conn.commit()
            print("✅ Premium games database setup complete!")
            
        except Exception as e:
            print(f"❌ Premium games database setup error: {e}")
    
    def add_premium_game(self, game_info):
        """Add a premium game to database"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_games 
                (message_id, file_name, file_type, file_size, upload_date, category, 
                 added_by, is_uploaded, is_forwarded, file_id, bot_message_id, stars_price, tokens_price, description, is_premium)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                game_info['bot_message_id'],
                game_info.get('stars_price', 0),
                game_info.get('tokens_price', 10),
                game_info.get('description', ''),
                game_info.get('is_premium', 1)
            ))
            
            self.bot.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error adding premium game: {e}")
            return False
    
    def get_premium_games(self, limit=50):
        """Get all premium games"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, file_name, file_type, file_size, stars_price, tokens_price, description, upload_date, file_id, bot_message_id, is_uploaded
                FROM premium_games 
                WHERE is_premium = 1
                ORDER BY created_at DESC 
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
                SELECT id, file_name, file_type, file_size, stars_price, tokens_price, description, 
                       file_id, bot_message_id, is_uploaded, message_id
                FROM premium_games 
                WHERE id = ?
            ''', (game_id,))
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
    
    def record_purchase(self, user_id, game_id, payment_method, stars_paid=0, tokens_paid=0, transaction_id=""):
        """Record a premium game purchase"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_purchases 
                (user_id, game_id, payment_method, stars_paid, tokens_paid, transaction_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, game_id, payment_method, stars_paid, tokens_paid, transaction_id, 'completed'))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error recording purchase: {e}")
            return False

# ==================== GITHUB BACKUP SYSTEM ====================

class GitHubBackupSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_github_config()
        print("✅ GitHub Backup system initialized!")
    
    def setup_github_config(self):
        """Setup GitHub configuration from environment variables"""
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo_owner = os.environ.get('GITHUB_REPO_OWNER', 'your-username')
        self.repo_name = os.environ.get('GITHUB_REPO_NAME', 'your-repo')
        self.backup_branch = os.environ.get('GITHUB_BACKUP_BRANCH', 'main')
        self.backup_path = os.environ.get('GITHUB_BACKUP_PATH', 'backups/telegram_bot.db')
        
        self.is_enabled = bool(self.github_token and self.repo_owner and self.repo_name)
        
        if self.is_enabled:
            print(f"✅ GitHub Backup: Enabled for {self.repo_owner}/{self.repo_name}")
            print(f"✅ Auto-backup will trigger on every game upload")
        else:
            print("⚠️ GitHub Backup: Disabled - Set environment variables")
    
    def create_db_backup(self):
        """Create a backup of the current database"""
        try:
            db_path = self.bot.get_db_path()
            backup_path = db_path + '.backup'
            
            import shutil
            shutil.copy2(db_path, backup_path)
            
            return backup_path
        except Exception as e:
            print(f"❌ Database backup error: {e}")
            return None
    
    def backup_database_to_github(self, commit_message="Auto backup: Database update"):
        """Backup database to GitHub"""
        if not self.is_enabled:
            return False
        
        try:
            backup_file = self.create_db_backup()
            if not backup_file:
                return False
            
            with open(backup_file, 'rb') as f:
                db_content = f.read()
            
            db_b64 = base64.b64encode(db_content).decode('utf-8')
            file_sha = self.get_file_sha()
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {'Authorization': f'token {self.github_token}', 'Accept': 'application/vnd.github.v3+json'}
            
            data = {'message': commit_message, 'content': db_b64, 'branch': self.backup_branch}
            if file_sha:
                data['sha'] = file_sha
            
            response = requests.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Database backed up to GitHub")
                try:
                    os.remove(backup_file)
                except:
                    pass
                return True
            else:
                print(f"❌ GitHub backup failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub backup error: {e}")
            return False
    
    def get_file_sha(self):
        """Get the SHA of the existing backup file on GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {'Authorization': f'token {self.github_token}', 'Accept': 'application/vnd.github.v3+json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()['sha']
            return None
        except:
            return None
    
    def restore_database_from_github(self):
        """Restore database from GitHub backup"""
        if not self.is_enabled:
            return False
        
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {'Authorization': f'token {self.github_token}', 'Accept': 'application/vnd.github.v3+json'}
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                return False
            
            file_data = response.json()
            db_content = base64.b64decode(file_data['content'])
            
            db_path = self.bot.get_db_path()
            with open(db_path, 'wb') as f:
                f.write(db_content)
            
            print(f"✅ Database restored from GitHub backup")
            return True
            
        except Exception as e:
            print(f"❌ GitHub restore error: {e}")
            return False
    
    def get_backup_info(self):
        """Get information about the latest backup"""
        if not self.is_enabled:
            return {"enabled": False}
        
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits?path={self.backup_path}&per_page=1"
            headers = {'Authorization': f'token {self.github_token}', 'Accept': 'application/vnd.github.v3+json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest_commit = commits[0]
                    return {
                        "enabled": True,
                        "last_backup": latest_commit['commit']['author']['date'],
                        "message": latest_commit['commit']['message'],
                        "url": latest_commit['html_url']
                    }
            return {"enabled": True, "last_backup": "Never"}
        except:
            return {"enabled": True, "error": "Could not fetch info"}

# ==================== REDEPLOY SYSTEM ====================

class RedeploySystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.redeploy_requests = {}
        print("✅ Redeploy system initialized!")
    
    def show_redeploy_menu(self, user_id, chat_id, message_id):
        """Show redeploy menu"""
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
        """Initiate a redeploy"""
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
        """Show current system status"""
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
        """Format uptime in human readable format"""
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
        
        # ===== IMPORTANT: Setup database FIRST =====
        self.setup_database()
        self.verify_database_schema()
        
        # ===== THEN initialize all systems that need database =====
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
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, referral_code, referred_by, game_tokens) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, referral_code, referred_by or 0, 0))
            self.conn.commit()
            
            if referred_by and referred_by != user_id:
                self.referral_system.register_referral(referred_by, user_id)
                self.robust_send_message(referred_by, 
                    f"🎉 New Referral!\n@{username or first_name} joined!\nYou earned 1 Game Token 💎\nTotal tokens: {self.referral_system.get_user_tokens(referred_by)}")
            
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
            cursor.execute('SELECT file_name, file_type, file_size, upload_date, category, is_uploaded FROM channel_games')
            games = cursor.fetchall()
            self.games_cache = {'zip': [], '7z': [], 'iso': [], 'apk': [], 'xapk': [], 'apks': [], 'cso': [], 'pbp': [], 'all': []}
            for game in games:
                file_name, file_type, file_size, upload_date, category, is_uploaded = game
                game_info = {'file_name': file_name, 'file_type': file_type, 'file_size': file_size, 
                             'upload_date': upload_date, 'category': category, 'is_uploaded': is_uploaded}
                file_type_lower = file_type.lower()
                if file_type_lower in self.games_cache:
                    self.games_cache[file_type_lower].append(game_info)
                self.games_cache['all'].append(game_info)
            print(f"🔄 Cache updated: {len(self.games_cache['all'])} games (APK: {len(self.games_cache.get('apk', []))}, XAPK: {len(self.games_cache.get('xapk', []))}, APKS: {len(self.games_cache.get('apks', []))})")
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
        else:
            return 'Other Games'
    
    def create_progress_bar(self, percentage, length=10):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    # ==================== TRIGGER AUTO BACKUP ON GAME UPLOAD ====================
    
    def trigger_auto_backup(self, file_name=""):
        """Trigger GitHub backup when a game is uploaded"""
        if self.github_backup.is_enabled:
            thread = Thread(target=self.github_backup.backup_database_to_github, args=(f"Auto-backup: Game '{file_name}' uploaded",))
            thread.start()
            print(f"💾 Auto-backup triggered for: {file_name}")
    
    # ==================== MENU BUTTONS ====================
    
    def create_main_menu_buttons(self):
        stats = self.get_channel_stats()
        keyboard = [
            [
                {"text": "📊 Profile", "callback_data": "profile"},
                {"text": "🕒 Time", "callback_data": "time"}
            ],
            [
                {"text": "📢 Channel", "callback_data": "channel_info"},
                {"text": f"🎮 Games ({stats['total_games'] + stats['premium_games']})", "callback_data": "games"}
            ],
            [
                {"text": "💰 Premium Games", "callback_data": "premium_games"},
                {"text": "🔍 Search Games", "callback_data": "search_games"}
            ],
            [
                {"text": "📝 Request Game", "callback_data": "request_game"},
                {"text": "⭐ Donate Stars", "callback_data": "stars_menu"}
            ],
            [
                {"text": "👥 Referral Program", "callback_data": "referral_menu"},
                {"text": "💎 My Tokens", "callback_data": "my_tokens"}
            ]
        ]
        
        if self.is_admin:
            keyboard.append([
                {"text": "🔧 Admin Panel", "callback_data": "admin_panel"}
            ])
        
        keyboard.append([
            {"text": "🔄 Redeploy Bot", "callback_data": "user_redeploy"}
        ])
        
        return {"inline_keyboard": keyboard}
    
    def create_admin_buttons(self):
        return {
            "inline_keyboard": [
                [
                    {"text": "📤 Upload Stats", "callback_data": "upload_stats"},
                    {"text": "🔄 Update Cache", "callback_data": "update_cache"}
                ],
                [
                    {"text": "📤 Upload Games", "callback_data": "upload_options"},
                    {"text": "🗑️ Remove Games", "callback_data": "remove_games"}
                ],
                [
                    {"text": "🗑️ Clear All Games", "callback_data": "clear_all_games"},
                    {"text": "🔍 Scan Bot Games", "callback_data": "scan_bot_games"}
                ],
                [
                    {"text": "📢 Broadcast", "callback_data": "broadcast_panel"},
                    {"text": "🎮 Game Requests", "callback_data": "admin_requests_panel"}
                ],
                [
                    {"text": "⭐ Stars Stats", "callback_data": "stars_stats"},
                    {"text": "💾 Backup System", "callback_data": "backup_menu"}
                ],
                [
                    {"text": "🔄 Redeploy System", "callback_data": "redeploy_panel"},
                    {"text": "📊 System Status", "callback_data": "system_status"}
                ],
                [
                    {"text": "👥 Referral Stats", "callback_data": "referral_stats"},
                    {"text": "💎 Token Management", "callback_data": "token_management"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
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
            [{"text": f"📦 ZIP ({len(self.games_cache.get('zip', []))})", "callback_data": "game_zip"}, 
             {"text": f"🗜️ 7Z ({len(self.games_cache.get('7z', []))})", "callback_data": "game_7z"}],
            [{"text": f"💿 ISO ({len(self.games_cache.get('iso', []))})", "callback_data": "game_iso"}, 
             {"text": f"📱 APK ({len(self.games_cache.get('apk', []))})", "callback_data": "game_apk"}],
            [{"text": f"🎮 PSP ({len(self.games_cache.get('cso', [])) + len(self.games_cache.get('pbp', []))})", "callback_data": "game_psp"}, 
             {"text": f"📋 All ({stats['total_games']})", "callback_data": "game_all"}],
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
    
    def create_broadcast_panel_buttons(self):
        return {"inline_keyboard": [
            [{"text": "📢 New Broadcast", "callback_data": "start_broadcast"}, {"text": "📊 Statistics", "callback_data": "broadcast_stats"}],
            [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
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
• This Month: {stats['monthly_referrals']}
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
        
        text += "\n💡 <i>1 Game Token = 1 Star value for premium games</i>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "💰 Browse Premium Games", "callback_data": "premium_games"},
                 {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
                [{"text": "📤 Share Link", "switch_inline_query": f"Join using my referral link: {referral_link}"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def show_token_balance(self, user_id, chat_id, message_id):
        tokens = self.referral_system.get_user_tokens(user_id)
        referral_link = self.referral_system.generate_referral_link(user_id)
        
        text = f"""💎 <b>Game Tokens Balance</b>

💰 Current Balance: <b>{tokens} Tokens</b>

💡 <b>What can you do with tokens?</b>
• Buy premium games (10 tokens each)
• Exchange for premium content
• Access exclusive features

🎮 <b>Value:</b> 1 Token = 1 Star

✨ <b>Get more tokens:</b>
• Invite friends (1 token each)
• Complete achievements
• Daily rewards

<a href="https://t.me/share/url?url={referral_link}">📤 Invite Friends Now!</a>"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎮 Browse Premium Games", "callback_data": "premium_games"},
                 {"text": "👥 Referral Program", "callback_data": "referral_menu"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
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
            
            self.robust_send_message(chat_id, 
                f"✅ <b>Purchase Successful!</b>\n\n"
                f"🎮 {game['file_name']}\n"
                f"💎 Paid: {game['tokens_price']} Tokens\n"
                f"💰 Remaining: {self.referral_system.get_user_tokens(user_id)} Tokens"
            )
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📥 Download Now", "callback_data": f"download_premium_{game_id}"}],
                    [{"text": "🎮 More Games", "callback_data": "premium_games"}]
                ]
            }
            self.robust_send_message(chat_id, "🎮 Your game is ready!", keyboard)
        else:
            self.robust_send_message(chat_id, 
                f"❌ <b>Insufficient Tokens!</b>\n\n"
                f"Need: {game['tokens_price']} Tokens\n"
                f"Your balance: {self.referral_system.get_user_tokens(user_id)} Tokens"
            )
    
    def purchase_with_stars(self, user_id, chat_id, game_id):
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            self.robust_send_message(chat_id, "❌ Game not found")
            return
        
        if self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id, f"✅ You already own {game['file_name']}!")
            return
        
        self.stars_system.create_premium_game_invoice(user_id, chat_id, game['stars_price'], game['file_name'], game_id)
    
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
            self.robust_send_message(chat_id, f"✅ Enjoy your game: <b>{game['file_name']}</b>!")
        else:
            self.robust_send_message(chat_id, "❌ Failed to send game. Please contact admin.")
    
    # ==================== GAME REQUESTS ====================
    
    def start_game_request(self, user_id, chat_id):
        self.request_sessions[user_id] = {'stage': 'waiting_game_name'}
        self.robust_send_message(chat_id, "🎮 <b>Game Request</b>\n\nPlease tell us the name of the game you'd like to request:")
    
    def handle_game_request(self, user_id, chat_id, game_name):
        self.request_sessions[user_id] = {'stage': 'waiting_platform', 'game_name': game_name}
        self.robust_send_message(chat_id, f"🎮 <b>Game Request</b>\n\nGame: <b>{game_name}</b>\n\nNow, please specify the platform:")
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
            self.robust_send_message(chat_id, f"✅ <b>Game Request Submitted!</b>\n\n🎮 Game: {game_name}\n📱 Platform: {platform}\n🆔 Request ID: {request_id}")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Sorry, there was an error submitting your request.")
            return False
    
    def start_request_reply_with_media(self, user_id, chat_id, request_id):
        if not self.is_admin(user_id):
            return False
        
        request = self.game_request_system.get_request_by_id(request_id)
        if not request:
            self.robust_send_message(chat_id, "❌ Request not found")
            return False
        
        self.media_reply_sessions[user_id] = {
            'stage': 'waiting_media_type',
            'request_id': request_id,
            'user_id': request['user_id'],
            'game_name': request['game_name']
        }
        
        reply_text = f"""📝 <b>Reply to Game Request #{request_id}</b>

🎮 Game: <b>{request['game_name']}</b>
👤 User ID: {request['user_id']}

Choose reply type:"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📝 Text Reply", "callback_data": f"reply_text_{request_id}"}],
                [{"text": "🖼️ Reply with Photo", "callback_data": f"reply_photo_{request_id}"}],
                [{"text": "🎥 Reply with Video", "callback_data": f"reply_video_{request_id}"}],
                [{"text": "📎 Reply with Document", "callback_data": f"reply_document_{request_id}"}],
                [{"text": "❌ Cancel", "callback_data": "cancel_reply"}]
            ]
        }
        
        self.robust_send_message(chat_id, reply_text, keyboard)
        return True
    
    def show_admin_requests_panel(self, user_id, chat_id, message_id):
        if not self.is_admin(user_id):
            self.answer_callback_query(message_id, "❌ Access denied. Admin only.", True)
            return
        
        pending_requests = self.game_request_system.get_pending_requests(10)
        
        text = f"""👑 <b>Game Request Management</b>

📊 Pending: {len(pending_requests)}

📝 <b>Pending Requests:</b>"""
        
        for req in pending_requests[:5]:
            req_id, uid, uname, gname, platform, created = req
            date = datetime.fromisoformat(created).strftime('%m/%d %H:%M')
            text += f"\n\n🎮 <b>{gname}</b>\n👤 {uname} | 📱 {platform}\n🆔 #{req_id} | 📅 {date}"
        
        if not pending_requests:
            text += "\n\nNo pending requests."
        
        keyboard = []
        for req in pending_requests[:10]:
            req_id, uid, uname, gname, platform, created = req
            keyboard.append([{"text": f"📝 #{req_id}: {gname[:20]}", "callback_data": f"reply_media_{req_id}"}])
        
        keyboard.append([{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}])
        
        self.edit_message(chat_id, message_id, text, {"inline_keyboard": keyboard})
    
    # ==================== BROADCAST ====================
    
    def start_broadcast(self, user_id, chat_id):
        if not self.is_admin(user_id):
            return
        self.broadcast_system.create_broadcast_with_buttons(user_id, chat_id)
    
    def cancel_broadcast(self, user_id, chat_id, message_id):
        if user_id in self.broadcast_system.broadcast_sessions:
            del self.broadcast_system.broadcast_sessions[user_id]
        self.edit_message(chat_id, message_id, "❌ Broadcast cancelled.", self.create_admin_buttons())
    
    def show_broadcast_stats(self, user_id, chat_id, message_id):
        self.edit_message(chat_id, message_id, "📊 Broadcast stats coming soon", self.create_admin_buttons())
    
    # ==================== STARS ====================
    
    def show_stars_menu(self, user_id, chat_id, message_id=None):
        balance = self.stars_system.get_balance()
        
        text = f"""⭐ <b>Support with Telegram Stars</b>

💫 <b>Star Packages:</b>
• 50 Stars ($0.50)
• 100 Stars ($1.00)
• 500 Stars ($5.00)
• 1000 Stars ($10.00)

📊 <b>Stars Stats:</b>
• Total Received: {balance['total_stars_earned']} ⭐
• Total USD: ${balance['total_usd_earned']:.2f}

💡 <b>1 Star = 1 Game Token value</b>"""
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⭐ 50 Stars", "callback_data": "donate_50"}, {"text": "⭐ 100 Stars", "callback_data": "donate_100"}],
                [{"text": "⭐ 500 Stars", "callback_data": "donate_500"}, {"text": "⭐ 1000 Stars", "callback_data": "donate_1000"}],
                [{"text": "💫 Custom Amount", "callback_data": "stars_custom"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        if message_id:
            self.edit_message(chat_id, message_id, text, keyboard)
        else:
            self.robust_send_message(chat_id, text, keyboard)
    
    def process_stars_donation(self, user_id, chat_id, stars_amount):
        self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount, "Bot Stars Donation")
    
    def show_stars_stats(self, user_id, chat_id, message_id):
        balance = self.stars_system.get_balance()
        self.edit_message(chat_id, message_id, f"⭐ Stars: {balance['total_stars_earned']}", self.create_admin_buttons())
    
    # ==================== MINI GAMES ====================
    
    def start_number_guess_game(self, user_id, chat_id):
        target = random.randint(1, 10)
        self.guess_games[user_id] = {'target': target, 'attempts': 0, 'max_attempts': 5}
        self.robust_send_message(chat_id, f"🎯 Guess a number between 1-10!")
    
    def generate_random_number(self, user_id, chat_id):
        number = random.randint(1, 100)
        self.robust_send_message(chat_id, f"🎲 Random number: {number}")
    
    def lucky_spin(self, user_id, chat_id):
        symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
        spins = [random.choice(symbols) for _ in range(3)]
        self.robust_send_message(chat_id, f"🎰 {spins[0]} | {spins[1]} | {spins[2]}")
    
    def big_spin(self, user_id, chat_id):
        self.lucky_spin(user_id, chat_id)
    
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
                self.cancel_broadcast(user_id, chat_id, message_id)
                return
            elif data == "start_broadcast":
                self.start_broadcast(user_id, chat_id)
                return
            elif data == "broadcast_stats":
                self.show_broadcast_stats(user_id, chat_id, message_id)
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
            elif data.startswith("reply_text_"):
                request_id = int(data.replace("reply_text_", ""))
                if user_id in self.media_reply_sessions:
                    session = self.media_reply_sessions[user_id]
                    session['stage'] = 'waiting_text'
                    self.robust_send_message(chat_id, "📝 Type your text reply:")
                return
            elif data.startswith("reply_photo_"):
                request_id = int(data.replace("reply_photo_", ""))
                if user_id in self.media_reply_sessions:
                    session = self.media_reply_sessions[user_id]
                    session['stage'] = 'waiting_photo'
                    self.robust_send_message(chat_id, "🖼️ Send the photo for your reply:")
                return
            elif data.startswith("reply_video_"):
                request_id = int(data.replace("reply_video_", ""))
                if user_id in self.media_reply_sessions:
                    session = self.media_reply_sessions[user_id]
                    session['stage'] = 'waiting_video'
                    self.robust_send_message(chat_id, "🎥 Send the video for your reply:")
                return
            elif data.startswith("reply_document_"):
                request_id = int(data.replace("reply_document_", ""))
                if user_id in self.media_reply_sessions:
                    session = self.media_reply_sessions[user_id]
                    session['stage'] = 'waiting_document'
                    self.robust_send_message(chat_id, "📎 Send the document for your reply:")
                return
            elif data.startswith("complete_request_"):
                request_id = int(data.replace("complete_request_", ""))
                self.game_request_system.update_request_status(request_id, 'completed', "Request completed by admin")
                self.answer_callback_query(callback_query['id'], "✅ Request marked as completed!", True)
                return
            elif data.startswith("reject_request_"):
                request_id = int(data.replace("reject_request_", ""))
                self.game_request_system.update_request_status(request_id, 'rejected', "Request rejected by admin")
                self.answer_callback_query(callback_query['id'], "❌ Request rejected.", True)
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
            elif data == "stars_custom":
                self.stars_sessions[user_id] = {}
                self.robust_send_message(chat_id, "💫 Enter Stars amount:")
                return
            elif data == "stars_stats":
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
                self.edit_message(chat_id, message_id, f"👤 {first_name}\n💎 Tokens: {tokens}", self.create_main_menu_buttons())
                return
            elif data == "time":
                self.edit_message(chat_id, message_id, f"🕒 {datetime.now()}", self.create_main_menu_buttons())
                return
            elif data == "channel_info":
                self.edit_message(chat_id, message_id, f"📢 {self.REQUIRED_CHANNEL}", self.create_main_menu_buttons())
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
                text = self.format_games_list(games, "ZIP")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "game_7z":
                games = self.games_cache.get('7z', [])
                text = self.format_games_list(games, "7Z")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "game_iso":
                games = self.games_cache.get('iso', [])
                text = self.format_games_list(games, "ISO")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "game_apk":
                games = self.games_cache.get('apk', [])
                text = self.format_games_list(games, "APK")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "game_psp":
                games = self.games_cache.get('cso', []) + self.games_cache.get('pbp', [])
                text = self.format_games_list(games, "PSP")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "game_all":
                games = self.games_cache.get('all', [])
                text = self.format_games_list(games, "ALL")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                return
            elif data == "rescan_games":
                self.update_games_cache()
                self.edit_message(chat_id, message_id, "✅ Cache updated!", self.create_game_files_buttons())
                return
            
            # Admin Actions
            elif data == "upload_stats" and self.is_admin(user_id):
                self.edit_message(chat_id, message_id, "📊 Upload stats", self.create_admin_buttons())
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
                text = f"💾 Backup System\n\nEnabled: {info.get('enabled', False)}\nLast backup: {info.get('last_backup', 'Never')}\nAuto-backup on every game upload"
                self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
                return
            elif data == "redeploy_panel" and self.is_admin(user_id):
                self.redeploy_system.show_redeploy_menu(user_id, chat_id, message_id)
                return
            elif data == "redeploy_soft" and self.is_admin(user_id):
                self.redeploy_system.initiate_redeploy(user_id, chat_id, "soft")
                return
            elif data == "redeploy_force" and self.is_admin(user_id):
                self.redeploy_system.initiate_redeploy(user_id, chat_id, "force")
                return
            elif data == "system_status" and self.is_admin(user_id):
                self.redeploy_system.show_system_status(user_id, chat_id, message_id)
                return
            elif data == "user_redeploy":
                self.edit_message(chat_id, message_id, "🔄 Redeploy requested", self.create_main_menu_buttons())
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
            elif data == "big_spin":
                self.big_spin(user_id, chat_id)
                return
            elif data == "mini_stats":
                self.show_mini_games_stats(user_id, chat_id, message_id)
                return
            
        except Exception as e:
            print(f"Callback error: {e}")
            traceback.print_exc()
    
    def format_games_list(self, games, category):
        if not games:
            return f"❌ No {category} games found."
        text = f"📁 <b>{category} GAMES</b>\n\n📊 Found: {len(games)} files\n\n"
        for i, game in enumerate(games[:8], 1):
            size = self.format_file_size(game['file_size'])
            text += f"{i}. <code>{game['file_name']}</code>\n   📦 {game['file_type']} | 📏 {size}\n\n"
        return text
    
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
    
    def scan_bot_uploaded_games(self):
        return 0
    
    def show_backup_menu(self, user_id, chat_id, message_id):
        self.edit_message(chat_id, message_id, "💾 Backup ready", self.create_admin_buttons())
    
    def handle_upload_stats(self, chat_id, message_id, user_id, first_name):
        self.edit_message(chat_id, message_id, "📊 Upload stats", self.create_admin_buttons())
    
    def handle_search_games(self, chat_id, message_id, user_id, first_name):
        self.edit_message(chat_id, message_id, "🔍 Type a game name to search:", self.create_search_buttons())
    
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
    
    # ==================== WEBHOOK UPDATE PROCESSING ====================
    
    def process_webhook_update(self, update):
        """Process incoming webhook updates"""
        try:
            if 'message' in update:
                self.process_message(update['message'])
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
            elif 'pre_checkout_query' in update:
                self.answer_callback_query(update['pre_checkout_query']['id'])
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
                        referral_code = parts[1].replace('ref_', '')
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_code,))
                        result = cursor.fetchone()
                        if result:
                            referrer_id = result[0]
                            self.register_user(user_id, username, first_name, referrer_id)
                        else:
                            self.register_user(user_id, username, first_name, None)
                    else:
                        self.register_user(user_id, username, first_name, None)
                    
                    code = self.generate_code()
                    self.save_verification_code(user_id, username, first_name, code)
                    welcome = f"""👋 Welcome {first_name}!

🔐 Your verification code: <code>{code}</code>

Please join @pspgamers5 and enter this code to verify."""
                    
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
                    
                    # Handle broadcast button input
                    if user_id in self.broadcast_system.broadcast_sessions:
                        session = self.broadcast_system.broadcast_sessions[user_id]
                        if session.get('stage') == 'waiting_buttons':
                            self.broadcast_system.process_buttons_input(user_id, chat_id, text)
                            return True
                        elif session.get('stage') == 'waiting_text':
                            session['message'] = text
                            session['stage'] = 'preview'
                            self.broadcast_system.show_preview(user_id, chat_id)
                            return True
                    
                    # Handle media reply text
                    if user_id in self.media_reply_sessions:
                        session = self.media_reply_sessions[user_id]
                        if session.get('stage') == 'waiting_text':
                            request = self.game_request_system.get_request_by_id(session['request_id'])
                            if request:
                                self.game_request_system.send_reply_to_user(session['user_id'], request, text)
                                self.robust_send_message(chat_id, "✅ Reply sent to user!")
                            del self.media_reply_sessions[user_id]
                            return True
                
                if self.is_user_verified(user_id):
                    if self.is_user_completed(user_id):
                        pass
            
            # Handle document uploads (game files) - TRIGGER AUTO BACKUP
            elif 'document' in message:
                file_name = message['document'].get('file_name', 'Unknown')
                print(f"📁 Game file uploaded: {file_name}")
                # Trigger GitHub backup after game upload
                self.trigger_auto_backup(file_name)
            
            return False
        except Exception as e:
            print(f"Process message error: {e}")
            return False

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    print("🚀 Starting Enhanced Telegram Bot with Webhook Mode...")
    print("💾 GitHub Auto-Backup will trigger on every game upload")
    print("🌐 Webhook mode enabled for 24/7 operation")
    
    # Start webhook server
    start_webhook_server()
    time.sleep(2)
    
    if BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            if response.json().get('ok'):
                print("✅ Bot token is valid")
                
                # Set webhook
                set_webhook()
                
                # Initialize bot
                bot_instance = CrossPlatformBot(BOT_TOKEN)
                
                # Start keep-alive service
                keep_alive = EnhancedKeepAliveService()
                keep_alive.start()
                
                # Keep main thread alive
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
