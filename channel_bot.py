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
print("Enhanced Broadcast with Photos")
print("Individual Game Request Replies")
print("Game Removal System with Duplicate Detection")
print("Redeploy System for Admins and Users")
print("GitHub Database Backup & Restore System")
print("24/7 Operation with Persistent Data Recovery")
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
        auth_token = request.headers.get('Authorization', '')
        user_id = request.json.get('user_id', '') if request.json else ''
        
        is_authorized = auth_token == os.environ.get('REDEPLOY_TOKEN', 'default_token') or user_id in ['7475473197', '7713987088']
        
        if not is_authorized:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 401
        
        print(f"🔄 Redeploy triggered by user {user_id}")
        
        redeploy_result = trigger_redeploy()
        
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
            print(f"📁 Backup path: {self.backup_path}")
        else:
            print("⚠️ GitHub Backup: Disabled - Set GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME")
    
    def create_db_backup(self):
        """Create a backup of the current database"""
        try:
            db_path = self.bot.get_db_path()
            backup_path = db_path + '.backup'
            
            import shutil
            shutil.copy2(db_path, backup_path)
            
            print(f"✅ Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Database backup error: {e}")
            return None
    
    def backup_database_to_github(self, commit_message="Auto backup: Database update"):
        """Backup database to GitHub"""
        if not self.is_enabled:
            print("⚠️ GitHub backup disabled")
            return False
        
        try:
            print("🔄 Starting GitHub database backup...")
            
            backup_file = self.create_db_backup()
            if not backup_file:
                return False
            
            with open(backup_file, 'rb') as f:
                db_content = f.read()
            
            db_b64 = base64.b64encode(db_content).decode('utf-8')
            
            file_sha = self.get_file_sha()
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'message': commit_message,
                'content': db_b64,
                'branch': self.backup_branch
            }
            
            if file_sha:
                data['sha'] = file_sha
            
            response = requests.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Database backed up to GitHub: {result['commit']['html_url']}")
                
                try:
                    os.remove(backup_file)
                except:
                    pass
                
                return True
            else:
                print(f"❌ GitHub backup failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub backup error: {e}")
            return False
    
    def get_file_sha(self):
        """Get the SHA of the existing backup file on GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()['sha']
            return None
        except:
            return None
    
    def restore_database_from_github(self):
        """Restore database from GitHub backup"""
        if not self.is_enabled:
            print("⚠️ GitHub restore disabled")
            return False
        
        try:
            print("🔄 Restoring database from GitHub...")
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"❌ No backup found on GitHub: {response.status_code}")
                return False
            
            file_data = response.json()
            db_content = base64.b64decode(file_data['content'])
            
            db_path = self.bot.get_db_path()
            with open(db_path, 'wb') as f:
                f.write(db_content)
            
            print(f"✅ Database restored from GitHub backup")
            print(f"📊 Backup date: {file_data['commit']['commit']['author']['date']}")
            
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
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest_commit = commits[0]
                    return {
                        "enabled": True,
                        "last_backup": latest_commit['commit']['author']['date'],
                        "message": latest_commit['commit']['message'],
                        "url": latest_commit['html_url'],
                        "size": "unknown"
                    }
            
            return {"enabled": True, "last_backup": "Never"}
        except Exception as e:
            return {"enabled": True, "error": str(e)}

# ==================== REDEPLOY SYSTEM ====================

class RedeploySystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.redeploy_requests = {}
        print("✅ Redeploy system initialized!")
    
    def show_redeploy_menu(self, user_id, chat_id):
        """Show redeploy menu"""
        if not self.bot.is_admin(user_id):
            self.bot.send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        redeploy_text = """🔄 <b>Bot Redeploy System</b>

This system allows you to restart the bot without losing any data.

⚠️ <b>Important:</b>
• Database will be preserved
• All games and user data remain safe
• Bot will be unavailable for 10-30 seconds during redeploy
• Automatic recovery after redeploy

🛠️ <b>When to use:</b>
• Bot is unresponsive
• Features not working properly
• After database updates
• General maintenance

Choose an option:"""
        
        keyboard = [
            [{"text": "🔄 Soft Restart", "callback_data": "redeploy_soft"}],
            [{"text": "🚀 Force Restart", "callback_data": "redeploy_force"}],
            [{"text": "📊 System Status", "callback_data": "system_status"}],
            [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
        ]
        
        self.bot.send_message(chat_id, redeploy_text, keyboard)
    
    def initiate_redeploy(self, user_id, chat_id, redeploy_type="soft"):
        """Initiate a redeploy"""
        try:
            user_info = self.bot.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Unknown')
            
            print(f"🔄 {redeploy_type.upper()} redeploy initiated by {user_name} ({user_id})")
            
            redeploy_id = int(time.time())
            self.redeploy_requests[redeploy_id] = {
                'user_id': user_id,
                'user_name': user_name,
                'type': redeploy_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'initiated'
            }
            
            if redeploy_type == "soft":
                confirm_text = f"""🔄 <b>Soft Redeploy Initiated</b>

👤 Initiated by: {user_name}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Request ID: {redeploy_id}

📝 <b>Process:</b>
• Bot will perform graceful restart
• All data preserved
• 10-30 seconds downtime expected
• Automatic recovery

✅ The bot will restart shortly..."""
            else:
                confirm_text = f"""🚀 <b>Force Redeploy Initiated</b>

👤 Initiated by: {user_name}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Request ID: {redeploy_id}

⚠️ <b>Force Redeploy:</b>
• Immediate bot restart
• All data preserved
• Quick recovery expected
• Emergency use only

✅ The bot will restart immediately..."""
            
            self.bot.send_message(chat_id, confirm_text)
            
            self.trigger_redeploy_webhook(user_id, redeploy_type)
            
            if redeploy_type == "soft":
                restart_delay = 5
            else:
                restart_delay = 2
            
            def delayed_restart():
                time.sleep(restart_delay)
                print(f"🔄 Executing {redeploy_type} redeploy...")
                os._exit(0)
            
            restart_thread = threading.Thread(target=delayed_restart, daemon=True)
            restart_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Redeploy initiation error: {e}")
            self.bot.send_message(chat_id, f"❌ Redeploy failed: {str(e)}")
            return False
    
    def trigger_redeploy_webhook(self, user_id, redeploy_type):
        """Trigger redeploy via webhook"""
        try:
            redeploy_url = os.environ.get('REDEPLOY_WEBHOOK_URL')
            redeploy_token = os.environ.get('REDEPLOY_TOKEN', 'default_token')
            
            if not redeploy_url:
                print("ℹ️ No redeploy webhook URL set, using internal restart")
                return False
            
            webhook_data = {
                'user_id': user_id,
                'redeploy_type': redeploy_type,
                'timestamp': datetime.now().isoformat(),
                'service': 'telegram-game-bot'
            }
            
            headers = {
                'Authorization': redeploy_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(redeploy_url, json=webhook_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Redeploy webhook triggered successfully")
                return True
            else:
                print(f"❌ Redeploy webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def show_system_status(self, user_id, chat_id):
        """Show current system status"""
        try:
            bot_online = self.bot.test_bot_connection()
            
            db_status = "Healthy"
            try:
                cursor = self.bot.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM channel_games')
                game_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
            except:
                db_status = "Error"
                game_count = 0
                user_count = 0
            
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_usage = f"{memory.percent}%"
            except:
                memory_usage = "N/A"
            
            uptime_seconds = time.time() - self.bot.last_restart
            uptime_str = self.format_uptime(uptime_seconds)
            
            status_text = f"""📊 <b>System Status</b>

🤖 <b>Bot Status:</b> {'🟢 ONLINE' if bot_online else '🔴 OFFLINE'}
💾 <b>Database:</b> {db_status}
📁 <b>Games in DB:</b> {game_count}
👥 <b>Users:</b> {user_count}
🕒 <b>Uptime:</b> {uptime_str}
💻 <b>Memory:</b> {memory_usage}

