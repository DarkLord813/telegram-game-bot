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
from typing import Dict, List, Optional, Tuple

print("TELEGRAM BOT - COMPLETE SYSTEM WITH STARS PAYMENTS")
print("Game Storage + Stars + Broadcast + Button Access + Admin Notifications")
print("=" * 60)

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
            'service': 'telegram-game-bot',
            'requests_pending': 0
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return jsonify({'service': 'Telegram Game Bot', 'status': 'running', 'version': '2.0'})

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

# ==================== REQUEST NOTIFICATION SYSTEM ====================

class RequestNotificationSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.pending_requests = {}
        print("✅ Request notification system initialized!")
    
    def notify_admins_of_request(self, request_id: int, user_id: int, user_name: str, 
                                game_name: str, platform: str, timestamp: str):
        """Send notification to all admins about new game request"""
        try:
            cursor = self.bot.conn.cursor()
            
            # Get all admin IDs
            admin_ids = self.bot.ADMIN_IDS
            
            notification_text = f"""🚨 <b>NEW GAME REQUEST</b>

👤 <b>User:</b> {user_name} (ID: {user_id})
🎮 <b>Game:</b> {game_name}
🖥️ <b>Platform:</b> {platform}
🆔 <b>Request ID:</b> <code>{request_id}</code>
⏰ <b>Time:</b> {timestamp}

📊 <b>Status:</b> ⏳ Pending
            
<b>Actions:</b>
✅ <code>/approve_{request_id}</code> - Approve request
❌ <code>/reject_{request_id}</code> - Reject request
📝 <code>/note_{request_id}</code> - Add note
            
Reply with action command."""
            
            # Store request details for admin actions
            self.pending_requests[request_id] = {
                'user_id': user_id,
                'user_name': user_name,
                'game_name': game_name,
                'platform': platform,
                'status': 'pending',
                'timestamp': timestamp
            }
            
            # Send to each admin
            for admin_id in admin_ids:
                try:
                    # Send notification with action buttons
                    keyboard = [
                        [{"text": f"✅ Approve RQ{request_id}", "callback_data": f"approve_{request_id}"}],
                        [{"text": f"❌ Reject RQ{request_id}", "callback_data": f"reject_{request_id}"}],
                        [{"text": f"📝 View Details", "callback_data": f"view_{request_id}"}],
                        [{"text": f"📋 All Requests", "callback_data": "view_all_requests"}]
                    ]
                    
                    url = self.bot.base_url + "sendMessage"
                    data = {
                        "chat_id": admin_id,
                        "text": notification_text,
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps({"inline_keyboard": keyboard})
                    }
                    
                    response = requests.post(url, data=data, timeout=30)
                    if not response.json().get('ok'):
                        print(f"❌ Failed to notify admin {admin_id}: {response.json()}")
                except Exception as e:
                    print(f"❌ Error notifying admin {admin_id}: {e}")
            
            print(f"✅ Notified {len(admin_ids)} admins about request #{request_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error in admin notification: {e}")
            traceback.print_exc()
            return False
    
    def process_admin_action(self, admin_id: int, action: str, request_id: int, note: str = None):
        """Process admin actions on requests"""
        try:
            if request_id not in self.pending_requests:
                self.bot.send_message(admin_id, f"❌ Request #{request_id} not found or already processed.")
                return False
            
            request_data = self.pending_requests[request_id]
            cursor = self.bot.conn.cursor()
            
            if action == 'approve':
                # Update request status
                cursor.execute('''
                    UPDATE game_requests 
                    SET status = 'approved', 
                        approved_by = ?,
                        approved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (admin_id, request_id))
                
                # Notify user
                user_notification = f"""✅ <b>REQUEST APPROVED</b>

🎮 <b>Game:</b> {request_data['game_name']}
🖥️ <b>Platform:</b> {request_data['platform']}
🆔 <b>Request ID:</b> {request_id}
👤 <b>Approved by:</b> Admin
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 <b>Note:</b> We'll notify you when the game is uploaded!"""
                
                if note:
                    user_notification += f"\n\n💬 <b>Admin Note:</b> {note}"
                
                self.bot.send_message(request_data['user_id'], user_notification)
                
                # Update request data
                request_data['status'] = 'approved'
                request_data['approved_by'] = admin_id
                request_data['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Notify admins
                admin_update = f"""✅ <b>REQUEST APPROVED</b>

👤 <b>User:</b> {request_data['user_name']}
🎮 <b>Game:</b> {request_data['game_name']}
🖥️ <b>Platform:</b> {request_data['platform']}
🆔 <b>Request ID:</b> {request_id}
👑 <b>Approved by:</b> You
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                if note:
                    admin_update += f"\n\n💬 <b>Your Note:</b> {note}"
                
                # Send to all admins
                for aid in self.bot.ADMIN_IDS:
                    if aid != admin_id:  # Don't send to the approving admin
                        self.bot.send_message(aid, admin_update)
                
                self.bot.send_message(admin_id, f"✅ Request #{request_id} approved and user notified.")
                
            elif action == 'reject':
                # Update request status
                cursor.execute('''
                    UPDATE game_requests 
                    SET status = 'rejected', 
                        rejected_by = ?,
                        rejected_at = CURRENT_TIMESTAMP,
                        rejection_reason = ?
                    WHERE id = ?
                ''', (admin_id, note or 'No reason provided', request_id))
                
                # Notify user
                user_notification = f"""❌ <b>REQUEST REJECTED</b>

🎮 <b>Game:</b> {request_data['game_name']}
🖥️ <b>Platform:</b> {request_data['platform']}
🆔 <b>Request ID:</b> {request_id}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                if note:
                    user_notification += f"\n\n💬 <b>Reason:</b> {note}"
                else:
                    user_notification += "\n\n💬 <b>Reason:</b> Not specified"
                
                self.bot.send_message(request_data['user_id'], user_notification)
                
                # Update request data
                request_data['status'] = 'rejected'
                request_data['rejected_by'] = admin_id
                request_data['rejection_reason'] = note or 'No reason provided'
                request_data['rejected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Notify other admins
                admin_update = f"""❌ <b>REQUEST REJECTED</b>

👤 <b>User:</b> {request_data['user_name']}
🎮 <b>Game:</b> {request_data['game_name']}
🖥️ <b>Platform:</b> {request_data['platform']}
🆔 <b>Request ID:</b> {request_id}
👑 <b>Rejected by:</b> You"""
                
                if note:
                    admin_update += f"\n💬 <b>Reason:</b> {note}"
                
                for aid in self.bot.ADMIN_IDS:
                    if aid != admin_id:
                        self.bot.send_message(aid, admin_update)
                
                self.bot.send_message(admin_id, f"❌ Request #{request_id} rejected and user notified.")
            
            self.bot.conn.commit()
            
            # Remove from pending if processed
            if action in ['approve', 'reject']:
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing admin action: {e}")
            traceback.print_exc()
            return False
    
    def get_pending_requests_count(self):
        """Get count of pending requests"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM game_requests WHERE status = "pending"')
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"❌ Error getting pending count: {e}")
            return 0
    
    def view_all_requests(self, admin_id: int):
        """Show all pending requests to admin"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                SELECT id, user_name, game_name, platform, created_at 
                FROM game_requests 
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            
            requests = cursor.fetchall()
            
            if not requests:
                self.bot.send_message(admin_id, "📭 No pending requests.")
                return
            
            requests_text = f"""📋 <b>PENDING REQUESTS</b>

Total pending: {len(requests)}

"""
            for req in requests:
                req_id, user_name, game_name, platform, created_at = req
                requests_text += f"""
🆔 <b>RQ{req_id}</b>
👤 {user_name}
🎮 {game_name}
🖥️ {platform}
⏰ {created_at}
└─ Actions: <code>/approve_{req_id}</code> | <code>/reject_{req_id}</code>
"""
            
            self.bot.send_message(admin_id, requests_text)
            
        except Exception as e:
            print(f"❌ Error viewing requests: {e}")
            self.bot.send_message(admin_id, "❌ Error loading requests.")

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
        self.request_system = RequestNotificationSystem(self)
        
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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
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
                    download_count INTEGER DEFAULT 0,
                    request_id INTEGER DEFAULT NULL
                )
            ''')
            
            # Game requests - Enhanced with admin tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    game_name TEXT,
                    platform TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    approved_by INTEGER DEFAULT NULL,
                    approved_at DATETIME DEFAULT NULL,
                    rejected_by INTEGER DEFAULT NULL,
                    rejected_at DATETIME DEFAULT NULL,
                    rejection_reason TEXT DEFAULT NULL,
                    admin_note TEXT DEFAULT NULL
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
            
            # Add index for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON game_requests(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_user ON game_requests(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_category ON regular_games(category)')
            
            self.conn.commit()
            print("✅ Database setup complete!")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            traceback.print_exc()
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.setup_database()
    
    def send_message(self, chat_id, text, keyboard=None, inline_keyboard=None, parse_mode="HTML"):
        """Send message with optional keyboard"""
        try:
            url = self.base_url + "sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            if keyboard:
                data["reply_markup"] = json.dumps({
                    "keyboard": keyboard,
                    "resize_keyboard": True,
                    "one_time_keyboard": False
                })
            elif inline_keyboard:
                data["reply_markup"] = json.dumps({"inline_keyboard": inline_keyboard})
            else:
                data["reply_markup"] = json.dumps({"remove_keyboard": True})
            
            response = requests.post(url, data=data, timeout=15)
            result = response.json()
            
            if not result.get('ok'):
                print(f"❌ Send message error: {result.get('description')}")
            
            return result.get('ok', False)
            
        except Exception as e:
            print(f"❌ Send message exception: {e}")
            return False
    
    def send_with_menu(self, chat_id, text, user_id, additional_buttons=None, is_admin=False):
        """Send message with standard menu buttons"""
        keyboard = []
        
        # Add custom buttons if provided
        if additional_buttons:
            if isinstance(additional_buttons[0], list):
                keyboard.extend(additional_buttons)
            else:
                keyboard.append(additional_buttons)
        
        # Always show these navigation buttons
        standard_buttons = []
        
        # Admin specific buttons
        if is_admin:
            standard_buttons.append("👑 Admin Panel")
            standard_buttons.append("📋 View Requests")
        
        # Standard buttons for all users
        standard_buttons.extend(["🎮 Browse Games", "💰 Premium Games"])
        standard_buttons.extend(["⭐ Stars Menu", "🎯 Mini Games"])
        standard_buttons.append("📝 Request Game")
        standard_buttons.append("🔙 Main Menu")
        
        # Add standard buttons in rows of 2
        for i in range(0, len(standard_buttons), 2):
            row = standard_buttons[i:i+2]
            keyboard.append(row)
        
        return self.send_message(chat_id, text, keyboard)
    
    def send_main_menu(self, chat_id, user_id, first_name):
        is_admin = self.is_admin(user_id)
        
        keyboard = [
            ["🎮 Browse Games", "💰 Premium Games"],
            ["⭐ Stars Menu", "🎯 Mini Games"],
            ["📝 Request Game", "📊 Profile"],
            ["📢 Channel", "🆘 Help"]
        ]
        
        if is_admin:
            # Add admin section
            keyboard.insert(2, ["👑 Admin Panel", "📋 View Requests"])
        
        welcome_text = f"""👋 Welcome <b>{first_name}</b>!

🤖 <b>Complete Game Bot System</b> v2.0

⭐ <b>Features:</b>
• Browse & download games instantly
• Premium games with Telegram Stars
• Request games (admins get notified)
• Admin broadcasts & management
• Fun mini-games

💡 <b>Tip:</b> Use /help for commands

Choose an option:"""
        
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def send_categories_menu(self, chat_id, user_id):
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
        
        keyboard.append(["💰 Premium Games", "🎯 Mini Games"])
        keyboard.append(["📝 Request Game", "🔙 Main Menu"])
        
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
            keyboard = [
                ["🎮 Browse Games", "📝 Request Game"],
                ["🔙 Main Menu"]
            ]
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
        
        keyboard.append(["🔙 Categories", "🔍 Search Games"])
        keyboard.append(["📝 Request Game", "🔙 Main Menu"])
        
        self.user_sessions[chat_id] = {
            'menu': 'category_games',
            'category': category_name,
            'page': page,
            'games': games
        }
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_premium_games_menu(self, chat_id, user_id):
        premium_games = self.stars_system.get_premium_games()
        
        is_admin = self.is_admin(user_id)
        
        if not premium_games:
            keyboard = [
                ["🎮 Regular Games", "⭐ Stars Menu"],
                ["📝 Request Game", "🔙 Main Menu"]
            ]
            
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games!"""
            
            if is_admin:
                keyboard.insert(0, ["👑 Admin Panel"])
        else:
            keyboard = []
            
            # Show up to 6 games in rows of 2
            for i in range(0, min(len(premium_games), 6), 2):
                row = []
                for j in range(2):
                    if i + j < len(premium_games):
                        game_id, file_name, file_type, file_size, stars_price, description = premium_games[i + j]
                        short_name = file_name[:12] + "..." if len(file_name) > 12 else file_name
                        row.append(f"💰 {short_name}")
                if row:
                    keyboard.append(row)
            
            keyboard.append(["🎮 Regular Games", "⭐ Stars Menu"])
            keyboard.append(["📝 Request Game", "🔙 Main Menu"])
            
            if is_admin:
                keyboard.insert(0, ["👑 Admin Panel"])
            
            premium_text = """💰 <b>Premium Games</b>

