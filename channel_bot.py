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
        
        # Simple authorization check (you can enhance this)
        is_authorized = auth_token == os.environ.get('REDEPLOY_TOKEN', 'default_token') or user_id in ['7475473197', '7713987088']
        
        if not is_authorized:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 401
        
        print(f"🔄 Redeploy triggered by user {user_id}")
        
        # Trigger redeploy logic
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
        
        # In a real deployment, this would trigger your CI/CD pipeline
        # For Render, you might use their API or webhook
        
        # For now, we'll simulate a redeploy by restarting the bot process
        # In production, this would be handled by your deployment platform
        print("✅ Redeploy signal sent - bot will restart shortly")
        
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
                
                # Dynamic ping interval: more frequent if issues detected
                if consecutive_failures > 0:
                    sleep_time = 60  # 1 minute if having issues
                else:
                    sleep_time = 240  # 4 minutes normally
                
                time.sleep(sleep_time)
        
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print(f"🔄 Enhanced keep-alive service started")
        print(f"🌐 Health endpoint: {self.health_url}")
        
    def emergency_restart(self):
        """Emergency restart procedure"""
        print("🔄 Initiating emergency restart...")
        # This will be caught by the main loop which will restart the bot
        os._exit(1)  # Force exit to trigger restart
        
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
            
            # Copy database file
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
            
            # Create local backup
            backup_file = self.create_db_backup()
            if not backup_file:
                return False
            
            # Read database file
            with open(backup_file, 'rb') as f:
                db_content = f.read()
            
            # Encode to base64
            db_b64 = base64.b64encode(db_content).decode('utf-8')
            
            # Get current file SHA if exists
            file_sha = self.get_file_sha()
            
            # Prepare API request
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
            
            # Upload to GitHub
            response = requests.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Database backed up to GitHub: {result['commit']['html_url']}")
                
                # Clean up local backup
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
            
            # Download database from GitHub
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
            
            # Save to database file
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
            self.bot.robust_send_message(chat_id, "❌ Access denied. Admin only.")
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

Choose an option by typing:
• <code>Redeploy Soft</code> - Soft restart
• <code>Redeploy Force</code> - Force restart
• <code>System Status</code> - Check system status
• <code>Back to Admin</code> - Return to admin menu"""
        
        self.bot.robust_send_message(chat_id, redeploy_text, self.bot.create_menu_buttons())
    
    def initiate_redeploy(self, user_id, chat_id, redeploy_type="soft"):
        """Initiate a redeploy"""
        try:
            user_info = self.bot.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Unknown')
            
            print(f"🔄 {redeploy_type.upper()} redeploy initiated by {user_name} ({user_id})")
            
            # Store redeploy request
            redeploy_id = int(time.time())
            self.redeploy_requests[redeploy_id] = {
                'user_id': user_id,
                'user_name': user_name,
                'type': redeploy_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'initiated'
            }
            
            # Send redeploy confirmation
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
            
            self.bot.robust_send_message(chat_id, confirm_text)
            
            # Trigger redeploy via webhook
            self.trigger_redeploy_webhook(user_id, redeploy_type)
            
            # Schedule actual restart
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
            self.bot.robust_send_message(chat_id, f"❌ Redeploy failed: {str(e)}")
            return False
    
    def trigger_redeploy_webhook(self, user_id, redeploy_type):
        """Trigger redeploy via webhook"""
        try:
            # Get the redeploy URL from environment
            redeploy_url = os.environ.get('REDEPLOY_WEBHOOK_URL')
            redeploy_token = os.environ.get('REDEPLOY_TOKEN', 'default_token')
            
            if not redeploy_url:
                print("ℹ️ No redeploy webhook URL set, using internal restart")
                return False
            
            # Prepare webhook data
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
            # Get bot connection status
            bot_online = self.bot.test_bot_connection()
            
            # Get database status
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
            
            # Get memory usage
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_usage = f"{memory.percent}%"
            except:
                memory_usage = "N/A"
            
            # Get uptime
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
• Last Restart: {datetime.fromtimestamp(self.bot.last_restart).strftime('%Y-%m-d %H:%M:%S')}

Type <code>Back to Admin</code> to return."""
            
            self.bot.robust_send_message(chat_id, status_text, self.bot.create_menu_buttons())
            
        except Exception as e:
            print(f"❌ System status error: {e}")
            self.bot.robust_send_message(chat_id, f"❌ Error getting system status: {str(e)}", self.bot.create_menu_buttons())
    
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
                    transaction_id TEXT,
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
                # Store premium purchase record
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
                set status = 'completed' 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            # Update stars balance
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
            
            # Game requests table
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
            
            # Game request replies table
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
            
            # Get the request ID
            request_id = cursor.lastrowid
            
            # Notify admins about new request
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
                self.bot.robust_send_message(admin_id, notification_text)
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
            
            # Premium games table
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
            
            # Premium game purchases table
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

# ==================== MAIN BOT CLASS ====================