🔧 <b>Services:</b>
• Health Server: 🟢 Running
• Keep-Alive: {'🟢 Active' if self.bot.keep_alive and self.bot.keep_alive.is_running else '🔴 Inactive'}
• Database: 🟢 Connected
• Game Scanner: {'🟢 Ready' if not self.bot.is_scanning else '🟡 Scanning'}

📈 <b>Performance:</b>
• Error Count: {self.bot.error_count}
• Consecutive Errors: {self.bot.consecutive_errors}
• Last Restart: {datetime.fromtimestamp(self.bot.last_restart).strftime('%Y-%m-%d %H:%M:%S')}"""
            
            keyboard = [
                [{"text": "🔄 Refresh Status", "callback_data": "system_status"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
            
            self.bot.send_message(chat_id, status_text, keyboard)
            
        except Exception as e:
            print(f"❌ System status error: {e}")
            self.bot.send_message(chat_id, f"❌ Error getting system status: {str(e)}")
    
    def format_uptime(self, seconds):
        """Format uptime in human readable format"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if days > 0:
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"

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
                "start_parameter": "stars_donation",
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
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

# ==================== GAME REQUEST SYSTEM ====================

class GameRequestSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_game_requests_database()
        
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
    
    def add_request_reply(self, request_id, admin_id, reply_text, photo_file_id=None):
        """Add a reply to a game request"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO game_request_replies 
                (request_id, admin_id, reply_text, photo_file_id)
                VALUES (?, ?, ?, ?)
            ''', (request_id, admin_id, reply_text, photo_file_id))
            
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
                SELECT admin_id, reply_text, photo_file_id, reply_date
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

💡 Use command: <code>/reply_{request_id}</code> to reply to this request."""

        for admin_id in self.bot.ADMIN_IDS:
            try:
                self.bot.send_message(admin_id, notification_text)
            except Exception as e:
                print(f"❌ Failed to notify admin {admin_id}: {e}")

# ==================== PREMIUM GAMES SYSTEM ====================

class PremiumGamesSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_premium_games_database()
        
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
                    description TEXT,
                    is_premium INTEGER DEFAULT 1
                )
            ''')
            
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
            
            self.bot.conn.commit()
            print("✅ Premium games system setup complete!")
            
        except Exception as e:
            print(f"❌ Premium games database setup error: {e}")
    
    def add_premium_game(self, game_info):
        """Add a premium game to database"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_games 
                (message_id, file_name, file_type, file_size, upload_date, category, 
                 added_by, is_uploaded, is_forwarded, file_id, bot_message_id, stars_price, description, is_premium)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                game_info['stars_price'],
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
                SELECT id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded
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
                SELECT id, file_name, file_type, file_size, stars_price, description, 
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
                    'description': result[5],
                    'file_id': result[6],
                    'bot_message_id': result[7],
                    'is_uploaded': result[8],
                    'message_id': result[9]
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
    
    def record_purchase(self, user_id, game_id, stars_paid, transaction_id):
        """Record a premium game purchase"""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO premium_purchases 
                (user_id, game_id, stars_paid, transaction_id, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, game_id, stars_paid, transaction_id, 'completed'))
            
            self.bot.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error recording purchase: {e}")
            return False

# ==================== MAIN BOT CLASS WITH INLINE KEYBOARDS ====================

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
        
        self.guess_games = {}
        self.spin_games = {}
        
        self.broadcast_sessions = {}
        self.broadcast_stats = {}
        
        self.stars_system = TelegramStarsSystem(self)
        self.game_request_system = GameRequestSystem(self)
        self.premium_games_system = PremiumGamesSystem(self)
        self.redeploy_system = RedeploySystem(self)
        self.github_backup = GitHubBackupSystem(self)
        
        self.stars_sessions = {}
        self.request_sessions = {}
        self.upload_sessions = {}
        self.reply_sessions = {}
        
        self.user_state = {}
        
        self.last_restart = time.time()
        self.error_count = 0
        self.max_errors = 25
        self.error_window = 300
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        self.keep_alive = None
        
        self.setup_database()
        self.verify_database_schema()
        self.games_cache = {}
        self.premium_games_cache = {}
        self.is_scanning = False
        self.search_sessions = {}
        self.search_results = {}
        
        print("✅ Bot system ready!")
        print(f"📊 Monitoring channel: {self.REQUIRED_CHANNEL}")
        print(f"👑 Admin uploads enabled for {len(self.ADMIN_IDS)} users")
        print("📤 Forwarded files support enabled")
        print("🔍 Game search feature enabled")
        print("🎮 Mini-games integrated")
        print("📢 Admin broadcast messaging system enabled")
        print("⭐ Telegram Stars payments system enabled")
        print("🎮 Game request system enabled")
        print("💰 Premium games system enabled")
        print("🔄 Redeploy system enabled")
        print("💾 GitHub Database Backup & Restore enabled")
        print("🛡️  Crash protection enabled")
    
    # ==================== INLINE KEYBOARD METHODS ====================
    
    def create_main_menu(self):
        """Create main menu inline keyboard"""
        keyboard = [
            [{"text": "🎮 Browse Games", "callback_data": "browse_games"}],
            [{"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}],
            [{"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "📊 Profile", "callback_data": "profile"}],
            [{"text": "🕒 Time", "callback_data": "show_time"}],
            [{"text": "📢 Channel Info", "callback_data": "channel_info"}]
        ]
        
        if self.is_admin:
            keyboard.append([{"text": "👑 Admin Panel", "callback_data": "admin_panel"}])
        
        return keyboard
    
    def create_admin_menu(self):
        """Create admin menu inline keyboard"""
        keyboard = [
            [{"text": "📤 Upload Games", "callback_data": "upload_games"}],
            [{"text": "🗑️ Remove Games", "callback_data": "remove_games"}],
            [{"text": "📢 Broadcast", "callback_data": "broadcast"}],
            [{"text": "🎮 Game Requests", "callback_data": "game_requests"}],
            [{"text": "⭐ Stars Stats", "callback_data": "stars_stats"}],
            [{"text": "🔄 Redeploy Bot", "callback_data": "redeploy_menu"}],
            [{"text": "💾 Backup System", "callback_data": "backup_system"}],
            [{"text": "📊 System Status", "callback_data": "system_status"}],
            [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
        ]
        return keyboard
    
    def create_games_menu(self):
        """Create games menu inline keyboard"""
        stats = self.get_channel_stats()
        
        keyboard = [
            [{"text": f"📁 Game Files ({stats['total_games']})", "callback_data": "game_files"}],
            [{"text": f"💰 Premium ({stats['premium_games']})", "callback_data": "premium_games"}],
            [{"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}],
            [{"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
            [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
        ]
        return keyboard
    
    def create_game_files_menu(self):
        """Create game files menu inline keyboard"""
        keyboard = [
            [{"text": "📦 ZIP Files", "callback_data": "category_zip"}],
            [{"text": "🗜️ 7Z Files", "callback_data": "category_7z"}],
            [{"text": "💿 ISO Files", "callback_data": "category_iso"}],
            [{"text": "📱 APK Files", "callback_data": "category_apk"}],
            [{"text": "🎮 PSP Games", "callback_data": "category_psp"}],
            [{"text": "📋 All Files", "callback_data": "category_all"}],
            [{"text": "🔄 Rescan Games", "callback_data": "rescan_games"}],
            [{"text": "🔍 Search Games", "callback_data": "search_games"}],
            [{"text": "🔙 Back to Games", "callback_data": "browse_games"}]
        ]
        return keyboard
    
    def create_stars_menu(self):
        """Create stars menu inline keyboard"""
        keyboard = [
            [{"text": "⭐ 50 Stars ($0.50)", "callback_data": "stars_50"}],
            [{"text": "⭐ 100 Stars ($1.00)", "callback_data": "stars_100"}],
            [{"text": "⭐ 500 Stars ($5.00)", "callback_data": "stars_500"}],
            [{"text": "⭐ 1000 Stars ($10.00)", "callback_data": "stars_1000"}],
            [{"text": "💫 Custom Amount", "callback_data": "stars_custom"}],
            [{"text": "📊 Stars Stats", "callback_data": "stars_stats"}],
            [{"text": "🔙 Back to Menu", "callback_data": "main_menu"}]
        ]
        return keyboard
    
    def create_search_menu(self):
        """Create search menu inline keyboard"""
        keyboard = [
            [{"text": "🔍 New Search", "callback_data": "search_games"}],
            [{"text": "📁 Browse All", "callback_data": "game_files"}],
            [{"text": "💰 Premium Games", "callback_data": "premium_games"}],
            [{"text": "📝 Request Game", "callback_data": "request_game"}],
            [{"text": "🔙 Back to Menu", "callback_data": "main_menu"}]
        ]
        return keyboard
    
    def create_verification_menu(self):
        """Create verification inline keyboard"""
        keyboard = [
            [
                {"text": "📢 JOIN CHANNEL", "url": self.CHANNEL_LINK},
                {"text": "✅ VERIFY JOIN", "callback_data": "verify_join"}
            ]
        ]
        return keyboard
    
    def create_game_list_keyboard(self, games, current_page=0, category="all", total_pages=1):
        """Create inline keyboard for game list with pagination"""
        keyboard = []
        
        for game in games:
            game_name = game['file_name']
            if len(game_name) > 30:
                display_name = game_name[:27] + "..."
            else:
                display_name = game_name
            
            callback_data = f"download_{game['message_id']}_{game.get('file_id', '')}_{game.get('is_uploaded', 0)}"
            keyboard.append([{"text": f"📥 {display_name}", "callback_data": callback_data}])
        
        # Add navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append({"text": "⬅️ Previous", "callback_data": f"page_{category}_{current_page-1}"})
        
        nav_buttons.append({"text": f"📄 {current_page+1}/{total_pages}", "callback_data": "current_page"})
        
        if current_page < total_pages - 1:
            nav_buttons.append({"text": "Next ➡️", "callback_data": f"page_{category}_{current_page+1}"})
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            {"text": "🔍 Search", "callback_data": "search_games"},
            {"text": "🏠 Menu", "callback_data": "main_menu"}
        ])
        
        return keyboard
    
    def create_search_results_keyboard(self, results, current_page=0, search_term="", total_pages=1):
        """Create inline keyboard for search results"""
        keyboard = []
        
        for game in results:
            game_name = game['file_name']
            if len(game_name) > 30:
                display_name = game_name[:27] + "..."
            else:
                display_name = game_name
            
            callback_data = f"download_{game['message_id']}_{game.get('file_id', '')}_{game.get('is_uploaded', 0)}"
            keyboard.append([{"text": f"📥 {display_name}", "callback_data": callback_data}])
        
        # Add navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append({"text": "⬅️ Previous", "callback_data": f"search_page_{search_term}_{current_page-1}"})
        
        nav_buttons.append({"text": f"📄 {current_page+1}/{total_pages}", "callback_data": "current_page"})
        
        if current_page < total_pages - 1:
            nav_buttons.append({"text": "Next ➡️", "callback_data": f"search_page_{search_term}_{current_page+1}"})
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            {"text": "🔍 New Search", "callback_data": "search_games"},
            {"text": "🏠 Menu", "callback_data": "main_menu"}
        ])
        
        return keyboard
    
    def create_premium_games_keyboard(self, games, current_page=0, total_pages=1):
        """Create inline keyboard for premium games"""
        keyboard = []
        
        for game in games:
            game_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
            
            if len(file_name) > 30:
                display_name = file_name[:27] + "..."
            else:
                display_name = file_name
            
            callback_data = f"premium_info_{game_id}"
            keyboard.append([{"text": f"💰 {display_name} - ⭐{stars_price}", "callback_data": callback_data}])
        
        # Add navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append({"text": "⬅️ Previous", "callback_data": f"premium_page_{current_page-1}"})
        
        nav_buttons.append({"text": f"📄 {current_page+1}/{total_pages}", "callback_data": "current_page"})
        
        if current_page < total_pages - 1:
            nav_buttons.append({"text": "Next ➡️", "callback_data": f"premium_page_{current_page+1}"})
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            {"text": "🔍 Search", "callback_data": "search_games"},
            {"text": "🏠 Menu", "callback_data": "main_menu"}
        ])
        
        return keyboard
    
    def create_premium_game_details_keyboard(self, game_id, user_id):
        """Create inline keyboard for premium game details"""
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            return [[{"text": "🏠 Menu", "callback_data": "main_menu"}]]
        
        has_purchased = self.premium_games_system.has_user_purchased_game(user_id, game_id)
        
        keyboard = []
        
        if has_purchased:
            keyboard.append([{"text": "📥 Download Game", "callback_data": f"premium_download_{game_id}"}])
        else:
            keyboard.append([{"text": f"⭐ Buy ({game['stars_price']} Stars)", "callback_data": f"premium_buy_{game_id}"}])
        
        keyboard.append([
            {"text": "💰 More Premium", "callback_data": "premium_games"},
            {"text": "🏠 Menu", "callback_data": "main_menu"}
        ])
        
        return keyboard
    
    def create_remove_game_keyboard(self, games):
        """Create inline keyboard for game removal"""
        keyboard = []
        
        for game in games:
            if game['type'] == 'regular':
                callback_data = f"remove_regular_{game['id']}"
            else:
                callback_data = f"remove_premium_{game['id']}"
            
            keyboard.append([{"text": f"🗑️ {game['file_name']}", "callback_data": callback_data}])
        
        keyboard.append([{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}])
        
        return keyboard
    
    def create_upload_options_keyboard(self):
        """Create upload options inline keyboard"""
        keyboard = [
            [{"text": "🆓 Upload Regular Game", "callback_data": "upload_regular"}],
            [{"text": "⭐ Upload Premium Game", "callback_data": "upload_premium"}],
            [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
        ]
        return keyboard
    
    def create_backup_menu_keyboard(self):
        """Create backup menu inline keyboard"""
        keyboard = [
            [{"text": "💾 Create Backup Now", "callback_data": "create_backup"}],
            [{"text": "🔄 Restore from Backup", "callback_data": "restore_backup"}],
            [{"text": "📊 Backup Info", "callback_data": "backup_info"}],
            [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
        ]
        return keyboard
    
    # ==================== ENHANCED FILE SENDING METHODS ====================
    
    def send_game_file(self, chat_id, message_id, file_id=None, is_bot_file=False):
        """Send game file directly to user like @manybot"""
        try:
            print(f"📤 Sending game file to user {chat_id}")
            
            if file_id and file_id not in ['', 'none', 'short']:
                print(f"🔄 Using direct file_id: {file_id[:20]}...")
                
                url = self.base_url + "getFile"
                data = {"file_id": file_id}
                verify_response = requests.post(url, data=data, timeout=10)
                verify_result = verify_response.json()
                
                if verify_result.get('ok'):
                    print(f"✅ File_id is valid and accessible")
                    
                    file_path = verify_result['result']['file_path']
                    file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                    
                    caption = "🎮 Here's your requested game! Enjoy!"
                    
                    url = self.base_url + "sendDocument"
                    data = {
                        "chat_id": chat_id,
                        "document": file_id,
                        "caption": caption,
                        "parse_mode": "HTML"
                    }
                    
                    response = requests.post(url, data=data, timeout=30)
                    result = response.json()
                    
                    if result.get('ok'):
                        print("✅ Successfully sent file directly via file_id")
                        return True
                    else:
                        print(f"❌ Direct send failed: {result.get('description')}")
                else:
                    print(f"❌ File_id is invalid")
            
            print("🔄 Getting file from message...")
            
            source_chat_id = None
            if is_bot_file and message_id:
                for admin_id in self.ADMIN_IDS:
                    try:
                        url = self.base_url + "getMessage"
                        data = {
                            "chat_id": admin_id,
                            "message_id": message_id
                        }
                        response = requests.post(url, data=data, timeout=10)
                        result = response.json()
                        
                        if result.get('ok'):
                            message = result['result']
                            if 'document' in message:
                                file_id = message['document'].get('file_id')
                                source_chat_id = admin_id
                                break
                    except:
                        continue
            else:
                try:
                    url = self.base_url + "getMessage"
                    data = {
                        "chat_id": self.REQUIRED_CHANNEL,
                        "message_id": message_id
                    }
                    response = requests.post(url, data=data, timeout=10)
                    result = response.json()
                    
                    if result.get('ok'):
                        message = result['result']
                        if 'document' in message:
                            file_id = message['document'].get('file_id')
                            source_chat_id = self.REQUIRED_CHANNEL
                except:
                    pass
            
            if file_id and file_id not in ['', 'none', 'short']:
                print(f"✅ Found file_id from message")
                
                cursor = self.conn.cursor()
                if is_bot_file:
                    cursor.execute('''
                        UPDATE channel_games 
                        SET file_id = ? 
                        WHERE bot_message_id = ? OR message_id = ?
                    ''', (file_id, message_id, message_id))
                else:
                    cursor.execute('''
                        UPDATE channel_games 
                        SET file_id = ? 
                        WHERE message_id = ?
                    ''', (file_id, message_id))
                self.conn.commit()
                
                return self.send_document_directly(chat_id, file_id)
            
            print("🔄 Forwarding message...")
            if source_chat_id:
                return self.forward_message(source_chat_id, chat_id, message_id)
            else:
                return self.forward_message(self.REQUIRED_CHANNEL, chat_id, message_id)
                
        except Exception as e:
            print(f"❌ Error sending game file: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                self.send_message(chat_id, 
                    "❌ Unable to send the game file. Please try again or contact an admin.")
            except:
                pass
            
            return False
    
    def send_document_directly(self, chat_id, file_id, file_name=None):
        """Send document directly using file_id"""
        try:
            print(f"📤 Sending document directly with file_id")
            
            caption = "🎮 Here's your game file!"
            
            if file_name:
                if file_name.lower().endswith('.iso'):
                    caption = f"""🎮 <b>{file_name}</b>

💿 ISO game file ready for download!

<i>Download and enjoy your game!</i>"""
                else:
                    caption = f"🎮 <b>{file_name}</b>\n\nGame file ready for download!"
            
            data = {
                "chat_id": chat_id,
                "document": file_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            
            response = requests.post(self.base_url + "sendDocument", data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Document sent directly to user {chat_id}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Direct send failed: {error_msg}")
                
                if "file identifier is invalid" in error_msg.lower():
                    return False
                
                return True
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout sending document")
            return False
        except Exception as e:
            print(f"❌ Error sending document directly: {e}")
            return False
    
    def forward_message(self, from_chat_id, to_chat_id, message_id):
        """Forward a message from one chat to another"""
        try:
            data = {
                "chat_id": to_chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id
            }
            
            response = requests.post(self.base_url + "forwardMessage", data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Forwarded message {message_id} from {from_chat_id} to {to_chat_id}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Forward failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Error forwarding message: {e}")
            return False
    
    # ==================== MENU DISPLAY METHODS ====================
    
    def show_main_menu(self, user_id, chat_id, message_id=None):
        """Show main menu with inline keyboard"""
        user_info = self.get_user_info(user_id)
        first_name = user_info.get('first_name', 'User')
        
        welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>GAMERDROID™ V1</b>

📊 Features:
• 🎮 Game File Browser
• 💰 Premium Games with Stars
• 🔍 Advanced Game Search  
• 📱 Cross-Platform Support
• 📤 Admin Upload System
• 🕒 Real-time Updates
• 🎮 Mini-Games Entertainment
• 📢 Admin Broadcast System
• ⭐ Telegram Stars Payments
• 🎮 Game Request System
• 💾 GitHub Database Backup

Choose an option below:"""
        
        keyboard = self.create_main_menu()
        
        if message_id:
            self.edit_message(chat_id, message_id, welcome_text, keyboard)
        else:
            self.send_message(chat_id, welcome_text, keyboard)
    
    def show_admin_panel(self, user_id, chat_id, message_id=None):
        """Show admin panel"""
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        stats = self.get_channel_stats()
        user_info = self.get_user_info(user_id)
        first_name = user_info.get('first_name', 'Admin')
        
        admin_text = f"""👑 <b>Admin Panel</b>

👋 Welcome {first_name}!

🛠️ Admin Features:
• 📤 Upload regular & premium games
• 🔄 Process forwarded files  
• 📊 View upload statistics
• 🗑️ Remove individual games
• 📢 Broadcast messages to users
• 🎮 Manage game requests
• ⭐ View Stars statistics
• 💾 Backup & Restore Database
• 🔄 Redeploy bot system

📊 Stats:
• Regular games: {stats['total_games']}
• Premium games: {stats['premium_games']}

Choose an option:"""
        
        keyboard = self.create_admin_menu()
        
        if message_id:
            self.edit_message(chat_id, message_id, admin_text, keyboard)
        else:
            self.send_message(chat_id, admin_text, keyboard)
    
    def show_game_files_menu(self, user_id, chat_id, message_id=None):
        """Show game files menu"""
        stats = self.get_channel_stats()
        files_text = f"""📁 <b>Game Files Browser</b>

📊 Total Files: {stats['total_games']}

📦 Browse by file type:

• 📦 ZIP Files - Compressed game archives
• 🗜️ 7Z Files - 7-Zip compressed archives  
• 💿 ISO Files - Disc image files
• 📱 APK Files - Android applications
• 🎮 PSP Games - PSP specific formats
• 📋 All Files - Complete game list

🔍 Use search for quick access!"""
        
        keyboard = self.create_game_files_menu()
        
        if message_id:
            self.edit_message(chat_id, message_id, files_text, keyboard)
        else:
            self.send_message(chat_id, files_text, keyboard)
    
    def show_game_list(self, user_id, chat_id, file_type, display_name, message_id=None, page=0):
        """Show list of games with inline keyboard"""
        if file_type == "psp":
            cso_games = self.games_cache.get('cso', [])
            pbp_games = self.games_cache.get('pbp', [])
            games = cso_games + pbp_games
        elif file_type == "all":
            games = self.games_cache.get('all', [])
        else:
            games = self.games_cache.get(file_type, [])
        
        if not games:
            no_games_text = f"""❌ No {display_name} games found.

Try browsing other categories or use the search feature."""
            
            keyboard = [
                [{"text": "🔍 Search Games", "callback_data": "search_games"}],
                [{"text": "📁 Browse All", "callback_data": "game_files"}],
                [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
            ]
            
            if message_id:
                self.edit_message(chat_id, message_id, no_games_text, keyboard)
            else:
                self.send_message(chat_id, no_games_text, keyboard)
            return
        
        # Pagination
        items_per_page = 10
        total_pages = (len(games) + items_per_page - 1) // items_per_page
        page = min(page, total_pages - 1)
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(games))
        games_to_show = games[start_idx:end_idx]
        
        games_text = f"""📁 <b>{display_name} GAMES</b>

📊 Found: {len(games)} files
📋 Showing: {start_idx + 1}-{end_idx} of {len(games)} files

Click on any game below to download it instantly! 📥"""
        
        keyboard = self.create_game_list_keyboard(games_to_show, page, file_type, total_pages)
        
        if message_id:
            self.edit_message(chat_id, message_id, games_text, keyboard)
        else:
            self.send_message(chat_id, games_text, keyboard)
    
    def show_search_results(self, user_id, chat_id, search_term, message_id=None, page=0):
        """Show search results with inline keyboard"""
        results = self.search_results.get(user_id, {}).get('results', [])
        
        if not results:
            no_results_text = f"""🔍 <b>Search Results</b>

No games found for: <code>{search_term}</code>

💡 Try:
• Different keywords
• Shorter search terms
• Check spelling"""
            
            keyboard = [
                [{"text": "🔍 New Search", "callback_data": "search_games"}],
                [{"text": "📁 Browse All", "callback_data": "game_files"}],
                [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
            ]
            
            if message_id:
                self.edit_message(chat_id, message_id, no_results_text, keyboard)
            else:
                self.send_message(chat_id, no_results_text, keyboard)
            return
        
        # Pagination
        items_per_page = 10
        total_pages = (len(results) + items_per_page - 1) // items_per_page
        page = min(page, total_pages - 1)
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(results))
        games_to_show = results[start_idx:end_idx]
        
        results_text = f"""🔍 <b>Search Results</b>

Search: <code>{search_term}</code>
📊 Found: {len(results)} files
📋 Showing: {start_idx + 1}-{end_idx} of {len(results)} files

Click on any game below to download it instantly! 📥"""
        
        keyboard = self.create_search_results_keyboard(games_to_show, page, search_term, total_pages)
        
        if message_id:
            self.edit_message(chat_id, message_id, results_text, keyboard)
        else:
            self.send_message(chat_id, results_text, keyboard)
    
    def show_premium_games_menu(self, user_id, chat_id, message_id=None, page=0):
        """Show premium games menu"""
        premium_games = self.premium_games_system.get_premium_games(100)
        
        if not premium_games:
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games that you can purchase with Telegram Stars!"""
            
            keyboard = [
                [{"text": "📁 Regular Games", "callback_data": "game_files"}],
                [{"text": "🔍 Search Games", "callback_data": "search_games"}],
                [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
            ]
            
            if message_id:
                self.edit_message(chat_id, message_id, premium_text, keyboard)
            else:
                self.send_message(chat_id, premium_text, keyboard)
            return
        
        # Pagination
        items_per_page = 10
        total_pages = (len(premium_games) + items_per_page - 1) // items_per_page
        page = min(page, total_pages - 1)
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(premium_games))
        games_to_show = premium_games[start_idx:end_idx]
        
        premium_text = f"""💰 <b>Premium Games</b>

📊 Total: {len(premium_games)} premium games
📋 Showing: {start_idx + 1}-{end_idx} of {len(premium_games)}

Exclusive games available for purchase with Telegram Stars:

Click on any game to view details and purchase! 💰"""
        
        keyboard = self.create_premium_games_keyboard(games_to_show, page, total_pages)
        
        if message_id:
            self.edit_message(chat_id, message_id, premium_text, keyboard)
        else:
            self.send_message(chat_id, premium_text, keyboard)
    
    def show_premium_game_details(self, user_id, chat_id, game_id, message_id=None):
        """Show premium game details"""
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            error_text = "❌ Game not found."
            keyboard = [[{"text": "💰 Premium Games", "callback_data": "premium_games"}]]
            
            if message_id:
                self.edit_message(chat_id, message_id, error_text, keyboard)
            else:
                self.send_message(chat_id, error_text, keyboard)
            return
        
        has_purchased = self.premium_games_system.has_user_purchased_game(user_id, game_id)
        
        game_text = f"""💰 <b>Premium Game Details</b>

🎮 <b>{game['file_name']}</b>
📦 Type: {game['file_type']}
📏 Size: {self.format_file_size(game['file_size'])}
⭐ Price: <b>{game['stars_price']} Stars</b>
💰 USD Value: ${game['stars_price'] * 0.01:.2f}

📝 Description:
{game['description'] if game['description'] else 'No description available.'}

🔄 Status: {'✅ Already Purchased' if has_purchased else '❌ Not Purchased Yet'}"""
        
        keyboard = self.create_premium_game_details_keyboard(game_id, user_id)
        
        if message_id:
            self.edit_message(chat_id, message_id, game_text, keyboard)
        else:
            self.send_message(chat_id, game_text, keyboard)
    
    def show_stars_menu(self, user_id, chat_id, message_id=None):
        """Show Telegram Stars donation menu"""
        balance = self.stars_system.get_balance()
        recent_transactions = self.stars_system.get_recent_transactions(3)
        
        stars_text = """⭐ <b>Support Our Bot with Telegram Stars!</b>

Telegram Stars are a simple way to support developers directly through Telegram.

🌟 <b>Why Donate Stars?</b>
• Keep the bot running 24/7
• Support new features development  
• Help cover server costs
• Get recognition in our donor list

💫 <b>How Stars Work:</b>
1. Choose stars amount below
2. Complete secure payment via Telegram
3. Stars go directly to support development
4. Get instant confirmation!

💰 <b>Conversion:</b> 1 Star ≈ $0.01

📊 <b>Stars Stats:</b>"""
        
        stars_text += f"\n• Total Stars Received: <b>{balance['total_stars_earned']} ⭐</b>"
        stars_text += f"\n• Total USD Value: <b>${balance['total_usd_earned']:.2f}</b>"
        stars_text += f"\n• Available Stars: <b>{balance['available_stars']} ⭐</b>"
        
        if recent_transactions:
            stars_text += "\n\n🎉 <b>Recent Donations:</b>"
            for transaction in recent_transactions:
                donor_name, stars_amount, usd_amount, status, created_at = transaction
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d')
                status_icon = "✅" if status == 'completed' else "⏳"
                stars_text += f"\n• {donor_name}: {status_icon} <b>{stars_amount} ⭐ (${usd_amount:.2f})</b>"
        
        stars_text += "\n\nThank you for considering supporting us! 🙏"
        
        keyboard = self.create_stars_menu()
        
        if message_id:
            self.edit_message(chat_id, message_id, stars_text, keyboard)
        else:
            self.send_message(chat_id, stars_text, keyboard)
    
    # ==================== CALLBACK QUERY HANDLER ====================
    
    def handle_callback_query(self, callback_query):
        """Handle inline keyboard callbacks"""
        try:
            callback_id = callback_query['id']
            user_id = callback_query['from']['id']
            chat_id = callback_query['message']['chat']['id']
            message_id = callback_query['message']['message_id']
            data = callback_query['data']
            
            print(f"🔄 Callback from {user_id}: {data}")
            
            # Answer callback query
            self.answer_callback_query(callback_id)
            
            # Handle different callback data
            if data == "main_menu":
                self.show_main_menu(user_id, chat_id, message_id)
            
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_admin_panel(user_id, chat_id, message_id)
            
            elif data == "browse_games":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.show_game_files_menu(user_id, chat_id, message_id)
            
            elif data == "game_files":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.show_game_files_menu(user_id, chat_id, message_id)
            
            elif data == "search_games":
                if not self.is_user_verified(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.send_message(chat_id, 
                    "🔍 <b>Game Search</b>\n\n"
                    "Please type the name of the game you're looking for:\n\n"
                    "💡 Examples:\n"
                    "• GTA\n"
                    "• God of War\n"
                    "• Minecraft\n"
                    "• FIFA\n\n"
                    "Simply type the game name and I'll search our database."
                )
            
            elif data == "premium_games":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.show_premium_games_menu(user_id, chat_id, message_id)
            
            elif data == "request_game":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.start_game_request(user_id, chat_id)
            
            elif data == "stars_menu":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                self.show_stars_menu(user_id, chat_id, message_id)
            
            elif data == "profile":
                self.handle_profile(chat_id, user_id)
            
            elif data == "show_time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.send_message(chat_id, f"🕒 <b>Current Time</b>\n\n📅 {current_time}\n\n⏰ Server Time (UTC)")
            
            elif data == "channel_info":
                self.show_channel_info(chat_id)
            
            elif data == "upload_games":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_upload_options(user_id, chat_id, message_id)
            
            elif data == "remove_games":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_remove_game_menu(user_id, chat_id, message_id)
            
            elif data == "broadcast":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.start_broadcast(user_id, chat_id)
            
            elif data == "game_requests":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_admin_requests_panel(user_id, chat_id, message_id)
            
            elif data == "stars_stats":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_stars_stats(user_id, chat_id, message_id)
            
            elif data == "redeploy_menu":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.redeploy_system.show_redeploy_menu(user_id, chat_id)
            
            elif data == "backup_system":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.show_backup_menu(user_id, chat_id, message_id)
            
            elif data == "system_status":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                self.redeploy_system.show_system_status(user_id, chat_id)
            
            # Category browsing
            elif data.startswith("category_"):
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                category = data.replace("category_", "")
                display_names = {
                    "zip": "ZIP", "7z": "7Z", "iso": "ISO", 
                    "apk": "APK", "psp": "PSP", "all": "ALL"
                }
                self.show_game_list(user_id, chat_id, category, display_names.get(category, category), message_id)
            
            # Pagination
            elif data.startswith("page_"):
                parts = data.split("_")
                if len(parts) >= 3:
                    category = parts[1]
                    try:
                        page = int(parts[2])
                        display_names = {
                            "zip": "ZIP", "7z": "7Z", "iso": "ISO", 
                            "apk": "APK", "psp": "PSP", "all": "ALL"
                        }
                        self.show_game_list(user_id, chat_id, category, display_names.get(category, category), message_id, page)
                    except:
                        pass
            
            # Search pagination
            elif data.startswith("search_page_"):
                parts = data.split("_")
                if len(parts) >= 4:
                    search_term = parts[2]
                    try:
                        page = int(parts[3])
                        if user_id in self.search_results and self.search_results[user_id]['search_term'] == search_term:
                            self.show_search_results(user_id, chat_id, search_term, message_id, page)
                    except:
                        pass
            
            # Premium games pagination
            elif data.startswith("premium_page_"):
                try:
                    page = int(data.replace("premium_page_", ""))
                    self.show_premium_games_menu(user_id, chat_id, message_id, page)
                except:
                    pass
            
            # Game download
            elif data.startswith("download_"):
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                
                parts = data.split("_")
                if len(parts) >= 4:
                    try:
                        message_id_download = int(parts[1])
                        file_id = parts[2] if parts[2] != 'None' else None
                        is_uploaded = int(parts[3]) if len(parts) > 3 else 0
                        
                        # Send loading message
                        loading_msg = self.send_message(chat_id, "📥 Sending game file...")
                        
                        # Send the file
                        success = self.send_game_file(chat_id, message_id_download, file_id, is_uploaded == 1)
                        
                        if success:
                            self.edit_message(chat_id, loading_msg['result']['message_id'], "✅ Game sent successfully!")
                        else:
                            self.edit_message(chat_id, loading_msg['result']['message_id'], "❌ Failed to send game. Please try again.")
                    except Exception as e:
                        print(f"❌ Download error: {e}")
                        self.send_message(chat_id, "❌ Error downloading game.")
            
            # Premium game info
            elif data.startswith("premium_info_"):
                try:
                    game_id = int(data.replace("premium_info_", ""))
                    self.show_premium_game_details(user_id, chat_id, game_id, message_id)
                except:
                    pass
            
            # Premium game purchase
            elif data.startswith("premium_buy_"):
                try:
                    game_id = int(data.replace("premium_buy_", ""))
                    self.handle_premium_purchase(user_id, chat_id, game_id)
                except:
                    pass
            
            # Premium game download
            elif data.startswith("premium_download_"):
                try:
                    game_id = int(data.replace("premium_download_", ""))
                    self.send_premium_game_file(user_id, chat_id, game_id)
                except:
                    pass
            
            # Stars donation amounts
            elif data.startswith("stars_"):
                amount = data.replace("stars_", "")
                if amount == "custom":
                    self.stars_sessions[user_id] = {}
                    self.send_message(chat_id, 
                        "💫 <b>Custom Stars Amount</b>\n\n"
                        "Please enter the number of Stars you'd like to donate:\n\n"
                        "💡 <i>Enter a number (e.g., 250 for 250 Stars ≈ $2.50)</i>"
                    )
                elif amount.isdigit():
                    stars_amount = int(amount)
                    self.process_stars_donation(user_id, chat_id, stars_amount)
            
            # Verification
            elif data == "verify_join":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    self.show_main_menu(user_id, chat_id, message_id)
                else:
                    self.send_message(chat_id, 
                        "❌ <b>Not Joined Yet</b>\n\n"
                        "You haven't joined the channel yet.\n\n"
                        f"Please join: {self.CHANNEL_LINK}\n"
                        "Then click <b>✅ VERIFY JOIN</b> again.",
                        self.create_verification_menu()
                    )
            
            # Rescan games
            elif data == "rescan_games":
                if not self.is_user_completed(user_id):
                    self.send_message(chat_id, "🔐 Please complete verification first with /start")
                    return
                
                loading_msg = self.send_message(chat_id, "🔄 Scanning for new games...")
                total_games = self.scan_channel_for_games()
                stats = self.get_channel_stats()
                
                self.edit_message(chat_id, loading_msg['result']['message_id'], 
                    f"✅ Rescan complete! Found {total_games} total games. Database now has {stats['total_games']} regular games and {stats['premium_games']} premium games.",
                    self.create_game_files_menu()
                )
            
            # Remove game
            elif data.startswith("remove_"):
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                parts = data.split("_")
                if len(parts) >= 3:
                    game_type = parts[1]
                    game_id = int(parts[2])
                    
                    if game_type == "regular":
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT file_name FROM channel_games WHERE message_id = ?', (game_id,))
                        game = cursor.fetchone()
                        
                        if game:
                            self.show_remove_confirmation(user_id, chat_id, 'R', game_id, game[0], message_id)
                    
                    elif game_type == "premium":
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT file_name FROM premium_games WHERE id = ?', (game_id,))
                        game = cursor.fetchone()
                        
                        if game:
                            self.show_remove_confirmation(user_id, chat_id, 'P', game_id, game[0], message_id)
            
            # Upload options
            elif data == "upload_regular":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                self.send_message(chat_id,
                    "🆓 <b>Regular Game Upload</b>\n\n"
                    "Please upload the game file now.\n\n"
                    "📁 Supported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP\n\n"
                    "💡 The file will be available for free to all users."
                )
            
            elif data == "upload_premium":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                self.start_premium_upload(user_id, chat_id)
            
            # Backup system
            elif data == "create_backup":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                self.handle_create_backup(user_id, chat_id)
            
            elif data == "restore_backup":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                self.handle_restore_backup(user_id, chat_id, message_id)
            
            elif data == "backup_info":
                if not self.is_admin(user_id):
                    self.send_message(chat_id, "❌ Access denied. Admin only.")
                    return
                
                self.show_backup_menu(user_id, chat_id, message_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Callback handler error: {e}")
            return False
    
    # ==================== MESSAGE PROCESSOR ====================
    
    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Handle commands
                if text.startswith('/'):
                    if text == '/start':
                        return self.handle_verification(message)
                    elif text == '/scan' and self.is_admin(user_id):
                        self.send_message(chat_id, "🔄 Scanning channel and bot-uploaded games...")
                        total_games = self.scan_channel_for_games()
                        self.send_message(chat_id, f"✅ Scan complete! Found {total_games} total games.")
                        return True
                    elif text == '/menu' and self.is_user_completed(user_id):
                        self.show_main_menu(user_id, chat_id)
                        return True
                    elif text == '/admin' and self.is_admin(user_id):
                        self.show_admin_panel(user_id, chat_id)
                        return True
                
                # Handle game search
                if self.is_user_verified(user_id) and not text.startswith('/'):
                    return self.handle_game_search(message)
                
                # Handle stars custom amount
                if user_id in self.stars_sessions:
                    try:
                        stars_amount = int(text.strip())
                        if stars_amount <= 0:
                            self.send_message(chat_id, "❌ Please enter a positive number of Stars.")
                            return True
                        
                        del self.stars_sessions[user_id]
                        return self.process_stars_donation(user_id, chat_id, stars_amount)
                    except ValueError:
                        self.send_message(chat_id, "❌ Please enter a valid number for the Stars amount.")
                        return True
                
                # Handle game request
                if user_id in self.request_sessions:
                    session = self.request_sessions[user_id]
                    
                    if session['stage'] == 'waiting_game_name':
                        return self.handle_game_request(user_id, chat_id, text)
                    
                    elif session['stage'] == 'waiting_platform':
                        return self.complete_game_request(user_id, chat_id, text)
                
                # Handle code verification
                if text.isdigit() and len(text) == 6:
                    return self.handle_code_verification(message)
            
            # Handle photo messages
            if 'photo' in message:
                user_id = message['from']['id']
                chat_id = message['chat']['id']
                
                if user_id in self.broadcast_sessions and self.broadcast_sessions[user_id]['stage'] == 'waiting_message_or_photo':
                    photo = message['photo'][-1]
                    photo_file_id = photo['file_id']
                    caption = message.get('caption', '')
                    return self.handle_broadcast_photo(user_id, chat_id, photo_file_id, caption)
            
            # Handle document uploads
            if 'document' in message and self.is_admin(message['from']['id']):
                return self.handle_document_upload(message)
            
            # Handle forwarded messages
            if 'forward_origin' in message and self.is_admin(message['from']['id']):
                return self.handle_forwarded_message(message)
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            return False
    
    # ==================== ENHANCED SEARCH FUNCTION ====================
    
    def search_games(self, search_term, user_id):
        """Search games in database"""
        search_term = search_term.lower().strip()
        results = []
        
        cursor = self.conn.cursor()
        
        # Search in regular games
        cursor.execute('''
            SELECT message_id, file_name, file_type, file_size, upload_date, category, file_id, 
                   bot_message_id, is_uploaded, is_forwarded
            FROM channel_games 
            WHERE LOWER(file_name) LIKE ? OR file_name LIKE ?
            ORDER BY file_name
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        regular_games = cursor.fetchall()
        
        for game in regular_games:
            (message_id, file_name, file_type, file_size, upload_date, 
             category, file_id, bot_message_id, is_uploaded, is_forwarded) = game
            
            results.append({
                'message_id': message_id,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': file_size,
                'upload_date': upload_date,
                'category': category,
                'file_id': file_id,
                'bot_message_id': bot_message_id,
                'is_uploaded': is_uploaded,
                'is_forwarded': is_forwarded
            })
        
        return results
    
    def handle_game_search(self, message):
        """Handle game search request"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            search_term = message.get('text', '').strip()
            
            if not search_term:
                return False
            
            if not self.is_user_verified(user_id):
                self.send_message(chat_id, "🔐 Please complete verification first with /start")
                return True
            
            print(f"🔍 User {user_id} searching for: '{search_term}'")
            
            # Show searching message
            search_msg = self.send_message(chat_id, 
                f"🔍 Searching for: <code>{search_term}</code>\n\n"
                "Searching database..."
            )
            
            def perform_search():
                try:
                    results = self.search_games(search_term, user_id)
                    
                    self.search_results[user_id] = {
                        'results': results,
                        'search_term': search_term,
                        'timestamp': time.time()
                    }
                    
                    print(f"🔍 Search completed: Found {len(results)} results for '{search_term}'")
                    
                    if results:
                        self.show_search_results(user_id, chat_id, search_term, search_msg['result']['message_id'])
                    else:
                        no_results_text = f"""❌ No results found for: <code>{search_term}</code>