Exclusive games available with Telegram Stars:

"""
            for i, game in enumerate(premium_games[:4], 1):
                game_id, file_name, file_type, file_size, stars_price, description = game
                size = self.format_file_size(file_size)
                
                premium_text += f"\n{i}. <b>{file_name}</b>"
                premium_text += f"\n   ⭐ {stars_price} Stars | 📦 {file_type} | 📏 {size}"
                premium_text += f"\n   └─ Type: <code>/premium_{game_id}</code>\n"
            
            if len(premium_games) > 4:
                premium_text += f"\n📋 ... and {len(premium_games) - 4} more premium games"
        
        return self.send_message(chat_id, premium_text, keyboard)
    
    def send_stars_menu(self, chat_id, user_id):
        balance = self.stars_system.get_balance()
        is_admin = self.is_admin(user_id)
        
        keyboard = [
            ["⭐ 50 Stars", "⭐ 100 Stars"],
            ["⭐ 500 Stars", "⭐ 1000 Stars"],
            ["💫 Custom Amount", "📊 Stars Stats"],
            ["💰 Premium Games", "🎮 Browse Games"],
            ["📝 Request Game", "🔙 Main Menu"]
        ]
        
        if is_admin:
            keyboard.insert(2, ["👑 Admin Panel"])
        
        stars_text = """⭐ <b>Telegram Stars Menu</b>