class CrossPlatformBot:
    def __init__(self, token):
        # ==================== BOT TOKEN VALIDATION ====================
        if not token:
            print("❌ CRITICAL: No BOT_TOKEN provided!")
            print("💡 Please set BOT_TOKEN in Render Environment Variables")
            raise ValueError("BOT_TOKEN is required")
        # ==================== END VALIDATION ====================
        
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
        self.broadcast_sessions = {}  # {admin_id: {'stage': 'waiting_message', 'message': '', 'photo': None}}
        self.broadcast_stats = {}     # Store broadcast statistics
        
        # Stars, request, redeploy, and backup systems
        self.stars_system = TelegramStarsSystem(self)
        self.game_request_system = GameRequestSystem(self)
        self.premium_games_system = PremiumGamesSystem(self)
        self.redeploy_system = RedeploySystem(self)
        self.github_backup = GitHubBackupSystem(self)  # NEW: GitHub backup system
        
        # Session management
        self.stars_sessions = {}  # {user_id: {'stars_amount': amount}}
        self.request_sessions = {}  # {user_id: {'stage': 'waiting_game_name', 'game_name': ''}}
        self.upload_sessions = {}  # {user_id: {'stage': 'waiting_stars_price', 'type': 'premium/regular'}}
        self.reply_sessions = {}  # {admin_id: {'stage': 'waiting_reply', 'request_id': id, 'type': 'text/photo'}}
        
        # User navigation state
        self.user_state = {}  # {user_id: {'menu': 'main', 'page': 0, 'data': {}}}
        
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
        self.premium_games_cache = {}
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
        print("⭐ Telegram Stars payments system enabled")
        print("🎮 Game request system enabled")
        print("💰 Premium games system enabled")
        print("📝 Individual request replies enabled")
        print("🖼️ Photo broadcast support enabled")
        print("🗑️ Game removal system enabled")
        print("🛡️ Duplicate detection enabled")
        print("🔄 Redeploy system enabled")
        print("💾 GitHub Database Backup & Restore enabled")
        print("🛡️  Crash protection enabled")
        print("🔋 Enhanced keep-alive system ready")
        print("💾 Persistent data recovery enabled")
    
    def initialize_with_persistence(self):
        """Initialize bot with persistent data recovery including GitHub restore"""
        try:
            print("🔄 Initializing bot with persistence...")
            
            # Try to restore from GitHub first
            if self.github_backup.is_enabled:
                print("🔍 Checking for GitHub backup...")
                if self.github_backup.restore_database_from_github():
                    print("✅ Database restored from GitHub")
                else:
                    print("ℹ️ No GitHub backup found or restore failed, using local database")
            
            # Ensure database is properly set up
            self.setup_database()
            self.verify_database_schema()
            
            # Recover games cache
            self.update_games_cache()
            
            # CRITICAL: Recover file access for all games
            self.recover_file_access_for_all_games()
            
            # Recover uploaded files
            self.recover_file_access_after_restart()
            
            # Recover sessions from database (if you want persistent sessions)
            self.recover_persistent_sessions()
            
            # Test bot connection
            if not self.test_bot_connection():
                print("❌ Bot connection failed during initialization")
                return False
                
            # Start keep-alive service
            if not self.start_keep_alive():
                print("❌ Keep-alive service failed to start")
                return False
                
            print("✅ Bot initialization with persistence completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Bot initialization failed: {e}")
            return False

    def recover_file_access_after_restart(self):
        """Recover file access for all uploaded games after restart"""
        try:
            print("🔄 Recovering file access after restart...")
            
            cursor = self.conn.cursor()
            
            # Recover regular games
            cursor.execute('''
                SELECT message_id, file_name, file_id, bot_message_id, is_uploaded 
                FROM channel_games 
                WHERE is_uploaded = 1
            ''')
            regular_games = cursor.fetchall()
            
            recovered_count = 0
            for game in regular_games:
                message_id, file_name, file_id, bot_message_id, is_uploaded = game
                
                # If we have a file_id, verify it's still accessible
                if file_id:
                    if self.verify_and_update_file_id(file_id, message_id, True):
                        recovered_count += 1
                        print(f"✅ Recovered regular game: {file_name}")
                    else:
                        print(f"❌ File ID invalid for: {file_name}")
                        # Try to get new file_id from bot message
                        if bot_message_id:
                            new_file_id = self.get_file_id_from_bot_message(bot_message_id)
                            if new_file_id:
                                cursor.execute(
                                    'UPDATE channel_games SET file_id = ? WHERE message_id = ?',
                                    (new_file_id, message_id)
                                )
                                recovered_count += 1
                                print(f"✅ Recovered file ID for: {file_name}")
            
            # Recover premium games
            cursor.execute('''
                SELECT id, file_name, file_id, bot_message_id 
                FROM premium_games 
                WHERE is_uploaded = 1
            ''')
            premium_games = cursor.fetchall()
            
            for game in premium_games:
                game_id, file_name, file_id, bot_message_id = game
                
                if file_id:
                    if self.verify_and_update_file_id(file_id, game_id, False):
                        recovered_count += 1
                        print(f"✅ Recovered premium game: {file_name}")
                    else:
                        if bot_message_id:
                            new_file_id = self.get_file_id_from_bot_message(bot_message_id)
                            if new_file_id:
                                cursor.execute(
                                    'UPDATE premium_games SET file_id = ? WHERE id = ?',
                                    (new_file_id, game_id)
                                )
                                recovered_count += 1
                                print(f"✅ Recovered file ID for: {file_name}")
            
            self.conn.commit()
            print(f"✅ File recovery complete: {recovered_count} files recovered")
            return recovered_count
            
        except Exception as e:
            print(f"❌ File recovery error: {e}")
            return 0

    def recover_file_access_for_all_games(self):
        """Recover and update file access for all games in database"""
        try:
            print("🔄 Recovering file access for all games...")
            
            cursor = self.conn.cursor()
            
            # Get all games that need file_id recovery
            cursor.execute('''
                SELECT message_id, file_name, file_id, bot_message_id, is_uploaded 
                FROM channel_games 
                WHERE file_id IS NULL OR file_id = '' OR file_id = 'none'
            ''')
            games_needing_recovery = cursor.fetchall()
            
            recovered_count = 0
            for game in games_needing_recovery:
                message_id, file_name, file_id, bot_message_id, is_uploaded = game
                
                if is_uploaded == 1 and bot_message_id:
                    # Try to get file_id from bot message
                    new_file_id = self.get_file_id_from_bot_message(bot_message_id)
                    if new_file_id:
                        # Test if this file_id is universally accessible
                        if self.test_file_id_accessibility(new_file_id):
                            cursor.execute(
                                'UPDATE channel_games SET file_id = ? WHERE message_id = ?',
                                (new_file_id, message_id)
                            )
                            recovered_count += 1
                            print(f"✅ Recovered file ID for: {file_name}")
            
            self.conn.commit()
            print(f"✅ File recovery complete: {recovered_count} files updated")
            return recovered_count
            
        except Exception as e:
            print(f"❌ File recovery error: {e}")
            return 0

    def verify_and_update_file_id(self, file_id, identifier, is_regular=True):
        """Verify file_id is still valid and update if needed"""
        try:
            # Test if file_id is still accessible
            url = self.base_url + "getFile"
            data = {"file_id": file_id}
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"❌ File ID {file_id[:10]}... invalid, needs update")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying file ID: {e}")
            return False

    def get_file_id_from_bot_message(self, bot_message_id):
        """Get file_id from a bot message by its message_id"""
        try:
            # Get the message details from the first admin's chat
            for admin_id in self.ADMIN_IDS:
                try:
                    # Try to get the message from admin's chat
                    url = self.base_url + "getMessage"
                    data = {
                        "chat_id": admin_id,
                        "message_id": bot_message_id
                    }
                    response = requests.post(url, data=data, timeout=10)
                    result = response.json()
                    
                    if result.get('ok'):
                        message = result['result']
                        if 'document' in message:
                            return message['document'].get('file_id')
                        elif 'photo' in message:
                            # Get the highest quality photo
                            return message['photo'][-1].get('file_id')
                except Exception as e:
                    print(f"❌ Error getting file ID from admin {admin_id}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting file ID from message: {e}")
            return None

    def test_file_id_accessibility(self, file_id):
        """Test if a file_id can be accessed by the bot universally"""
        try:
            if not file_id:
                return False
                
            # Try to get file info - this tests if file_id is valid and accessible
            url = self.base_url + "getFile"
            data = {"file_id": file_id}
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ File ID is universally accessible: {file_id[:20]}...")
                return True
            else:
                print(f"❌ File ID not accessible: {result.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ File ID accessibility test error: {e}")
            return False

    def recover_persistent_sessions(self):
        """Recover persistent sessions from database"""
        try:
            # Reset sessions on restart
            self.guess_games = {}
            self.spin_games = {}
            self.broadcast_sessions = {}
            self.stars_sessions = {}
            self.request_sessions = {}
            self.upload_sessions = {}
            self.reply_sessions = {}
            self.search_sessions = {}
            self.search_results = {}
            self.user_state = {}
            
            print("✅ Sessions reset for fresh start")
        except Exception as e:
            print(f"❌ Session recovery error: {e}")

    def start_keep_alive(self):
        """Start the enhanced keep-alive service"""
        try:
            # Get the actual Render URL from environment or use local
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                health_url = f"{render_url}/health"
            else:
                health_url = f"http://localhost:{os.environ.get('PORT', 8080)}/health"
            
            self.keep_alive = EnhancedKeepAliveService(health_url)
            self.keep_alive.start()
            print("🔋 Enhanced keep-alive service activated - bot will stay awake!")
            return True
        except Exception as e:
            print(f"❌ Failed to start keep-alive: {e}")
            return False

    # ==================== REGULAR KEYBOARD METHODS ====================
    
    def create_main_menu_buttons(self):
        """Create main menu keyboard for regular users"""
        keyboard = [
            ["🎮 Games", "🔍 Search Games"],
            ["💰 Premium Games", "📝 Request Game"],
            ["⭐ Donate Stars", "📊 Profile"],
            ["🕒 Time", "📢 Channel Info"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_admin_menu_buttons(self):
        """Create admin menu keyboard"""
        keyboard = [
            ["🎮 Games", "🔍 Search Games"],
            ["💰 Premium Games", "📝 Request Game"],
            ["🔧 Admin Panel", "📢 Broadcast"],
            ["📤 Upload Games", "🗑️ Remove Games"],
            ["🔄 Redeploy Bot", "💾 Backup System"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_games_menu_buttons(self):
        """Create games menu keyboard"""
        stats = self.get_channel_stats()
        total_games = stats['total_games'] + stats['premium_games']
        
        keyboard = [
            [f"📁 Game Files ({stats['total_games']})", f"💰 Premium ({stats['premium_games']})"],
            ["🎮 Mini Games", "🔍 Search Games"],
            ["📝 Request Game", "⭐ Donate Stars"],
            ["🏠 Main Menu"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_game_files_buttons(self):
        """Create game files menu keyboard"""
        stats = self.get_channel_stats()
        
        keyboard = [
            ["📦 ZIP Files", "🗜️ 7Z Files"],
            ["💿 ISO Files", "📱 APK Files"],
            ["🎮 PSP Games", "📋 All Files"],
            ["💰 Premium Games", "🔍 Search Games"],
            ["🔄 Rescan Games", "🔙 Back to Games"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_mini_games_buttons(self):
        """Create mini-games menu keyboard"""
        keyboard = [
            ["🎯 Number Guess", "🎲 Random Number"],
            ["🎰 Lucky Spin", "📊 My Stats"],
            ["🔙 Back to Games"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_admin_buttons(self):
        """Create admin panel keyboard"""
        keyboard = [
            ["📤 Upload Stats", "🔄 Update Cache"],
            ["📤 Upload Games", "🗑️ Remove Games"],
            ["🗑️ Clear All Games", "🔍 Scan Bot Games"],
            ["📢 Broadcast", "🎮 Game Requests"],
            ["⭐ Stars Stats", "💾 Backup System"],
            ["🔄 Redeploy System", "📊 System Status"],
            ["🏠 Main Menu"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_upload_options_buttons(self):
        """Create upload options keyboard"""
        keyboard = [
            ["🆓 Upload Regular Game", "⭐ Upload Premium Game"],
            ["🔙 Back to Admin"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_remove_game_buttons(self):
        """Create remove game menu keyboard"""
        keyboard = [
            ["🔍 Search & Remove Game", "📋 View Recent Uploads"],
            ["🔙 Back to Admin"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_broadcast_buttons(self):
        """Create broadcast menu keyboard"""
        keyboard = [
            ["📢 Start Broadcast", "📊 Broadcast Stats"],
            ["🔙 Back to Admin"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_stars_menu_buttons(self):
        """Create stars menu keyboard"""
        keyboard = [
            ["⭐ 50 Stars ($0.50)", "⭐ 100 Stars ($1.00)"],
            ["⭐ 500 Stars ($5.00)", "⭐ 1000 Stars ($10.00)"],
            ["💫 Custom Amount", "📊 Stars Stats"],
            ["🔙 Back to Menu"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_search_buttons(self):
        """Create search menu keyboard"""
        keyboard = [
            ["🔍 New Search", "📁 Browse All"],
            ["💰 Premium Games", "📝 Request Game"],
            ["🔙 Back to Menu"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_verification_buttons(self):
        """Create verification keyboard"""
        keyboard = [
            ["📢 JOIN CHANNEL", "✅ VERIFY JOIN"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": True,
            "selective": False
        }
    
    def create_backup_menu_buttons(self):
        """Create backup menu keyboard"""
        keyboard = [
            ["💾 Create Backup Now", "🔄 Restore from Backup"],
            ["📊 Backup Info", "🔙 Back to Admin"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def create_menu_buttons(self):
        """Create dynamic menu based on user status"""
        if self.is_admin:
            return self.create_admin_menu_buttons()
        return self.create_main_menu_buttons()

    # ==================== TEXT COMMAND HANDLERS ====================
    
    def handle_text_command(self, user_id, chat_id, command):
        """Handle text commands from regular keyboard"""
        try:
            print(f"📝 Handling command: {command} from user {user_id}")
            
            # Main menu commands
            if command == "🏠 Main Menu":
                self.show_main_menu(user_id, chat_id)
                return True
                
            elif command == "🎮 Games":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                # FIXED: Show game files menu instead of just games menu
                self.show_game_files_menu(user_id, chat_id)
                return True
                
            elif command == "🔍 Search Games":
                if not self.is_user_verified(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.robust_send_message(chat_id, 
                    "🔍 <b>Game Search</b>\n\n"
                    "Please type the name of the game you're looking for:\n\n"
                    "💡 Examples:\n"
                    "• GTA\n"
                    "• God of War\n"
                    "• Minecraft\n"
                    "• FIFA\n\n"
                    "Simply type the game name and I'll search our database.",
                    self.create_search_buttons()
                )
                return True
                
            elif command == "💰 Premium Games":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_premium_games_menu(user_id, chat_id)
                return True
                
            elif command == "📝 Request Game":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.start_game_request(user_id, chat_id)
                return True
                
            elif command == "⭐ Donate Stars":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_stars_menu(user_id, chat_id)
                return True
                
            elif command == "📊 Profile":
                self.handle_profile(chat_id, user_id)
                return True
                
            elif command == "🕒 Time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.robust_send_message(chat_id, f"🕒 <b>Current Time</b>\n\n📅 {current_time}\n\n⏰ Server Time (UTC)")
                return True
                
            elif command == "📢 Channel Info":
                self.show_channel_info(chat_id)
                return True
                
            elif command == "🔧 Admin Panel":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_admin_panel(user_id, chat_id)
                return True
                
            elif command == "📤 Upload Games":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_upload_options(user_id, chat_id)
                return True
                
            elif command == "🗑️ Remove Games":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_remove_game_menu(user_id, chat_id)
                return True
                
            elif command == "🔄 Redeploy Bot":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.redeploy_system.show_redeploy_menu(user_id, chat_id)
                return True
                
            elif command == "💾 Backup System":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_backup_menu(user_id, chat_id)
                return True
                
            elif command == "📢 Broadcast":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.start_broadcast(user_id, chat_id)
                return True
                
            elif command == "🎮 Game Requests":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_admin_requests_panel(user_id, chat_id)
                return True
                
            elif command == "⭐ Stars Stats":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_stars_stats(user_id, chat_id)
                return True
                
            elif command == "📊 System Status":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.redeploy_system.show_system_status(user_id, chat_id)
                return True
                
            elif command == "📤 Upload Stats":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.handle_upload_stats(user_id, chat_id)
                return True
                
            elif command == "🔄 Update Cache":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.robust_send_message(chat_id, "🔄 Updating games cache...")
                self.update_games_cache()
                stats = self.get_channel_stats()
                self.robust_send_message(chat_id, 
                    f"✅ Cache updated! {stats['total_games']} regular games and {stats['premium_games']} premium games loaded.",
                    self.create_admin_buttons()
                )
                return True
                
            elif command == "🗑️ Clear All Games":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.clear_all_games_confirmation(user_id, chat_id)
                return True
                
            elif command == "🔍 Scan Bot Games":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.robust_send_message(chat_id, "🔍 Scanning for bot-uploaded games...")
                bot_games_found = self.scan_bot_uploaded_games()
                self.update_games_cache()
                self.robust_send_message(chat_id, 
                    f"✅ Bot games scan complete! Found {bot_games_found} new games.",
                    self.create_admin_buttons()
                )
                return True
                
            elif command == "📊 Broadcast Stats":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.get_broadcast_stats(user_id, chat_id)
                return True
                
            elif command == "📢 Start Broadcast":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.start_broadcast(user_id, chat_id)
                return True
                
            # Games menu commands
            elif command == "📁 Game Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_files_menu(user_id, chat_id)
                return True
                
            elif command == "🎮 Mini Games":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_mini_games_menu(user_id, chat_id)
                return True
                
            elif command == "🔙 Back to Games":
                self.show_games_menu(user_id, chat_id)
                return True
                
            elif command == "📦 ZIP Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "zip", "ZIP")
                return True
                
            elif command == "🗜️ 7Z Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "7z", "7Z")
                return True
                
            elif command == "💿 ISO Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "iso", "ISO")
                return True
                
            elif command == "📱 APK Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "apk", "APK")
                return True
                
            elif command == "🎮 PSP Games":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "psp", "PSP")
                return True
                
            elif command == "📋 All Files":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_game_list(user_id, chat_id, "all", "ALL")
                return True
                
            elif command == "🔄 Rescan Games":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.robust_send_message(chat_id, "🔄 Scanning for new games...")
                total_games = self.scan_channel_for_games()
                stats = self.get_channel_stats()
                self.robust_send_message(chat_id, 
                    f"✅ Rescan complete! Found {total_games} total games. Database now has {stats['total_games']} regular games and {stats['premium_games']} premium games.",
                    self.create_game_files_buttons()
                )
                return True
                
            # Mini-games commands
            elif command == "🎯 Number Guess":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.start_number_guess_game(user_id, chat_id)
                return True
                
            elif command == "🎲 Random Number":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.generate_random_number(user_id, chat_id)
                return True
                
            elif command == "🎰 Lucky Spin":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.lucky_spin(user_id, chat_id)
                return True
                
            elif command == "📊 My Stats":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_mini_games_stats(user_id, chat_id)
                return True
                
            # Upload options
            elif command == "🆓 Upload Regular Game":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.robust_send_message(chat_id,
                    "🆓 <b>Regular Game Upload</b>\n\n"
                    "Please upload the game file now.\n\n"
                    "📁 Supported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP\n\n"
                    "💡 The file will be available for free to all users."
                )
                return True
                
            elif command == "⭐ Upload Premium Game":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.start_premium_upload(user_id, chat_id)
                return True
                
            elif command == "🔙 Back to Admin":
                self.show_admin_panel(user_id, chat_id)
                return True
                
            # Remove game options
            elif command == "🔍 Search & Remove Game":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.start_remove_game_search(user_id, chat_id)
                return True
                
            elif command == "📋 View Recent Uploads":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_recent_uploads_for_removal(user_id, chat_id)
                return True
                
            # Stars menu commands
            elif command == "⭐ 50 Stars ($0.50)":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.process_stars_donation(user_id, chat_id, 50)
                return True
                
            elif command == "⭐ 100 Stars ($1.00)":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.process_stars_donation(user_id, chat_id, 100)
                return True
                
            elif command == "⭐ 500 Stars ($5.00)":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.process_stars_donation(user_id, chat_id, 500)
                return True
                
            elif command == "⭐ 1000 Stars ($10.00)":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.process_stars_donation(user_id, chat_id, 1000)
                return True
                
            elif command == "💫 Custom Amount":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.stars_sessions[user_id] = {}
                self.robust_send_message(chat_id, 
                    "💫 <b>Custom Stars Amount</b>\n\n"
                    "Please enter the number of Stars you'd like to donate:\n\n"
                    "💡 <i>Enter a number (e.g., 250 for 250 Stars ≈ $2.50)</i>"
                )
                return True
                
            elif command == "📊 Stars Stats":
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                self.show_stars_stats(user_id, chat_id)
                return True
                
            elif command == "🔙 Back to Menu":
                self.show_main_menu(user_id, chat_id)
                return True
                
            # Verification commands
            elif command == "📢 JOIN CHANNEL":
                self.robust_send_message(chat_id, 
                    "📢 <b>Join Our Channel</b>\n\n"
                    f"Please join our channel: {self.CHANNEL_LINK}\n\n"
                    "After joining, click <b>✅ VERIFY JOIN</b>",
                    self.create_verification_buttons()
                )
                return True
                
            elif command == "✅ VERIFY JOIN":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    self.robust_send_message(chat_id, 
                        "✅ <b>Verification Complete!</b>\n\n"
                        "You have successfully joined the channel!\n\n"
                        "Now you can access all features:",
                        self.create_main_menu_buttons()
                    )
                else:
                    self.robust_send_message(chat_id, 
                        "❌ <b>Not Joined Yet</b>\n\n"
                        "You haven't joined the channel yet.\n\n"
                        f"Please join: {self.CHANNEL_LINK}\n"
                        "Then click <b>✅ VERIFY JOIN</b> again.",
                        self.create_verification_buttons()
                    )
                return True
                
            # Backup system commands
            elif command == "💾 Create Backup Now":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.handle_create_backup(user_id, chat_id)
                return True
                
            elif command == "🔄 Restore from Backup":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.handle_restore_backup(user_id, chat_id)
                return True
                
            elif command == "📊 Backup Info":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.show_backup_menu(user_id, chat_id)
                return True
                
            # Redeploy commands
            elif command == "Redeploy Soft":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.redeploy_system.initiate_redeploy(user_id, chat_id, "soft")
                return True
                
            elif command == "Redeploy Force":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.redeploy_system.initiate_redeploy(user_id, chat_id, "force")
                return True
                
            elif command == "System Status":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                self.redeploy_system.show_system_status(user_id, chat_id)
                return True
                
            elif command == "Back to Admin":
                self.show_admin_panel(user_id, chat_id)
                return True
            
            # Game download commands (format: "Download: filename")
            elif command.startswith("Download: "):
                filename = command.replace("Download: ", "")
                self.handle_game_download(user_id, chat_id, filename)
                return True
            
            # Game removal commands (format: "Remove: filename")
            elif command.startswith("Remove: "):
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                filename = command.replace("Remove: ", "")
                self.handle_game_removal(user_id, chat_id, filename)
                return True
            
            # Premium game purchase commands (format: "Buy Premium: gamename")
            elif command.startswith("Buy Premium: "):
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                
                game_name = command.replace("Buy Premium: ", "")
                self.handle_premium_purchase(user_id, chat_id, game_name)
                return True
            
            # Premium game download commands (format: "Get Premium: gamename")
            elif command.startswith("Get Premium: "):
                if not self.is_user_completed(user_id):
                    self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                    return True
                
                game_name = command.replace("Get Premium: ", "")
                self.handle_premium_download(user_id, chat_id, game_name)
                return True
            
            # Confirm removal commands
            elif command == "✅ Yes, Remove Game":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                if user_id in self.user_state and 'remove_game' in self.user_state[user_id]:
                    game_info = self.user_state[user_id]['remove_game']
                    self.remove_game(user_id, chat_id, game_info['type'], game_info['id'])
                    del self.user_state[user_id]['remove_game']
                return True
                
            elif command == "❌ Cancel Remove":
                if user_id in self.user_state and 'remove_game' in self.user_state[user_id]:
                    del self.user_state[user_id]['remove_game']
                self.show_remove_game_menu(user_id, chat_id)
                return True
            
            # Confirm clear all games
            elif command == "✅ Yes, Clear All Games":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                self.clear_all_games(user_id, chat_id)
                return True
                
            elif command == "❌ Cancel Clear":
                self.show_admin_panel(user_id, chat_id)
                return True
            
            # Confirm backup restore
            elif command == "✅ Yes, Restore Backup":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                self.handle_confirm_restore(user_id, chat_id)
                return True
                
            elif command == "❌ Cancel Restore":
                self.show_backup_menu(user_id, chat_id)
                return True
            
            # Broadcast confirmation
            elif command == "✅ Send Broadcast":
                if not self.is_admin(user_id):
                    self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                    return True
                
                self.send_broadcast_to_all(user_id, chat_id)
                return True
                
            elif command == "❌ Cancel Broadcast":
                if user_id in self.broadcast_sessions:
                    del self.broadcast_sessions[user_id]
                self.robust_send_message(chat_id, "❌ Broadcast cancelled.", self.create_broadcast_buttons())
                return True
                
            elif command == "✏️ Edit Broadcast":
                if not self.is_admin(user_id) or user_id not in self.broadcast_sessions:
                    return True
                
                self.broadcast_sessions[user_id]['stage'] = 'waiting_message_or_photo'
                self.robust_send_message(chat_id, "✏️ Please type your new broadcast message or send a photo:")
                return True
            
            # Search navigation
            elif command == "🔍 New Search":
                self.robust_send_message(chat_id, 
                    "🔍 <b>Game Search</b>\n\n"
                    "Please type the name of the game you're looking for:",
                    self.create_search_buttons()
                )
                return True
                
            elif command == "📁 Browse All":
                self.show_game_files_menu(user_id, chat_id)
                return True
            
            # Number guess quick buttons
            elif command in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                if user_id in self.guess_games:
                    return self.handle_guess_input(user_id, chat_id, command)
                return False
            
            # Handle game file sending from search results
            elif command.startswith("Send: "):
                parts = command.replace("Send: ", "").split(" | ")
                if len(parts) >= 2:
                    message_id = int(parts[0])
                    file_id = parts[1] if len(parts) > 1 else None
                    is_bot_file = "BOT" in command
                    
                    self.send_game_file(chat_id, message_id, file_id, is_bot_file)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Text command handler error: {e}")
            return False
    
    # ==================== MENU DISPLAY METHODS ====================
    
    def show_main_menu(self, user_id, chat_id):
        """Show main menu"""
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
• 🔄 Forward Support
• 🕒 Real-time Updates
• 🎮 Mini-Games Entertainment
• 📢 Admin Broadcast System
• ⭐ Telegram Stars Payments
• 🎮 Game Request System
• 📝 Individual Request Replies
• 🖼️ Photo Broadcast Support
• 🗑️ Game Removal System
• 🛡️ Duplicate Detection
• 🔄 Redeploy System
• 💾 GitHub Database Backup
• 🔋 Keep-Alive Protection
• 💾 Persistent Data Recovery

Choose an option below:"""
        
        if self.is_admin(user_id):
            self.robust_send_message(chat_id, welcome_text, self.create_admin_menu_buttons())
        else:
            self.robust_send_message(chat_id, welcome_text, self.create_main_menu_buttons())
    
    def show_games_menu(self, user_id, chat_id):
        """Show games menu"""
        stats = self.get_channel_stats()
        total_games = stats['total_games'] + stats['premium_games']
        
        games_text = f"""🎮 <b>Games Section</b>

📊 Total Games: {total_games}
• 🆓 Regular: {stats['total_games']}
• 💰 Premium: {stats['premium_games']}

🎯 Choose an option below:

• 📁 Game Files - Browse all regular games
• 💰 Premium Games - Exclusive paid games
• 🎮 Mini Games - Fun mini-games to play
• 🔍 Search Games - Search for specific games
• 📝 Request Game - Request games not in our collection
• ⭐ Donate Stars - Support our bot with Telegram Stars

🔗 Channel: @pspgamers5"""
        
        self.robust_send_message(chat_id, games_text, self.create_games_menu_buttons())
    
    def show_game_files_menu(self, user_id, chat_id):
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
        
        self.robust_send_message(chat_id, files_text, self.create_game_files_buttons())
    
    def show_mini_games_menu(self, user_id, chat_id):
        """Show mini-games menu"""
        games_text = """🎮 <b>Mini Games</b>

🎯 Choose a game to play:

• 🎯 Number Guess - Guess the random number (1-10)
• 🎲 Random Number - Generate random numbers with analysis
• 🎰 Lucky Spin - Spin for lucky symbols and coins
• 📊 My Stats - View your gaming statistics

Have fun! 🎉"""
        
        self.robust_send_message(chat_id, games_text, self.create_mini_games_buttons())
    
    def show_admin_panel(self, user_id, chat_id):
        """Show admin panel"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
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
• 🗃️ Update games cache
• 🗑️ Remove individual games
• 🗑️ Clear all games
• 🔍 Scan bot-uploaded games
• 📢 Broadcast messages to users
• 🎮 Manage game requests
• ⭐ View Stars statistics
• 💾 Backup & Restore Database
• 🔄 Redeploy bot system
• 🔍 Monitor system status

📊 Your Stats:
• Total uploads: {self.get_upload_stats(user_id)}
• Forwarded files: {self.get_forward_stats(user_id)}
• Regular games: {stats['total_games']}
• Premium games: {stats['premium_games']}

Choose an option:"""
        
        self.robust_send_message(chat_id, admin_text, self.create_admin_buttons())
    
    def show_upload_options(self, user_id, chat_id):
        """Show upload options for admin"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        upload_text = """📤 <b>Upload Games - Admin Panel</b>

Choose the type of game to upload:

🆓 <b>Regular Game</b>
• Free for all users
• No payment required
• Direct download

⭐ <b>Premium Game</b>  
• Requires Stars payment
• Set your price in Stars
• Users pay to download

📁 Both support all file formats (ZIP, ISO, APK, etc.)"""
        
        self.robust_send_message(chat_id, upload_text, self.create_upload_options_buttons())
    
    def show_remove_game_menu(self, user_id, chat_id):
        """Show game removal menu for admins"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        remove_text = """🗑️ <b>Game Removal System</b>

Remove games from the database.

🔍 <b>How to use:</b>
1. Search for the game you want to remove
2. View search results
3. Click "Remove" button next to any game
4. Confirm removal

⚠️ <b>Warning:</b> This action cannot be undone!

Choose an option:"""
        
        self.robust_send_message(chat_id, remove_text, self.create_remove_game_buttons())
    
    def show_backup_menu(self, user_id, chat_id):
        """Show backup management menu for admins"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        backup_info = self.github_backup.get_backup_info()
        
        if backup_info.get('enabled'):
            if 'last_backup' in backup_info:
                status_text = f"""💾 <b>GitHub Backup System</b>

✅ Status: <b>ENABLED</b>
📅 Last Backup: {backup_info.get('last_backup', 'Unknown')}
💬 Message: {backup_info.get('message', 'Unknown')}
🔗 Repository: {self.github_backup.repo_owner}/{self.github_backup.repo_name}
📁 Path: {self.github_backup.backup_path}

🔄 Backup occurs automatically when:
• Games are uploaded
• Games are removed  
• All games are cleared
• Manual backup triggered"""
            else:
                status_text = f"""💾 <b>GitHub Backup System</b>

✅ Status: <b>ENABLED</b>
❌ Last Backup: Never (No backup exists yet)
🔗 Repository: {self.github_backup.repo_owner}/{self.github_backup.repo_name}
📁 Path: {self.github_backup.backup_path}

⚠️ <b>No backup exists yet!</b>
Create your first backup now."""
        else:
            status_text = """💾 <b>GitHub Backup System</b>

❌ Status: <b>DISABLED</b>

To enable GitHub backups, set these environment variables:
• <code>GITHUB_TOKEN</code> - Your GitHub personal access token
• <code>GITHUB_REPO_OWNER</code> - Repository owner username
• <code>GITHUB_REPO_NAME</code> - Repository name
• <code>GITHUB_BACKUP_PATH</code> - Backup file path (optional)
• <code>GITHUB_BACKUP_BRANCH</code> - Branch name (optional)"""
        
        if backup_info.get('enabled'):
            self.robust_send_message(chat_id, status_text, self.create_backup_menu_buttons())
        else:
            self.robust_send_message(chat_id, status_text, self.create_admin_buttons())
    
    def show_channel_info(self, chat_id):
        """Show channel information"""
        channel_info = f"""📢 <b>Channel Information</b>

🏷️ Channel: @pspgamers5
🔗 Link: https://t.me/pspgamers5
📝 Description: PSP Games & More!

🎮 Available Games:
• PSP Games (ISO/CSO)
• PS2 Games
• Android Games (APK)
• Emulator Games
• And much more!

📥 How to Download:
1. Join our channel
2. Browse available games
3. Click on files to download

⚠️ Note: You need to join channel and complete verification to access games."""
        
        self.robust_send_message(chat_id, channel_info, self.create_main_menu_buttons())
    
    def show_game_list(self, user_id, chat_id, file_type, display_name):
        """Show list of games for a specific file type"""
        if file_type == "psp":
            cso_games = self.games_cache.get('cso', [])
            pbp_games = self.games_cache.get('pbp', [])
            games = cso_games + pbp_games
        elif file_type == "all":
            games = self.games_cache.get('all', [])
        else:
            games = self.games_cache.get(file_type, [])
        
        if not games:
            self.robust_send_message(chat_id, 
                f"❌ No {display_name} games found.\n\n"
                "Try browsing other categories or use the search feature.",
                self.create_game_files_buttons()
            )
            return
        
        # Limit to first 20 games
        games_to_show = games[:20]
        
        games_text = f"""📁 <b>{display_name} GAMES</b>

📊 Found: {len(games)} files
📋 Showing: {len(games_to_show)} files

Click on any game below to download it:\n\n"""
        
        # Create buttons for each game
        keyboard = []
        for i, game in enumerate(games_to_show, 1):
            game_name = game['file_name']
            if len(game_name) > 30:
                display_game_name = game_name[:27] + "..."
            else:
                display_game_name = game_name
            
            # Create a button for each game
            keyboard.append([f"Download: {display_game_name}"])
            
            # Add game info to text
            size = self.format_file_size(game['file_size'])
            games_text += f"{i}. <b>{game_name}</b>\n"
            games_text += f"   📦 {game['file_type']} | 📏 {size} | 🗂️ {game.get('category', 'Unknown')}\n\n"
        
        # Add navigation buttons
        keyboard.append(["🔙 Back to Game Files", "🔍 Search Games"])
        keyboard.append(["🏠 Main Menu"])
        
        games_text += "📥 Click on any game above to download it instantly!"
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, games_text, reply_markup)
    
    # ==================== GAME DOWNLOAD HANDLER ====================
    
    def handle_game_download(self, user_id, chat_id, filename):
        """Handle game download request"""
        try:
            # Find the game in cache
            game_found = None
            for game_list in self.games_cache.values():
                for game in game_list:
                    if game['file_name'] == filename:
                        game_found = game
                        break
                if game_found:
                    break
            
            if not game_found:
                # Try to find by partial name
                for game_list in self.games_cache.values():
                    for game in game_list:
                        if filename in game['file_name']:
                            game_found = game
                            break
                    if game_found:
                        break
            
            if not game_found:
                self.robust_send_message(chat_id, 
                    f"❌ Game not found: {filename}\n\n"
                    "Please try searching for the game again.",
                    self.create_game_files_buttons()
                )
                return True
            
            # Get the game from database to get message_id
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT message_id, file_id, bot_message_id, is_uploaded 
                FROM channel_games 
                WHERE file_name = ?
            ''', (game_found['file_name'],))
            
            game_db = cursor.fetchone()
            
            if game_db:
                message_id, file_id, bot_message_id, is_uploaded = game_db
                
                # Send the game file
                self.robust_send_message(chat_id, f"📥 Sending game: <b>{game_found['file_name']}</b>...")
                
                is_bot_file = is_uploaded == 1 and bot_message_id is not None
                if is_bot_file:
                    # Use bot_message_id for bot-uploaded files
                    success = self.send_game_file(chat_id, bot_message_id, file_id, True)
                else:
                    # Use channel message_id for channel files
                    success = self.send_game_file(chat_id, message_id, file_id, False)
                
                if not success:
                    self.robust_send_message(chat_id, 
                        "❌ Failed to send game file. Please try again or contact admin.",
                        self.create_game_files_buttons()
                    )
            else:
                self.robust_send_message(chat_id, 
                    f"❌ Game not found in database: {game_found['file_name']}",
                    self.create_game_files_buttons()
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Game download error: {e}")
            self.robust_send_message(chat_id, 
                "❌ Error downloading game. Please try again.",
                self.create_game_files_buttons()
            )
            return True
    
    # ==================== PREMIUM GAMES MENU ====================
    
    def show_premium_games_menu(self, user_id, chat_id):
        """Show premium games menu to users"""
        premium_games = self.premium_games_system.get_premium_games(10)
        
        if not premium_games:
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games that you can purchase with Telegram Stars!"""
            
            keyboard = [
                ["🆓 Regular Games", "🔍 Search Games"],
                ["📝 Request Game", "⭐ Donate Stars"],
                ["🔙 Back to Games", "🏠 Main Menu"]
            ]
        else:
            premium_text = """💰 <b>Premium Games</b>

Exclusive games available for purchase with Telegram Stars:

📥 <b>Click on any game to view details:</b>\n\n"""
            
            # Create buttons for premium games
            keyboard = []
            for i, game in enumerate(premium_games, 1):
                game_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
                
                # Shorten filename if too long
                display_name = file_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                
                premium_text += f"{i}. <b>{display_name}</b>\n"
                premium_text += f"   ⭐ {stars_price} Stars | 📦 {file_type}\n\n"
                
                # Add button for this game
                keyboard.append([f"Buy Premium: {file_name}"])
            
            premium_text += "💡 <i>Click on any game to purchase with Telegram Stars!</i>"
            
            # Add navigation buttons
            keyboard.append(["🆓 Regular Games", "🔍 Search Games"])
            keyboard.append(["⭐ Donate Stars", "📝 Request Game"])
            keyboard.append(["🔙 Back to Games", "🏠 Main Menu"])
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, premium_text, reply_markup)
    
    def handle_premium_purchase(self, user_id, chat_id, game_name):
        """Handle premium game purchase request"""
        # Find the premium game
        premium_games = self.premium_games_system.get_premium_games(50)
        target_game = None
        game_id = None
        
        for game in premium_games:
            g_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
            if file_name == game_name or game_name in file_name:
                target_game = game
                game_id = g_id
                break
        
        if not target_game:
            self.robust_send_message(chat_id, 
                f"❌ Premium game not found: {game_name}\n\n"
                "Please check the premium games list again.",
                self.create_games_menu_buttons()
            )
            return True
        
        game_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = target_game
        
        # Check if user already purchased this game
        if self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id,
                f"✅ <b>You already own this game!</b>\n\n"
                f"🎮 Game: <b>{file_name}</b>\n"
                f"⭐ Price: {stars_price} Stars (Already purchased)\n\n"
                "Click below to download it:",
                self.create_premium_download_button(file_name)
            )
            return True
        
        # Show purchase confirmation
        purchase_text = f"""💰 <b>Premium Game Purchase</b>

🎮 Game: <b>{file_name}</b>
📦 Type: {file_type}
📏 Size: {self.format_file_size(file_size)}
⭐ Price: <b>{stars_price} Stars</b>
💰 USD Value: ${stars_price * 0.01:.2f}

📝 Description:
{description if description else 'No description available.'}

⚠️ <b>Are you sure you want to purchase this game?</b>

You will receive a Telegram Stars invoice for {stars_price} Stars."""
        
        keyboard = [
            [f"✅ Confirm Purchase: {file_name}", "❌ Cancel Purchase"],
            ["🔙 Back to Premium Games"]
        ]
        
        # Store purchase intent in user state
        if user_id not in self.user_state:
            self.user_state[user_id] = {}
        self.user_state[user_id]['purchase_intent'] = {
            'game_id': game_id,
            'game_name': file_name,
            'stars_price': stars_price
        }
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, purchase_text, reply_markup)
        return True
    
    def create_premium_download_button(self, game_name):
        """Create keyboard with premium download button"""
        keyboard = [
            [f"Get Premium: {game_name}"],
            ["💰 Premium Games", "🎮 Games"],
            ["🏠 Main Menu"]
        ]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
    
    def handle_premium_download(self, user_id, chat_id, game_name):
        """Handle premium game download request"""
        # Find the premium game
        premium_games = self.premium_games_system.get_premium_games(50)
        target_game = None
        game_id = None
        
        for game in premium_games:
            g_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
            if file_name == game_name or game_name in file_name:
                target_game = game
                game_id = g_id
                break
        
        if not target_game:
            self.robust_send_message(chat_id, 
                f"❌ Premium game not found: {game_name}",
                self.create_games_menu_buttons()
            )
            return True
        
        # Check if user has purchased this game
        if not self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id,
                f"❌ <b>Purchase Required</b>\n\n"
                f"You haven't purchased <b>{target_game[1]}</b> yet.\n\n"
                f"Price: {target_game[4]} Stars\n\n"
                "Please purchase the game first to download it.",
                self.create_games_menu_buttons()
            )
            return True
        
        # Send the premium game file
        self.send_premium_game_file(user_id, chat_id, game_id)
        return True
    
    # ==================== STARS DONATION HANDLERS ====================
    
    def show_stars_menu(self, user_id, chat_id):
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
        
        self.robust_send_message(chat_id, stars_text, self.create_stars_menu_buttons())
    
    def show_stars_stats(self, user_id, chat_id):
        """Show stars statistics"""
        balance = self.stars_system.get_balance()
        recent_transactions = self.stars_system.get_recent_transactions(10)
        
        stats_text = """📊 <b>Telegram Stars Statistics</b>

💰 <b>Financial Overview:</b>"""
        
        stats_text += f"\n• Total Stars Earned: <b>{balance['total_stars_earned']} ⭐</b>"
        stats_text += f"\n• Total USD Earned: <b>${balance['total_usd_earned']:.2f}</b>"
        stats_text += f"\n• Available Stars: <b>{balance['available_stars']} ⭐</b>"
        stats_text += f"\n• Available USD: <b>${balance['available_usd']:.2f}</b>"
        stats_text += f"\n• Last Updated: {balance['last_updated'][:16] if balance['last_updated'] else 'Never'}"
        
        if recent_transactions:
            stats_text += "\n\n🎉 <b>Recent Transactions (Top 10):</b>"
            for i, transaction in enumerate(recent_transactions, 1):
                donor_name, stars_amount, usd_amount, status, created_at = transaction
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d %H:%M')
                status_icon = "✅" if status == 'completed' else "⏳"
                stats_text += f"\n{i}. {donor_name}: {status_icon} <b>{stars_amount} ⭐ (${usd_amount:.2f})</b> - {date_str}"
        
        keyboard = [
            ["⭐ Donate Stars", "🔄 Refresh Stats"],
            ["🔙 Back to Menu"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, stats_text, reply_markup)
    
    def process_stars_donation(self, user_id, chat_id, stars_amount):
        """Process stars donation"""
        try:
            print(f"⭐ Processing stars donation: {stars_amount} stars for user {user_id}")
            
            success = self.stars_system.create_stars_invoice(
                user_id, chat_id, stars_amount, "Bot Stars Donation"
            )
            
            if success:
                self.robust_send_message(chat_id,
                    f"✅ <b>Stars Invoice Created!</b>\n\n"
                    f"Amount: <b>{stars_amount} Stars</b> (${stars_amount * 0.01:.2f})\n\n"
                    "Please complete the payment in the invoice that was just sent to you.\n\n"
                    "Thank you for your support! 🙏",
                    self.create_main_menu_buttons()
                )
                return True
            else:
                self.robust_send_message(chat_id, 
                    "❌ Sorry, there was an error creating the Stars invoice. Please try again.",
                    self.create_stars_menu_buttons()
                )
                return False
                
        except Exception as e:
            print(f"❌ Stars donation processing error: {e}")
            self.robust_send_message(chat_id, 
                "❌ Sorry, there was an error processing your Stars donation. Please try again.",
                self.create_stars_menu_buttons()
            )
            return False
    
    # ==================== GAME REQUEST SYSTEM ====================
    
    def start_game_request(self, user_id, chat_id):
        """Start game request process"""
        self.robust_send_message(chat_id,
            "🎮 <b>Game Request</b>\n\n"
            "Please tell us the name of the game you'd like to request:\n\n"
            "💡 <i>Example: 'God of War: Chains of Olympus'</i>"
        )
        # Store that we're waiting for game name
        self.request_sessions[user_id] = {'stage': 'waiting_game_name'}
        return True
    
    def show_user_requests(self, user_id, chat_id):
        """Show user's game requests"""
        user_requests = self.game_request_system.get_user_requests(user_id, 10)
        
        if not user_requests:
            requests_text = """📋 <b>My Game Requests</b>

You haven't submitted any game requests yet.

Click 'Request New Game' to make your first request!"""
        else:
            requests_text = f"""📋 <b>My Game Requests</b>

📊 Total requests: {len(user_requests)}

📝 <b>Your Requests:</b>"""
            
            for i, req in enumerate(user_requests, 1):
                req_id, game_name, platform, status, created_at = req
                date_str = datetime.fromisoformat(created_at).strftime('%Y-%m-%d')
                
                if status == 'completed':
                    status_icon = "✅"
                    status_text = "Completed"
                elif status == 'pending':
                    status_icon = "⏳"
                    status_text = "Pending"
                else:
                    status_icon = "❌"
                    status_text = "Rejected"
                
                requests_text += f"\n\n{i}. <b>{game_name}</b>"
                requests_text += f"\n📱 {platform} | {status_icon} {status_text}"
                requests_text += f"\n🆔 {req_id} | 📅 {date_str}"
                
                # Check if there are replies
                replies = self.game_request_system.get_request_replies(req_id)
                if replies:
                    requests_text += f"\n💬 {len(replies)} admin replies"
        
        keyboard = [
            ["📝 Request New Game", "🔄 Refresh"],
            ["🔙 Back to Menu"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, requests_text, reply_markup)
    
    # ==================== ADMIN GAME REQUEST MANAGEMENT ====================
    
    def show_admin_requests_panel(self, user_id, chat_id):
        """Show admin game requests management panel"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return
        
        pending_requests = self.game_request_system.get_pending_requests(5)
        
        if not pending_requests:
            requests_text = """👑 <b>Admin - Game Requests</b>

📊 No pending game requests.

All requests have been processed!"""
        else:
            requests_text = f"""👑 <b>Admin - Game Requests</b>

📊 Pending requests: {len(pending_requests)}

📝 <b>Recent Requests:</b>"""
            
            for req in pending_requests:
                req_id, user_id_req, user_name, game_name, platform, created_at = req
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d %H:%M')
                requests_text += f"\n\n🎮 <b>{game_name}</b>"
                requests_text += f"\n👤 {user_name} (ID: {user_id_req}) | 📱 {platform}"
                requests_text += f"\n🆔 ID: {req_id} | 📅 {date_str}"
                requests_text += f"\n└─ Reply command: <code>/reply_{req_id}</code>"
        
        keyboard = [
            ["📝 Manage Requests", "🔄 Refresh"],
            ["🔙 Back to Admin"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, requests_text, reply_markup)
    
    # ==================== BROADCAST MESSAGING SYSTEM ====================
    
    def start_broadcast(self, user_id, chat_id):
        """Start broadcast message creation"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return False
            
        self.broadcast_sessions[user_id] = {
            'stage': 'waiting_message_or_photo',
            'message': '',
            'photo': None,
            'chat_id': chat_id
        }
        
        broadcast_info = """📢 <b>Admin Broadcast System</b>

You can send messages to all bot subscribers.

📝 <b>How to use:</b>
1. Type your broadcast message OR send a photo with caption
2. Preview the message before sending
3. Send to all users or cancel

⚡ <b>Features:</b>
• HTML formatting support
• Photo attachments
• Preview before sending
• Send to all verified users
• Delivery statistics

💡 <b>Type your broadcast message or send a photo now:</b>"""
        
        keyboard = [
            ["❌ Cancel Broadcast"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, broadcast_info, reply_markup)
        return True
    
    def get_broadcast_stats(self, user_id, chat_id):
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
            
            # Count broadcast types
            text_broadcasts = sum(1 for stats in self.broadcast_stats.values() if stats.get('type') == 'text')
            photo_broadcasts = sum(1 for stats in self.broadcast_stats.values() if stats.get('type') == 'photo')
            
            # Get recent broadcasts
            recent_broadcasts = sorted(self.broadcast_stats.items(), key=lambda x: x[0], reverse=True)[:5]
            
            stats_text = f"""📊 <b>Broadcast Statistics</b>

📈 Overview:
• Total broadcasts: {total_broadcasts}
• Text broadcasts: {text_broadcasts}
• Photo broadcasts: {photo_broadcasts}
• Total messages sent: {total_sent}
• Total failed: {total_failed}
• Unique users reached: {total_users_reached}

📋 Recent broadcasts:"""
            
            for broadcast_id, stats in recent_broadcasts:
                date = datetime.fromisoformat(stats['timestamp']).strftime('%Y-%m-%d %H:%M')
                broadcast_type = "📷 Photo" if stats.get('type') == 'photo' else "📝 Text"
                stats_text += f"\n• {date}: {broadcast_type} - {stats['success_count']}/{stats['total_users']} users"
        
        keyboard = [
            ["📢 Start Broadcast", "🔄 Refresh Stats"],
            ["🔙 Back to Admin"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, stats_text, reply_markup)
    
    # ==================== GAME REMOVAL SYSTEM ====================
    
    def start_remove_game_search(self, user_id, chat_id):
        """Start game removal search process"""
        if not self.is_admin(user_id):
            return False
        
        self.robust_send_message(chat_id,
            "🔍 <b>Game Removal Search</b>\n\n"
            "Please enter the game name you want to search and remove:\n\n"
            "💡 You can search by full name or partial keywords"
        )
        
        # Set session for removal search
        self.search_sessions[user_id] = {'mode': 'remove'}
        return True
    
    def show_recent_uploads_for_removal(self, user_id, chat_id):
        """Show recent uploads for removal"""
        if not self.is_admin(user_id):
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT message_id, file_name, file_type, file_size, upload_date, is_uploaded 
            FROM channel_games 
            WHERE is_uploaded = 1 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_uploads = cursor.fetchall()
        
        if not recent_uploads:
            self.robust_send_message(chat_id, "❌ No recent uploads found.", self.create_remove_game_buttons())
            return
        
        uploads_text = "📋 <b>Recent Admin Uploads</b>\n\n"
        uploads_text += "Click 'Remove' to delete any game:\n\n"
        
        # Create keyboard with remove buttons
        keyboard = []
        for upload in recent_uploads:
            msg_id, file_name, file_type, file_size, upload_date, is_uploaded = upload
            size = self.format_file_size(file_size)
            
            uploads_text += f"📁 <b>{file_name}</b>\n"
            uploads_text += f"📦 {file_type} | 📏 {size} | 📅 {upload_date[:10]}\n"
            uploads_text += f"🆔 {msg_id}\n\n"
            
            # Add remove button for this game
            keyboard.append([f"Remove: {file_name}"])
        
        keyboard.append(["🔙 Back to Remove Menu"])
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, uploads_text, reply_markup)
    
    def handle_game_removal(self, user_id, chat_id, filename):
        """Handle game removal request"""
        if not self.is_admin(user_id):
            return False
        
        # Find the game in database
        cursor = self.conn.cursor()
        
        # First try to find in regular games
        cursor.execute('SELECT message_id, file_name FROM channel_games WHERE file_name = ?', (filename,))
        regular_game = cursor.fetchone()
        
        if regular_game:
            message_id, file_name = regular_game
            self.show_remove_confirmation(user_id, chat_id, 'R', message_id, file_name)
            return True
        
        # Try to find in premium games
        cursor.execute('SELECT id, file_name FROM premium_games WHERE file_name = ?', (filename,))
        premium_game = cursor.fetchone()
        
        if premium_game:
            game_id, file_name = premium_game
            self.show_remove_confirmation(user_id, chat_id, 'P', game_id, file_name)
            return True
        
        # If not found by exact name, try partial match
        cursor.execute('SELECT message_id, file_name FROM channel_games WHERE file_name LIKE ? LIMIT 1', (f'%{filename}%',))
        partial_regular = cursor.fetchone()
        
        if partial_regular:
            message_id, file_name = partial_regular
            self.show_remove_confirmation(user_id, chat_id, 'R', message_id, file_name)
            return True
        
        cursor.execute('SELECT id, file_name FROM premium_games WHERE file_name LIKE ? LIMIT 1', (f'%{filename}%',))
        partial_premium = cursor.fetchone()
        
        if partial_premium:
            game_id, file_name = partial_premium
            self.show_remove_confirmation(user_id, chat_id, 'P', game_id, file_name)
            return True
        
        self.robust_send_message(chat_id, f"❌ Game not found: {filename}", self.create_remove_game_buttons())
        return True
    
    def show_remove_confirmation(self, user_id, chat_id, game_type, game_id, file_name):
        """Show removal confirmation"""
        game_type_text = "Regular" if game_type == 'R' else "Premium"
        
        confirm_text = f"""⚠️ <b>Confirm Game Removal</b>

📁 <b>File:</b> <code>{file_name}</code>
🎮 <b>Game Type:</b> {game_type_text}
🆔 <b>ID:</b> {game_id}

❌ <b>This action cannot be undone!</b>

Are you sure you want to remove this game?"""
        
        keyboard = [
            ["✅ Yes, Remove Game", "❌ Cancel Remove"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        # Store removal info in user state
        if user_id not in self.user_state:
            self.user_state[user_id] = {}
        self.user_state[user_id]['remove_game'] = {
            'type': game_type,
            'id': game_id,
            'name': file_name
        }
        
        self.robust_send_message(chat_id, confirm_text, reply_markup)
    
    def remove_game(self, user_id, chat_id, game_type, game_id):
        """Remove a game from database"""
        try:
            if not self.is_admin(user_id):
                return False
            
            cursor = self.conn.cursor()
            game_name = ""
            
            if game_type == 'R':  # Regular game
                # Get game info before deletion
                cursor.execute('SELECT file_name FROM channel_games WHERE message_id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if not game_info:
                    self.robust_send_message(chat_id, "❌ Game not found.")
                    return False
                
                game_name = game_info[0]
                
                # Delete the game
                cursor.execute('DELETE FROM channel_games WHERE message_id = ?', (game_id,))
                self.conn.commit()
                
            elif game_type == 'P':  # Premium game
                # Get game info before deletion
                cursor.execute('SELECT file_name FROM premium_games WHERE id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if not game_info:
                    self.robust_send_message(chat_id, "❌ Premium game not found.")
                    return False
                
                game_name = game_info[0]
                
                # Delete the game and associated purchases
                cursor.execute('DELETE FROM premium_games WHERE id = ?', (game_id,))
                cursor.execute('DELETE FROM premium_purchases WHERE game_id = ?', (game_id,))
                self.conn.commit()
            
            else:
                self.robust_send_message(chat_id, "❌ Invalid game type.")
                return False
            
            # Update cache
            self.update_games_cache()
            
            # Trigger backup after removal
            self.backup_after_game_action("Game Removal", game_name)
            
            result_text = f"✅ <b>{'Regular' if game_type == 'R' else 'Premium'} Game Removed</b>\n\n📁 <code>{game_name}</code>\n🆔 {game_id}\n\nGame has been removed from the database."
            
            self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
            
            return True
            
        except Exception as e:
            print(f"❌ Remove game error: {e}")
            self.robust_send_message(chat_id, "❌ Error removing game.", self.create_admin_buttons())
            return False
    
    # ==================== CLEAR ALL GAMES CONFIRMATION ====================
    
    def clear_all_games_confirmation(self, user_id, chat_id):
        """Show clear all games confirmation"""
        if not self.is_admin(user_id):
            return
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM channel_games')
        total_games = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM premium_games')
        premium_games = cursor.fetchone()[0]
        
        confirm_text = f"""⚠️ <b>Clear All Games Confirmation</b>

📊 Current Statistics:
• Regular Games: {total_games}
• Premium Games: {premium_games}
• Total Games: {total_games + premium_games}

❌ <b>This action will delete ALL games from the database!</b>
⚠️ <b>This cannot be undone!</b>

Are you sure you want to clear all games?"""
        
        keyboard = [
            ["✅ Yes, Clear All Games", "❌ Cancel Clear"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, confirm_text, reply_markup)
    
    def clear_all_games(self, user_id, chat_id):
        """Clear all games from database"""
        if not self.is_admin(user_id):
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Count games before deletion
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games_before = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
            uploaded_games_before = cursor.fetchone()[0]
            
            # Count premium games
            cursor.execute('SELECT COUNT(*) FROM premium_games')
            premium_games_before = cursor.fetchone()[0]
            
            # Delete all games
            cursor.execute('DELETE FROM channel_games')
            cursor.execute('DELETE FROM premium_games')
            self.conn.commit()
            
            # Update cache
            self.update_games_cache()
            
            # Trigger backup after clearing all games
            self.backup_after_game_action("Clear All Games", f"Removed {total_games_before} regular + {premium_games_before} premium games")
            
            clear_text = f"""🗑️ <b>All Games Cleared Successfully!</b>

📊 Before clearing:
• Total regular games: {total_games_before}
• Admin uploaded: {uploaded_games_before}
• Premium games: {premium_games_before}

✅ After clearing:
• All games removed from database
• Cache updated
• Backup created
• Ready for fresh start

🔄 You can now upload new games or rescan the channel."""
            
            self.robust_send_message(chat_id, clear_text, self.create_admin_buttons())
            
            print(f"🗑️ Admin {user_id} cleared all games from database")
            
        except Exception as e:
            error_text = f"❌ Error clearing games: {str(e)}"
            self.robust_send_message(chat_id, error_text, self.create_admin_buttons())
            print(f"❌ Clear games error: {e}")
    
    # ==================== BACKUP SYSTEM HANDLERS ====================
    
    def handle_create_backup(self, user_id, chat_id):
        """Handle manual backup creation"""
        if not self.is_admin(user_id):
            return False
        
        self.robust_send_message(chat_id, "💾 Creating manual backup...")
        
        def backup_operation():
            success = self.github_backup.backup_database_to_github("Manual backup: Admin triggered")
            
            if success:
                result_text = "✅ <b>Backup Created Successfully!</b>\n\nYour database has been backed up to GitHub."
            else:
                result_text = "❌ <b>Backup Failed!</b>\n\nCheck the logs for more information."
            
            self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
        
        # Run backup in background thread
        backup_thread = threading.Thread(target=backup_operation, daemon=True)
        backup_thread.start()
        
        return True
    
    def handle_restore_backup(self, user_id, chat_id):
        """Handle backup restoration with confirmation"""
        if not self.is_admin(user_id):
            return False
        
        backup_info = self.github_backup.get_backup_info()
        
        if not backup_info.get('enabled'):
            self.robust_send_message(chat_id, "❌ GitHub backup is not enabled.", self.create_admin_buttons())
            return False
        
        if backup_info.get('last_backup') == 'Never':
            self.robust_send_message(chat_id, "❌ No backup exists to restore.", self.create_admin_buttons())
            return False
        
        confirm_text = f"""⚠️ <b>Restore Database from Backup?</b>

This will replace your current database with the backup from GitHub.

📅 Backup Date: {backup_info.get('last_backup', 'Unknown')}
💬 Message: {backup_info.get('message', 'Unknown')}

❌ <b>This action cannot be undone!</b>
All current data will be replaced with the backup.

Are you sure you want to continue?"""
        
        keyboard = [
            ["✅ Yes, Restore Backup", "❌ Cancel Restore"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, confirm_text, reply_markup)
        return True
    
    def handle_confirm_restore(self, user_id, chat_id):
        """Handle confirmed backup restoration"""
        if not self.is_admin(user_id):
            return False
        
        self.robust_send_message(chat_id, "🔄 Restoring database from GitHub backup...")
        
        def restore_operation():
            success = self.github_backup.restore_database_from_github()
            
            if success:
                # Reinitialize bot with restored database
                self.setup_database()
                self.verify_database_schema()
                self.update_games_cache()
                self.recover_file_access_after_restart()  # Recover file access after restore
                
                result_text = """✅ <b>Database Restored Successfully!</b>

Your database has been restored from the GitHub backup.

The bot will now use the restored data."""
            else:
                result_text = "❌ <b>Restore Failed!</b>\n\nCheck the logs for more information."
            
            self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
        
        # Run restore in background thread
        restore_thread = threading.Thread(target=restore_operation, daemon=True)
        restore_thread.start()
        
        return True
    
    # ==================== UPLOAD STATS HANDLER ====================
    
    def handle_upload_stats(self, user_id, chat_id):
        """Handle upload statistics display"""
        if not self.is_admin(user_id):
            return
        
        total_uploads = self.get_upload_stats()
        user_uploads = self.get_upload_stats(user_id)
        total_forwards = self.get_forward_stats()
        user_forwards = self.get_forward_stats(user_id)
        total_games = len(self.games_cache.get('all', []))
        
        # Count premium games
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM premium_games')
        premium_games = cursor.fetchone()[0]
        
        # Count bot-uploaded games
        cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1 AND bot_message_id IS NOT NULL')
        bot_uploaded = cursor.fetchone()[0]
        
        stats_text = f"""👑 Admin Panel

📊 Upload Statistics:
• Your uploads: {user_uploads} files
• Your forwarded: {user_forwards} files
• Total bot uploads: {total_uploads} files
• Bot-uploaded games: {bot_uploaded} files
• Total forwarded: {total_forwards} files
• Total regular games: {total_games}
• Premium games: {premium_games}

📤 Upload Methods:
1. Send files directly to bot
2. Forward files from channels/chats
3. Use rescan to find existing bot uploads
4. Premium games with Stars pricing"""
        
        self.robust_send_message(chat_id, stats_text, self.create_admin_buttons())
    
    # ==================== PROFILE HANDLER ====================
    
    def handle_profile(self, chat_id, user_id):
        """Handle profile display"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT created_at, is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            user_info = self.get_user_info(user_id)
            first_name = user_info.get('first_name', 'User')
            
            if result:
                created_at, is_verified, joined_channel = result
                profile_text = f"""👤 <b>User Profile</b>

🆔 User ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Verified: {'Yes' if is_verified else 'No'}
📢 Channel Joined: {'Yes' if joined_channel else 'No'}
📅 Member Since: {created_at}

💡 Your unique ID: <code>{user_id}</code>
Use this ID for admin verification if needed."""
            else:
                profile_text = f"""👤 <b>User Profile</b>

🆔 User ID: <code>{user_id}</code>
👋 Name: {first_name}
✅ Verified: No
📢 Channel Joined: No

💡 Complete verification with /start"""
            
            self.robust_send_message(chat_id, profile_text, self.create_menu_buttons())
            
        except Exception as e:
            print(f"Profile error: {e}")
    
    # ==================== MINI-GAMES METHODS ====================
    
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

🎮 <b>Type your first guess now!</b>

💡 <b>Quick buttons:</b> 1 2 3 4 5 6 7 8 9 10"""
        
        # Create number buttons
        keyboard = [
            ["1", "2", "3", "4", "5"],
            ["6", "7", "8", "9", "10"],
            ["🔄 New Game", "🔙 Back to Mini-Games"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, game_text, reply_markup)
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
        
        keyboard = [
            ["🔄 New Number", "🎯 1-10 Range"],
            ["🎰 1-1000 Range", "💰 Lucky 7"],
            ["🔙 Back to Mini-Games"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, random_text, reply_markup)
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
        
        keyboard = [
            ["🎰 Spin Again", "🎯 Big Spin (3x)"],
            ["🔙 Back to Mini-Games"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, spin_text, reply_markup)
        return True
    
    def show_mini_games_stats(self, user_id, chat_id):
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
        
        self.robust_send_message(chat_id, stats_text, self.create_mini_games_buttons())
    
    # ==================== ENHANCED DATABASE OPERATIONS WITH BACKUP ====================
    
    def backup_after_game_action(self, action_type, game_name=""):
        """Trigger backup after game-related actions"""
        if not self.github_backup.is_enabled:
            return
        
        def async_backup():
            try:
                commit_message = f"Auto backup: {action_type}"
                if game_name:
                    commit_message += f" - {game_name}"
                
                success = self.github_backup.backup_database_to_github(commit_message)
                if success:
                    print(f"✅ Automatic backup completed for: {action_type}")
                else:
                    print(f"⚠️ Automatic backup failed for: {action_type}")
            except Exception as e:
                print(f"❌ Backup thread error: {e}")
        
        # Start backup in background thread
        backup_thread = threading.Thread(target=async_backup, daemon=True)
        backup_thread.start()
    
    # ==================== FILE SENDING METHODS (FIXED) ====================
    
    def send_game_file(self, chat_id, message_id, file_id=None, is_bot_file=False):
        """Universal file sending that works for all users - FIXED VERSION"""
        try:
            print(f"📤 Sending game file to user {chat_id}: msg_id={message_id}, file_id={file_id[:20] if file_id else 'None'}, is_bot_file={is_bot_file}")
            
            # If we have a file_id, try to send it directly first
            if file_id and file_id not in ['short', 'none', '']:
                print(f"🔄 Attempting direct file_id send: {file_id[:20]}...")
                if self.send_document_directly(chat_id, file_id):
                    print("✅ Successfully sent via direct file_id")
                    return True
            
            # If it's a bot-uploaded file, we need to handle it differently
            if is_bot_file:
                print("🔄 Handling bot-uploaded file...")
                
                # Get game info from database
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT message_id, file_name, file_type, file_size, added_by, file_id, bot_message_id, is_uploaded 
                    FROM channel_games 
                    WHERE bot_message_id = ? OR message_id = ?
                    LIMIT 1
                ''', (message_id, message_id))
                
                game_info = cursor.fetchone()
                
                if game_info:
                    db_message_id, file_name, file_type, file_size, added_by, db_file_id, bot_msg_id, is_uploaded = game_info
                    print(f"📁 Found game in DB: {file_name}, added_by: {added_by}, bot_msg_id: {bot_msg_id}")
                    
                    # If we have a file_id in DB, try it
                    if db_file_id and db_file_id not in ['short', 'none', '']:
                        print(f"🔄 Trying DB file_id: {db_file_id[:20]}...")
                        if self.send_document_directly(chat_id, db_file_id):
                            print("✅ Successfully sent via DB file_id")
                            return True
                    
                    # Try to get fresh file_id from admin's chat
                    if bot_msg_id and added_by in self.ADMIN_IDS:
                        print(f"🔄 Getting fresh file_id from admin {added_by}...")
                        fresh_file_id = self.get_file_id_from_message(added_by, bot_msg_id)
                        if fresh_file_id:
                            print(f"🔄 Got fresh file_id: {fresh_file_id[:20]}...")
                            if self.send_document_directly(chat_id, fresh_file_id):
                                # Update DB with new file_id
                                cursor.execute('UPDATE channel_games SET file_id = ? WHERE bot_message_id = ?', (fresh_file_id, bot_msg_id))
                                self.conn.commit()
                                print("✅ Successfully sent via fresh file_id and updated DB")
                                return True
                    
                    # Last resort: try to forward the original message
                    if bot_msg_id and added_by in self.ADMIN_IDS:
                        print(f"🔄 Forwarding original message from admin {added_by}...")
                        if self.forward_message(chat_id, added_by, bot_msg_id):
                            print("✅ Successfully forwarded message")
                            return True
            
            # If it's a channel file, try to forward it
            if not is_bot_file:
                print("🔄 Forwarding channel file...")
                if self.forward_message(chat_id, self.REQUIRED_CHANNEL, message_id):
                    print("✅ Successfully forwarded channel file")
                    return True
            
            # If all methods fail, send error message
            print("❌ All file sending methods failed")
            self.robust_send_message(chat_id, 
                "❌ Unable to send file. The file may have been removed or is inaccessible. "
                "Please contact an admin for assistance.",
                self.create_main_menu_buttons()
            )
            return False
            
        except Exception as e:
            print(f"❌ Error sending game file: {e}")
            traceback.print_exc()
            self.robust_send_message(chat_id, 
                "❌ Error sending file. Please try again or contact admin.",
                self.create_main_menu_buttons()
            )
            return False
    
    def send_document_directly(self, chat_id, file_id):
        """Send document directly using file_id with enhanced error handling"""
        try:
            print(f"📤 Sending document directly with file_id: {file_id[:30]}...")
            
            # First verify the file_id is valid
            url = self.base_url + "getFile"
            data = {"file_id": file_id}
            verify_response = requests.post(url, data=data, timeout=10)
            verify_result = verify_response.json()
            
            if not verify_result.get('ok'):
                print(f"❌ File_id is invalid: {verify_result.get('description')}")
                return False
            
            # Now send the document
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id,
                "caption": "📥 Here's your requested file!"
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Sent document directly to user {chat_id}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ Direct send failed: {error_msg}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout sending document")
            return False
        except Exception as e:
            print(f"❌ Error sending document directly: {e}")
            return False
    
    def get_file_id_from_message(self, chat_id, message_id):
        """Get file_id from a specific message"""
        try:
            url = self.base_url + "getMessage"
            data = {
                "chat_id": chat_id,
                "message_id": message_id
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                message = result['result']
                if 'document' in message:
                    file_id = message['document'].get('file_id')
                    print(f"✅ Got file_id from message {message_id}: {file_id[:20]}...")
                    return file_id
                elif 'photo' in message:
                    # Get the highest quality photo
                    file_id = message['photo'][-1].get('file_id')
                    print(f"✅ Got photo file_id from message {message_id}: {file_id[:20]}...")
                    return file_id
            
            print(f"❌ No document or photo in message {message_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting file_id from message: {e}")
            return None
    
    def forward_message(self, from_chat_id, to_chat_id, message_id):
        """Forward a message from one chat to another"""
        try:
            url = self.base_url + "forwardMessage"
            data = {
                "chat_id": to_chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id
            }
            
            response = requests.post(url, data=data, timeout=30)
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
    
    def send_premium_game_file(self, user_id, chat_id, game_id):
        """Send premium game file to user"""
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            self.robust_send_message(chat_id, "❌ Game not found.")
            return False
        
        # Verify purchase
        if not self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(chat_id, "❌ You haven't purchased this game yet.")
            return False
        
        # Send the game file
        if game['is_uploaded'] == 1 and game['bot_message_id']:
            # Bot-uploaded file - use enhanced file sending
            success = self.send_game_file(chat_id, game['bot_message_id'], game['file_id'], True)
        else:
            # Channel file
            success = self.send_game_file(chat_id, game['message_id'], game['file_id'], False)
        
        if success:
            self.robust_send_message(chat_id, f"✅ Enjoy your premium game: <b>{game['file_name']}</b>!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send game file. Please contact admin.")
            return False
    
    # ==================== UPLOAD SYSTEM ENHANCEMENTS ====================
    
    def handle_document_upload(self, message):
        """Handle document uploads from admins - FIXED VERSION"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            if not self.is_admin(user_id):
                print(f"❌ Non-admin user {user_id} attempted upload")
                return False
            
            if 'document' not in message:
                print("❌ No document in message")
                return False
            
            # Check if this is a premium game upload
            if user_id in self.upload_sessions and self.upload_sessions[user_id]['type'] == 'premium':
                result = self.handle_premium_document_upload(message)
                if result:
                    # Trigger backup for premium game upload
                    file_name = message['document'].get('file_name', 'Unknown')
                    self.backup_after_game_action("Premium Game Upload", file_name)
                return result
            
            # Regular game upload
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            bot_message_id = message['message_id']
            
            print(f"📥 Admin {user_id} uploading: {file_name} (Size: {file_size}, Message ID: {bot_message_id})")
            print(f"📁 File ID: {file_id[:30]}...")
            
            # Check for duplicates
            regular_duplicate, premium_duplicate = self.check_duplicate_game(file_name, file_size, file_type)
            
            if regular_duplicate or premium_duplicate:
                duplicate_text = f"""⚠️ <b>Duplicate Game Detected!</b>

📁 File: <code>{file_name}</code>
📏 Size: {self.format_file_size(file_size)}
📦 Type: {file_type}

This game already exists in the database:"""
                
                if regular_duplicate:
                    dup_msg_id, dup_file_name = regular_duplicate
                    duplicate_text += f"\n\n🆓 <b>Regular Game:</b>"
                    duplicate_text += f"\n📝 Name: <code>{dup_file_name}</code>"
                    duplicate_text += f"\n🆔 Message ID: {dup_msg_id}"
                
                if premium_duplicate:
                    dup_id, dup_file_name = premium_duplicate
                    duplicate_text += f"\n\n💰 <b>Premium Game:</b>"
                    duplicate_text += f"\n📝 Name: <code>{dup_file_name}</code>"
                    duplicate_text += f"\n🆔 Game ID: {dup_id}"
                
                duplicate_text += "\n\n❌ Upload cancelled. Please upload a different file."
                
                # Clean up session
                if user_id in self.upload_sessions:
                    del self.upload_sessions[user_id]
                
                self.robust_send_message(chat_id, duplicate_text)
                return True
            
            # Check if it's a supported game file
            game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk', '.txt', '.pdf']
            if not any(file_name.lower().endswith(ext) for ext in game_extensions):
                self.robust_send_message(chat_id, f"❌ File type not supported: {file_name}")
                print(f"❌ Unsupported file type: {file_name}")
                return False
            
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine if this is a forwarded file
            is_forwarded = 'forward_origin' in message
            forward_info = ""
            original_message_id = None
            
            if is_forwarded:
                forward_origin = message['forward_origin']
                if 'sender_user' in forward_origin:
                    forward_user = forward_origin['sender_user']
                    forward_name = forward_user.get('first_name', 'Unknown')
                    forward_info = f"\n🔄 Forwarded from: {forward_name}"
                elif 'chat' in forward_origin:
                    forward_chat = forward_origin['chat']
                    forward_title = forward_chat.get('title', 'Unknown Chat')
                    forward_info = f"\n🔄 Forwarded from: {forward_title}"
                
                # Get original message ID for channel forwards
                if 'chat' in forward_origin and forward_origin['chat']['type'] == 'channel':
                    original_message_id = message.get('forward_from_message_id')
                    print(f"📨 Forwarded from channel, original message ID: {original_message_id}")
            
            # Generate unique message ID for storage
            if original_message_id:
                storage_message_id = original_message_id
            else:
                # For bot-uploaded files, create a unique ID
                storage_message_id = int(time.time() * 1000) + random.randint(1000, 9999)
            
            # CRITICAL: Test if file_id is accessible by other users
            file_id_accessible = self.test_file_id_accessibility(file_id)
            
            if not file_id_accessible:
                print("⚠️ File ID not universally accessible, will use message forwarding")
                # We'll rely on message forwarding instead of file_id
            
            # Prepare game info
            game_info = {
                'message_id': storage_message_id,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': file_size,
                'upload_date': upload_date,
                'category': self.determine_file_category(file_name),
                'added_by': user_id,
                'is_uploaded': 1,  # Mark as uploaded by admin
                'is_forwarded': 1 if is_forwarded else 0,
                'file_id': file_id if file_id_accessible else None,  # Only store if accessible
                'bot_message_id': bot_message_id  # Store the actual bot message ID
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
            source_type = "Channel Forward" if original_message_id else "Direct Upload"
            file_access = "✅ Universal Access" if file_id_accessible else "⚠️ Forwarding Required"
            
            confirm_text = f"""✅ Game file added successfully!{forward_info}

📁 File: <code>{file_name}</code>
📦 Type: {file_type}
📏 Size: {size}
🗂️ Category: {game_info['category']}
🕒 Added: {upload_date}
📮 Source: {source_type}
🔗 Access: {file_access}
🆔 Storage ID: {storage_message_id}
🤖 Bot Message ID: {bot_message_id}

The file is now available in the games browser and search!"""
            
            self.robust_send_message(chat_id, confirm_text)
            
            # Trigger backup after successful upload
            self.backup_after_game_action("Regular Game Upload", file_name)
            
            print(f"✅ Successfully stored: {file_name} (Storage ID: {storage_message_id}, Bot Message ID: {bot_message_id})")
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            import traceback
            traceback.print_exc()
            self.robust_send_message(chat_id, f"❌ Error uploading file: {str(e)[:100]}")
            return False
    
    def start_premium_upload(self, user_id, chat_id):
        """Start premium game upload process"""
        if not self.is_admin(user_id):
            return False
        
        self.upload_sessions[user_id] = {
            'stage': 'waiting_stars_price',
            'type': 'premium',
            'chat_id': chat_id
        }
        
        self.robust_send_message(chat_id,
            "⭐ <b>Premium Game Upload</b>\n\n"
            "Please set the price in Telegram Stars for this game:\n\n"
            "💡 <i>Enter a number (e.g., 50 for 50 Stars ≈ $0.50)</i>\n"
            "💰 <i>Recommended: 50-500 Stars</i>"
        )
        return True
    
    def handle_premium_document_upload(self, message):
        """Handle premium game document upload"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            if user_id not in self.upload_sessions or self.upload_sessions[user_id]['type'] != 'premium':
                return False
            
            if 'document' not in message:
                return False
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            bot_message_id = message['message_id']
            
            # Check for duplicates
            regular_duplicate, premium_duplicate = self.check_duplicate_game(file_name, file_size, file_type)
            
            if regular_duplicate or premium_duplicate:
                duplicate_text = f"""⚠️ <b>Duplicate Premium Game Detected!</b>

📁 File: <code>{file_name}</code>
📏 Size: {self.format_file_size(file_size)}
📦 Type: {file_type}

This game already exists in the database:"""
                
                if regular_duplicate:
                    dup_msg_id, dup_file_name = regular_duplicate
                    duplicate_text += f"\n\n🆓 <b>Regular Game:</b>"
                    duplicate_text += f"\n📝 Name: <code>{dup_file_name}</code>"
                    duplicate_text += f"\n🆔 Message ID: {dup_msg_id}"
                
                if premium_duplicate:
                    dup_id, dup_file_name = premium_duplicate
                    duplicate_text += f"\n\n💰 <b>Premium Game:</b>"
                    duplicate_text += f"\n📝 Name: <code>{dup_file_name}</code>"
                    duplicate_text += f"\n🆔 Game ID: {dup_id}"
                
                duplicate_text += "\n\n❌ Upload cancelled. Please upload a different file."
                
                # Clean up session
                del self.upload_sessions[user_id]
                
                self.robust_send_message(chat_id, duplicate_text)
                return True
            
            session = self.upload_sessions[user_id]
            
            # Prepare premium game info
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
                'bot_message_id': bot_message_id,
                'stars_price': session['stars_price'],
                'description': session.get('description', ''),
                'is_premium': 1
            }
            
            # Store in premium games database
            game_id = self.premium_games_system.add_premium_game(game_info)
            
            if game_id:
                # Clean up session
                del self.upload_sessions[user_id]
                
                # Send confirmation
                size = self.format_file_size(file_size)
                confirm_text = f"""✅ <b>Premium Game Added Successfully!</b>

🎮 Game: <code>{file_name}</code>
💰 Price: <b>{session['stars_price']} Stars</b>
📦 Type: {game_info['file_type']}
📏 Size: {size}
🗂️ Category: {game_info['category']}
📝 Description: {session.get('description', 'None')}
🆔 Game ID: {game_id}

⭐ The game is now available in the premium games section!"""
                
                self.robust_send_message(chat_id, confirm_text)
                
                # Trigger backup for premium game upload
                self.backup_after_game_action("Premium Game Upload", file_name)
                
                print(f"✅ Premium game added: {file_name} for {session['stars_price']} Stars")
                return True
            else:
                self.robust_send_message(chat_id, "❌ Failed to add premium game to database.")
                return False
                
        except Exception as e:
            print(f"❌ Premium upload error: {e}")
            self.robust_send_message(chat_id, "❌ Error processing premium game upload.")
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
                
                # Handle text commands from keyboard
                if self.handle_text_command(user_id, chat_id, text):
                    return True
                
                # Handle command replies for game requests
                if text.startswith('/reply_') and self.is_admin(user_id):
                    try:
                        request_id = int(text.replace('/reply_', ''))
                        return self.start_request_reply(user_id, chat_id, request_id)
                    except ValueError:
                        pass
                
                # Handle game removal search
                if user_id in self.search_sessions and self.search_sessions[user_id].get('mode') == 'remove':
                    return self.handle_remove_game_search(message)
                
                # Handle premium upload process
                if user_id in self.upload_sessions:
                    session = self.upload_sessions[user_id]
                    
                    if session['stage'] == 'waiting_stars_price':
                        return self.handle_stars_price(user_id, chat_id, text)
                    
                    elif session['stage'] == 'waiting_description':
                        return self.handle_premium_description(user_id, chat_id, text)
                
                # Handle game request process
                if user_id in self.request_sessions:
                    session = self.request_sessions[user_id]
                    
                    if session['stage'] == 'waiting_game_name':
                        # User provided game name, now ask for platform
                        return self.handle_game_request(user_id, chat_id, text)
                    
                    elif session['stage'] == 'waiting_platform':
                        # User provided platform, complete the request
                        return self.complete_game_request(user_id, chat_id, text)
                
                # Handle request reply process
                if user_id in self.reply_sessions:
                    session = self.reply_sessions[user_id]
                    
                    if session['stage'] == 'waiting_reply':
                        return self.handle_request_reply(user_id, chat_id, text)
                
                # Handle stars custom amount input
                if user_id in self.stars_sessions:
                    try:
                        stars_amount = int(text.strip())
                        if stars_amount <= 0:
                            self.robust_send_message(chat_id, "❌ Please enter a positive number of Stars.")
                            return True
                        
                        # Process the stars donation
                        del self.stars_sessions[user_id]
                        return self.process_stars_donation(user_id, chat_id, stars_amount)
                    except ValueError:
                        self.robust_send_message(chat_id, "❌ Please enter a valid number for the Stars amount.")
                        return True
                
                # Handle broadcast messages from admins
                if user_id in self.broadcast_sessions:
                    return self.handle_broadcast_message(user_id, chat_id, text)
                
                # Handle mini-games input
                if user_id in self.guess_games:
                    # Check if it's a number guess for an active game
                    if text.strip().isdigit():
                        return self.handle_guess_input(user_id, chat_id, text)
                
                # Handle commands
                if text.startswith('/'):
                    if text == '/start':
                        return self.handle_verification(message)
                    elif text == '/scan' and self.is_admin(user_id):
                        self.robust_send_message(chat_id, "🔄 Scanning channel and bot-uploaded games...")
                        total_games = self.scan_channel_for_games()
                        self.robust_send_message(chat_id, f"✅ Scan complete! Found {total_games} total games.")
                        return True
                    elif text == '/menu' and self.is_user_completed(user_id):
                        self.show_main_menu(user_id, chat_id)
                        return True
                    elif text == '/minigames' and self.is_user_completed(user_id):
                        self.show_mini_games_menu(user_id, chat_id)
                        return True
                    elif text == '/guess' and self.is_user_completed(user_id):
                        return self.start_number_guess_game(user_id, chat_id)
                    elif text == '/random' and self.is_user_completed(user_id):
                        return self.generate_random_number(user_id, chat_id)
                    elif text == '/spin' and self.is_user_completed(user_id):
                        return self.lucky_spin(user_id, chat_id)
                    elif text == '/stars' and self.is_user_completed(user_id):
                        self.show_stars_menu(user_id, chat_id)
                        return True
                    elif text == '/premium' and self.is_user_completed(user_id):
                        self.show_premium_games_menu(user_id, chat_id)
                        return True
                    elif text == '/request' and self.is_user_completed(user_id):
                        return self.start_game_request(user_id, chat_id)
                    elif text == '/broadcast' and self.is_admin(user_id):
                        return self.start_broadcast(user_id, chat_id)
                    elif text == '/cleargames' and self.is_admin(user_id):
                        self.clear_all_games_confirmation(user_id, chat_id)
                        return True
                    elif text == '/removegames' and self.is_admin(user_id):
                        self.show_remove_game_menu(user_id, chat_id)
                        return True
                    elif text == '/upload' and self.is_admin(user_id):
                        self.show_upload_options(user_id, chat_id)
                        return True
                    elif text == '/debug_uploads' and self.is_admin(user_id):
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            SELECT message_id, file_name, bot_message_id, is_uploaded, is_forwarded 
                            FROM channel_games 
                            WHERE is_uploaded = 1 
                            ORDER BY id DESC 
                            LIMIT 10
                        ''')
                        recent_uploads = cursor.fetchall()
                        
                        debug_text = "🔧 Recent Uploads Debug:\n\n"
                        for upload in recent_uploads:
                            msg_id, file_name, bot_msg_id, is_uploaded, is_forwarded = upload
                            debug_text += f"📁 {file_name}\n"
                            debug_text += f"   🆔: {msg_id} | 🤖: {bot_msg_id}\n"
                            debug_text += f"   📤: {is_uploaded} | 🔄: {is_forwarded}\n\n"
                        
                        self.robust_send_message(chat_id, debug_text)
                        return True
                    elif text == '/keepalive' and self.is_admin(user_id):
                        if self.keep_alive and self.keep_alive.is_running:
                            status = "🟢 RUNNING"
                            ping_count = self.keep_alive.ping_count
                        else:
                            status = "🔴 STOPPED"
                            ping_count = 0
                        
                        keepalive_text = f"""🔋 <b>Keep-Alive Status</b>

Status: {status}
Ping Count: {ping_count}
Health URL: {self.keep_alive.health_url if self.keep_alive else 'Not set'}

This service pings the bot every 4 minutes to prevent sleep on free hosting."""
                        self.robust_send_message(chat_id, keepalive_text)
                        return True
                    elif text == '/starsstats' and self.is_admin(user_id):
                        self.show_stars_stats(user_id, chat_id)
                        return True
                    elif text == '/requests' and self.is_admin(user_id):
                        self.show_admin_requests_panel(user_id, chat_id)
                        return True
                    elif text == '/redeploy' and self.is_admin(user_id):
                        self.redeploy_system.show_redeploy_menu(user_id, chat_id)
                        return True
                    elif text == '/status' and self.is_admin(user_id):
                        self.redeploy_system.show_system_status(user_id, chat_id)
                        return True
                    elif text == '/backup' and self.is_admin(user_id):
                        self.show_backup_menu(user_id, chat_id)
                        return True
                
                # Handle code verification
                if text.isdigit() and len(text) == 6:
                    return self.handle_code_verification(message)
                
                # Handle game search
                if self.is_user_verified(user_id):
                    return self.handle_game_search(message)
            
            # Handle photo messages for broadcasts and request replies
            if 'photo' in message:
                user_id = message['from']['id']
                chat_id = message['chat']['id']
                
                # Check if this is a broadcast photo
                if user_id in self.broadcast_sessions and self.broadcast_sessions[user_id]['stage'] == 'waiting_message_or_photo':
                    photo = message['photo'][-1]  # Get the highest resolution photo
                    photo_file_id = photo['file_id']
                    caption = message.get('caption', '')
                    return self.handle_broadcast_photo(user_id, chat_id, photo_file_id, caption)
                
                # Check if this is a request reply photo
                if user_id in self.reply_sessions and self.reply_sessions[user_id]['stage'] == 'waiting_photo':
                    photo = message['photo'][-1]
                    photo_file_id = photo['file_id']
                    caption = message.get('caption', '')
                    return self.handle_photo_reply(user_id, chat_id, photo_file_id, caption)
            
            # Handle document uploads from admins
            if 'document' in message and self.is_admin(message['from']['id']):
                return self.handle_document_upload(message)
            
            # Handle forwarded messages from admins
            if 'forward_origin' in message and self.is_admin(message['from']['id']):
                return self.handle_forwarded_message(message)
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            return False
    
    # ==================== YOUR ORIGINAL METHODS (SIMPLIFIED) ====================
    
    # These are the original methods from your code that I've kept
    # I've removed the callback query handling parts since we're using regular keyboards
    
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
                self.show_main_menu(user_id, chat_id)
                return True
            
            # Check if user is verified but not joined channel
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                self.robust_send_message(chat_id,
                    f"""📢 <b>Channel Verification Required</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:""",
                    self.create_verification_buttons()
                )
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
                    self.show_main_menu(user_id, chat_id)
                else:
                    self.robust_send_message(chat_id, 
                        f"""✅ <b>Code Verified!</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

📝 <b>Step 2: Join Our Channel</b>

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:""",
                        self.create_verification_buttons()
                    )
                return True
            else:
                self.robust_send_message(chat_id, "❌ Invalid or expired code. Please use /start to get a new code.")
                return True
                
        except Exception as e:
            print(f"❌ Code verification error: {e}")
            return False
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def create_progress_bar(self, percentage, length=10):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty
    
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
        
        # Create number buttons
        keyboard = [
            ["1", "2", "3", "4", "5"],
            ["6", "7", "8", "9", "10"],
            ["🔄 New Game", "🔙 Back to Mini-Games"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        if guess == target:
            time_taken = time.time() - game['start_time']
            win_text = f"""🎉 <b>Congratulations! You won!</b>

✅ Correct guess: <b>{guess}</b>
🎯 Target number: <b>{target}</b>
📊 Attempts used: <b>{game['attempts']}</b>
⏱️ Time taken: <b>{time_taken:.1f} seconds</b>

🏆 <b>Well done!</b>"""
            
            self.robust_send_message(chat_id, win_text, reply_markup)
            del self.guess_games[user_id]
            
        elif game['attempts'] >= game['max_attempts']:
            lose_text = f"""😔 <b>Game Over!</b>

🎯 The number was: <b>{target}</b>
📊 Your attempts: <b>{game['attempts']}</b>
💡 Better luck next time!

🔄 Want to try again?"""
            
            self.robust_send_message(chat_id, lose_text, reply_markup)
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
            
            self.robust_send_message(chat_id, progress_text, reply_markup)
        
        return True
    
    def scan_bot_uploaded_games(self):
        """Scan for game files uploaded directly to the bot by admins"""
        try:
            print("🔍 Scanning for bot-uploaded games...")
            
            # Get recent messages from the bot's chat
            url = self.base_url + "getUpdates"
            params = {"timeout": 10, "limit": 100}
            response = requests.get(url, params=params, timeout=30)
            result = response.json()
            
            if not result.get('ok'):
                print(f"❌ Cannot get updates: {result.get('description')}")
                return 0
            
            updates = result.get('result', [])
            bot_games_found = 0
            
            for update in updates:
                if 'message' in update:
                    message = update['message']
                    
                    # Check if message is from admin and contains a document
                    if (message.get('from', {}).get('id') in self.ADMIN_IDS and 
                        'document' in message):
                        
                        doc = message['document']
                        file_name = doc.get('file_name', '').lower()
                        
                        game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk', '.txt', '.pdf']
                        if any(file_name.endswith(ext) for ext in game_extensions):
                            
                            # Check if this game is already in database
                            cursor = self.conn.cursor()
                            cursor.execute('SELECT message_id FROM channel_games WHERE bot_message_id = ?', (message['message_id'],))
                            existing_game = cursor.fetchone()
                            
                            if not existing_game:
                                # Add to database
                                file_type = file_name.split('.')[-1].upper()
                                file_size = doc.get('file_size', 0)
                                file_id = doc.get('file_id', '')
                                upload_date = datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
                                
                                game_info = {
                                    'message_id': int(time.time() * 1000) + random.randint(1000, 9999),
                                    'file_name': doc.get('file_name', 'Unknown'),
                                    'file_type': file_type,
                                    'file_size': file_size,
                                    'upload_date': upload_date,
                                    'category': self.determine_file_category(file_name),
                                    'added_by': message['from']['id'],
                                    'is_uploaded': 1,
                                    'is_forwarded': 0,
                                    'file_id': file_id,
                                    'bot_message_id': message['message_id']
                                }
                                
                                cursor.execute('''
                                    INSERT OR IGNORE INTO channel_games 
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
                                bot_games_found += 1
                                print(f"✅ Found bot-uploaded game: {file_name}")
            
            if bot_games_found > 0:
                print(f"✅ Added {bot_games_found} bot-uploaded games to database")
                # Trigger backup after scanning
                self.backup_after_game_action("Bot Games Scan", f"Found {bot_games_found} games")
            
            return bot_games_found
            
        except Exception as e:
            print(f"❌ Bot games scan error: {e}")
            return 0
    
    def search_games(self, search_term, user_id):
        search_term = search_term.lower().strip()
        results = []
        
        total_steps = 5
        progress_messages = [
            "🔍 Starting search...",
            "📁 Scanning database...",
            "🔎 Matching files...",
            "📊 Analyzing results...",
            "✅ Search complete!"
        ]
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT message_id, file_name, file_type, file_size, upload_date, category, file_id, 
                   bot_message_id, is_uploaded, is_forwarded
            FROM channel_games 
            WHERE LOWER(file_name) LIKE ? OR file_name LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        all_games = cursor.fetchall()
        
        for step in range(total_steps):
            progress = int((step + 1) * 100 / total_steps)
            
            if user_id in self.search_sessions:
                self.search_sessions[user_id]['progress'] = progress
                self.search_sessions[user_id]['message'] = progress_messages[step]
            
            time.sleep(0.3)
            
            if step == total_steps - 1:
                for game in all_games:
                    (message_id, file_name, file_type, file_size, upload_date, 
                     category, file_id, bot_message_id, is_uploaded, is_forwarded) = game
                    
                    # More flexible matching
                    if (search_term in file_name.lower() or 
                        search_term.replace(' ', '').lower() in file_name.lower().replace(' ', '') or
                        any(word in file_name.lower() for word in search_term.split())):
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
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            search_term = message.get('text', '').strip()
            first_name = message['from']['first_name']
            
            if not search_term:
                return False
            
            if not self.is_user_verified(user_id):
                self.robust_send_message(chat_id, "🔐 Please complete verification first with /start")
                return True
            
            print(f"🔍 User {user_id} searching for: '{search_term}'")
            
            # Show initial search message
            search_msg = self.robust_send_message(chat_id, 
                f"🔍 Searching for: <code>{search_term}</code>\n\n"
                f"{self.create_progress_bar(0)} 0%\n"
                f"🕒 Starting search..."
            )
            
            if not search_msg:
                return False
            
            def perform_search():
                try:
                    results = self.search_games(search_term, user_id)
                    
                    progress_info = self.search_sessions.get(user_id, {})
                    search_time = time.time() - progress_info.get('start_time', time.time())
                    
                    self.search_results[user_id] = {
                        'results': results,
                        'search_term': search_term,
                        'timestamp': time.time()
                    }
                    
                    print(f"🔍 Search completed: Found {len(results)} results for '{search_term}'")
                    
                    if results:
                        results_text = f"✅ Search Complete! ({search_time:.1f}s)\n\n"
                        results_text += f"🔍 Found {len(results)} results for: <code>{search_term}</code>\n\n"
                        results_text += "📥 Click on any file below to download it:\n\n"
                        
                        # Create keyboard with search results
                        keyboard = []
                        for i, game in enumerate(results[:10], 1):
                            size = self.format_file_size(game['file_size'])
                            source = "🤖 Bot" if game['is_uploaded'] == 1 else "📢 Channel"
                            
                            results_text += f"{i}. <code>{game['file_name']}</code>\n"
                            results_text += f"   📦 {game['file_type']} | 📏 {size} | 🗂️ {game['category']} | {source}\n\n"
                            
                            # Add download button for this game
                            keyboard.append([f"Download: {game['file_name']}"])
                        
                        if len(results) > 10:
                            results_text += f"📋 ... and {len(results) - 10} more files\n\n"
                        
                        results_text += "🔗 Click any file above to download it instantly!"
                        
                        # Add navigation buttons
                        keyboard.append(["🔍 New Search", "📁 Browse All"])
                        keyboard.append(["💰 Premium Games", "📝 Request Game"])
                        keyboard.append(["🔙 Back to Menu"])
                        
                        reply_markup = {
                            "keyboard": keyboard,
                            "resize_keyboard": True,
                            "one_time_keyboard": False,
                            "selective": False
                        }
                        
                        self.robust_send_message(chat_id, results_text, reply_markup)
                    else:
                        results_text = f"❌ No results found for: <code>{search_term}</code>\n\n"
                        results_text += "💡 Try:\n• Different keywords\n• Shorter search terms\n• Check spelling"
                        results_text += "\n\n🔍 Try a new search:"
                        
                        self.robust_send_message(chat_id, results_text, self.create_search_buttons())
                    
                    if user_id in self.search_sessions:
                        del self.search_sessions[user_id]
                        
                except Exception as e:
                    print(f"❌ Search error: {e}")
                    self.robust_send_message(chat_id, "❌ Search failed. Please try again.")
                    if user_id in self.search_sessions:
                        del self.search_sessions[user_id]
            
            search_thread = threading.Thread(target=perform_search, daemon=True)
            search_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Search handler error: {e}")
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
            elif 'gba' in filename_lower:
                return 'GBA Games'
            elif 'nes' in filename_lower:
                return 'NES Games'
            else:
                return 'ZIP Games'
        elif filename_lower.endswith('.7z'):
            return '7Z Games'
        elif filename_lower.endswith('.pkg'):
            return 'PS Vita Games'
        elif filename_lower.endswith('.cso') or filename_lower.endswith('.pbp'):
            return 'PSP Games'
        elif filename_lower.endswith('.txt'):
            return 'Text Files'
        elif filename_lower.endswith('.pdf'):
            return 'PDF Files'
        else:
            return 'Other Games'
    
    def get_upload_stats(self, user_id=None):
        try:
            cursor = self.conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT COUNT(*) FROM channel_games 
                    WHERE added_by = ? AND is_uploaded = 1
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM channel_games 
                    WHERE is_uploaded = 1
                ''')
            
            upload_count = cursor.fetchone()[0]
            return upload_count
        except:
            return 0
    
    def get_forward_stats(self, user_id=None):
        try:
            cursor = self.conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT COUNT(*) FROM channel_games 
                    WHERE added_by = ? AND is_uploaded = 1 AND is_forwarded = 1
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM channel_games 
                    WHERE is_uploaded = 1 AND is_forwarded = 1
                ''')
            
            forward_count = cursor.fetchone()[0]
            return forward_count
        except:
            return 0
    
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
            
            # Stars tables
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
            
            # Game requests table
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
            
            # Game request replies table
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
            
            # Premium games table
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
            
            # Premium game purchases table
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
            
            # Initialize balances if not exists
            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')
            
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
    
    def scan_channel_for_games(self):
        """Enhanced scan that includes both channel and bot-uploaded games"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        try:
            print(f"🔍 Scanning {self.REQUIRED_CHANNEL} and bot-uploaded games...")
            
            channel_games_found = 0
            bot_games_found = 0
            
            # Scan channel for games
            url = self.base_url + "getChat"
            data = {"chat_id": self.REQUIRED_CHANNEL}
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                url = self.base_url + "getChatHistory"
                data = {
                    "chat_id": self.REQUIRED_CHANNEL,
                    "limit": 50
                }
                response = requests.post(url, data=data, timeout=30)
                result = response.json()
                
                if result.get('ok'):
                    messages = result.get('result', [])
                    game_files = []
                    
                    for message in messages:
                        game_info = self.extract_game_info(message)
                        if game_info:
                            game_files.append(game_info)
                    
                    if game_files:
                        self.store_games_in_db(game_files)
                        channel_games_found = len(game_files)
                        print(f"✅ Found {channel_games_found} channel game files")
                    else:
                        print("ℹ️ No game files found in channel messages")
                else:
                    print(f"❌ Cannot get channel messages: {result.get('description')}")
            else:
                print("❌ Bot needs to be admin in the channel")
            
            # Scan for bot-uploaded games
            bot_games_found = self.scan_bot_uploaded_games()
            
            # Update cache
            self.update_games_cache()
            
            total_games = channel_games_found + bot_games_found
            print(f"🔄 Rescan complete! Found {total_games} total games ({channel_games_found} from channel, {bot_games_found} from bot uploads)")
            
            self.is_scanning = False
            return total_games
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            self.is_scanning = False
            return 0
    
    def extract_game_info(self, message):
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
    
    def store_games_in_db(self, game_files):
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
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
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
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Original send_message - now uses robust version"""
        return self.robust_send_message(chat_id, text, reply_markup)
    
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
    
    def check_duplicate_game(self, file_name, file_size, file_type):
        """Check if a game already exists in database"""
        try:
            cursor = self.conn.cursor()
            
            # Check in regular games
            cursor.execute('''
                SELECT message_id, file_name FROM channel_games 
                WHERE file_name = ? AND file_size = ? AND file_type = ?
            ''', (file_name, file_size, file_type))
            regular_duplicate = cursor.fetchone()
            
            # Check in premium games
            cursor.execute('''
                SELECT id, file_name FROM premium_games 
                WHERE file_name = ? AND file_size = ? AND file_type = ?
            ''', (file_name, file_size, file_type))
            premium_duplicate = cursor.fetchone()
            
            return regular_duplicate, premium_duplicate
            
        except Exception as e:
            print(f"❌ Error checking duplicates: {e}")
            return None, None
    
    def handle_remove_game_search(self, message):
        """Handle game removal search"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            search_term = message.get('text', '').strip()
            
            if not search_term:
                return False
            
            if not self.is_admin(user_id):
                self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
                return True
            
            print(f"🔍 Admin {user_id} searching for removal: '{search_term}'")
            
            # Search in both regular and premium games
            cursor = self.conn.cursor()
            
            # Search regular games
            cursor.execute('''
                SELECT message_id, file_name, file_type, file_size, upload_date, category, 
                       file_id, bot_message_id, is_uploaded, is_forwarded
                FROM channel_games 
                WHERE LOWER(file_name) LIKE ? OR file_name LIKE ?
                ORDER BY file_name
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            regular_results = cursor.fetchall()
            
            # Search premium games
            cursor.execute('''
                SELECT id, file_name, file_type, file_size, stars_price, description, 
                       upload_date, file_id, bot_message_id, is_uploaded
                FROM premium_games 
                WHERE LOWER(file_name) LIKE ? OR file_name LIKE ?
                ORDER BY file_name
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            premium_results = cursor.fetchall()
            
            all_results = []
            
            # Format regular games results
            for game in regular_results:
                (message_id, file_name, file_type, file_size, upload_date, 
                 category, file_id, bot_message_id, is_uploaded, is_forwarded) = game
                
                all_results.append({
                    'type': 'regular',
                    'id': message_id,
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
            
            # Format premium games results
            for game in premium_results:
                (game_id, file_name, file_type, file_size, stars_price, description,
                 upload_date, file_id, bot_message_id, is_uploaded) = game
                
                all_results.append({
                    'type': 'premium',
                    'id': game_id,
                    'file_name': file_name,
                    'file_type': file_type,
                    'file_size': file_size,
                    'stars_price': stars_price,
                    'description': description,
                    'upload_date': upload_date,
                    'file_id': file_id,
                    'bot_message_id': bot_message_id,
                    'is_uploaded': is_uploaded
                })
            
            if not all_results:
                self.robust_send_message(chat_id, 
                    f"❌ No games found for: <code>{search_term}</code>\n\n"
                    "💡 Try different keywords or check the spelling.",
                    self.create_remove_game_buttons()
                )
                return True
            
            # Create removal results message
            results_text = f"""🔍 <b>Removal Search Results</b>

Search: <code>{search_term}</code>
Found: {len(all_results)} games

⚠️ <b>Click "Remove" to delete any game:</b>\n\n"""
            
            # Create keyboard with remove buttons
            keyboard = []
            for i, game in enumerate(all_results, 1):
                game_type = "🆓 Regular" if game['type'] == 'regular' else "💰 Premium"
                size = self.format_file_size(game['file_size'])
                
                results_text += f"{i}. <b>{game['file_name']}</b>\n"
                results_text += f"   📦 {game['file_type']} | 📏 {size} | {game_type}\n"
                
                if game['type'] == 'premium':
                    results_text += f"   ⭐ {game['stars_price']} Stars\n"
                
                results_text += f"   🆔 {game['id']} | 📅 {game['upload_date'][:10]}\n\n"
                
                # Add remove button for this game
                keyboard.append([f"Remove: {game['file_name']}"])
            
            # Add navigation buttons
            keyboard.append(["🔍 New Search", "🔙 Back to Remove Menu"])
            
            reply_markup = {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": False,
                "selective": False
            }
            
            self.robust_send_message(chat_id, results_text, reply_markup)
            return True
            
        except Exception as e:
            print(f"❌ Remove game search error: {e}")
            self.robust_send_message(chat_id, "❌ Error searching for games. Please try again.", self.create_remove_game_buttons())
            return False
    
    def handle_stars_price(self, user_id, chat_id, price_text):
        """Handle stars price input for premium games"""
        if user_id not in self.upload_sessions:
            return False
        
        try:
            stars_price = int(price_text.strip())
            if stars_price <= 0:
                self.robust_send_message(chat_id, "❌ Please enter a positive number of Stars.")
                return True
            
            if stars_price > 10000:  # Reasonable limit
                self.robust_send_message(chat_id, "❌ Price too high. Maximum is 10,000 Stars.")
                return True
            
            self.upload_sessions[user_id]['stars_price'] = stars_price
            self.upload_sessions[user_id]['stage'] = 'waiting_description'
            
            self.robust_send_message(chat_id,
                f"⭐ <b>Price Set: {stars_price} Stars</b>\n\n"
                "Now, please provide a description for this premium game:\n\n"
                "💡 <i>Describe the game features, requirements, or any important notes</i>\n"
                "📝 <i>You can skip this by sending 'skip'</i>"
            )
            return True
            
        except ValueError:
            self.robust_send_message(chat_id, "❌ Please enter a valid number for the Stars price.")
            return True
    
    def handle_premium_description(self, user_id, chat_id, description):
        """Handle premium game description"""
        if user_id not in self.upload_sessions:
            return False
        
        if description.lower() == 'skip':
            description = ""
        
        self.upload_sessions[user_id]['description'] = description
        self.upload_sessions[user_id]['stage'] = 'waiting_file'
        
        self.robust_send_message(chat_id,
            f"✅ <b>Premium Game Setup Complete!</b>\n\n"
            f"⭐ Price: {self.upload_sessions[user_id]['stars_price']} Stars\n"
            f"📝 Description: {description if description else 'No description'}\n\n"
            "📁 <b>Now please upload the game file</b>\n"
            "Supported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP"
        )
        return True
    
    def handle_game_request(self, user_id, chat_id, game_name):
        """Handle game name input and ask for platform"""
        try:
            # Store game name and ask for platform
            self.request_sessions[user_id] = {
                'stage': 'waiting_platform',
                'game_name': game_name
            }
            
            self.robust_send_message(chat_id,
                f"🎮 <b>Game Request</b>\n\n"
                f"Game: <b>{game_name}</b>\n\n"
                "Now, please specify the platform:\n\n"
                "💡 <i>Examples: PSP, Android, PS1, PS2, Nintendo Switch, etc.</i>"
            )
            return True
        except Exception as e:
            print(f"❌ Game request handling error: {e}")
            return False
    
    def complete_game_request(self, user_id, chat_id, platform):
        """Complete game request submission"""
        try:
            if user_id not in self.request_sessions:
                return False
            
            session = self.request_sessions[user_id]
            if session['stage'] != 'waiting_platform':
                return False
            
            game_name = session['game_name']
            
            # Submit the request
            request_id = self.game_request_system.submit_game_request(user_id, game_name, platform)
            
            if request_id:
                # Clean up session
                del self.request_sessions[user_id]
                
                # Send confirmation
                confirm_text = f"""✅ <b>Game Request Submitted!</b>

🎮 Game: <b>{game_name}</b>
📱 Platform: <b>{platform}</b>
👤 Requested by: {self.get_user_info(user_id)['first_name']}
🆔 Request ID: {request_id}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for your request! We'll review it and notify you if we add the game to our collection.

📊 You can check your request status in 'My Requests'."""
                
                self.robust_send_message(chat_id, confirm_text, self.create_main_menu_buttons())
                return True
            else:
                self.robust_send_message(chat_id, "❌ Sorry, there was an error submitting your request. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Game request completion error: {e}")
            return False
    
    def start_request_reply(self, user_id, chat_id, request_id):
        """Start replying to a game request"""
        if not self.is_admin(user_id):
            return False
        
        request = self.game_request_system.get_request_by_id(request_id)
        if not request:
            self.robust_send_message(chat_id, "❌ Request not found.")
            return False
        
        self.reply_sessions[user_id] = {
            'stage': 'waiting_reply',
            'request_id': request_id,
            'type': 'text',
            'chat_id': chat_id
        }
        
        reply_text = f"""📝 <b>Reply to Game Request</b>

🎮 Game: <b>{request['game_name']}</b>
👤 User: {request['user_name']} (ID: {request['user_id']})
📱 Platform: {request['platform']}
🆔 Request ID: {request_id}

💬 <b>Please type your reply message:</b>

💡 You can include:
• Game availability status
• Download links
• Alternative suggestions
• Any other information

📎 You can also attach a photo with your reply."""
        
        keyboard = [
            ["📎 Add Photo to Reply", "❌ Cancel Reply"]
        ]
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": False
        }
        
        self.robust_send_message(chat_id, reply_text, reply_markup)
        return True
    
    def handle_request_reply(self, user_id, chat_id, reply_text):
        """Handle text reply to game request"""
        if user_id not in self.reply_sessions:
            return False
        
        session = self.reply_sessions[user_id]
        request_id = session['request_id']
        
        # Add the reply to database
        success = self.game_request_system.add_request_reply(
            request_id, user_id, reply_text
        )
        
        if success:
            # Notify the user about the reply
            request = self.game_request_system.get_request_by_id(request_id)
            if request:
                user_notification = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request['game_name']}</b>
👤 Admin: {self.get_user_info(user_id)['first_name']}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 <b>Message:</b>
{reply_text}

Thank you for using our service! 🙏"""
                
                self.robust_send_message(request['user_id'], user_notification)
            
            # Clean up session
            del self.reply_sessions[user_id]
            
            self.robust_send_message(chat_id, f"✅ Reply sent to user successfully!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send reply.")
            return False
    
    def handle_broadcast_message(self, user_id, chat_id, text):
        """Handle broadcast message input"""
        if user_id not in self.broadcast_sessions:
            return False
            
        session = self.broadcast_sessions[user_id]
        
        if session['stage'] == 'waiting_message_or_photo':
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
            
            keyboard = [
                ["✅ Send Broadcast", "✏️ Edit Broadcast"],
                ["❌ Cancel Broadcast"]
            ]
            
            reply_markup = {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": False,
                "selective": False
            }
            
            self.robust_send_message(chat_id, preview_text, reply_markup)
            return True
            
        return False
    
    def handle_broadcast_photo(self, user_id, chat_id, photo_file_id, caption):
        """Handle broadcast photo input"""
        if user_id not in self.broadcast_sessions:
            return False
            
        session = self.broadcast_sessions[user_id]
        
        if session['stage'] == 'waiting_message_or_photo':
            # Store the photo and caption, show preview
            session['stage'] = 'preview'
            session['photo'] = photo_file_id
            session['message'] = caption or ""
            
            preview_text = f"""📋 <b>Broadcast Preview</b>

📷 <b>Photo Broadcast</b>
💬 Caption: {caption if caption else 'No caption'}

📊 This broadcast will be sent to all verified users.

⚠️ <b>Please review carefully before sending!</b>"""
            
            keyboard = [
                ["✅ Send Broadcast", "✏️ Edit Broadcast"],
                ["❌ Cancel Broadcast"]
            ]
            
            reply_markup = {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": False,
                "selective": False
            }
            
            # Send the photo preview
            photo_url = self.base_url + "sendPhoto"
            photo_data = {
                "chat_id": chat_id,
                "photo": photo_file_id,
                "caption": preview_text,
                "reply_markup": json.dumps(reply_markup),
                "parse_mode": "HTML"
            }
            
            try:
                requests.post(photo_url, data=photo_data, timeout=30)
                return True
            except Exception as e:
                print(f"❌ Error sending photo preview: {e}")
                return False
            
        return False
    
    def send_broadcast_to_all(self, user_id, chat_id):
        """Send broadcast to all users"""
        if user_id not in self.broadcast_sessions:
            return False
            
        session = self.broadcast_sessions[user_id]
        
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
        
        # Prepare broadcast content
        has_photo = session['photo'] is not None
        message_text = f"📢 <b>Announcement from Admin</b>\n\n{session['message']}\n\n────────────────────\n<i>This is an automated broadcast message</i>"
        
        # Send to users with rate limiting
        for i, (user_id_target,) in enumerate(users):
            try:
                if has_photo:
                    # Send photo broadcast
                    photo_url = self.base_url + "sendPhoto"
                    photo_data = {
                        "chat_id": user_id_target,
                        "photo": session['photo'],
                        "caption": message_text,
                        "parse_mode": "HTML"
                    }
                    response = requests.post(photo_url, data=photo_data, timeout=30)
                else:
                    # Send text broadcast
                    response = requests.post(self.base_url + "sendMessage", data={
                        "chat_id": user_id_target,
                        "text": message_text,
                        "parse_mode": "HTML"
                    }, timeout=30)
                
                if response.json().get('ok'):
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
        
        broadcast_type = "Photo" if has_photo else "Text"
        stats_text = f"""✅ <b>Broadcast Completed!</b>

📊 Final Statistics:
• 📤 Total users: {total_users}
• ✅ Successful: {success_count}
• ❌ Failed: {failed_count}
• 📈 Success rate: {success_rate:.1f}%
• ⏱️ Total time: {elapsed_total:.1f}s
• 🚀 Speed: {total_users/elapsed_total:.1f} users/second
• 📝 Type: {broadcast_type} Broadcast

📝 Message sent to {success_count} users successfully."""

        # Store broadcast statistics
        broadcast_id = int(time.time())
        self.broadcast_stats[broadcast_id] = {
            'admin_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'total_users': total_users,
            'success_count': success_count,
            'failed_count': failed_count,
            'type': 'photo' if has_photo else 'text',
            'message_preview': session['message'][:100] + "..." if len(session['message']) > 100 else session['message']
        }
        
        self.robust_send_message(chat_id, stats_text, self.create_admin_buttons())
        
        # Clean up session
        del self.broadcast_sessions[user_id]
        
        return True
    
    def handle_photo_reply(self, user_id, chat_id, photo_file_id, caption):
        """Handle photo reply to game request"""
        if user_id not in self.reply_sessions:
            return False
        
        session = self.reply_sessions[user_id]
        request_id = session['request_id']
        
        # Add the reply to database with photo
        success = self.game_request_system.add_request_reply(
            request_id, user_id, caption or "Photo attached", photo_file_id
        )
        
        if success:
            # Notify the user about the reply with photo
            request = self.game_request_system.get_request_by_id(request_id)
            if request:
                # Send photo with caption to user
                photo_url = self.base_url + "sendPhoto"
                photo_data = {
                    "chat_id": request['user_id'],
                    "photo": photo_file_id,
                    "caption": f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request['game_name']}</b>
👤 Admin: {self.get_user_info(user_id)['first_name']}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 <b>Message:</b>
{caption if caption else 'Photo attached'}""",
                    "parse_mode": "HTML"
                }
                
                try:
                    requests.post(photo_url, data=photo_data, timeout=30)
                except Exception as e:
                    print(f"❌ Failed to send photo reply: {e}")
            
            # Clean up session
            del self.reply_sessions[user_id]
            
            self.robust_send_message(chat_id, "✅ Photo reply sent to user successfully!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send photo reply.")
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
    
    # ==================== ENHANCED RUN METHOD ====================
    
    def run(self):
        """Enhanced main bot loop with comprehensive crash protection"""
        if not self.initialize_with_persistence():
            print("❌ Bot cannot start. Initialization failed.")
            return
    
        print("🤖 Bot is running with enhanced protection...")
        print("📊 Monitoring: Health checks every 4 minutes")
        print("🛡️  Protection: Auto-restart on failures")
        print("💾 Persistence: Data preserved across restarts")
        
        offset = 0
        last_successful_update = time.time()
        update_failures = 0
        max_update_failures = 10
        
        while True:
            try:
                updates = self.get_updates(offset)
                
                if updates:
                    last_successful_update = time.time()
                    update_failures = 0
                    
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        try:
                            if 'message' in update:
                                self.process_message(update['message'])
                            # Note: We no longer handle callback queries since we're using regular keyboards
                        except Exception as e:
                            print(f"❌ Update processing error: {e}")
                            # Continue processing other updates
                            continue
                else:
                    update_failures += 1
                    print(f"ℹ️ No updates received (Failure #{update_failures})")
                
                # Check if we're having connection issues
                current_time = time.time()
                time_since_last_update = current_time - last_successful_update
                
                if time_since_last_update > 300:  # 5 minutes without updates
                    print(f"🚨 No updates for {time_since_last_update:.0f} seconds, testing connection...")
                    if not self.test_bot_connection():
                        print("❌ Bot connection lost, triggering restart...")
                        raise ConnectionError("Bot connection lost")
                
                if update_failures >= max_update_failures:
                    print("🚨 Too many update failures, triggering restart...")
                    raise ConnectionError("Too many update failures")
                
                # Normal delay
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                if self.keep_alive:
                    self.keep_alive.stop()
                break
                
            except ConnectionError as e:
                print(f"🔌 Connection issue: {e}")
                self.handle_error(e, "connection_lost")
                # This will trigger a restart
                raise
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Main loop error: {error_msg}")
                
                # Don't restart for minor errors, only for critical ones
                if any(keyword in error_msg.lower() for keyword in ['token', 'connection', 'network', 'timeout']):
                    self.handle_error(e, "critical_error")
                    raise  # This will trigger restart
                else:
                    self.handle_error(e, "non_critical_error")
                    # Continue for non-critical errors
                    time.sleep(5)

# ==================== ENVIRONMENT VARIABLES CONFIG ====================

# Try to load from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("ℹ️ python-dotenv not installed, using system environment variables")

# Get tokens from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# GitHub Backup Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO_OWNER = os.environ.get('GITHUB_REPO_OWNER')
GITHUB_REPO_NAME = os.environ.get('GITHUB_REPO_NAME')

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    print("💡 Please set BOT_TOKEN in:")
    print("   - Render.com environment variables")
    print("   - OR create a .env file with BOT_TOKEN=your_token")
    # Don't exit - let the health server continue running
    print("💡 Health server will continue running for monitoring")

if GITHUB_TOKEN and GITHUB_REPO_OWNER and GITHUB_REPO_NAME:
    print("✅ GitHub Backup: Configuration detected")
else:
    print("ℹ️ GitHub Backup: Not configured (optional)")

# Test the token before starting
def test_bot_connection(token):
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
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

if __name__ == "__main__":
    print("🚀 Starting Enhanced Telegram Bot with GitHub Backup System...")
    
    # Start health check server first (always)
    start_health_check()
    
    # Wait a moment for health server to start
    time.sleep(2)
    
    if BOT_TOKEN:
        print("🔍 Testing bot token...")
        
        if test_bot_connection(BOT_TOKEN):
            print("✅ Bot token is valid")
            
            # Main loop with enhanced restart capability
            restart_count = 0
            max_restarts = 50  # Increased limit
            restart_delay = 10
            
            while restart_count < max_restarts:
                try:
                    restart_count += 1
                    print(f"🔄 Bot start attempt #{restart_count}")
                    
                    bot = CrossPlatformBot(BOT_TOKEN)
                    bot.run()
                    
                    # If we get here, the bot stopped gracefully
                    print("🤖 Bot stopped gracefully")
                    break
                    
                except Exception as e:
                    print(f"💥 Bot crash (#{restart_count}): {e}")
                    
                    if restart_count < max_restarts:
                        print(f"🔄 Restarting in {restart_delay} seconds...")
                        time.sleep(restart_delay)
                        
                        # Increase delay for consecutive restarts (exponential backoff)
                        restart_delay = min(restart_delay * 1.5, 300)  # Max 5 minutes
                    else:
                        print(f"❌ Maximum restarts ({max_restarts}) reached.")
                        break
            else:
                print(f"🚨 Maximum restarts reached. Bot cannot recover automatically.")
        else:
            print("❌ Invalid bot token - cannot start")
    else:
        print("❌ No BOT_TOKEN provided")
    
    print("🔴 Bot service ended")