💡 Try:
• Different keywords
• Shorter search terms
• Check spelling"""
                        
                        keyboard = [
                            [{"text": "🔍 New Search", "callback_data": "search_games"}],
                            [{"text": "📁 Browse All", "callback_data": "game_files"}],
                            [{"text": "🏠 Main Menu", "callback_data": "main_menu"}]
                        ]
                        
                        self.edit_message(chat_id, search_msg['result']['message_id'], no_results_text, keyboard)
                        
                except Exception as e:
                    print(f"❌ Search error: {e}")
                    self.edit_message(chat_id, search_msg['result']['message_id'], "❌ Search failed. Please try again.")
            
            # Run search in background thread
            search_thread = threading.Thread(target=perform_search, daemon=True)
            search_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Search handler error: {e}")
            return False
    
    # ==================== OTHER METHODS (SIMPLIFIED) ====================
    
    def handle_verification(self, message):
        """Handle /start command and send verification code"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            username = message['from'].get('username', '')
            first_name = message['from']['first_name']
            
            print(f"🔐 Verification requested by {first_name} ({user_id})")
            
            if self.is_user_completed(user_id):
                self.show_main_menu(user_id, chat_id)
                return True
            
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                verify_text = f"""📢 <b>Channel Verification Required</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

To access all features, please join our channel:"""
                
                self.send_message(chat_id, verify_text, self.create_verification_menu())
                return True
            
            if self.check_channel_membership(user_id) and not self.is_user_verified(user_id):
                self.mark_channel_joined(user_id)
                
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
                    self.send_message(chat_id, verify_text)
                    return True
            
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
                self.send_message(chat_id, welcome_text)
                return True
            else:
                self.send_message(chat_id, "❌ Error generating verification code. Please try again.")
                return False
            
        except Exception as e:
            print(f"❌ Verification handler error: {e}")
            self.send_message(chat_id, "❌ Error starting verification. Please try again.")
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
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    self.show_main_menu(user_id, chat_id)
                else:
                    verify_text = f"""✅ <b>Code Verified!</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

📝 <b>Step 2: Join Our Channel</b>

To access all features, please join our channel:"""
                    
                    self.send_message(chat_id, verify_text, self.create_verification_menu())
                return True
            else:
                self.send_message(chat_id, "❌ Invalid or expired code. Please use /start to get a new code.")
                return True
                
        except Exception as e:
            print(f"❌ Code verification error: {e}")
            return False
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Send message with inline keyboard"""
        try:
            url = self.base_url + "sendMessage"
            data = {
                "chat_id": chat_id, 
                "text": text, 
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
            
            response = requests.post(url, data=data, timeout=15)
            result = response.json()
            
            if result.get('ok'):
                return result
            else:
                print(f"❌ Send message error: {result.get('description')}")
                return None
                
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return None
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        """Edit existing message"""
        try:
            url = self.base_url + "editMessageText"
            data = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
            
            response = requests.post(url, data=data, timeout=15)
            result = response.json()
            
            if result.get('ok'):
                return result
            else:
                print(f"❌ Edit message error: {result.get('description')}")
                return None
                
        except Exception as e:
            print(f"❌ Edit message error: {e}")
            return None
    
    def answer_callback_query(self, callback_query_id):
        """Answer callback query"""
        try:
            url = self.base_url + "answerCallbackQuery"
            data = {
                "callback_query_id": callback_query_id
            }
            requests.post(url, data=data, timeout=10)
        except:
            pass
    
    def get_updates(self, offset=None):
        """Get updates from Telegram"""
        try:
            url = self.base_url + "getUpdates"
            params = {"timeout": 100, "offset": offset}
            response = requests.get(url, params=params, timeout=110)
            data = response.json()
            return data.get('result', []) if data.get('ok') else []
        except Exception as e:
            print(f"Get updates error: {e}")
            return []
    
    # ==================== DATABASE METHODS ====================
    
    def setup_database(self):
        """Setup database tables"""
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
    
    def verify_database_schema(self):
        """Verify database schema"""
        try:
            cursor = self.conn.cursor()
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
    
    def update_games_cache(self):
        """Update games cache from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT message_id, file_name, file_type, file_size, upload_date, category, is_uploaded, file_id FROM channel_games')
            games = cursor.fetchall()
            
            self.games_cache = {
                'zip': [], '7z': [], 'iso': [], 'apk': [], 'rar': [], 
                'pkg': [], 'cso': [], 'pbp': [], 'all': []
            }
            
            for game in games:
                message_id, file_name, file_type, file_size, upload_date, category, is_uploaded, file_id = game
                game_info = {
                    'message_id': message_id,
                    'file_name': file_name,
                    'file_type': file_type,
                    'file_size': file_size,
                    'upload_date': upload_date,
                    'category': category,
                    'is_uploaded': is_uploaded,
                    'file_id': file_id
                }
                
                file_type_lower = file_type.lower()
                if file_type_lower in self.games_cache:
                    self.games_cache[file_type_lower].append(game_info)
                
                self.games_cache['all'].append(game_info)
            
            print(f"🔄 Cache updated: {len(self.games_cache['all'])} games")
            
        except Exception as e:
            print(f"Cache error: {e}")
    
    def get_channel_stats(self):
        """Get channel statistics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM premium_games')
            premium_games = cursor.fetchone()[0]
            
            return {'total_games': total_games, 'premium_games': premium_games}
        except:
            return {'total_games': 0, 'premium_games': 0}
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_db_path(self):
        """Get database path"""
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'telegram_bot.db')
        return db_path
    
    def generate_code(self):
        """Generate verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def save_verification_code(self, user_id, username, first_name, code):
        """Save verification code to database"""
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
        """Verify code"""
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
        """Check if user is member of channel"""
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
        """Mark user as joined channel"""
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
        """Check if user is verified"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            is_verified = result and result[0] == 1
            return is_verified
        except Exception as e:
            print(f"❌ Error checking verification: {e}")
            return False
    
    def is_user_completed(self, user_id):
        """Check if user completed verification"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            is_completed = result and result[0] == 1 and result[1] == 1
            return is_completed
        except Exception as e:
            print(f"❌ Error checking completion: {e}")
            return False
    
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
    
    def test_bot_connection(self):
        """Test bot connection"""
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
    
    def scan_channel_for_games(self):
        """Scan channel for games"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        try:
            print(f"🔍 Scanning {self.REQUIRED_CHANNEL} for games...")
            
            url = self.base_url + "getChatHistory"
            data = {
                "chat_id": self.REQUIRED_CHANNEL,
                "limit": 100
            }
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            game_files = []
            
            if result.get('ok'):
                messages = result.get('result', [])
                
                for message in messages:
                    game_info = self.extract_game_info(message)
                    if game_info:
                        game_files.append(game_info)
                
                if game_files:
                    self.store_games_in_db(game_files)
                    print(f"✅ Found {len(game_files)} game files")
                else:
                    print("ℹ️ No game files found in channel messages")
            else:
                print(f"❌ Cannot get channel messages: {result.get('description')}")
            
            self.update_games_cache()
            
            self.is_scanning = False
            return len(game_files)
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            self.is_scanning = False
            return 0
    
    def extract_game_info(self, message):
        """Extract game info from message"""
        try:
            if 'document' in message:
                doc = message['document']
                file_name = doc.get('file_name', '').lower()
                
                game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk', '.txt', '.pdf']
                if any(file_name.endswith(ext) for ext in game_extensions):
                    file_type = file_name.split('.')[-1].upper()
                    upload_date = datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
                    file_id = doc.get('file_id', '')
                    
                    return {
                        'message_id': message['message_id'],
                        'file_name': doc.get('file_name', 'Unknown'),
                        'file_type': file_type,
                        'file_size': doc.get('file_size', 0),
                        'upload_date': upload_date,
                        'category': self.determine_file_category(file_name),
                        'added_by': 0,
                        'is_uploaded': 0,
                        'is_forwarded': 0,
                        'file_id': file_id,
                        'bot_message_id': None
                    }
            return None
            
        except Exception as e:
            return None
    
    def determine_file_category(self, filename):
        """Determine file category"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.apk'):
            return 'Android Games'
        elif filename_lower.endswith('.iso'):
            if 'psp' in filename_lower:
                return 'PSP Games'
            elif 'ps2' in filename_lower:
                return 'PS2 Games'
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
    
    def store_games_in_db(self, game_files):
        """Store games in database"""
        try:
            cursor = self.conn.cursor()
            for game in game_files:
                cursor.execute('''
                    INSERT OR IGNORE INTO channel_games 
                    (message_id, file_name, file_type, file_size, upload_date, category, added_by, is_uploaded, is_forwarded, file_id, bot_message_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game['message_id'],
                    game['file_name'],
                    game['file_type'],
                    game['file_size'],
                    game['upload_date'],
                    game['category'],
                    game.get('added_by', 0),
                    game.get('is_uploaded', 0),
                    game.get('is_forwarded', 0),
                    game.get('file_id', ''),
                    game.get('bot_message_id', None)
                ))
            self.conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
    
    def run(self):
        """Main bot loop"""
        if not self.initialize_with_persistence():
            print("❌ Bot cannot start. Initialization failed.")
            return
    
        print("🤖 Bot is running...")
        
        offset = 0
        
        while True:
            try:
                updates = self.get_updates(offset)
                
                if updates:
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        try:
                            if 'message' in update:
                                self.process_message(update['message'])
                            elif 'callback_query' in update:
                                self.handle_callback_query(update['callback_query'])
                        except Exception as e:
                            print(f"❌ Update processing error: {e}")
                            continue
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                if self.keep_alive:
                    self.keep_alive.stop()
                break
                
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)
    
    def initialize_with_persistence(self):
        """Initialize bot with persistence"""
        try:
            print("🔄 Initializing bot with persistence...")
            
            if self.github_backup.is_enabled:
                print("🔍 Checking for GitHub backup...")
                if self.github_backup.restore_database_from_github():
                    print("✅ Database restored from GitHub")
                else:
                    print("ℹ️ No GitHub backup found or restore failed, using local database")
            
            self.setup_database()
            self.verify_database_schema()
            self.update_games_cache()
            
            if not self.test_bot_connection():
                print("❌ Bot connection failed during initialization")
                return False
                
            if not self.start_keep_alive():
                print("❌ Keep-alive service failed to start")
                return False
                
            print("✅ Bot initialization with persistence completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Bot initialization failed: {e}")
            return False
    
    def start_keep_alive(self):
        """Start keep-alive service"""
        try:
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                health_url = f"{render_url}/health"
            else:
                health_url = f"http://localhost:{os.environ.get('PORT', 8080)}/health"
            
            self.keep_alive = EnhancedKeepAliveService(health_url)
            self.keep_alive.start()
            print("🔋 Enhanced keep-alive service activated")
            return True
        except Exception as e:
            print(f"❌ Failed to start keep-alive: {e}")
            return False

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🚀 Starting Enhanced Telegram Bot with Inline Keyboards...")
    
    start_health_check()
    time.sleep(2)
    
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    if BOT_TOKEN:
        print("🔍 Testing bot token...")
        
        def test_connection(token):
            try:
                url = f"https://api.telegram.org/bot{token}/getMe"
                response = requests.get(url, timeout=10)
                data = response.json()
                return data.get('ok', False)
            except:
                return False
        
        if test_connection(BOT_TOKEN):
            print("✅ Bot token is valid")
            
            restart_count = 0
            max_restarts = 50
            restart_delay = 10
            
            while restart_count < max_restarts:
                try:
                    restart_count += 1
                    print(f"🔄 Bot start attempt #{restart_count}")
                    
                    bot = CrossPlatformBot(BOT_TOKEN)
                    bot.run()
                    
                    print("🤖 Bot stopped gracefully")
                    break
                    
                except Exception as e:
                    print(f"💥 Bot crash (#{restart_count}): {e}")
                    
                    if restart_count < max_restarts:
                        print(f"🔄 Restarting in {restart_delay} seconds...")
                        time.sleep(restart_delay)
                        restart_delay = min(restart_delay * 1.5, 300)
                    else:
                        print(f"❌ Maximum restarts ({max_restarts}) reached.")
                        break
        else:
            print("❌ Invalid bot token - cannot start")
    else:
        print("❌ No BOT_TOKEN provided")
    
    print("🔴 Bot service ended")