Support our bot with Telegram Stars!

🌟 <b>Why Donate Stars?</b>
• Keep the bot running 24/7
• Support development
• Purchase premium games
• Request new games

💰 <b>Conversion:</b> 1 Star ≈ $0.01

📊 <b>Stats:</b>"""
        
        stars_text += f"\n• Total Stars Earned: <b>{balance['total_stars_earned']} ⭐</b>"
        stars_text += f"\n• Total USD Value: <b>${balance['total_usd_earned']:.2f}</b>"
        stars_text += "\n\nThank you for supporting us! 🙏"
        
        return self.send_message(chat_id, stars_text, keyboard)
    
    def send_mini_games_menu(self, chat_id, user_id):
        is_admin = self.is_admin(user_id)
        
        keyboard = [
            ["🎯 Number Guess", "🎲 Random Number"],
            ["🎰 Lucky Spin", "🎮 Dice Game"],
            ["🎮 Browse Games", "⭐ Stars Menu"],
            ["📝 Request Game", "🔙 Main Menu"]
        ]
        
        if is_admin:
            keyboard.insert(2, ["👑 Admin Panel"])
        
        games_text = """🎮 <b>Mini Games</b>

Choose a game to play:

🎯 <b>Number Guess</b> - Guess the number (1-100)
🎲 <b>Random Number</b> - Get random numbers
🎰 <b>Lucky Spin</b> - Spin for prizes
🎮 <b>Dice Game</b> - Roll dice vs bot

All games are free! Have fun! 🎉"""
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_admin_menu(self, chat_id, user_id):
        cursor = self.conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM regular_games')
        regular_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM premium_games')
        premium_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM game_requests WHERE status = "pending"')
        pending_requests = cursor.fetchone()[0]
        
        keyboard = [
            ["📤 Upload Game", "💰 Upload Premium"],
            ["📢 Broadcast", "📋 View Requests"],
            ["📊 Statistics", "🗑️ Manage Games"],
            ["🎮 Browse Games", "⭐ Stars Menu"],
            ["🔙 Main Menu"]
        ]
        
        admin_text = f"""👑 <b>Admin Panel</b>

📊 <b>Statistics:</b>
• Regular games: {regular_count}
• Premium games: {premium_count}
• Total users: {users_count}
• Pending requests: <b>{pending_requests}</b> ⚠️

🚨 <b>Quick Actions:</b>
• /requests - View all pending requests
• /stats - Detailed statistics
• /broadcast - Send message to all users
• /upload - Upload new game

⚡ <b>Features:</b>
• Manage game requests
• Upload games
• Broadcast messages
• View analytics

Choose an option:"""
        
        return self.send_message(chat_id, admin_text, keyboard)
    
    def send_upload_menu(self, chat_id):
        keyboard = [
            ["🆓 Regular Game", "💰 Premium Game"],
            ["🎮 Browse Games", "🔙 Admin Menu"]
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
            ["🎮 Browse Games", "🔙 Admin Menu"]
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
    
    def send_request_menu(self, chat_id):
        keyboard = [
            ["🎮 Browse Games", "💰 Premium Games"],
            ["⭐ Stars Menu", "🔙 Main Menu"]
        ]
        
        request_text = """📝 <b>Game Request System</b>

Request any game you want!

🎮 <b>How it works:</b>
1. Enter game name
2. Specify platform (PSP, Android, PC, etc.)
3. Submit request

✅ <b>Benefits:</b>
• Admins get notified instantly
• Priority for popular requests
• Get notified when game is added

Click "Request Game" to start!"""
        
        return self.send_message(chat_id, request_text, keyboard)
    
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
    
    def save_regular_game(self, file_id, file_name, file_type, file_size, category, description, added_by, request_id=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO regular_games 
                (file_id, file_name, file_type, file_size, category, description, added_by, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_name, file_type, file_size, category, description, added_by, request_id))
            
            game_id = cursor.lastrowid
            
            # If this game was from a request, update the request
            if request_id:
                cursor.execute('''
                    UPDATE game_requests 
                    SET status = 'fulfilled',
                        admin_note = 'Game has been uploaded'
                    WHERE id = ?
                ''', (request_id,))
                
                # Notify the user who requested it
                cursor.execute('SELECT user_id, game_name FROM game_requests WHERE id = ?', (request_id,))
                req_info = cursor.fetchone()
                if req_info:
                    req_user_id, req_game_name = req_info
                    notification = f"""✅ <b>YOUR REQUEST HAS BEEN FULFILLED!</b>

🎮 <b>Game:</b> {req_game_name}
📁 <b>Now available in:</b> {category}
🔗 <b>Find it in:</b> Browse Games > {category}

Thank you for your request! 😊"""
                    self.send_message(req_user_id, notification)
            
            self.conn.commit()
            return game_id
        except Exception as e:
            print(f"❌ Error saving regular game: {e}")
            return False
    
    def handle_game_request(self, user_id, chat_id, user_name, game_name, platform):
        """Process game request from user and notify admins"""
        try:
            cursor = self.conn.cursor()
            
            # Save request to database
            cursor.execute('''
                INSERT INTO game_requests (user_id, user_name, game_name, platform)
                VALUES (?, ?, ?, ?)
            ''', (user_id, user_name, game_name, platform))
            
            request_id = cursor.lastrowid
            self.conn.commit()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Notify admins
            self.request_system.notify_admins_of_request(
                request_id, user_id, user_name, game_name, platform, timestamp
            )
            
            # Confirm to user
            confirmation = f"""✅ <b>REQUEST SUBMITTED!</b>

🎮 <b>Game:</b> {game_name}
🖥️ <b>Platform:</b> {platform}
🆔 <b>Request ID:</b> <code>{request_id}</code>
⏰ <b>Time:</b> {timestamp}

📋 <b>Status:</b> ⏳ Pending admin approval

💡 <b>What happens next:</b>
1. All admins have been notified
2. You'll get notified when approved/rejected
3. If approved, you'll be notified when game is uploaded

Thank you for your request! 🙏"""
            
            self.send_with_menu(
                chat_id, 
                confirmation, 
                user_id,
                additional_buttons=[["🎮 Browse Games", "💰 Premium Games"]],
                is_admin=self.is_admin(user_id)
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling game request: {e}")
            traceback.print_exc()
            return False
    
    def process_message(self, message):
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                user_name = message['from'].get('username', first_name)
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Update user activity
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_active)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, user_name, first_name))
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
                        self.send_with_menu(
                            chat_id, 
                            "✅ Payment successful! Thank you for your support! 🙏", 
                            user_id,
                            is_admin=self.is_admin(user_id)
                        )
                    return success
                
                # Handle callback queries (for inline buttons)
                if 'callback_query' in message:
                    callback = message['callback_query']
                    callback_id = callback['id']
                    callback_data = callback.get('data', '')
                    from_user = callback['from']
                    
                    # Answer callback query
                    requests.post(self.base_url + "answerCallbackQuery", 
                                data={"callback_query_id": callback_id})
                    
                    # Handle request actions from admins
                    if callback_data.startswith('approve_'):
                        request_id = int(callback_data.replace('approve_', ''))
                        self.request_system.process_admin_action(from_user['id'], 'approve', request_id)
                        return True
                    elif callback_data.startswith('reject_'):
                        request_id = int(callback_data.replace('reject_', ''))
                        self.request_system.process_admin_action(from_user['id'], 'reject', request_id)
                        return True
                    elif callback_data == 'view_all_requests':
                        self.request_system.view_all_requests(from_user['id'])
                        return True
                
                # Handle admin commands for requests
                if text.startswith('/approve_'):
                    if self.is_admin(user_id):
                        try:
                            request_id = int(text.replace('/approve_', ''))
                            self.request_system.process_admin_action(user_id, 'approve', request_id)
                        except:
                            self.send_message(chat_id, "❌ Invalid request ID.")
                    return True
                
                elif text.startswith('/reject_'):
                    if self.is_admin(user_id):
                        try:
                            request_id = int(text.replace('/reject_', ''))
                            # Ask for rejection reason
                            self.user_sessions[chat_id] = {
                                'state': 'waiting_reject_reason',
                                'request_id': request_id
                            }
                            self.send_message(chat_id, "📝 Please provide a reason for rejection:")
                        except:
                            self.send_message(chat_id, "❌ Invalid request ID.")
                    return True
                
                elif text.startswith('/requests') and self.is_admin(user_id):
                    self.request_system.view_all_requests(user_id)
                    return True
                
                # Handle session states
                if chat_id in self.user_sessions:
                    session = self.user_sessions[chat_id]
                    
                    # Handle rejection reason
                    if session.get('state') == 'waiting_reject_reason':
                        request_id = session.get('request_id')
                        reason = text
                        self.request_system.process_admin_action(user_id, 'reject', request_id, reason)
                        del self.user_sessions[chat_id]
                        return True
                    
                    if session.get('state') == 'waiting_code':
                        if text.isdigit() and len(text) == 6:
                            if self.verify_code(user_id, text):
                                if self.check_channel_membership(user_id):
                                    self.mark_channel_joined(user_id)
                                    self.send_with_menu(
                                        chat_id, 
                                        "✅ Verification complete! You now have full access.", 
                                        user_id,
                                        is_admin=self.is_admin(user_id)
                                    )
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
                            'state': 'waiting_platform',
                            'request_data': {'game_name': text}
                        }
                        self.send_with_menu(
                            chat_id, 
                            f"🎮 Game: <b>{text}</b>\n\nNow specify platform (PSP, Android, PC, etc.):", 
                            user_id,
                            is_admin=self.is_admin(user_id)
                        )
                        return True
                    
                    elif session.get('state') == 'waiting_platform':
                        game_name = session['request_data']['game_name']
                        platform = text
                        
                        # Process the request and notify admins
                        success = self.handle_game_request(user_id, chat_id, first_name, game_name, platform)
                        
                        if success:
                            del self.user_sessions[chat_id]
                        return True
                    
                    elif session.get('state') == 'waiting_stars_amount':
                        try:
                            stars_amount = int(text)
                            if stars_amount > 0 and stars_amount <= 10000:
                                success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount)
                                if success:
                                    self.send_with_menu(
                                        chat_id, 
                                        f"✅ Stars invoice created! Check your Telegram messages.", 
                                        user_id,
                                        is_admin=self.is_admin(user_id)
                                    )
                                else:
                                    self.send_with_menu(
                                        chat_id, 
                                        "❌ Failed to create invoice.", 
                                        user_id,
                                        is_admin=self.is_admin(user_id)
                                    )
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
                                self.send_with_menu(
                                    chat_id, 
                                    f"⭐ Price set: {stars_price} Stars\n\nEnter description:", 
                                    user_id,
                                    is_admin=True
                                )
                            else:
                                self.send_message(chat_id, "❌ Enter price 1-10000.")
                        except:
                            self.send_message(chat_id, "❌ Invalid number.")
                        return True
                    
                    elif session.get('state') == 'waiting_premium_description':
                        description = text
                        self.temp_uploads[chat_id]['description'] = description
                        self.user_sessions[chat_id]['state'] = 'waiting_premium_file'
                        self.send_with_menu(
                            chat_id, 
                            "✅ Description saved!\n\nNow upload the game file.", 
                            user_id,
                            is_admin=True
                        )
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
                                        self.send_with_menu(
                                            chat_id, 
                                            f"✅ Regular game saved! ID: {game_id}\n\nGame: {file_info['file_name']}", 
                                            user_id,
                                            is_admin=True
                                        )
                                    else:
                                        self.send_with_menu(
                                            chat_id, 
                                            "❌ Failed to save game.", 
                                            user_id,
                                            is_admin=True
                                        )
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
                                        self.send_with_menu(
                                            chat_id, 
                                            f"✅ Premium game saved! ID: {game_id}\nPrice: {stars_price} Stars\nGame: {file_info['file_name']}", 
                                            user_id,
                                            is_admin=True
                                        )
                                    else:
                                        self.send_with_menu(
                                            chat_id, 
                                            "❌ Failed to save premium game.", 
                                            user_id,
                                            is_admin=True
                                        )
                                
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
                                    self.send_with_menu(
                                        chat_id, 
                                        f"✅ Regular game saved! ID: {game_id}\nCustom category: {category}", 
                                        user_id,
                                        is_admin=True
                                    )
                                else:
                                    self.send_with_menu(
                                        chat_id, 
                                        "❌ Failed to save game.", 
                                        user_id,
                                        is_admin=True
                                    )
                            
                            del self.temp_uploads[chat_id]
                        
                        del self.user_sessions[chat_id]
                        return True
                    
                    elif session.get('state') == 'waiting_search':
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
                            self.send_with_menu(
                                chat_id, 
                                f"❌ No results found for: <code>{query}</code>", 
                                user_id,
                                additional_buttons=[["🎮 Browse Games", "📝 Request Game"]],
                                is_admin=self.is_admin(user_id)
                            )
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
                        
                        self.send_with_menu(
                            chat_id, 
                            results_text, 
                            user_id,
                            additional_buttons=[["🎮 Browse Games", "🔍 Search Again"]],
                            is_admin=self.is_admin(user_id)
                        )
                        return True
                
                # Handle premium game purchase
                if text.startswith('/premium_'):
                    try:
                        game_id = int(text.replace('/premium_', ''))
                        game = self.stars_system.get_premium_game_by_id(game_id)
                        
                        if not game:
                            self.send_with_menu(
                                chat_id, 
                                "❌ Premium game not found.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                            return True
                        
                        if self.stars_system.has_user_purchased_game(user_id, game_id):
                            if game['file_id']:
                                self.send_document(chat_id, game['file_id'], f"🎮 <b>{game['file_name']}</b>\n\nEnjoy your game! 😊")
                            else:
                                self.send_with_menu(
                                    chat_id, 
                                    "❌ Game file not available.", 
                                    user_id,
                                    is_admin=self.is_admin(user_id)
                                )
                            return True
                        
                        success, invoice_id = self.stars_system.create_premium_game_invoice(
                            user_id, chat_id, game['stars_price'], game['file_name'], game_id
                        )
                        
                        if success:
                            self.send_with_menu(
                                chat_id, 
                                f"✅ Invoice created for <b>{game['file_name']}</b>!\nPrice: {game['stars_price']} Stars\n\nCheck Telegram for payment.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                        else:
                            self.send_with_menu(
                                chat_id, 
                                "❌ Failed to create invoice.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                        
                        return True
                    except:
                        self.send_with_menu(
                            chat_id, 
                            "❌ Invalid premium game ID.", 
                            user_id,
                            is_admin=self.is_admin(user_id)
                        )
                        return True
                
                # Handle get game command
                if text.startswith('/get_'):
                    try:
                        game_id = int(text.replace('/get_', ''))
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT file_id, file_name, description FROM regular_games WHERE id = ? AND is_active = 1', (game_id,))
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
                                self.send_with_menu(
                                    chat_id, 
                                    f"✅ <b>{file_name}</b> sent!\n\nEnjoy the game! 🎮", 
                                    user_id,
                                    additional_buttons=[["📁 Send Again", "🎮 Browse More"]],
                                    is_admin=self.is_admin(user_id)
                                )
                            else:
                                self.send_with_menu(
                                    chat_id, 
                                    "❌ Failed to send file.", 
                                    user_id,
                                    is_admin=self.is_admin(user_id)
                                )
                        else:
                            self.send_with_menu(
                                chat_id, 
                                "❌ Game not found or not active.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                    except:
                        self.send_with_menu(
                            chat_id, 
                            "❌ Invalid game ID.", 
                            user_id,
                            is_admin=self.is_admin(user_id)
                        )
                    return True
                
                # ============ MAIN MENU NAVIGATION ============
                
                if text == '/start' or text == '🔙 Main Menu':
                    self.send_main_menu(chat_id, user_id, first_name)
                    return True
                
                elif text == '👑 Admin Panel':
                    if self.is_admin(user_id):
                        self.send_admin_menu(chat_id, user_id)
                    else:
                        self.send_with_menu(
                            chat_id, 
                            "❌ Admin access required.", 
                            user_id,
                            is_admin=False
                        )
                    return True
                
                elif text == '🎮 Browse Games':
                    self.send_categories_menu(chat_id, user_id)
                    return True
                
                elif text == '🔙 Categories':
                    self.send_categories_menu(chat_id, user_id)
                    return True
                
                elif text == '💰 Premium Games':
                    self.send_premium_games_menu(chat_id, user_id)
                    return True
                
                elif text == '⭐ Stars Menu':
                    self.send_stars_menu(chat_id, user_id)
                    return True
                
                elif text == '🎯 Mini Games':
                    self.send_mini_games_menu(chat_id, user_id)
                    return True
                
                elif text == '📝 Request Game':
                    self.user_sessions[chat_id] = {'state': 'waiting_game_name'}
                    self.send_with_menu(
                        chat_id, 
                        "🎮 <b>Game Request</b>\n\nEnter the name of the game you want to request:", 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    return True
                
                elif text == '📋 View Requests' and self.is_admin(user_id):
                    self.request_system.view_all_requests(user_id)
                    return True
                
                elif text == '🔍 Search Games':
                    self.send_with_menu(
                        chat_id, 
                        "🔍 <b>Search Games</b>\n\nEnter search query:", 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    self.user_sessions[chat_id] = {'state': 'waiting_search'}
                    return True
                
                elif text == '📊 Profile':
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT created_at, is_verified, last_active FROM users WHERE user_id = ?', (user_id,))
                    result = cursor.fetchone()
                    
                    profile_text = f"""👤 <b>Profile</b>

🆔 ID: <code>{user_id}</code>
👋 Name: {first_name}
📛 Username: @{user_name if user_name else 'No username'}"""
                    
                    if result:
                        created_at, is_verified, last_active = result
                        profile_text += f"""
✅ Verified: {'Yes' if is_verified else 'No'}
📅 Joined: {created_at}
🕒 Last active: {last_active}"""
                    
                    self.send_with_menu(
                        chat_id, 
                        profile_text, 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    return True
                
                elif text == '📢 Channel':
                    self.send_with_menu(
                        chat_id, 
                        "📢 <b>Our Channel</b>\n\nJoin our official channel:\n@pspgamers5\n\nStay updated with new games and announcements!", 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    return True
                
                elif text == '🆘 Help':
                    help_text = """🆘 <b>Help & Commands</b>

🎮 <b>Main Commands:</b>
/start - Start bot & main menu
/menu - Show main menu
/help - This help message

🎯 <b>Game Commands:</b>
/browse - Browse games by category
/search - Search for games
/request - Request a new game
/premium - View premium games

⭐ <b>Stars Commands:</b>
/stars - Stars menu & donations
/donate - Donate stars

👑 <b>Admin Commands:</b>
/admin - Admin panel
/requests - View pending requests
/stats - View statistics

📝 <b>Game Requests:</b>
• Request any game
• Admins get notified instantly
• Get notified when approved/added

Need more help? Contact admins!"""
                    
                    self.send_with_menu(
                        chat_id, 
                        help_text, 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    return True
                
                # ============ MINI GAMES ============
                
                elif text == '🎯 Number Guess':
                    self.user_sessions[chat_id] = {
                        'game': 'number_guess',
                        'target': random.randint(1, 100),
                        'attempts': 0
                    }
                    return self.send_with_menu(
                        chat_id,
                        "🎯 <b>Number Guess Game</b>\n\nI'm thinking of a number between 1-100.\nTry to guess it!\n\nEnter your guess (1-100):",
                        user_id,
                        additional_buttons=[["🎲 Random Game", "🎰 Lucky Spin"]],
                        is_admin=self.is_admin(user_id)
                    )
                
                elif text == '🎲 Random Number':
                    number = random.randint(1, 100)
                    return self.send_with_menu(
                        chat_id,
                        f"🎲 <b>Random Number:</b> <code>{number}</code>",
                        user_id,
                        additional_buttons=[["🎲 New Random", "🎯 Number Guess"]],
                        is_admin=self.is_admin(user_id)
                    )
                
                elif text == '🎰 Lucky Spin':
                    prizes = ["⭐ 10 Stars", "🎮 Free Game", "💎 Bonus", "🎉 Nothing", "✨ Try Again", "💰 50 Stars"]
                    prize = random.choice(prizes)
                    return self.send_with_menu(
                        chat_id,
                        f"🎰 <b>Lucky Spin Result:</b>\n\n🎁 You won: <b>{prize}</b>!",
                        user_id,
                        additional_buttons=[["🎰 Spin Again", "🎮 Dice Game"]],
                        is_admin=self.is_admin(user_id)
                    )
                
                elif text == '🎮 Dice Game':
                    user_roll = random.randint(1, 6)
                    bot_roll = random.randint(1, 6)
                    
                    if user_roll > bot_roll:
                        result = "🎉 You win!"
                    elif bot_roll > user_roll:
                        result = "🤖 Bot wins!"
                    else:
                        result = "🤝 It's a tie!"
                    
                    return self.send_with_menu(
                        chat_id,
                        f"🎮 <b>Dice Game</b>\n\n🎲 Your roll: {user_roll}\n🤖 Bot roll: {bot_roll}\n\n<b>{result}</b>",
                        user_id,
                        additional_buttons=[["🎮 Roll Again", "🎯 Number Guess"]],
                        is_admin=self.is_admin(user_id)
                    )
                
                # ============ ADMIN PANEL ============
                
                elif text == '📤 Upload Game' and self.is_admin(user_id):
                    self.send_upload_menu(chat_id)
                    return True
                
                elif text == '🆓 Regular Game' and self.is_admin(user_id):
                    self.send_with_menu(
                        chat_id, 
                        "📤 <b>Upload Regular Game</b>\n\nSend the game file.\nSupported: ZIP, 7Z, ISO, APK, EXE, etc.", 
                        user_id,
                        is_admin=True
                    )
                    self.user_sessions[chat_id] = {'state': 'waiting_regular_file'}
                    return True
                
                elif text == '💰 Premium Game' and self.is_admin(user_id):
                    self.user_sessions[chat_id] = {'state': 'waiting_premium_price'}
                    self.send_with_menu(
                        chat_id, 
                        "💰 <b>Upload Premium Game</b>\n\nEnter price in Stars (1-10000):", 
                        user_id,
                        is_admin=True
                    )
                    return True
                
                elif text == '📢 Broadcast' and self.is_admin(user_id):
                    self.send_broadcast_menu(chat_id)
                    return True
                
                elif text == '📝 Text Broadcast' and self.is_admin(user_id):
                    self.user_sessions[chat_id] = {'state': 'waiting_broadcast'}
                    self.send_with_menu(
                        chat_id, 
                        "📝 <b>Text Broadcast</b>\n\nEnter broadcast message:", 
                        user_id,
                        is_admin=True
                    )
                    return True
                
                elif text == '📷 Photo Broadcast' and self.is_admin(user_id):
                    self.send_with_menu(
                        chat_id, 
                        "📷 <b>Photo Broadcast</b>\n\nSend photo with caption for broadcast.", 
                        user_id,
                        is_admin=True
                    )
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
                    cursor.execute('SELECT COUNT(*) FROM game_requests WHERE status = "pending"')
                    pending = cursor.fetchone()[0]
                    cursor.execute('SELECT COUNT(*) FROM game_requests WHERE status = "approved"')
                    approved = cursor.fetchone()[0]
                    
                    balance = self.stars_system.get_balance()
                    
                    stats_text = f"""📊 <b>Statistics</b>

🎮 <b>Games:</b>
• Regular games: {regular}
• Premium games: {premium}
• Total games: {regular + premium}

👥 <b>Users:</b>
• Total users: {users}
• Verified users: {users}  # Assuming all are verified

📝 <b>Requests:</b>
• Pending: {pending}
• Approved: {approved}
• Total: {pending + approved}

⭐ <b>Stars:</b>
• Total earned: {balance['total_stars_earned']}
• USD value: ${balance['total_usd_earned']:.2f}"""
                    
                    self.send_with_menu(
                        chat_id, 
                        stats_text, 
                        user_id,
                        is_admin=True
                    )
                    return True
                
                elif text == '🗑️ Manage Games' and self.is_admin(user_id):
                    keyboard = [
                        ["📊 View All Games", "❌ Delete Game"],
                        ["🔄 Update Game", "🎮 Browse Games"],
                        ["🔙 Admin Menu"]
                    ]
                    self.send_message(chat_id, "🗑️ <b>Game Management</b>\n\nComing soon with advanced features!", keyboard)
                    return True
                
                elif text == '🔙 Admin Menu' and self.is_admin(user_id):
                    self.send_admin_menu(chat_id, user_id)
                    return True
                
                # ============ STARS PAYMENTS ============
                
                elif text == '💫 Custom Amount':
                    self.user_sessions[chat_id] = {'state': 'waiting_stars_amount'}
                    self.send_with_menu(
                        chat_id, 
                        "💫 <b>Custom Stars Amount</b>\n\nEnter Stars amount (1-10000):", 
                        user_id,
                        is_admin=self.is_admin(user_id)
                    )
                    return True
                
                elif text.startswith('⭐ '):
                    stars_text = text.replace('⭐ ', '').replace(' Stars', '')
                    try:
                        stars_amount = int(stars_text)
                        success, invoice_id = self.stars_system.create_stars_invoice(user_id, chat_id, stars_amount)
                        if success:
                            self.send_with_menu(
                                chat_id, 
                                f"✅ Stars invoice created! Check Telegram for payment.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                        else:
                            self.send_with_menu(
                                chat_id, 
                                "❌ Failed to create invoice.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
                    except:
                        self.send_with_menu(
                            chat_id, 
                            "❌ Invalid amount.", 
                            user_id,
                            is_admin=self.is_admin(user_id)
                        )
                    return True
                
                elif text == '📊 Stars Stats' and self.is_admin(user_id):
                    balance = self.stars_system.get_balance()
                    stats_text = f"""📊 <b>Stars Statistics</b>

⭐ Total Stars Earned: {balance['total_stars_earned']}
💰 Total USD Value: ${balance['total_usd_earned']:.2f}
💎 Available Stars: {balance['available_stars']}
💵 Available USD: ${balance['available_usd']:.2f}
💳 Total Transactions: {balance['total_stars_earned'] // 50}"""
                    
                    self.send_with_menu(
                        chat_id, 
                        stats_text, 
                        user_id,
                        is_admin=True
                    )
                    return True
                
                # ============ CATEGORY SELECTION ============
                
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
                                        
                                        self.send_with_menu(
                                            chat_id, 
                                            f"✅ <b>{file_name}</b> sent!\n\nEnjoy the game! 🎮", 
                                            user_id,
                                            additional_buttons=[["📁 Send Again", "🎮 Browse More"]],
                                            is_admin=self.is_admin(user_id)
                                        )
                                    else:
                                        self.send_with_menu(
                                            chat_id, 
                                            "❌ Failed to send file.", 
                                            user_id,
                                            is_admin=self.is_admin(user_id)
                                        )
                                else:
                                    self.send_with_menu(
                                        chat_id, 
                                        "❌ File not found.", 
                                        user_id,
                                        is_admin=self.is_admin(user_id)
                                    )
                            else:
                                self.send_with_menu(
                                    chat_id, 
                                    "❌ Invalid selection.", 
                                    user_id,
                                    is_admin=self.is_admin(user_id)
                                )
                        except:
                            self.send_with_menu(
                                chat_id, 
                                "❌ Error processing selection.", 
                                user_id,
                                is_admin=self.is_admin(user_id)
                            )
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
                
                # Number guess game input
                elif chat_id in self.user_sessions and self.user_sessions[chat_id].get('game') == 'number_guess':
                    try:
                        guess = int(text)
                        session = self.user_sessions[chat_id]
                        target = session['target']
                        session['attempts'] += 1
                        
                        if guess < 1 or guess > 100:
                            self.send_message(chat_id, "❌ Please enter a number between 1-100.")
                            return True
                        
                        if guess < target:
                            message = f"📈 Too low! Try a higher number.\nAttempts: {session['attempts']}"
                        elif guess > target:
                            message = f"📉 Too high! Try a lower number.\nAttempts: {session['attempts']}"
                        else:
                            message = f"""🎉 <b>CONGRATULATIONS!</b>

🎯 You guessed it! The number was {target}
✅ Attempts: {session['attempts']}
🏆 Great job!"""
                            del self.user_sessions[chat_id]
                        
                        self.send_with_menu(
                            chat_id,
                            message,
                            user_id,
                            additional_buttons=[["🎯 Guess Again", "🎲 Random Game"]] if guess != target else None,
                            is_admin=self.is_admin(user_id)
                        )
                        return True
                    except:
                        self.send_message(chat_id, "❌ Please enter a valid number.")
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
            
            print(f"📥 Admin upload: {file_name} (ID: {file_id}) by {user_id}")
            
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
                
                self.send_with_menu(
                    chat_id, 
                    f"✅ <b>Premium game ready!</b>\n\n📁 File: {file_name}\n⭐ Price: {stars_price} Stars\n📝 Description: {description}", 
                    user_id,
                    is_admin=True
                )
            
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
            keyboard.append(["🔙 Admin Menu"])
            
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
    
    def run(self):
        print("🤖 Complete Bot System running...")
        print(f"📊 Admin IDs: {self.ADMIN_IDS}")
        print(f"📺 Required channel: {self.REQUIRED_CHANNEL}")
        print(f"⭐ Stars system: Active")
        print(f"📝 Request system: Active (notifies admins)")
        print("=" * 60)
        
        offset = 0
        
        while True:
            try:
                url = self.base_url + "getUpdates"
                params = {
                    "timeout": 100, 
                    "offset": offset,
                    "allowed_updates": ["message", "callback_query", "pre_checkout_query"]
                }
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
                            elif 'callback_query' in update:
                                self.process_message(update)
                        except Exception as e:
                            print(f"❌ Update processing error: {e}")
                            traceback.print_exc()
                            continue
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
                
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                traceback.print_exc()
                time.sleep(5)

# ==================== START THE BOT ====================

if __name__ == "__main__":
    print("🚀 Starting Complete Telegram Bot System v2.0...")
    print("📝 Features: Game Storage + Stars Payments + Admin Notifications")
    print("=" * 60)
    
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
                bot_username = data['result']['username']
                print(f"✅ Bot connected: {bot_name} (@{bot_username})")
                
                bot = CrossPlatformBot(BOT_TOKEN)
                bot.run()
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            traceback.print_exc()
    else:
        print("❌ ERROR: BOT_TOKEN not set!")
        print("💡 Set BOT_TOKEN environment variable.")
        
        while True:
            time.sleep(60)
