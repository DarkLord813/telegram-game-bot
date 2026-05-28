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
import html
from flask import Flask, jsonify, request as flask_request
from threading import Thread
import traceback
import base64
from io import BytesIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load .env file FIRST so all os.environ.get() calls below see the values
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; fall through to system env vars

# ── Shared HTTP session with connection pooling ────────────────────────────────
# Re-using TCP connections saves ~200-400 ms per Telegram API call.
_tg_session = requests.Session()
_tg_session.mount('https://', HTTPAdapter(
    pool_connections=4,
    pool_maxsize=16,
    max_retries=Retry(total=2, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
))
# ──────────────────────────────────────────────────────────────────────────────

# ==================== CENTRAL ENVIRONMENT VARIABLE CONFIG ====================
# All runtime config lives here. Set these in Choreo / Render / .env
# -----------------------------------------------------------------------
BOT_TOKEN           = os.environ.get('BOT_TOKEN', '')
BOT_USERNAME        = os.environ.get('BOT_USERNAME', 'GAMERDROIDV1BOT')
BOT_SERVICE_NAME    = os.environ.get('BOT_SERVICE_NAME', 'GAMERDROID™ Bot')
REQUIRED_CHANNEL    = os.environ.get('REQUIRED_CHANNEL', '@pspgamers5')
CHANNEL_LINK        = os.environ.get('CHANNEL_LINK', f"https://t.me/{os.environ.get('REQUIRED_CHANNEL', '@pspgamers5').lstrip('@')}")
_raw_admin_ids      = os.environ.get('ADMIN_IDS', '7475473197,7713987088')
ADMIN_IDS           = [int(x.strip()) for x in _raw_admin_ids.split(',') if x.strip().isdigit()]
REDEPLOY_TOKEN      = os.environ.get('REDEPLOY_TOKEN', 'default_token')
DB_NAME             = os.environ.get('DB_NAME', 'telegram_bot.db')
PORT                = int(os.environ.get('PORT', 8080))
PUBLIC_URL          = (
    os.environ.get('CHOREO_URL')
    or os.environ.get('RENDER_EXTERNAL_URL')
    or os.environ.get('PUBLIC_URL', '')
)
GITHUB_TOKEN        = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO_OWNER   = os.environ.get('GITHUB_REPO_OWNER', 'your-username')
GITHUB_REPO_NAME    = os.environ.get('GITHUB_REPO_NAME', 'your-repo')
GITHUB_BACKUP_BRANCH= os.environ.get('GITHUB_BACKUP_BRANCH', 'main')
GITHUB_BACKUP_PATH  = os.environ.get('GITHUB_BACKUP_PATH', 'backups/telegram_bot.db')
# ==================== END CONFIG ====================

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

# ==================== STARTUP INFO ====================
print("🔍 Startup: Python", sys.version.split()[0], "| Dir:", os.getcwd())
print(f"🔍 BOT_TOKEN: {'SET ✅' if BOT_TOKEN else 'MISSING ❌'}")
if BOT_TOKEN:
    print(f"🔍 Token starts with: {BOT_TOKEN[:10]}...")
else:
    print("❌ BOT_TOKEN is MISSING! Check environment variables.")

# ==================== FLASK APP — WEBHOOK + HEALTH (CHOREO-READY) ====================

app = Flask(__name__)
bot_instance = None  # Set after bot is created

@app.route('/health')
def health_check():
    """Health endpoint for Choreo / uptime monitoring"""
    try:
        bot_status = 'unknown'
        if bot_instance and hasattr(bot_instance, 'test_bot_connection'):
            bot_status = 'healthy' if bot_instance.test_bot_connection() else 'unhealthy'
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'service': BOT_SERVICE_NAME,
            'mode': 'webhook',
            'bot_status': bot_status
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint — receives all updates"""
    try:
        if not bot_instance:
            return jsonify({'ok': False, 'error': 'Bot not initialized'}), 200
        update = flask_request.get_json()
        if update:
            Thread(target=bot_instance.process_update, args=(update,), daemon=True).start()
        return jsonify({'ok': True}), 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'ok': False}), 200

@app.route('/redeploy', methods=['POST'])
def redeploy_endpoint():
    """Redeploy endpoint for admins"""
    try:
        auth_token = flask_request.headers.get('Authorization', '')
        payload = flask_request.get_json() or {}
        user_id = str(payload.get('user_id', ''))
        is_authorized = (
            auth_token == REDEPLOY_TOKEN
            or user_id in [str(i) for i in ADMIN_IDS]
        )
        if not is_authorized:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        print(f"🔄 Redeploy triggered by user {user_id}")
        def delayed_restart():
            time.sleep(5)
            os._exit(0)
        threading.Thread(target=delayed_restart, daemon=True).start()
        return jsonify({'status': 'success', 'message': 'Redeploy initiated', 'timestamp': datetime.now().isoformat()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        'service': BOT_SERVICE_NAME,
        'status': 'running',
        'mode': 'webhook',
        'endpoints': {'/health': 'GET', '/webhook': 'POST (Telegram)', '/redeploy': 'POST (Admin)'}
    })

def run_flask_server():
    """Run the Flask server (webhook + health)"""
    print(f"🌐 Starting Flask server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

def start_health_check():
    """Start Flask server in a background daemon thread"""
    def wrapper():
        while True:
            try:
                run_flask_server()
            except Exception as e:
                print(f"❌ Flask server crashed, restarting: {e}")
                time.sleep(10)
    t = Thread(target=wrapper, daemon=True)
    t.start()
    print(f"✅ Flask server (webhook + health) started on port {PORT}")

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
                    response = _tg_session.get(self.health_url, timeout=15)
                    
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
    def __init__(self, bot):
        self.bot = bot
        self.setup_tables()
        print("✅ Referral system initialized!")

    def setup_tables(self):
        """Add referral/token columns to users table if they don't exist yet"""
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
            if 'pending_referrer_id' not in cols:
                # Stores the referrer until the user finishes full verification
                cursor.execute('ALTER TABLE users ADD COLUMN pending_referrer_id INTEGER DEFAULT 0')
            self.bot.conn.commit()
        except Exception as e:
            print(f"Referral table setup error: {e}")

    def get_tokens(self, user_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute('SELECT game_tokens FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception:
            return 0

    def add_tokens(self, user_id, amount):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute(
                'UPDATE users SET game_tokens = game_tokens + ? WHERE user_id = ?',
                (amount, user_id)
            )
            self.bot.conn.commit()
            return True
        except Exception:
            return False

    def deduct_tokens(self, user_id, amount):
        """Atomically deduct tokens. Returns False if user has insufficient balance."""
        try:
            cursor = self.bot.conn.cursor()
            # Atomic: only update if current balance >= amount
            cursor.execute(
                '''UPDATE users SET game_tokens = game_tokens - ?
                   WHERE user_id = ? AND game_tokens >= ?''',
                (amount, user_id, amount)
            )
            self.bot.conn.commit()
            if cursor.rowcount == 0:
                return False  # insufficient tokens or user not found
            return True
        except Exception:
            return False

    def store_pending_referral(self, referrer_id, referred_id):
        """
        Store referrer when new user clicks referral link.
        Uses referred_by=referrer_id as the pending marker (token credited after verification).
        Safe to call multiple times — only writes once, never overwrites an existing referral.
        """
        try:
            if referrer_id == referred_id:
                return False
            cursor = self.bot.conn.cursor()
            # Only store if user hasn't been referred yet
            cursor.execute(
                'SELECT referred_by FROM users WHERE user_id = ?',
                (referred_id,)
            )
            row = cursor.fetchone()
            if row is None:
                # User doesn't exist yet — insert with referral
                cursor.execute(
                    'INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)',
                    (referred_id, referrer_id)
                )
            elif not row[0]:
                # User exists but no referral stored yet
                cursor.execute(
                    'UPDATE users SET referred_by = ? WHERE user_id = ? AND (referred_by IS NULL OR referred_by = 0)',
                    (referrer_id, referred_id)
                )
            else:
                return False  # already referred
            self.bot.conn.commit()
            print(f"📌 Referral stored: {referrer_id} → {referred_id}")
            return True
        except Exception as e:
            print(f"store_pending_referral error: {e}")
            return False

    def complete_referral(self, referred_id):
        """
        Called when referred_id finishes full verification.
        Awards 1 token to the referrer exactly once.
        Uses referred_by != 0 as the pending marker;
        sets pending_referrer_id = -1 to mark as already credited.
        """
        try:
            cursor = self.bot.conn.cursor()

            # Check pending_referrer_id column exists (migration safety)
            try:
                cursor.execute(
                    'SELECT referred_by, pending_referrer_id FROM users WHERE user_id = ?',
                    (referred_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                referrer_id, already_credited = row[0], row[1]
                # pending_referrer_id = -1 means already credited
                if already_credited == -1:
                    return None
            except Exception:
                # pending_referrer_id column may not exist on old DBs
                cursor.execute('SELECT referred_by FROM users WHERE user_id = ?', (referred_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                referrer_id = row[0]
                already_credited = 0

            if not referrer_id or referrer_id == 0:
                return None  # no referrer

            # Award 1 token to referrer
            cursor.execute(
                '''UPDATE users
                   SET game_tokens = game_tokens + 1,
                       total_referrals = total_referrals + 1
                   WHERE user_id = ?''',
                (referrer_id,)
            )
            # Mark as credited (pending_referrer_id = -1)
            try:
                cursor.execute(
                    'UPDATE users SET pending_referrer_id = -1 WHERE user_id = ?',
                    (referred_id,)
                )
            except Exception:
                pass
            self.bot.conn.commit()

            # Notify referrer
            referrer_tokens = self.get_tokens(referrer_id)
            self.bot.robust_send_message(
                referrer_id,
                f"🎉 <b>Referral Completed!</b>\n\n"
                f"Your referral just finished verification!\n"
                f"You earned <b>1 Game Token</b> 💎\n\n"
                f"💰 Total Tokens: <b>{referrer_tokens}</b>"
            )
            print(f"✅ Referral credited: {referrer_id} earned 1 token for referring {referred_id}")
            return referrer_id
        except Exception as e:
            print(f"complete_referral error: {e}")
            return None

    def register_referral(self, referrer_id, referred_id):
        """Legacy shim — kept for any existing call sites. Routes to store_pending_referral."""
        return self.store_pending_referral(referrer_id, referred_id)

    def get_referral_link(self, user_id):
        return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    def get_stats(self, user_id):
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute(
                'SELECT game_tokens, total_referrals FROM users WHERE user_id = ?', (user_id,)
            )
            result = cursor.fetchone()
            if result:
                return {'tokens': result[0] or 0, 'referrals': result[1] or 0}
            return {'tokens': 0, 'referrals': 0}
        except Exception:
            return {'tokens': 0, 'referrals': 0}

# ==================== ADMIN CODE SYSTEM ====================

class AdminCodeSystem:
    """
    Admin-generated 6-digit access codes.
    Each code has: expiry (days), max uses, per-user use limit (once per user).
    """

    PRESET_DURATIONS = {
        '1':    ('1 Day',    1),
        '7':    ('7 Days',   7),
        '14':   ('14 Days', 14),
        '30':   ('30 Days', 30),
        '90':   ('90 Days', 90),
        '365':  ('1 Year',  365),
        '0':    ('No Expiry', None),
    }

    def __init__(self, bot):
        self.bot = bot
        self._ensure_token_reward_column()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _generate_code(self):
        """Return a random 6-digit string not already in DB."""
        cursor = self.bot.conn.cursor()
        for _ in range(20):
            code = ''.join(secrets.choice('0123456789') for _ in range(6))
            cursor.execute('SELECT id FROM admin_codes WHERE code = ?', (code,))
            if not cursor.fetchone():
                return code
        raise RuntimeError("Could not generate unique code after 20 attempts")

    def _ensure_token_reward_column(self):
        """Migrate: add token_reward column if missing (safe for existing DBs)."""
        try:
            cursor = self.bot.conn.cursor()
            cursor.execute("PRAGMA table_info(admin_codes)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'token_reward' not in cols:
                cursor.execute('ALTER TABLE admin_codes ADD COLUMN token_reward INTEGER DEFAULT 5')
                self.bot.conn.commit()
        except Exception:
            pass

    def _is_valid(self, code_row, user_id):
        """Return (ok: bool, reason: str) for a given row from admin_codes."""
        cid        = code_row[0]
        max_uses   = code_row[4]
        used_count = code_row[5]
        is_active  = code_row[6]
        expires_at = code_row[3]

        if not is_active:
            return False, "This code has been deactivated."
        if expires_at and not expires_at.startswith('9999'):
            try:
                if datetime.now() > datetime.fromisoformat(expires_at):
                    return False, "This code has expired."
            except (ValueError, TypeError):
                pass
        if max_uses > 0 and used_count >= max_uses:
            return False, "This code has reached its maximum number of uses."
        cursor = self.bot.conn.cursor()
        cursor.execute(
            'SELECT id FROM admin_code_uses WHERE code_id = ? AND user_id = ?',
            (cid, user_id)
        )
        if cursor.fetchone():
            return False, "You have already used this code."
        return True, "ok"

    # ── public API ─────────────────────────────────────────────────────────────

    def create_code(self, admin_id, days, max_uses=100, description='', token_reward=5):
        """
        Create a new code.
        days=None means no expiry. max_uses=0 means unlimited.
        token_reward = tokens awarded to user on redemption.
        Returns the code string.
        """
        code = self._generate_code()
        if days is None:
            expires_at = datetime(9999, 12, 31)
        else:
            expires_at = datetime.now() + timedelta(days=days)
        cursor = self.bot.conn.cursor()
        cursor.execute(
            '''INSERT INTO admin_codes
               (code, created_by, expires_at, max_uses, token_reward, description)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (code, admin_id, expires_at.isoformat(), max_uses, token_reward, description)
        )
        self.bot.conn.commit()
        return code

    def redeem(self, code_str, user_id):
        """
        Try to redeem a code for user_id.
        Returns (success: bool, message: str, tokens_awarded: int).
        Works for ALL users including admins.
        """
        cursor = self.bot.conn.cursor()
        cursor.execute(
            '''SELECT id, code, created_by, expires_at, max_uses, used_count, is_active
               FROM admin_codes WHERE code = ?''',
            (code_str,)
        )
        row = cursor.fetchone()
        if not row:
            return False, "❌ Invalid or redeemed code.", 0

        ok, reason = self._is_valid(row, user_id)
        if not ok:
            return False, f"❌ {reason}", 0

        code_id = row[0]

        # Fetch token_reward (may not exist in old DBs — default 5)
        try:
            cursor.execute('SELECT token_reward FROM admin_codes WHERE id = ?', (code_id,))
            tr = cursor.fetchone()
            token_reward = tr[0] if tr and tr[0] is not None else 5
        except Exception:
            token_reward = 5

        # Mark use
        cursor.execute(
            'INSERT INTO admin_code_uses (code_id, user_id) VALUES (?, ?)',
            (code_id, user_id)
        )
        cursor.execute(
            'UPDATE admin_codes SET used_count = used_count + 1 WHERE id = ?',
            (code_id,)
        )
        self.bot.conn.commit()

        # Award tokens
        self.bot.referral.add_tokens(user_id, token_reward)

        return True, f"You received <b>{token_reward} Game Token(s)</b>! 🎉", token_reward

    def list_codes(self, admin_id):
        """Return all codes created by this admin, active ones first."""
        cursor = self.bot.conn.cursor()
        cursor.execute(
            '''SELECT code, expires_at, max_uses, used_count, is_active, description, token_reward
               FROM admin_codes
               WHERE created_by = ?
               ORDER BY is_active DESC, created_at DESC
               LIMIT 20''',
            (admin_id,)
        )
        return cursor.fetchall()

    def deactivate_code(self, admin_id, code_str):
        cursor = self.bot.conn.cursor()
        cursor.execute(
            'UPDATE admin_codes SET is_active = 0 WHERE code = ? AND created_by = ?',
            (code_str, admin_id)
        )
        self.bot.conn.commit()
        return cursor.rowcount > 0

    def get_code_stats(self, code_str):
        """Return a dict of stats for a given code."""
        cursor = self.bot.conn.cursor()
        cursor.execute(
            '''SELECT id, code, expires_at, max_uses, used_count, is_active, description
               FROM admin_codes WHERE code = ?''',
            (code_str,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        cursor.execute(
            'SELECT COUNT(*) FROM admin_code_uses WHERE code_id = ?',
            (row[0],)
        )
        unique_users = cursor.fetchone()[0]
        return {
            'code': row[1], 'expires_at': row[2], 'max_uses': row[3],
            'used_count': row[4], 'is_active': bool(row[5]),
            'description': row[6], 'unique_users': unique_users
        }

# ==================== GITHUB BACKUP SYSTEM ====================

class GitHubBackupSystem:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.setup_github_config()
        print("✅ GitHub Backup system initialized!")

    def setup_github_config(self):
        """Use the global config constants — no duplicate env reads"""
        self.github_token  = GITHUB_TOKEN
        self.repo_owner    = GITHUB_REPO_OWNER
        self.repo_name     = GITHUB_REPO_NAME
        self.backup_branch = GITHUB_BACKUP_BRANCH
        self.backup_path   = GITHUB_BACKUP_PATH
        self.is_enabled    = bool(self.github_token
                                  and self.repo_owner not in ('', 'your-username')
                                  and self.repo_name  not in ('', 'your-repo'))
        if self.is_enabled:
            print(f"✅ GitHub Backup: Enabled → {self.repo_owner}/{self.repo_name} @ {self.backup_path}")
        else:
            print("⚠️ GitHub Backup: Disabled – set GITHUB_TOKEN / GITHUB_REPO_OWNER / GITHUB_REPO_NAME")

    @property
    def _headers(self):
        return {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    @property
    def _api_url(self):
        return f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.backup_path}"

    def get_file_sha(self):
        """Return the blob SHA of the current backup file, or None if it doesn't exist yet."""
        try:
            r = _tg_session.get(
                self._api_url,
                headers=self._headers,
                params={'ref': self.backup_branch},
                timeout=15
            )
            if r.status_code == 200:
                return r.json().get('sha')
            return None
        except Exception:
            return None

    def create_db_backup(self):
        """Create a consistent backup of the live DB using SQLite's native backup API."""
        try:
            db_path     = self.bot.get_db_path()
            backup_path = db_path + '.backup'
            # Use sqlite3.connect().backup() — safe even with WAL mode and concurrent writes
            dest_conn = sqlite3.connect(backup_path)
            self.bot.conn.backup(dest_conn, pages=0)   # pages=0 = copy entire DB at once
            dest_conn.close()
            print(f"✅ Consistent DB snapshot: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ DB snapshot error: {e}")
            return None

    def backup_database_to_github(self, commit_message="Auto backup: Database update"):
        """Push the current DB to GitHub (create or update the file)."""
        if not self.is_enabled:
            print("⚠️ GitHub backup disabled – skipping")
            return False
        try:
            print("🔄 Starting GitHub backup …")
            backup_file = self.create_db_backup()
            if not backup_file:
                return False

            with open(backup_file, 'rb') as f:
                db_b64 = base64.b64encode(f.read()).decode('utf-8')

            # Always fetch the current SHA so we can update (not create-duplicate)
            file_sha = self.get_file_sha()

            payload = {
                'message': commit_message,
                'content': db_b64,
                'branch':  self.backup_branch,
            }
            if file_sha:
                payload['sha'] = file_sha

            r = _tg_session.put(self._api_url, headers=self._headers, json=payload, timeout=60)

            try:
                os.remove(backup_file)
            except Exception:
                pass

            if r.status_code in (200, 201):
                commit_url = r.json().get('commit', {}).get('html_url', 'n/a')
                print(f"✅ DB backed up to GitHub → {commit_url}")
                return True
            else:
                print(f"❌ GitHub backup failed {r.status_code}: {r.text[:300]}")
                return False
        except Exception as e:
            print(f"❌ GitHub backup error: {e}")
            return False

    def restore_database_from_github(self):
        """Download the backup blob from GitHub and replace the local DB."""
        if not self.is_enabled:
            print("⚠️ GitHub restore disabled")
            return False
        try:
            print("🔄 Fetching backup from GitHub …")
            r = _tg_session.get(
                self._api_url,
                headers=self._headers,
                params={'ref': self.backup_branch},
                timeout=60
            )
            if r.status_code != 200:
                print(f"❌ Backup not found on GitHub ({r.status_code})")
                return False

            file_data   = r.json()
            encoding    = file_data.get('encoding', 'base64')
            raw_content = file_data.get('content', '')

            if encoding == 'base64':
                # GitHub may split lines with \n — strip before decoding
                db_content = base64.b64decode(raw_content.replace('\n', ''))
            else:
                print(f"❌ Unexpected encoding from GitHub: {encoding}")
                return False

            db_path = self.bot.get_db_path()
            # Write to a temp file first so we don't corrupt the live DB on partial write
            tmp_path = db_path + '.restore_tmp'
            with open(tmp_path, 'wb') as f:
                f.write(db_content)
            import shutil
            shutil.move(tmp_path, db_path)

            # Log commit metadata safely (the contents endpoint may or may not include it)
            last_modified = (
                file_data.get('commit', {}).get('commit', {}).get('author', {}).get('date')
                or r.headers.get('Last-Modified', 'unknown')
            )
            print(f"✅ DB restored from GitHub (last modified: {last_modified})")
            return True
        except Exception as e:
            print(f"❌ GitHub restore error: {e}")
            return False

    def get_backup_info(self):
        """Return metadata about the latest backup commit."""
        if not self.is_enabled:
            return {"enabled": False}
        try:
            # Use the commits API — more reliable for metadata than contents
            r = _tg_session.get(
                f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits",
                headers=self._headers,
                params={'path': self.backup_path, 'per_page': 1},
                timeout=15
            )
            if r.status_code == 200:
                commits = r.json()
                if commits:
                    c = commits[0]
                    return {
                        "enabled":     True,
                        "last_backup": c['commit']['author']['date'],
                        "message":     c['commit']['message'],
                        "url":         c['html_url'],
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
    
    def show_redeploy_menu(self, user_id, chat_id, message_id):
        """Show redeploy menu"""
        if not self.bot.is_admin(user_id):
            self.bot.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.bot.create_admin_buttons())
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
            
            self.bot.robust_send_message(chat_id, confirm_text)
            
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
            self.bot.robust_send_message(chat_id, f"❌ Redeploy failed: {str(e)}")
            return False
    
    def trigger_redeploy_webhook(self, user_id, redeploy_type):
        """Trigger redeploy via webhook"""
        try:
            redeploy_url = os.environ.get('REDEPLOY_WEBHOOK_URL')
            
            if not redeploy_url:
                print("ℹ️ No REDEPLOY_WEBHOOK_URL set, using internal restart")
                return False
            
            webhook_data = {
                'user_id': user_id,
                'redeploy_type': redeploy_type,
                'timestamp': datetime.now().isoformat(),
                'service': BOT_SERVICE_NAME
            }
            
            headers = {
                'Authorization': REDEPLOY_TOKEN,
                'Content-Type': 'application/json'
            }
            
            response = _tg_session.post(redeploy_url, json=webhook_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("✅ Redeploy webhook triggered successfully")
                return True
            else:
                print(f"❌ Redeploy webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def show_system_status(self, user_id, chat_id, message_id):
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
            except Exception:
                db_status = "Error"
                game_count = 0
                user_count = 0
            
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_usage = f"{memory.percent}%"
            except Exception:
                memory_usage = "N/A"
            
            uptime_seconds = time.time() - self.bot.last_restart
            uptime_str = self.bot.format_uptime(uptime_seconds)
            
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

            keyboard = {
                "inline_keyboard": [
                    [{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}],
                    [{"text": "🔄 Refresh Status", "callback_data": "system_status"}],
                    [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
                ]
            }
            
            self.bot.edit_message(chat_id, message_id, status_text, keyboard)
            
        except Exception as e:
            print(f"❌ System status error: {e}")
            self.bot.edit_message(chat_id, message_id, f"❌ Error getting system status: {str(e)}", self.bot.create_admin_buttons())
    
    def format_uptime(self, seconds):
        """Format uptime in human readable format"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        if days > 0:
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(remaining_seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(remaining_seconds)}s"
        else:
            return f"{int(remaining_seconds)}s"

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
                "prices": prices,
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }

            print(f"⭐ Creating Stars invoice for {stars_amount} stars (${usd_amount:.2f})")

            url = self.bot.base_url + "sendInvoice"
            response = _tg_session.post(url, json=invoice_data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO stars_transactions 
                    (user_id, user_name, stars_amount, usd_amount, description, transaction_id, payment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    self.bot.get_user_info(user_id).get('first_name', 'User'),
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

            # prices amounts for XTR (Stars) are in whole stars, not cents
            prices = [{"label": f"Premium Game: {game_name}", "amount": stars_amount}]

            invoice_data = {
                "chat_id": chat_id,
                "title": f"🎮 {game_name}",
                "description": f"Premium Game Purchase — {stars_amount} Stars",
                "payload": invoice_payload,
                "currency": "XTR",
                "prices": prices,
                # Boolean fields MUST be sent as real JSON booleans (not strings)
                "need_name": False,
                "need_phone_number": False,
                "need_email": False,
                "need_shipping_address": False,
                "is_flexible": False
            }

            print(f"⭐ Creating premium game invoice: {game_name} for {stars_amount} stars")

            url = self.bot.base_url + "sendInvoice"
            # Use json= so all values are properly JSON-encoded (booleans, nested objects)
            response = _tg_session.post(url, json=invoice_data, timeout=30)
            result = response.json()

            if result.get('ok'):
                cursor = self.bot.conn.cursor()
                cursor.execute('''
                    INSERT INTO premium_purchases
                    (user_id, game_id, stars_paid, transaction_id, status)
                    VALUES (?, ?, ?, ?, 'pending')
                ''', (user_id, game_id, stars_amount, invoice_payload))
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

💡 Use /reply_{request_id} to reply to this request."""

        for admin_id in self.bot.ADMIN_IDS:
            try:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📝 Reply to Request", "callback_data": f"reply_request_{request_id}"},
                            {"text": "✅ Mark Completed", "callback_data": f"complete_request_{request_id}"}
                        ]
                    ]
                }
                self.bot.robust_send_message(admin_id, notification_text, keyboard)
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
                 added_by, is_uploaded, is_forwarded, file_id, bot_message_id,
                 stars_price, tokens_price, description, is_premium)
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
                game_info['stars_price'],
                game_info.get('tokens_price') or game_info['stars_price'],
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
                       file_id, bot_message_id, is_uploaded, message_id, tokens_price
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
                    'message_id': result[9],
                    'tokens_price': result[10] if result[10] is not None else 10
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
        
        # Channel and admin config — from global env-var constants
        self.REQUIRED_CHANNEL = REQUIRED_CHANNEL
        self.CHANNEL_LINK = CHANNEL_LINK
        self.ADMIN_IDS = list(ADMIN_IDS)  # copy so mutations don't affect global
        
        # Mini-games state management
        self.guess_games = {}
        self.spin_games = {}
        
        # Broadcast system
        self.broadcast_sessions = {}
        self.broadcast_stats = {}
        
        # ==================== DATABASE MUST BE INITIALIZED FIRST ====================
        self.setup_database()
        self.verify_database_schema()
        # ==================== END DATABASE INIT ====================

        # Referral & token system (must come after DB setup)
        self.referral = ReferralSystem(self)

        # Admin code system
        self.admin_codes = AdminCodeSystem(self)

        # Stars, request, redeploy, and backup systems
        self.stars_system = TelegramStarsSystem(self)
        self.game_request_system = GameRequestSystem(self)
        self.premium_games_system = PremiumGamesSystem(self)
        self.redeploy_system = RedeploySystem(self)
        self.github_backup = GitHubBackupSystem(self)

        # Session management
        self.stars_sessions = {}
        self.request_sessions = {}
        self.upload_sessions = {}
        self.reply_sessions = {}
        self.search_mode = {}
        self.code_sessions = {}   # admin code creation flow
        
        # CRASH PROTECTION
        self.last_restart = time.time()
        self.error_count = 0
        self.max_errors = 25
        self.error_window = 300
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        # Keep-alive service
        self.keep_alive = None
        
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
        print("🛡️ Crash protection enabled")
        print("🔋 Enhanced keep-alive system ready")
        print("💾 Persistent data recovery enabled")
    
    def get_db_path(self):
        """Get fixed database path from DB_NAME env var"""
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
        return db_path
    
    def initialize_with_persistence(self):
        """Initialize bot with persistent data recovery including GitHub restore"""
        try:
            print("🔄 Initializing bot with persistence...")
            
            # Ensure database directory exists
            db_path = self.get_db_path()
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Restore from GitHub only if local DB doesn't exist or is empty
            if self.github_backup.is_enabled:
                db_path = self.get_db_path()
                local_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 4096
                if not local_exists:
                    print("🔍 No local DB found — attempting GitHub restore …")
                    if self.github_backup.restore_database_from_github():
                        print("✅ Database restored from GitHub")
                    else:
                        print("ℹ️ No GitHub backup found, starting fresh")
                else:
                    print("ℹ️ Local DB found — skipping GitHub restore")
            
            # Ensure database is properly set up
            self.setup_database()
            self.verify_database_schema()
            
            # Recover games cache
            self.update_games_cache()
            
            # Recover uploaded files
            self.recover_uploaded_files()
            
            # Recover sessions from database
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

    def recover_persistent_sessions(self):
        """Recover persistent sessions from database"""
        try:
            self.guess_games = {}
            self.spin_games = {}
            self.broadcast_sessions = {}
            self.stars_sessions = {}
            self.request_sessions = {}
            self.upload_sessions = {}
            self.reply_sessions = {}
            self.search_sessions = {}
            self.search_results = {}
            self.search_mode = {}
            self.code_sessions = {}
            
            print("✅ Sessions reset for fresh start")
        except Exception as e:
            print(f"❌ Session recovery error: {e}")

    def recover_uploaded_files(self):
        """Count uploaded files on startup — skip slow per-file getFile API verification."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
            bot_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM premium_games WHERE is_uploaded = 1')
            premium_count = cursor.fetchone()[0]
            print(f"✅ File recovery: {bot_count} regular + {premium_count} premium uploads in DB")
            return bot_count + premium_count
        except Exception as e:
            print(f"❌ File recovery error: {e}")
            return 0

    def verify_file_accessible(self, message_id, file_id, is_bot_file):
        """Verify if a file is still accessible"""
        try:
            url = self.base_url + "getFile"
            data = {"file_id": file_id}
            response = _tg_session.post(url, data=data, timeout=10)
            result = response.json()
            return result.get('ok', False)
        except Exception:
            return False

    def start_keep_alive(self):
        """Start the enhanced keep-alive service"""
        try:
            if PUBLIC_URL:
                health_url = f"{PUBLIC_URL.rstrip('/')}/health"
            else:
                health_url = f"http://localhost:{PORT}/health"
            
            self.keep_alive = EnhancedKeepAliveService(health_url)
            self.keep_alive.start()
            print(f"🔋 Enhanced keep-alive activated → {health_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to start keep-alive: {e}")
            return False

    # ==================== GITHUB BACKUP INTEGRATION ====================

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
        
        backup_thread = threading.Thread(target=async_backup, daemon=True)
        backup_thread.start()

    def show_backup_menu(self, user_id, chat_id, message_id):
        """Show backup management menu for admins"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
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

        keyboard = {
            "inline_keyboard": []
        }
        
        if backup_info.get('enabled'):
            keyboard["inline_keyboard"].extend([
                [{"text": "💾 Create Backup Now", "callback_data": "create_backup"}],
                [{"text": "🔄 Restore from Backup", "callback_data": "restore_backup"}],
                [{"text": "📊 Backup Info", "callback_data": "backup_info"}]
            ])
        
        keyboard["inline_keyboard"].append([{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}])
        
        self.edit_message(chat_id, message_id, status_text, keyboard)

    def handle_create_backup(self, user_id, chat_id, message_id):
        """Handle manual backup creation"""
        if not self.is_admin(user_id):
            return False
        
        self.edit_message(chat_id, message_id, "💾 Creating manual backup...", None)
        
        def backup_operation():
            success = self.github_backup.backup_database_to_github("Manual backup: Admin triggered")
            
            if success:
                result_text = "✅ <b>Backup Created Successfully!</b>\n\nYour database has been backed up to GitHub."
            else:
                result_text = "❌ <b>Backup Failed!</b>\n\nCheck the logs for more information."
            
            self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
        
        backup_thread = threading.Thread(target=backup_operation, daemon=True)
        backup_thread.start()
        
        return True

    def handle_restore_backup(self, user_id, chat_id, message_id):
        """Handle backup restoration with confirmation"""
        if not self.is_admin(user_id):
            return False
        
        backup_info = self.github_backup.get_backup_info()
        
        if not backup_info.get('enabled'):
            self.edit_message(chat_id, message_id, "❌ GitHub backup is not enabled.", self.create_admin_buttons())
            return False
        
        if backup_info.get('last_backup') == 'Never':
            self.edit_message(chat_id, message_id, "❌ No backup exists to restore.", self.create_admin_buttons())
            return False
        
        confirm_text = f"""⚠️ <b>Restore Database from Backup?</b>

This will replace your current database with the backup from GitHub.

📅 Backup Date: {backup_info.get('last_backup', 'Unknown')}
💬 Message: {backup_info.get('message', 'Unknown')}

❌ <b>This action cannot be undone!</b>
All current data will be replaced with the backup.

Are you sure you want to continue?"""
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Yes, Restore Backup", "callback_data": "confirm_restore_backup"},
                    {"text": "❌ Cancel", "callback_data": "backup_menu"}
                ]
            ]
        }
        
        self.edit_message(chat_id, message_id, confirm_text, keyboard)
        return True

    def handle_confirm_restore(self, user_id, chat_id, message_id):
        """Handle confirmed backup restoration"""
        if not self.is_admin(user_id):
            return False
        
        self.edit_message(chat_id, message_id, "🔄 Restoring database from GitHub backup...", None)
        
        def restore_operation():
            success = self.github_backup.restore_database_from_github()
            
            if success:
                # Close old connection and reconnect to the freshly-restored file
                try:
                    self.conn.close()
                except Exception:
                    pass
                self.setup_database()
                self.verify_database_schema()
                self.update_games_cache()
                
                result_text = """✅ <b>Database Restored Successfully!</b>

Your database has been restored from the GitHub backup.

The bot will now use the restored data."""
            else:
                result_text = "❌ <b>Restore Failed!</b>\n\nCheck the logs for more information."
            
            self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
        
        restore_thread = threading.Thread(target=restore_operation, daemon=True)
        restore_thread.start()
        
        return True

    # ==================== REDEPLOY SYSTEM INTEGRATION ====================
    
    def create_main_menu_buttons(self, user_id=None):
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
            ],
            [
                {"text": "🔑 Redeem Code", "callback_data": "redeem_code_info"}
            ]
        ]
        
        if self.is_admin(user_id):
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
                    {"text": "🔑 Code Manager", "callback_data": "code_manager"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }

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
    
    def create_games_buttons(self):
        stats = self.get_channel_stats()
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎮 Mini Games", "callback_data": "mini_games"},
                    {"text": f"📁 Game Files ({stats['total_games']})", "callback_data": "game_files"}
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
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }
        return keyboard
    
    def create_game_files_buttons(self):
        stats = self.get_channel_stats()

        psp_count = len(self.games_cache.get('cso', [])) + len(self.games_cache.get('pbp', []))
        android_count = (len(self.games_cache.get('apk', []))
                         + len(self.games_cache.get('xapk', []))
                         + len(self.games_cache.get('apks', [])))

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": f"📦 ZIP ({len(self.games_cache.get('zip', []))})",  "callback_data": "game_zip"},
                    {"text": f"🗜️ 7Z ({len(self.games_cache.get('7z', []))})",   "callback_data": "game_7z"}
                ],
                [
                    {"text": f"💿 ISO ({len(self.games_cache.get('iso', []))})",  "callback_data": "game_iso"},
                    {"text": f"🎮 PSP ({psp_count})",                             "callback_data": "game_psp"}
                ],
                [
                    {"text": f"📱 APK ({len(self.games_cache.get('apk', []))})",   "callback_data": "game_apk"},
                    {"text": f"📦 XAPK ({len(self.games_cache.get('xapk', []))})", "callback_data": "game_xapk"}
                ],
                [
                    {"text": f"🗂️ APKS ({len(self.games_cache.get('apks', []))})", "callback_data": "game_apks"},
                    {"text": f"📋 All ({stats['total_games']})",                   "callback_data": "game_all"}
                ],
                [
                    {"text": "💰 Premium Games", "callback_data": "premium_games"},
                    {"text": "🔍 Search Games",  "callback_data": "search_games"}
                ],
                [
                    {"text": "🔄 Rescan", "callback_data": "rescan_games"},
                    {"text": "🔙 Back",   "callback_data": "games"}
                ]
            ]
        }
        return keyboard
    
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
    
    def create_broadcast_panel_buttons(self):
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
    
    def create_search_buttons(self):
        return {
            "inline_keyboard": [
                [
                    {"text": "🔍 New Search", "callback_data": "search_games"},
                    {"text": "📁 Browse All", "callback_data": "game_files"}
                ],
                [
                    {"text": "💰 Premium Games", "callback_data": "premium_games"},
                    {"text": "📝 Request Game", "callback_data": "request_game"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }

    def handle_user_redeploy_request(self, user_id, chat_id, message_id):
        """Handle user redeploy requests"""
        try:
            user_info = self.get_user_info(user_id)
            user_name = user_info.get('first_name', 'Unknown')
            
            if self.is_admin(user_id):
                redeploy_text = f"""🔄 <b>Admin Redeploy Access</b>

👤 Admin: {user_name}
🆔 User ID: {user_id}

You have admin privileges and can redeploy the bot directly.

Choose redeploy type:"""
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"}],
                        [{"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}],
                        [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
                    ]
                }
                
                self.edit_message(chat_id, message_id, redeploy_text, keyboard)
                
            else:
                notification_text = f"""🔄 <b>User Redeploy Request</b>

👤 User: {user_name} (ID: {user_id})
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📝 Status: Requested redeploy

💡 <i>The user reports the bot may not be responding properly.</i>"""

                for admin_id in self.ADMIN_IDS:
                    try:
                        admin_keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "🔄 Soft Redeploy", "callback_data": "redeploy_soft"},
                                    {"text": "🚀 Force Redeploy", "callback_data": "redeploy_force"}
                                ],
                                [
                                    {"text": "📊 Check Status", "callback_data": "system_status"}
                                ]
                            ]
                        }
                        self.robust_send_message(admin_id, notification_text, admin_keyboard)
                    except Exception as e:
                        print(f"❌ Failed to notify admin {admin_id}: {e}")
                
                user_response = f"""🔄 <b>Redeploy Request Sent</b>

Thank you {user_name}! 

Your redeploy request has been sent to the admins. They will review the bot status and perform a redeploy if necessary.

⏰ Expected response time: 5-15 minutes

📊 <b>Current Bot Status:</b>
• 🤖 Bot: 🟢 Online
• 💾 Database: 🟢 Connected  
• 📡 Services: 🟢 Running

If the issue persists, please contact the admins directly."""

                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
                    ]
                }
                
                self.edit_message(chat_id, message_id, user_response, keyboard)
                
        except Exception as e:
            print(f"❌ User redeploy request error: {e}")
            self.edit_message(chat_id, message_id, "❌ Error processing redeploy request.", self.create_main_menu_buttons(user_id))

    # ==================== ENHANCED CALLBACK HANDLER ====================

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
            
            # Backup System Callbacks
            if data == "backup_menu":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.show_backup_menu(user_id, chat_id, message_id)
                return
                
            elif data == "create_backup":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.handle_create_backup(user_id, chat_id, message_id)
                return
                
            elif data == "restore_backup":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.handle_restore_backup(user_id, chat_id, message_id)
                return
                
            elif data == "confirm_restore_backup":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.handle_confirm_restore(user_id, chat_id, message_id)
                return
                
            elif data == "backup_info":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.show_backup_menu(user_id, chat_id, message_id)
                return

            # Redeploy System Callbacks
            elif data == "redeploy_panel":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.redeploy_system.show_redeploy_menu(user_id, chat_id, message_id)
                return
                
            elif data == "user_redeploy":
                self.handle_user_redeploy_request(user_id, chat_id, message_id)
                return
                
            elif data.startswith("redeploy_"):
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                
                redeploy_type = data.replace("redeploy_", "")
                if redeploy_type in ["soft", "force"]:
                    self.redeploy_system.initiate_redeploy(user_id, chat_id, redeploy_type)
                return
                
            elif data == "system_status":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.redeploy_system.show_system_status(user_id, chat_id, message_id)
                return

            # Game Removal System Callbacks
            elif data == "remove_games":
                self.show_remove_game_menu(user_id, chat_id, message_id)
                return
                
            elif data == "search_remove_game":
                self.start_remove_game_search(user_id, chat_id)
                return
                
            elif data.startswith("confirm_remove_"):
                parts = data.replace("confirm_remove_", "").split("_")
                if len(parts) >= 2:
                    game_type = parts[0]
                    game_id = parts[1]
                    self.show_remove_confirmation(user_id, chat_id, message_id, game_type, game_id)
                return

            elif data.startswith("remove_"):
                parts = data.replace("remove_", "").split("_")
                if len(parts) >= 2:
                    game_type = parts[0]
                    game_id = parts[1]
                    self.remove_game(user_id, chat_id, game_type, game_id, message_id)
                return

            elif data == "cancel_remove":
                self.show_remove_game_menu(user_id, chat_id, message_id)
                return

            elif data == "view_recent_uploads":
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
                    self.edit_message(chat_id, message_id, "❌ No recent uploads found.", self.create_admin_buttons())
                    return
                
                uploads_text = "📋 <b>Recent Admin Uploads</b>\n\n"
                uploads_text += "Click 'Remove' to delete any game:\n\n"
                
                keyboard_buttons = []
                for upload in recent_uploads:
                    msg_id, file_name, file_type, file_size, upload_date, is_uploaded = upload
                    size = self.format_file_size(file_size)
                    
                    uploads_text += f"📁 <b>{file_name}</b>\n"
                    uploads_text += f"📦 {file_type} | 📏 {size} | 📅 {upload_date[:10]}\n"
                    uploads_text += f"🆔 {msg_id}\n\n"
                    
                    keyboard_buttons.append([{
                        "text": f"🗑️ Remove {file_name[:20]}{'...' if len(file_name) > 20 else ''}",
                        "callback_data": f"confirm_remove_R_{msg_id}"
                    }])
                
                keyboard_buttons.append([{"text": "🔙 Back", "callback_data": "remove_games"}])
                keyboard = {"inline_keyboard": keyboard_buttons}
                
                self.edit_message(chat_id, message_id, uploads_text, keyboard)
                return

            # Premium games callbacks
            elif data == "premium_games":
                self.show_premium_games_menu(user_id, chat_id, message_id)
                return
                
            elif data.startswith("purchase_premium_"):
                game_id = int(data.replace("purchase_premium_", ""))
                self.purchase_premium_game(user_id, chat_id, game_id, message_id)
                return

            elif data.startswith("buy_tokens_"):
                game_id = int(data.replace("buy_tokens_", ""))
                game = self.premium_games_system.get_premium_game_by_id(game_id)
                if not game:
                    self.answer_callback_query(callback_query['id'], "❌ Game not found.", True)
                    return
                if self.premium_games_system.has_user_purchased_game(user_id, game_id):
                    self.answer_callback_query(callback_query['id'], "✅ You already own this game!", True)
                    self.send_premium_game_file(user_id, chat_id, game_id)
                    return
                tokens_price = game.get('tokens_price') or game['stars_price']
                if self.referral.deduct_tokens(user_id, tokens_price):
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO premium_purchases (user_id, game_id, stars_paid, transaction_id, status)
                        VALUES (?, ?, 0, ?, 'completed')
                    ''', (user_id, game_id, f'tokens_{int(time.time())}'))
                    self.conn.commit()
                    self.answer_callback_query(callback_query['id'], f"✅ Purchased with {tokens_price} tokens!", True)
                    self.send_premium_game_file(user_id, chat_id, game_id)
                else:
                    user_tokens = self.referral.get_tokens(user_id)
                    self.answer_callback_query(
                        callback_query['id'],
                        f"❌ Insufficient tokens! Need {tokens_price}, you have {user_tokens}.",
                        True
                    )
                return

            elif data.startswith("download_premium_"):
                game_id = int(data.replace("download_premium_", ""))
                self.send_premium_game_file(user_id, chat_id, game_id)
                return
                
            elif data.startswith("premium_details_"):
                game_id = int(data.replace("premium_details_", ""))
                self.show_premium_game_details(user_id, chat_id, game_id, message_id)
                return

            # Upload system callbacks
            elif data == "upload_options":
                self.show_upload_options(user_id, chat_id, message_id)
                return
                
            elif data == "upload_regular":
                self.robust_send_message(chat_id,
                    "🆓 <b>Regular Game Upload</b>\n\n"
                    "Please upload the game file now.\n\n"
                    "📁 Supported formats: ZIP, 7Z, ISO, APK, XAPK, APKS, RAR, PKG, CSO, PBP\n\n"
                    "💡 The file will be available for free to all users."
                )
                return
                
            elif data == "upload_premium":
                self.start_premium_upload(user_id, chat_id)
                return

            # Game request management callbacks
            elif data == "manage_requests":
                self.show_request_management(user_id, chat_id, message_id)
                return
                
            elif data.startswith("reply_request_"):
                request_id = int(data.replace("reply_request_", ""))
                self.start_request_reply(user_id, chat_id, request_id)
                return
                
            elif data.startswith("complete_request_"):
                request_id = int(data.replace("complete_request_", ""))
                if self.game_request_system.update_request_status(request_id, "completed", "Request completed by admin"):
                    self.answer_callback_query(callback_query['id'], "✅ Request marked as completed!", True)
                else:
                    self.answer_callback_query(callback_query['id'], "❌ Failed to update request.", True)
                return
                
            elif data.startswith("reply_with_photo_"):
                request_id = int(data.replace("reply_with_photo_", ""))
                if user_id not in self.reply_sessions:
                    self.reply_sessions[user_id] = {}
                self.reply_sessions[user_id] = {
                    'stage': 'waiting_photo',
                    'request_id': request_id,
                    'type': 'photo',
                    'chat_id': chat_id
                }
                self.robust_send_message(chat_id, "📎 Please send the photo for your reply (with optional caption):")
                return
                
            elif data == "cancel_reply":
                if user_id in self.reply_sessions:
                    del self.reply_sessions[user_id]
                self.robust_send_message(chat_id, "❌ Reply cancelled.")
                return

            # ==================== REFERRAL & TOKEN CALLBACKS ====================
            elif data == "rescan_games":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied.", self.create_main_menu_buttons(user_id))
                    return
                self.edit_message(chat_id, message_id, "🔄 Rescanning games...", self.create_game_files_buttons())
                self.scan_channel_for_games()
                self.edit_message(chat_id, message_id,
                                  f"✅ Rescan complete! {len(self.games_cache.get('all', []))} games loaded.",
                                  self.create_game_files_buttons())
                return

            elif data == "redeem_code_info":
                tokens = self.referral.get_tokens(user_id)
                text = (
                    f"🔑 <b>Redeem an Access Code</b>\n\n"
                    f"💎 Your current tokens: <b>{tokens}</b>\n\n"
                    f"To redeem a code, simply type the <b>6-digit code</b> and send it as a message.\n\n"
                    f"✅ Each code can only be used <b>once per user</b>.\n"
                    f"🎁 Token reward depends on the code.\n\n"
                    f"<i>Get codes from admins or special events!</i>"
                )
                keyboard = {"inline_keyboard": [
                    [{"text": "💎 My Tokens", "callback_data": "my_tokens"},
                     {"text": "👥 Referral", "callback_data": "referral_menu"}],
                    [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data == "referral_menu":
                stats = self.referral.get_stats(user_id)
                link = self.referral.get_referral_link(user_id)
                text = f"""👥 <b>Referral Program</b>

💎 <b>Your Stats:</b>
• Total Referrals: {stats['referrals']}
• Current Token Balance: {stats['tokens']}

🎁 <b>How it works:</b>
1. Share your referral link below
2. Friends join using your link
3. You earn <b>1 Game Token</b> per referral
4. Use tokens to buy premium games!

🔗 <b>Your Referral Link:</b>
<code>{link}</code>

💡 1 Game Token = 1 Star value for premium games"""
                keyboard = {"inline_keyboard": [
                    [{"text": "💰 Premium Games", "callback_data": "premium_games"},
                     {"text": "💎 My Tokens", "callback_data": "my_tokens"}],
                    [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data == "my_tokens":
                tokens = self.referral.get_tokens(user_id)
                text = f"""💎 <b>Game Tokens Balance</b>

💰 Current Balance: <b>{tokens} Tokens</b>

💡 <b>What can you do with tokens?</b>
• Buy premium games (10 tokens each)
• Access exclusive content

🎮 1 Token = 1 Star value"""
                keyboard = {"inline_keyboard": [
                    [{"text": "🎮 Premium Games", "callback_data": "premium_games"},
                     {"text": "👥 Referral Program", "callback_data": "referral_menu"}],
                    [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data == "referral_stats":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_main_menu_buttons(user_id))
                    return
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT user_id, first_name, total_referrals, game_tokens
                    FROM users WHERE total_referrals > 0
                    ORDER BY total_referrals DESC LIMIT 10
                ''')
                top = cursor.fetchall()
                cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by != 0')
                total_referred = cursor.fetchone()[0]
                cursor.execute('SELECT SUM(game_tokens) FROM users')
                total_tokens = cursor.fetchone()[0] or 0
                text = f"🏆 <b>Referral Leaderboard</b>\n\n📊 Total referred users: {total_referred}\n💎 Total tokens in circulation: {total_tokens}\n\n"
                for i, (uid, name, refs, tokens) in enumerate(top, 1):
                    text += f"{i}. {name} — {refs} referrals ({tokens} tokens)\n"
                if not top:
                    text += "No referrals yet."
                self.edit_message(chat_id, message_id, text, self.create_admin_buttons())
                return

            elif data == "code_manager":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied.", self.create_main_menu_buttons(user_id))
                    return
                codes = self.admin_codes.list_codes(user_id)
                text  = "🔑 <b>Admin Code Manager</b>\n\n"
                if codes:
                    for c in codes[:10]:
                        code_str, expires, max_uses, used, active, desc, reward = c
                        status = "✅" if active else "❌"
                        exp_str = expires[:10] if expires and expires[:4] != '9999' else "No expiry"
                        uses_str = f"{used}/{max_uses}" if max_uses > 0 else f"{used}/∞"
                        text += f"{status} <code>{code_str}</code> — {uses_str} uses — {reward}🪙 — exp:{exp_str}"
                        if desc:
                            text += f" — {desc}"
                        text += "\n"
                else:
                    text += "No codes created yet.\n"
                keyboard = {"inline_keyboard": [
                    [{"text": "➕ Create New Code", "callback_data": "create_code_start"}],
                    [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data == "create_code_start":
                if not self.is_admin(user_id):
                    return
                self.code_sessions[user_id] = {'stage': 'waiting_duration'}
                text = ("🔑 <b>Create Access Code</b>\n\n"
                        "Select the code duration:")
                keyboard = {"inline_keyboard": [
                    [{"text": "1 Day",   "callback_data": "code_dur_1"},
                     {"text": "7 Days",  "callback_data": "code_dur_7"}],
                    [{"text": "14 Days", "callback_data": "code_dur_14"},
                     {"text": "30 Days", "callback_data": "code_dur_30"}],
                    [{"text": "90 Days", "callback_data": "code_dur_90"},
                     {"text": "1 Year",  "callback_data": "code_dur_365"}],
                    [{"text": "No Expiry","callback_data": "code_dur_0"}],
                    [{"text": "❌ Cancel", "callback_data": "code_manager"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data.startswith("code_dur_"):
                if not self.is_admin(user_id):
                    return
                days_str = data.replace("code_dur_", "")
                days = None if days_str == '0' else int(days_str)
                self.code_sessions[user_id] = {
                    'stage': 'waiting_max_uses',
                    'days':  days
                }
                label = "No Expiry" if days is None else f"{days} Day(s)"
                text = (f"🔑 Duration: <b>{label}</b>\n\n"
                        "Select max number of uses\n"
                        "(how many different users can redeem this code):")
                keyboard = {"inline_keyboard": [
                    [{"text": "1",   "callback_data": "code_uses_1"},
                     {"text": "5",   "callback_data": "code_uses_5"},
                     {"text": "10",  "callback_data": "code_uses_10"}],
                    [{"text": "25",  "callback_data": "code_uses_25"},
                     {"text": "50",  "callback_data": "code_uses_50"},
                     {"text": "100", "callback_data": "code_uses_100"}],
                    [{"text": "Unlimited", "callback_data": "code_uses_0"}],
                    [{"text": "❌ Cancel", "callback_data": "code_manager"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data.startswith("code_uses_"):
                if not self.is_admin(user_id):
                    return
                if user_id not in self.code_sessions:
                    self.answer_callback_query(callback_query['id'], "❌ Session expired.", True)
                    return
                uses_str = data.replace("code_uses_", "")
                max_uses = 0 if uses_str == '0' else int(uses_str)
                self.code_sessions[user_id]['max_uses'] = max_uses
                self.code_sessions[user_id]['stage'] = 'waiting_token_reward'
                uses_label = "Unlimited" if max_uses == 0 else str(max_uses)
                days = self.code_sessions[user_id].get('days')
                dur_label = "No Expiry" if days is None else f"{days} Day(s)"
                text = (f"🔑 Duration: <b>{dur_label}</b> | Max uses: <b>{uses_label}</b>\n\n"
                        "Step 3 — How many tokens should this code reward?")
                keyboard = {"inline_keyboard": [
                    [{"text": "1 Token",   "callback_data": "code_reward_1"},
                     {"text": "3 Tokens",  "callback_data": "code_reward_3"},
                     {"text": "5 Tokens",  "callback_data": "code_reward_5"}],
                    [{"text": "10 Tokens", "callback_data": "code_reward_10"},
                     {"text": "20 Tokens", "callback_data": "code_reward_20"},
                     {"text": "50 Tokens", "callback_data": "code_reward_50"}],
                    [{"text": "❌ Cancel", "callback_data": "code_manager"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data.startswith("code_reward_"):
                if not self.is_admin(user_id):
                    return
                if user_id not in self.code_sessions:
                    self.answer_callback_query(callback_query['id'], "❌ Session expired.", True)
                    return
                reward = int(data.replace("code_reward_", ""))
                self.code_sessions[user_id]['token_reward'] = reward
                self.code_sessions[user_id]['stage'] = 'waiting_description'
                days     = self.code_sessions[user_id].get('days')
                max_uses = self.code_sessions[user_id].get('max_uses', 1)
                dur_label  = "No Expiry" if days is None else f"{days} Day(s)"
                uses_label = "Unlimited" if max_uses == 0 else str(max_uses)
                text = (f"🔑 Duration: <b>{dur_label}</b> | Uses: <b>{uses_label}</b> | Reward: <b>{reward}🪙</b>\n\n"
                        "Step 4 — Send a short description for this code\n"
                        "(e.g. 'Beta testers') or send <code>skip</code>:")
                keyboard = {"inline_keyboard": [[{"text": "❌ Cancel", "callback_data": "code_manager"}]]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            elif data.startswith("deactivate_code_"):
                if not self.is_admin(user_id):
                    return
                code_str = data.replace("deactivate_code_", "")
                ok = self.admin_codes.deactivate_code(user_id, code_str)
                self.answer_callback_query(
                    callback_query['id'],
                    "✅ Code deactivated." if ok else "❌ Could not deactivate.",
                    True
                )
                # Refresh manager
                codes = self.admin_codes.list_codes(user_id)
                text = "🔑 <b>Admin Code Manager</b>\n\n"
                for c in codes[:10]:
                    code_val, expires, max_uses, used, active, desc, reward = c
                    status = "✅" if active else "❌"
                    exp_str = expires[:10] if expires and expires[:4] != '9999' else "No expiry"
                    uses_str = f"{used}/{max_uses}" if max_uses > 0 else f"{used}/∞"
                    text += f"{status} <code>{code_val}</code> — {uses_str} — {reward}🪙 — {exp_str}\n"
                keyboard = {"inline_keyboard": [
                    [{"text": "➕ Create New Code", "callback_data": "create_code_start"}],
                    [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
                ]}
                self.edit_message(chat_id, message_id, text, keyboard)
                return

            # Stars system callbacks
            elif data == "stars_menu":
                self.show_stars_menu(user_id, chat_id, message_id)
                return
                
            elif data.startswith("stars_"):
                if data == "stars_custom":
                    self.stars_sessions[user_id] = {}
                    self.robust_send_message(chat_id, 
                        "💫 <b>Custom Stars Amount</b>\n\n"
                        "Please enter the number of Stars you'd like to donate:\n\n"
                        "💡 <i>Enter a number (e.g., 250 for 250 Stars ≈ $2.50)</i>"
                    )
                elif data == "stars_stats":
                    self.show_stars_stats(user_id, chat_id, message_id)
                    return
                else:
                    stars_str = data.replace("stars_", "")
                    try:
                        stars_amount = int(stars_str)
                        self.process_stars_donation(user_id, chat_id, stars_amount)
                    except ValueError:
                        self.robust_send_message(chat_id, "❌ Invalid stars amount.")
                return

            # Game request system callbacks
            elif data == "request_game":
                self.start_game_request(user_id, chat_id)
                return
                
            elif data == "my_requests":
                self.show_user_requests(user_id, chat_id, message_id)
                return

            # Admin game request management
            elif data == "admin_requests_panel":
                self.show_admin_requests_panel(user_id, chat_id, message_id)
                return

            # Broadcast system callbacks
            elif data == "broadcast_panel":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                
                broadcast_info = """📢 <b>Admin Broadcast System</b>

Send messages to all bot subscribers.

⚡ Features:
• Send to all verified users
• HTML formatting support
• Photo attachments
• Preview before sending
• Delivery statistics
• Progress tracking

Choose an option:"""
                self.edit_message(chat_id, message_id, broadcast_info, self.create_broadcast_panel_buttons())
                return
                
            elif data == "start_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.start_broadcast_with_photo(user_id, chat_id)
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
                broadcast_thread = threading.Thread(
                    target=self.send_broadcast_to_all_enhanced,
                    args=(user_id, chat_id),
                    daemon=True
                )
                broadcast_thread.start()
                return
                
            elif data == "cancel_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                self.cancel_broadcast(user_id, chat_id, message_id)
                return
                
            elif data == "broadcast_add_button":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied.", True)
                    return
                if user_id not in self.broadcast_sessions:
                    self.answer_callback_query(callback_query['id'], "❌ No active broadcast.", True)
                    return
                self.broadcast_sessions[user_id]['stage'] = 'waiting_button_text'
                self.edit_message(chat_id, message_id,
                    "🔘 <b>Add Inline Button</b>\n\nSend the button label text (e.g. 'Visit Website'):",
                    {"inline_keyboard": [[{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]]})
                return

            elif data == "edit_broadcast":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied.", True)
                    return
                if user_id in self.broadcast_sessions:
                    session = self.broadcast_sessions[user_id]
                    session['stage'] = 'waiting_message_or_media'
                    session['photo'] = None
                    session['video'] = None
                    session['buttons'] = []
                    self.edit_message(chat_id, message_id,
                        "✏️ Broadcast reset. Send your new message, photo, or video:",
                        {"inline_keyboard": [[{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]]})
                return

            # Mini-games callbacks
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
                
            elif data.startswith("random_"):
                range_type = data.replace("random_", "")
                self.generate_custom_random(user_id, chat_id, range_type)
                return
                
            elif data == "mini_stats":
                self.show_mini_games_stats(user_id, chat_id, message_id)
                return
                
            elif data.startswith("quick_guess_"):
                guess = int(data.replace("quick_guess_", ""))
                self.handle_guess_input(user_id, chat_id, str(guess))
                return
                
            elif data == "quick_numbers":
                quick_buttons = []
                row = []
                for i in range(1, 11):
                    row.append({"text": str(i), "callback_data": f"quick_guess_{i}"})
                    if i % 5 == 0:
                        quick_buttons.append(row)
                        row = []
                
                keyboard = {"inline_keyboard": quick_buttons}
                self.edit_message(chat_id, message_id, "🔢 Choose your guess quickly:", keyboard)
                return

            # Admin management callbacks
            elif data == "clear_all_games":
                self.clear_all_games(user_id, chat_id, message_id)
                return
                
            elif data == "scan_bot_games":
                if not self.is_admin(user_id):
                    self.answer_callback_query(callback_query['id'], "❌ Access denied. Admin only.", True)
                    return
                
                self.edit_message(chat_id, message_id, "🔍 Scanning for bot-uploaded games...", self.create_admin_buttons())
                bot_games_found = self.scan_bot_uploaded_games()
                self.update_games_cache()
                self.edit_message(chat_id, message_id, f"✅ Bot games scan complete! Found {bot_games_found} new games.", self.create_admin_buttons())
                return

            # Handle game file sending directly as documents
            elif data.startswith('send_game_'):
                parts = data.replace('send_game_', '').split('_')
                if len(parts) >= 3:
                    message_id_to_send = int(parts[0])
                    file_id = parts[1] if len(parts) > 1 else None
                    is_bot_file = int(parts[2]) == 1
                    
                    if file_id == 'short':
                        file_id = None
                    else:
                        file_id = file_id.replace('_', '-').replace('eq', '=')
                    
                    self.answer_callback_query(callback_query['id'], "📥 Sending file...", False)
                    
                    success = self.send_document_by_file_id(chat_id, file_id, is_bot_file, message_id_to_send)
                    
                    if success:
                        self.answer_callback_query(callback_query['id'], "✅ File sent!", False)
                    else:
                        self.answer_callback_query(callback_query['id'], "❌ Failed to send file. Please try again or contact admin.", True)
                return
            
            elif data.startswith('search_page_'):
                remainder = data[len('search_page_'):]
                # Use rsplit so the search term (which may contain underscores) is preserved
                parts = remainder.rsplit('_', 1)
                if len(parts) == 2:
                    search_term = parts[0]
                    try:
                        page = int(parts[1])
                    except ValueError:
                        return
                    
                    user_results = self.search_results.get(user_id, {})
                    if user_results and user_results.get('search_term') == search_term:
                        results = user_results.get('results', [])
                        
                        results_text = f"🔍 Search Results: <code>{html.escape(search_term)}</code>\n\n"
                        results_text += f"📄 Page {page + 1}\n"
                        results_text += f"📊 Total results: {len(results)}\n\n"
                        results_text += "📥 Click on any file below to download it:"
                        
                        self.edit_message(
                            chat_id, 
                            message_id, 
                            results_text,
                            self.create_search_results_buttons(results, search_term, user_id, page)
                        )
                return
            
            # Handle other existing callbacks
            elif data == "profile":
                self.handle_profile(chat_id, message_id, user_id, first_name)
                
            elif data == "time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_text = f"🕒 <b>Current Time</b>\n\n📅 {current_time}\n\n⏰ Server Time (UTC)"
                self.edit_message(chat_id, message_id, time_text, self.create_main_menu_buttons(user_id))
                
            elif data == "channel_info":
                channel_info = f"""📢 <b>Channel Information</b>

🏷️ Channel: {self.REQUIRED_CHANNEL}
🔗 Link: {self.CHANNEL_LINK}
📝 Description: PSP Games & More!

🎮 Available Games:
• PSP Games (ISO/CSO)
• PS1 Games
• Android Games (APK / XAPK / APKS)
• Emulator Games
• And much more!

📥 How to Download:
1. Join our channel
2. Browse available games
3. Click on files to download

⚠️ Note: You need to join channel and complete verification to access games."""
                self.edit_message(chat_id, message_id, channel_info, self.create_main_menu_buttons(user_id))
                
            elif data == "games":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_main_menu_buttons(user_id))
                    return
                
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

🔗 Channel: {self.REQUIRED_CHANNEL}"""
                self.edit_message(chat_id, message_id, games_text, self.create_games_buttons())
                
            elif data == "game_files":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_games_buttons())
                    return
                
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
                self.edit_message(chat_id, message_id, files_text, self.create_game_files_buttons())
                
            elif data == "mini_games":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_games_buttons())
                    return
                
                games_text = """🎮 <b>Mini Games</b>

🎯 Choose a game to play:

• 🎯 Number Guess - Guess the random number (1-10)
• 🎲 Random Number - Generate random numbers with analysis
• 🎰 Lucky Spin - Spin for lucky symbols and coins
• 📊 My Stats - View your gaming statistics

Have fun! 🎉"""
                self.edit_message(chat_id, message_id, games_text, self.create_mini_games_buttons())
                
            elif data == "search_games":
                if not self.is_user_verified(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_main_menu_buttons(user_id))
                    return
                
                self.handle_search_games(chat_id, message_id, user_id, first_name)
                
            elif data == "game_zip":
                games = self.games_cache.get('zip', [])
                text = self.format_games_list(games, "ZIP")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                
            elif data == "game_7z":
                games = self.games_cache.get('7z', [])
                text = self.format_games_list(games, "7Z")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                
            elif data == "game_iso":
                games = self.games_cache.get('iso', [])
                text = self.format_games_list(games, "ISO")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                
            elif data == "game_apk":
                games = self.games_cache.get('apk', [])
                text = self.format_games_list(games, "APK")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())

            elif data == "game_xapk":
                games = self.games_cache.get('xapk', [])
                text = self.format_games_list(games, "XAPK")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())

            elif data == "game_apks":
                games = self.games_cache.get('apks', [])
                text = self.format_games_list(games, "APKS")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())

            elif data == "game_psp":
                cso_games = self.games_cache.get('cso', [])
                pbp_games = self.games_cache.get('pbp', [])
                psp_games = cso_games + pbp_games
                text = self.format_games_list(psp_games, "PSP")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                
            elif data == "game_all":
                games = self.games_cache.get('all', [])
                text = self.format_games_list(games, "ALL")
                self.edit_message(chat_id, message_id, text, self.create_game_files_buttons())
                
            elif data == "rescan_games":
                self.edit_message(chat_id, message_id, "🔄 Scanning for new games...", self.create_game_files_buttons())
                total_games = self.scan_channel_for_games()
                stats = self.get_channel_stats()
                self.edit_message(chat_id, message_id, f"✅ Rescan complete! Found {total_games} total games. Database now has {stats['total_games']} regular games and {stats['premium_games']} premium games.", self.create_game_files_buttons())
            
            elif data == "back_to_menu":
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
                self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons(user_id))
            
            elif data == "verify_channel":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)

                    # Credit referral token now that both steps are complete
                    self.referral.complete_referral(user_id)

                    welcome_text = (
                        f"✅ <b>Verification Complete!</b>\n\n"
                        f"👋 Welcome {first_name}!\n\n"
                        f"🎉 You now have full access:\n"
                        f"• 🎮 Game File Browser\n"
                        f"• 💰 Premium Games\n"
                        f"• 🔍 Game Search\n"
                        f"• 🎮 Mini-Games\n"
                        f"• ⭐ Stars Donations\n"
                        f"• 📝 Game Requests\n\n"
                        f"📢 Channel: {self.REQUIRED_CHANNEL}\n"
                        f"Choose an option below:"
                    )
                    self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons(user_id))
                else:
                    self.edit_message(
                        chat_id, message_id,
                        f"❌ You haven't joined the channel yet!\n\n"
                        f"Please join {self.REQUIRED_CHANNEL} first, then tap Verify Join again.",
                        self.create_channel_buttons()
                    )
            
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_main_menu_buttons(user_id))
                    return
                
                stats = self.get_channel_stats()
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
                self.edit_message(chat_id, message_id, admin_text, self.create_admin_buttons())
            
            elif data == "upload_stats":
                if not self.is_admin(user_id):
                    return
                self.handle_upload_stats(chat_id, message_id, user_id, first_name)
            
            elif data == "update_cache":
                if not self.is_admin(user_id):
                    return
                self.edit_message(chat_id, message_id, "🔄 Updating games cache...", self.create_admin_buttons())
                self.update_games_cache()
                stats = self.get_channel_stats()
                self.edit_message(chat_id, message_id, f"✅ Cache updated! {stats['total_games']} regular games and {stats['premium_games']} premium games loaded.", self.create_admin_buttons())
                
        except Exception as e:
            print(f"Callback error: {e}")
            traceback.print_exc()

    # ==================== FIXED: ENHANCED FILE SENDING METHODS ====================
    
    def send_document_by_file_id(self, chat_id, file_id, is_bot_file, message_id):
        """Send document directly using file_id"""
        try:
            if not file_id or file_id == 'None':
                cursor = self.conn.cursor()
                if is_bot_file:
                    cursor.execute('SELECT file_id FROM channel_games WHERE bot_message_id = ?', (message_id,))
                else:
                    cursor.execute('SELECT file_id FROM channel_games WHERE message_id = ?', (message_id,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    file_id = result[0]
                else:
                    return self.send_game_file(chat_id, message_id, None, is_bot_file)
            
            print(f"📤 Sending document with file_id: {file_id}")
            
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id
            }
            
            response = _tg_session.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Sent document using file_id to user {chat_id}")
                return True
            else:
                print(f"❌ Direct send failed: {result.get('description')}")
                return self.send_game_file(chat_id, message_id, file_id, is_bot_file)
                
        except Exception as e:
            print(f"❌ Error sending document by file_id: {e}")
            return self.send_game_file(chat_id, message_id, file_id, is_bot_file)

    def send_game_file(self, chat_id, message_id, file_id=None, is_bot_file=False):
        """Send game file (forward or send as document)"""
        try:
            print(f"📤 Sending game file: msg_id={message_id}, is_bot_file={is_bot_file}, file_id={file_id}")
            
            if file_id:
                success = self.send_document_by_file_id(chat_id, file_id, is_bot_file, message_id)
                if success:
                    return True
            
            if is_bot_file:
                # Bot-uploaded files: always send by file_id (forwarding is unreliable
                # since the source chat_id is the admin's private chat, not the user's).
                if file_id and file_id != 'None':
                    url = self.base_url + "sendDocument"
                    data = {
                        "chat_id": chat_id,
                        "document": file_id
                    }
                    response = _tg_session.post(url, data=data, timeout=30)
                    result = response.json()
                    if result.get('ok'):
                        print(f"✅ Successfully sent bot file {message_id} by file_id")
                        return True
                    else:
                        print(f"❌ Bot file send by file_id failed: {result.get('description')}")
                        return False
                else:
                    print(f"❌ No file_id available for bot file {message_id}")
                    return False
            else:
                url = self.base_url + "forwardMessage"
                data = {
                    "chat_id": chat_id,
                    "from_chat_id": self.REQUIRED_CHANNEL,
                    "message_id": message_id
                }
                
                response = _tg_session.post(url, data=data, timeout=30)
                result = response.json()
                
                if result.get('ok'):
                    print(f"✅ Successfully forwarded channel file {message_id}")
                    return True
                else:
                    print(f"❌ Channel forward failed: {result.get('description')}")
                    cursor = self.conn.cursor()
                    cursor.execute('SELECT file_id FROM channel_games WHERE message_id = ?', (message_id,))
                    result_db = cursor.fetchone()
                    if result_db and result_db[0]:
                        return self.send_document_by_file_id(chat_id, result_db[0], False, message_id)
                    
                    return False
                
        except Exception as e:
            print(f"❌ Error sending game file: {e}")
            return False

    # ==================== ENHANCED DATABASE OPERATIONS WITH BACKUP ====================

    def handle_document_upload(self, message):
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            if not self.is_admin(user_id):
                print(f"❌ Non-admin user {user_id} attempted upload")
                return False
            
            if 'document' not in message:
                print("❌ No document in message")
                return False
            
            if user_id in self.upload_sessions and self.upload_sessions[user_id].get('type') == 'premium':
                result = self.handle_premium_document_upload(message)
                if result:
                    file_name = message['document'].get('file_name', 'Unknown')
                    self.backup_after_game_action("Premium Game Upload", file_name)
                return result
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            bot_message_id = message['message_id']
            
            print(f"📥 Admin {user_id} uploading: {file_name} (Size: {file_size}, Message ID: {bot_message_id})")
            
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
                
                if user_id in self.upload_sessions:
                    del self.upload_sessions[user_id]
                
                self.robust_send_message(chat_id, duplicate_text)
                return True
            
            game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk', '.xapk', '.apks']
            if not any(file_name.lower().endswith(ext) for ext in game_extensions):
                self.robust_send_message(chat_id, f"❌ File type not supported: {file_name}")
                print(f"❌ Unsupported file type: {file_name}")
                return False
            
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
                
                if 'chat' in forward_origin and forward_origin['chat']['type'] == 'channel':
                    original_message_id = message.get('forward_from_message_id')
                    print(f"📨 Forwarded from channel, original message ID: {original_message_id}")
            
            if original_message_id:
                storage_message_id = original_message_id
            else:
                storage_message_id = int(time.time() * 1000) + random.randint(1000, 9999)
            
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
            
            self.update_games_cache()
            
            size = self.format_file_size(file_size)
            source_type = "Channel Forward" if original_message_id else "Direct Upload"
            
            confirm_text = f"""✅ Game file added successfully!{forward_info}

📁 File: <code>{file_name}</code>
📦 Type: {file_type}
📏 Size: {size}
🗂️ Category: {game_info['category']}
🕒 Added: {upload_date}
📮 Source: {source_type}
🆔 Storage ID: {storage_message_id}
🤖 Bot Message ID: {bot_message_id}

The file is now available in the games browser and search!"""
            
            self.robust_send_message(chat_id, confirm_text)
            
            self.backup_after_game_action("Regular Game Upload", file_name)
            
            print(f"✅ Successfully stored: {file_name} (Storage ID: {storage_message_id}, Bot Message ID: {bot_message_id})")
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            traceback.print_exc()
            return False

    def remove_game(self, user_id, chat_id, game_type, game_id, message_id=None):
        """Remove a game from database with backup"""
        try:
            if not self.is_admin(user_id):
                return False
            
            cursor = self.conn.cursor()
            game_name = ""
            
            if game_type == 'R':
                cursor.execute('SELECT file_name FROM channel_games WHERE message_id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if not game_info:
                    self.robust_send_message(chat_id, "❌ Game not found.")
                    return False
                
                game_name = game_info[0]
                cursor.execute('DELETE FROM channel_games WHERE message_id = ?', (game_id,))
                self.conn.commit()
                
            elif game_type == 'P':
                cursor.execute('SELECT file_name FROM premium_games WHERE id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if not game_info:
                    self.robust_send_message(chat_id, "❌ Premium game not found.")
                    return False
                
                game_name = game_info[0]
                cursor.execute('DELETE FROM premium_games WHERE id = ?', (game_id,))
                cursor.execute('DELETE FROM premium_purchases WHERE game_id = ?', (game_id,))
                self.conn.commit()
            
            else:
                self.robust_send_message(chat_id, "❌ Invalid game type.")
                return False
            
            self.update_games_cache()
            
            print(f"🗑️ Admin {user_id} removed {game_type} game: {game_name} (ID: {game_id})")
            
            self.backup_after_game_action("Game Removal", game_name)
            
            result_text = f"✅ <b>{'Regular' if game_type == 'R' else 'Premium'} Game Removed</b>\n\n📁 <code>{game_name}</code>\n🆔 {game_id}\n\nGame has been removed from the database."
            
            if message_id:
                self.edit_message(chat_id, message_id, result_text, self.create_admin_buttons())
            else:
                self.robust_send_message(chat_id, result_text, self.create_admin_buttons())
            
            return True
            
        except Exception as e:
            print(f"❌ Remove game error: {e}")
            self.robust_send_message(chat_id, "❌ Error removing game.")
            return False

    def clear_all_games(self, user_id, chat_id, message_id):
        """Clear all games from database with backup"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
            return
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games_before = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
            uploaded_games_before = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM premium_games')
            premium_games_before = cursor.fetchone()[0]
            
            cursor.execute('DELETE FROM channel_games')
            cursor.execute('DELETE FROM premium_games')
            self.conn.commit()
            
            self.update_games_cache()
            
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
            
            self.edit_message(chat_id, message_id, clear_text, self.create_admin_buttons())
            
            print(f"🗑️ Admin {user_id} cleared all games from database")
            
        except Exception as e:
            error_text = f"❌ Error clearing games: {str(e)}"
            self.edit_message(chat_id, message_id, error_text, self.create_admin_buttons())
            print(f"❌ Clear games error: {e}")

    # ==================== DUPLICATE DETECTION SYSTEM ====================
    
    def check_duplicate_game(self, file_name, file_size, file_type):
        """Check if a game already exists in database"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT message_id, file_name FROM channel_games 
                WHERE file_name = ? AND file_size = ? AND file_type = ?
            ''', (file_name, file_size, file_type))
            regular_duplicate = cursor.fetchone()
            
            cursor.execute('''
                SELECT id, file_name FROM premium_games 
                WHERE file_name = ? AND file_size = ? AND file_type = ?
            ''', (file_name, file_size, file_type))
            premium_duplicate = cursor.fetchone()
            
            return regular_duplicate, premium_duplicate
            
        except Exception as e:
            print(f"❌ Error checking duplicates: {e}")
            return None, None

    # ==================== GAME REMOVAL SYSTEM ====================
    
    def show_remove_game_menu(self, user_id, chat_id, message_id):
        """Show game removal menu for admins"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
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
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔍 Search & Remove Game", "callback_data": "search_remove_game"}],
                [{"text": "📋 View Recent Uploads", "callback_data": "view_recent_uploads"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, remove_text, keyboard)

    def start_remove_game_search(self, user_id, chat_id):
        """Start game removal search process"""
        if not self.is_admin(user_id):
            return False
        
        self.robust_send_message(chat_id,
            "🔍 <b>Game Removal Search</b>\n\n"
            "Please enter the game name you want to search and remove:\n\n"
            "💡 You can search by full name or partial keywords"
        )
        
        self.search_sessions[user_id] = {'mode': 'remove'}
        return True

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
            
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT message_id, file_name, file_type, file_size, upload_date, category, 
                       file_id, bot_message_id, is_uploaded, is_forwarded
                FROM channel_games 
                WHERE LOWER(file_name) LIKE ? OR file_name LIKE ?
                ORDER BY file_name
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            regular_results = cursor.fetchall()
            
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
                    "💡 Try different keywords or check the spelling."
                )
                return True
            
            results_text = f"""🔍 <b>Removal Search Results</b>

Search: <code>{search_term}</code>
Found: {len(all_results)} games

⚠️ <b>Click "Remove" to delete any game:</b>\n\n"""
            
            for i, game in enumerate(all_results[:10], 1):
                game_type = "🆓 Regular" if game['type'] == 'regular' else "💰 Premium"
                size = self.format_file_size(game['file_size'])
                
                results_text += f"{i}. <b>{game['file_name']}</b>\n"
                results_text += f"   📦 {game['file_type']} | 📏 {size} | {game_type}\n"
                
                if game['type'] == 'premium':
                    results_text += f"   ⭐ {game['stars_price']} Stars\n"
                
                results_text += f"   🆔 {game['id']} | 📅 {game['upload_date'][:10]}\n\n"
            
            keyboard_buttons = []
            for game in all_results[:10]:
                game_type_char = "R" if game['type'] == 'regular' else "P"
                button_text = f"🗑️ {game['file_name'][:20]}{'...' if len(game['file_name']) > 20 else ''}"
                
                keyboard_buttons.append([{
                    "text": button_text,
                    "callback_data": f"confirm_remove_{game_type_char}_{game['id']}"
                }])
            
            keyboard_buttons.extend([
                [{"text": "🔍 New Search", "callback_data": "search_remove_game"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ])
            
            keyboard = {"inline_keyboard": keyboard_buttons}
            
            self.robust_send_message(chat_id, results_text, keyboard)
            return True
            
        except Exception as e:
            print(f"❌ Remove game search error: {e}")
            self.robust_send_message(chat_id, "❌ Error searching for games. Please try again.")
            return False

    def show_remove_confirmation(self, user_id, chat_id, message_id, game_type, game_id):
        """Show removal confirmation dialog"""
        if not self.is_admin(user_id):
            return False
        
        try:
            cursor = self.conn.cursor()
            
            if game_type == 'R':
                cursor.execute('SELECT file_name, file_size, file_type FROM channel_games WHERE message_id = ?', (game_id,))
            else:
                cursor.execute('SELECT file_name, file_size, file_type FROM premium_games WHERE id = ?', (game_id,))
            
            game_info = cursor.fetchone()
            
            if not game_info:
                self.edit_message(chat_id, message_id, "❌ Game not found.", self.create_admin_buttons())
                return False
            
            file_name, file_size, file_type = game_info
            size = self.format_file_size(file_size)
            game_type_text = "Regular" if game_type == 'R' else "Premium"
            
            confirm_text = f"""⚠️ <b>Confirm Game Removal</b>

📁 <b>File:</b> <code>{file_name}</code>
📦 <b>Type:</b> {file_type}
📏 <b>Size:</b> {size}
🎮 <b>Game Type:</b> {game_type_text}
🆔 <b>ID:</b> {game_id}

❌ <b>This action cannot be undone!</b>

Are you sure you want to remove this game?"""
            
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Yes, Remove Game", "callback_data": f"remove_{game_type}_{game_id}"},
                        {"text": "❌ Cancel", "callback_data": "cancel_remove"}
                    ]
                ]
            }
            
            self.edit_message(chat_id, message_id, confirm_text, keyboard)
            return True
            
        except Exception as e:
            print(f"❌ Remove confirmation error: {e}")
            return False

    # ==================== PREMIUM GAMES METHODS ====================
    
    def show_premium_games_menu(self, user_id, chat_id, message_id=None):
        """Show premium games menu to users"""
        premium_games = self.premium_games_system.get_premium_games(20)
        
        if not premium_games:
            premium_text = """💰 <b>Premium Games</b>

No premium games available yet.

Check back later for exclusive games that you can purchase with Telegram Stars!"""
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🆓 Regular Games", "callback_data": "game_files"}],
                    [{"text": "🔄 Refresh", "callback_data": "premium_games"}],
                    [{"text": "🔙 Back to Games", "callback_data": "games"}]
                ]
            }
        else:
            premium_text = """💰 <b>Premium Games</b>

Exclusive games available for purchase with Telegram Stars:

"""
            for i, game in enumerate(premium_games[:10], 1):
                game_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
                size = self.format_file_size(file_size)
                
                display_name = file_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                
                premium_text += f"\n{i}. <b>{display_name}</b>"
                premium_text += f"\n   ⭐ {stars_price} Stars | 📦 {file_type} | 📏 {size}"
                if description:
                    premium_text += f"\n   📝 {description[:50]}{'...' if len(description) > 50 else ''}"
                premium_text += f"\n   └─ <code>/premium_{game_id}</code>\n"
            
            premium_text += "\n💡 <i>Click on any game to view details and purchase!</i>"
            
            keyboard_buttons = []
            for i, game in enumerate(premium_games[:5], 1):
                game_id, file_name, file_type, file_size, stars_price, description, upload_date, file_id, bot_message_id, is_uploaded = game
                display_name = file_name
                if len(display_name) > 20:
                    display_name = display_name[:17] + "..."
                
                keyboard_buttons.append([{
                    "text": f"💰 {i}. {display_name}",
                    "callback_data": f"premium_details_{game_id}"
                }])
            
            keyboard_buttons.extend([
                [{"text": "🆓 Regular Games", "callback_data": "game_files"}],
                [{"text": "🔄 Refresh", "callback_data": "premium_games"}],
                [{"text": "🔙 Back to Games", "callback_data": "games"}]
            ])
            
            keyboard = {"inline_keyboard": keyboard_buttons}
        
        if message_id:
            self.edit_message(chat_id, message_id, premium_text, keyboard)
        else:
            self.robust_send_message(chat_id, premium_text, keyboard)
    
    def show_premium_game_details(self, user_id, chat_id, game_id, message_id):
        """Show details of a specific premium game"""
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            self.edit_message(chat_id, message_id, "❌ Game not found.", {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "premium_games"}]]})
            return
        
        game_text = f"""💰 <b>Premium Game Details</b>

🎮 <b>{game['file_name']}</b>

📊 Details:
• 📦 File Type: {game['file_type']}
• 📏 Size: {self.format_file_size(game['file_size'])}
• ⭐ Price: <b>{game['stars_price']} Stars</b>
• 💰 USD Value: ${game['stars_price'] * 0.01:.2f}

📝 Description:
{game['description'] if game['description'] else 'No description available.'}

"""
        
        has_purchased = self.premium_games_system.has_user_purchased_game(user_id, game_id)

        if has_purchased:
            game_text += "✅ <b>You already own this game!</b>\n\nClick below to download it."
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📥 Download Game", "callback_data": f"download_premium_{game_id}"}],
                    [{"text": "🔙 Back to Premium Games", "callback_data": "premium_games"}]
                ]
            }
        else:
            user_tokens  = self.referral.get_tokens(user_id)
            tokens_price = game.get('tokens_price') or game['stars_price']
            game_text += (
                f"💡 <i>Purchase with Telegram Stars or Game Tokens.</i>\n\n"
                f"💎 Your Tokens: <b>{user_tokens}</b>"
            )
            keyboard = {
                "inline_keyboard": [
                    [{"text": f"⭐ Buy with Stars ({game['stars_price']} Stars)", "callback_data": f"purchase_premium_{game_id}"}],
                    [{"text": f"💎 Buy with Tokens ({tokens_price} Tokens)", "callback_data": f"buy_tokens_{game_id}"}],
                    [{"text": "🔙 Back to Premium Games", "callback_data": "premium_games"}]
                ]
            }
        
        self.edit_message(chat_id, message_id, game_text, keyboard)
    
    def purchase_premium_game(self, user_id, chat_id, game_id, message_id):
        """Start purchase process for premium game"""
        game = self.premium_games_system.get_premium_game_by_id(game_id)
        
        if not game:
            self.edit_message(chat_id, message_id, "❌ Game not found.", {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "premium_games"}]]})
            return
        
        if self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.edit_message(chat_id, message_id, "✅ You already own this game! Sending it now...", None)
            self.send_premium_game_file(user_id, chat_id, game_id)
            return
        
        success = self.stars_system.create_premium_game_invoice(
            user_id, chat_id, game['stars_price'], game['file_name'], game_id
        )
        
        if success:
            self.edit_message(chat_id, message_id, f"✅ Invoice created for {game['stars_price']} Stars!\n\nPlease complete the payment in the invoice above.", {"inline_keyboard": [[{"text": "🔙 Back to Premium Games", "callback_data": "premium_games"}]]})
        else:
            self.edit_message(chat_id, message_id, "❌ Failed to create invoice. Please try again.", {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "premium_games"}]]})
    
    def send_premium_game_file(self, user_id, chat_id, game_id):
        """Send premium game file — only delivers if purchase is confirmed in DB."""
        game = self.premium_games_system.get_premium_game_by_id(game_id)

        if not game:
            self.robust_send_message(chat_id, "❌ Game not found.")
            return False

        # Hard gate — never deliver without a confirmed purchase record
        if not self.premium_games_system.has_user_purchased_game(user_id, game_id):
            self.robust_send_message(
                chat_id,
                "❌ Purchase not found. Please complete payment first.\n\n"
                "If you paid with Stars, please wait a moment and try again."
            )
            return False

        if game['is_uploaded'] == 1 and game['bot_message_id']:
            success = self.send_game_file(chat_id, game['bot_message_id'], game['file_id'], True)
        else:
            success = self.send_game_file(chat_id, game['message_id'], game['file_id'], False)

        if success:
            self.robust_send_message(chat_id, f"✅ Enjoy your premium game: <b>{game['file_name']}</b>!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send game file. Please contact admin.")
            return False

    def handle_stars_price(self, user_id, chat_id, text):
        """Handle stars price input for premium game upload"""
        try:
            stars_price = int(text.strip())
            if stars_price <= 0:
                self.robust_send_message(chat_id, "❌ Please enter a positive number of Stars.")
                return True
        except ValueError:
            self.robust_send_message(chat_id, "❌ Please enter a valid number for the Stars price.")
            return True

        self.upload_sessions[user_id]['stars_price'] = stars_price
        self.upload_sessions[user_id]['stage'] = 'waiting_description'

        self.robust_send_message(chat_id,
            f"✅ Price set: <b>{stars_price} Stars</b>\n\n"
            "📝 Now enter a short description for this game\n"
            "(or send <code>skip</code> to skip):"
        )
        return True

    def handle_premium_description(self, user_id, chat_id, text):
        """Handle description input for premium game upload"""
        description = '' if text.strip().lower() == 'skip' else text.strip()
        self.upload_sessions[user_id]['description'] = description
        self.upload_sessions[user_id]['stage'] = 'waiting_file'

        price = self.upload_sessions[user_id].get('stars_price', 0)
        self.robust_send_message(chat_id,
            f"✅ Description saved.\n\n"
            f"⭐ Price: <b>{price} Stars</b>\n"
            f"📝 Description: {description or 'None'}\n\n"
            "📤 Now send the game file to upload it as a premium game:"
        )
        return True

    # ==================== UPLOAD SYSTEM ENHANCEMENTS ====================
    
    def show_upload_options(self, user_id, chat_id, message_id):
        """Show upload options for admin"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
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

📁 Both support all file formats (ZIP, ISO, APK, XAPK, APKS, etc.)"""

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🆓 Upload Regular Game", "callback_data": "upload_regular"},
                    {"text": "⭐ Upload Premium Game", "callback_data": "upload_premium"}
                ],
                [
                    {"text": "🔙 Back to Admin", "callback_data": "admin_panel"}
                ]
            ]
        }
        
        self.edit_message(chat_id, message_id, upload_text, keyboard)
    
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
    
    def handle_stars_price(self, user_id, chat_id, price_text):
        """Handle stars price input for premium games"""
        if user_id not in self.upload_sessions:
            return False
        
        try:
            stars_price = int(price_text.strip())
            if stars_price <= 0:
                self.robust_send_message(chat_id, "❌ Please enter a positive number of Stars.")
                return True
            
            if stars_price > 10000:
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
            "Supported formats: ZIP, 7Z, ISO, APK, XAPK, APKS, RAR, PKG, CSO, PBP"
        )
        return True
    
    def handle_premium_document_upload(self, message):
        """Handle premium game document upload"""
        try:
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            if user_id not in self.upload_sessions or self.upload_sessions[user_id].get('type') != 'premium':
                return False
            
            if 'document' not in message:
                return False
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            bot_message_id = message['message_id']
            
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
                
                del self.upload_sessions[user_id]
                
                self.robust_send_message(chat_id, duplicate_text)
                return True
            
            session = self.upload_sessions[user_id]
            
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
            
            game_id = self.premium_games_system.add_premium_game(game_info)
            
            if game_id:
                del self.upload_sessions[user_id]
                
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

    # ==================== GAME REQUEST REPLY SYSTEM ====================
    
    def show_request_management(self, user_id, chat_id, message_id):
        """Show game request management panel for admins"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
            return
        
        pending_requests = self.game_request_system.get_pending_requests(10)
        
        if not pending_requests:
            requests_text = """👑 <b>Game Request Management</b>

📊 No pending game requests.

All requests have been processed!"""
        else:
            requests_text = f"""👑 <b>Game Request Management</b>

📊 Pending requests: {len(pending_requests)}

📝 <b>Recent Requests:</b>"""
            
            for req in pending_requests:
                req_id, user_id_req, user_name, game_name, platform, created_at = req
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d %H:%M')
                requests_text += f"\n\n🎮 <b>{game_name}</b>"
                requests_text += f"\n👤 {user_name} (ID: {user_id_req})"
                requests_text += f"\n📱 {platform} | 🆔 {req_id} | 📅 {date_str}"
                requests_text += f"\n└─ <code>/reply_{req_id}</code>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 Refresh", "callback_data": "manage_requests"}],
                [{"text": "📋 View All Requests", "callback_data": "admin_requests_panel"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, requests_text, keyboard)
    
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
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📎 Add Photo to Reply", "callback_data": f"reply_with_photo_{request_id}"}],
                [{"text": "❌ Cancel Reply", "callback_data": "cancel_reply"}]
            ]
        }
        
        self.robust_send_message(chat_id, reply_text, keyboard)
        return True
    
    def handle_request_reply(self, user_id, chat_id, reply_text):
        """Handle text reply to game request"""
        if user_id not in self.reply_sessions:
            return False
        
        session = self.reply_sessions[user_id]
        request_id = session['request_id']
        
        success = self.game_request_system.add_request_reply(
            request_id, user_id, reply_text
        )
        
        if success:
            request = self.game_request_system.get_request_by_id(request_id)
            if request:
                safe_reply_text = html.escape(reply_text)
                user_notification = f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request['game_name']}</b>
👤 Admin: {self.get_user_info(user_id).get('first_name', 'Admin')}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 <b>Message:</b>
{safe_reply_text}

Thank you for using our service! 🙏"""
                
                self.robust_send_message(request['user_id'], user_notification)
            
            del self.reply_sessions[user_id]
            
            self.robust_send_message(chat_id, f"✅ Reply sent to user successfully!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send reply.")
            return False
    
    def handle_photo_reply(self, user_id, chat_id, photo_file_id, caption):
        """Handle photo reply to game request"""
        if user_id not in self.reply_sessions:
            return False
        
        session = self.reply_sessions[user_id]
        request_id = session['request_id']
        
        success = self.game_request_system.add_request_reply(
            request_id, user_id, caption or "Photo attached", photo_file_id
        )
        
        if success:
            request = self.game_request_system.get_request_by_id(request_id)
            if request:
                photo_url = self.base_url + "sendPhoto"
                photo_data = {
                    "chat_id": request['user_id'],
                    "photo": photo_file_id,
                    "caption": f"""📨 <b>Reply to Your Game Request</b>

🎮 Game: <b>{request['game_name']}</b>
👤 Admin: {self.get_user_info(user_id).get('first_name', 'Admin')}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 <b>Message:</b>
{caption if caption else 'Photo attached'}""",
                    "parse_mode": "HTML"
                }
                
                try:
                    _tg_session.post(photo_url, data=photo_data, timeout=30)
                except Exception as e:
                    print(f"❌ Failed to send photo reply: {e}")
            
            del self.reply_sessions[user_id]
            
            self.robust_send_message(chat_id, "✅ Photo reply sent to user successfully!")
            return True
        else:
            self.robust_send_message(chat_id, "❌ Failed to send photo reply.")
            return False

    # ==================== ENHANCED BROADCAST SYSTEM ====================
    
    def start_broadcast_with_photo(self, user_id, chat_id):
        """Start broadcast message creation — supports text, photo, and video with optional inline buttons"""
        if not self.is_admin(user_id):
            self.robust_send_message(chat_id, "❌ Access denied. Admin only.")
            return False

        self.broadcast_sessions[user_id] = {
            'stage': 'waiting_message_or_media',
            'message': '',
            'photo': None,
            'video': None,
            'buttons': [],          # list of {"text": ..., "url": ...}
            'chat_id': chat_id
        }

        broadcast_info = """📢 <b>Admin Broadcast System</b>

Send a message to all verified subscribers.

📝 <b>Step 1 — Content:</b>
• Type a text message, OR
• Send a photo with optional caption, OR
• Send a video with optional caption

💡 HTML formatting is supported in text."""

        keyboard = {
            "inline_keyboard": [
                [{"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
            ]
        }

        self.robust_send_message(chat_id, broadcast_info, keyboard)
        return True
    
    def _advance_to_buttons_stage(self, user_id, chat_id, media_type, preview_label):
        """After content is set, ask admin if they want to add inline URL buttons"""
        session = self.broadcast_sessions[user_id]
        session['stage'] = 'waiting_buttons'

        keyboard = {
            "inline_keyboard": [
                [{"text": "➕ Add Button (URL)", "callback_data": "broadcast_add_button"}],
                [{"text": "✅ Send Now (No Buttons)", "callback_data": "confirm_broadcast"},
                 {"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
            ]
        }
        self.robust_send_message(chat_id,
            f"📋 <b>Broadcast Preview</b>\n\n"
            f"📎 Content: {preview_label}\n\n"
            f"<b>Step 2 — Inline Buttons (optional):</b>\n"
            f"Add URL buttons that appear below the message, or send directly.",
            keyboard
        )

    def handle_broadcast_message(self, user_id, chat_id, text):
        """Handle broadcast text input"""
        if user_id not in self.broadcast_sessions:
            return False

        session = self.broadcast_sessions[user_id]

        if session['stage'] == 'waiting_message_or_media':
            session['message'] = text
            self._advance_to_buttons_stage(user_id, chat_id, 'text',
                                           f"📝 Text ({len(text)} chars)")
            return True

        if session['stage'] == 'waiting_button_text':
            session['_pending_button_text'] = text
            session['stage'] = 'waiting_button_url'
            self.robust_send_message(chat_id, "🔗 Now send the URL for this button (must start with https://):")
            return True

        if session['stage'] == 'waiting_button_url':
            if not text.startswith(('http://', 'https://')):
                self.robust_send_message(chat_id, "❌ URL must start with http:// or https://. Try again:")
                return True
            btn_text = session.pop('_pending_button_text', 'Button')
            session['buttons'].append({"text": btn_text, "url": text})
            session['stage'] = 'waiting_buttons'
            keyboard = {
                "inline_keyboard": [
                    [{"text": "➕ Add Another Button", "callback_data": "broadcast_add_button"}],
                    [{"text": "✅ Send Now", "callback_data": "confirm_broadcast"},
                     {"text": "❌ Cancel", "callback_data": "cancel_broadcast"}]
                ]
            }
            self.robust_send_message(chat_id,
                f"✅ Button added: <b>{btn_text}</b>\n"
                f"Total buttons: {len(session['buttons'])}\n\n"
                "Add more or send the broadcast now.", keyboard)
            return True

        return False

    def handle_broadcast_photo(self, user_id, chat_id, photo_file_id, caption):
        """Handle broadcast photo input"""
        if user_id not in self.broadcast_sessions:
            return False

        session = self.broadcast_sessions[user_id]
        if session['stage'] == 'waiting_message_or_media':
            session['photo'] = photo_file_id
            session['message'] = caption or ""
            self._advance_to_buttons_stage(user_id, chat_id, 'photo',
                                           f"📷 Photo + caption: {caption[:40] if caption else 'none'}")
            # Send preview photo to admin
            try:
                _tg_session.post(self.base_url + "sendPhoto", data={
                    "chat_id": chat_id,
                    "photo": photo_file_id,
                    "caption": f"👆 Preview of your broadcast photo\nCaption: {caption or '(none)'}",
                    "parse_mode": "HTML"
                }, timeout=15)
            except Exception:
                pass
            return True
        return False

    def handle_broadcast_video(self, user_id, chat_id, video_file_id, caption):
        """Handle broadcast video input"""
        if user_id not in self.broadcast_sessions:
            return False

        session = self.broadcast_sessions[user_id]
        if session['stage'] == 'waiting_message_or_media':
            session['video'] = video_file_id
            session['message'] = caption or ""
            self._advance_to_buttons_stage(user_id, chat_id, 'video',
                                           f"🎥 Video + caption: {caption[:40] if caption else 'none'}")
            # Send preview note to admin (can't re-send video in preview easily without forwarding)
            self.robust_send_message(chat_id, "🎥 Video received and queued for broadcast.")
            return True
        return False
    
    def send_broadcast_to_all_enhanced(self, user_id, chat_id):
        """Send broadcast (text / photo / video) with optional inline buttons to all verified users"""
        if user_id not in self.broadcast_sessions:
            self.robust_send_message(chat_id, "❌ No active broadcast session.")
            return False

        session = self.broadcast_sessions[user_id]

        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')
        users = cursor.fetchall()

        total_users = len(users)
        if total_users == 0:
            self.robust_send_message(chat_id, "❌ No verified users found.")
            del self.broadcast_sessions[user_id]
            return False

        self.robust_send_message(chat_id,
            f"📤 Starting broadcast to {total_users} users...")

        success_count = 0
        failed_count = 0
        start_time = time.time()

        has_photo  = bool(session.get('photo'))
        has_video  = bool(session.get('video'))
        buttons    = session.get('buttons', [])
        msg_text   = (f"📢 <b>Announcement from Admin</b>\n\n"
                      f"{session['message']}\n\n"
                      f"────────────────────\n"
                      f"<i>This is an automated broadcast</i>")

        # Build reply_markup if any buttons were added
        reply_markup = None
        if buttons:
            reply_markup = json.dumps({
                "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in buttons]
            })

        for i, (uid,) in enumerate(users):
            try:
                if has_photo:
                    payload = {
                        "chat_id": uid,
                        "photo": session['photo'],
                        "caption": msg_text,
                        "parse_mode": "HTML"
                    }
                    if reply_markup:
                        payload["reply_markup"] = reply_markup
                    r = _tg_session.post(self.base_url + "sendPhoto", data=payload, timeout=30)

                elif has_video:
                    payload = {
                        "chat_id": uid,
                        "video": session['video'],
                        "caption": msg_text,
                        "parse_mode": "HTML"
                    }
                    if reply_markup:
                        payload["reply_markup"] = reply_markup
                    r = _tg_session.post(self.base_url + "sendVideo", data=payload, timeout=60)

                else:
                    payload = {
                        "chat_id": uid,
                        "text": msg_text,
                        "parse_mode": "HTML"
                    }
                    if reply_markup:
                        payload["reply_markup"] = reply_markup
                    r = _tg_session.post(self.base_url + "sendMessage", data=payload, timeout=30)

                if r.status_code == 200 and r.json().get('ok'):
                    success_count += 1
                else:
                    failed_count += 1

                # Progress update every 20 users
                if (i + 1) % 20 == 0:
                    elapsed = time.time() - start_time
                    pct = int((i + 1) * 100 / total_users)
                    self.robust_send_message(chat_id,
                        f"📤 Progress: {i+1}/{total_users} ({pct}%)\n"
                        f"✅ {success_count} | ❌ {failed_count} | ⏱ {elapsed:.0f}s")

                time.sleep(0.05)  # ~20 msg/s — well under Telegram's 30/s limit

            except Exception as e:
                failed_count += 1
                print(f"❌ Broadcast error for {uid}: {e}")

        elapsed_total = time.time() - start_time
        media_type = "Video" if has_video else "Photo" if has_photo else "Text"
        btn_info = f" + {len(buttons)} button(s)" if buttons else ""

        stats = (
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"📊 {success_count}/{total_users} delivered\n"
            f"❌ {failed_count} failed\n"
            f"⏱ {elapsed_total:.1f}s | 📝 {media_type}{btn_info}"
        )

        broadcast_id = int(time.time())
        self.broadcast_stats[broadcast_id] = {
            'admin_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'total_users': total_users,
            'success_count': success_count,
            'failed_count': failed_count,
            'type': media_type.lower(),
            'buttons': len(buttons),
            'message_preview': session['message'][:100]
        }

        self.robust_send_message(chat_id, stats)
        del self.broadcast_sessions[user_id]
        return True

    # ==================== STARS PAYMENT METHODS ====================
    
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
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "⭐ 50 Stars ($0.50)", "callback_data": "stars_50"},
                    {"text": "⭐ 100 Stars ($1.00)", "callback_data": "stars_100"}
                ],
                [
                    {"text": "⭐ 500 Stars ($5.00)", "callback_data": "stars_500"},
                    {"text": "⭐ 1000 Stars ($10.00)", "callback_data": "stars_1000"}
                ],
                [
                    {"text": "💫 Custom Amount", "callback_data": "stars_custom"},
                    {"text": "📊 Stars Stats", "callback_data": "stars_stats"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }
        
        if message_id:
            self.edit_message(chat_id, message_id, stars_text, keyboard)
        else:
            self.robust_send_message(chat_id, stars_text, keyboard)
    
    def process_stars_donation(self, user_id, chat_id, stars_amount):
        """Process stars donation"""
        try:
            print(f"⭐ Processing stars donation: {stars_amount} stars for user {user_id}")
            
            success = self.stars_system.create_stars_invoice(
                user_id, chat_id, stars_amount, "Bot Stars Donation"
            )
            
            if success:
                return True
            else:
                self.robust_send_message(chat_id, "❌ Sorry, there was an error creating the Stars invoice. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Stars donation processing error: {e}")
            self.robust_send_message(chat_id, "❌ Sorry, there was an error processing your Stars donation. Please try again.")
            return False
    
    def show_stars_stats(self, user_id, chat_id, message_id):
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
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "⭐ Donate Stars", "callback_data": "stars_menu"}],
                [{"text": "🔄 Refresh Stats", "callback_data": "stars_stats"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, stats_text, keyboard)

    # ==================== GAME REQUEST METHODS ====================
    
    def show_game_request_menu(self, user_id, chat_id, message_id=None):
        """Show game request menu"""
        user_requests = self.game_request_system.get_user_requests(user_id, 3)
        
        request_text = """🎮 <b>Game Request System</b>

Can't find the game you're looking for? Request it here!

🌟 <b>How it works:</b>
1. Tell us the game name
2. Specify the platform (PSP, Android, etc.)
3. We'll notify our team
4. We'll try to add it to our collection

📝 <b>Your Recent Requests:</b>"""
        
        if user_requests:
            for req in user_requests:
                req_id, game_name, platform, status, created_at = req
                date_str = datetime.fromisoformat(created_at).strftime('%m/%d')
                status_icon = "✅" if status == 'completed' else "⏳" if status == 'pending' else "❌"
                request_text += f"\n• {game_name} ({platform}) - {status_icon} {status.title()} (ID: {req_id})"
        else:
            request_text += "\n• No requests yet"
        
        request_text += "\n\nClick below to submit a new game request!"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📝 Request New Game", "callback_data": "request_game"}],
                [{"text": "📋 My Requests", "callback_data": "my_requests"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        if message_id:
            self.edit_message(chat_id, message_id, request_text, keyboard)
        else:
            self.robust_send_message(chat_id, request_text, keyboard)
    
    def start_game_request(self, user_id, chat_id):
        """Start game request process"""
        self.robust_send_message(chat_id,
            "🎮 <b>Game Request</b>\n\n"
            "Please tell us the name of the game you'd like to request:\n\n"
            "💡 <i>Example: 'God of War: Chains of Olympus'</i>"
        )
        self.request_sessions[user_id] = {'stage': 'waiting_game_name'}
        return True
    
    def handle_game_request(self, user_id, chat_id, game_name):
        """Handle game name input and ask for platform"""
        try:
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
            
            request_id = self.game_request_system.submit_game_request(user_id, game_name, platform)
            
            if request_id:
                del self.request_sessions[user_id]
                
                confirm_text = f"""✅ <b>Game Request Submitted!</b>

🎮 Game: <b>{game_name}</b>
📱 Platform: <b>{platform}</b>
👤 Requested by: {self.get_user_info(user_id).get('first_name', 'User')}
🆔 Request ID: {request_id}
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for your request! We'll review it and notify you if we add the game to our collection.

📊 You can check your request status in 'My Requests'."""
                
                self.robust_send_message(chat_id, confirm_text)
                return True
            else:
                self.robust_send_message(chat_id, "❌ Sorry, there was an error submitting your request. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Game request completion error: {e}")
            return False
    
    def show_user_requests(self, user_id, chat_id, message_id):
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
                
                replies = self.game_request_system.get_request_replies(req_id)
                if replies:
                    requests_text += f"\n💬 {len(replies)} admin replies"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📝 Request New Game", "callback_data": "request_game"}],
                [{"text": "🔄 Refresh", "callback_data": "my_requests"}],
                [{"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, requests_text, keyboard)

    # ==================== ADMIN GAME REQUEST MANAGEMENT ====================
    
    def show_admin_requests_panel(self, user_id, chat_id, message_id):
        """Show admin game requests management panel"""
        if not self.is_admin(user_id):
            self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_admin_buttons())
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
                requests_text += f"\n└─ <code>/reply_{req_id}</code>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📝 Manage Requests", "callback_data": "manage_requests"}],
                [{"text": "🔄 Refresh", "callback_data": "admin_requests_panel"}],
                [{"text": "🔙 Back to Admin", "callback_data": "admin_panel"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, requests_text, keyboard)

    # ==================== BROADCAST MESSAGING SYSTEM ====================
    
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
            
            text_broadcasts = sum(1 for stats in self.broadcast_stats.values() if stats.get('type') == 'text')
            photo_broadcasts = sum(1 for stats in self.broadcast_stats.values() if stats.get('type') == 'photo')
            
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

    # ==================== CRASH PROTECTION METHODS ====================
    
    def handle_error(self, error, context="general"):
        """Comprehensive error handling with auto-recovery"""
        self.error_count += 1
        self.consecutive_errors += 1
        current_time = time.time()
        
        if current_time - self.last_restart > self.error_window:
            self.error_count = 1
            self.consecutive_errors = 1
            self.last_restart = current_time
        
        print(f"❌ Error in {context}: {str(error)[:100]}...")
        print(f"📊 Error stats: {self.error_count}/{self.max_errors} total, {self.consecutive_errors}/{self.max_consecutive_errors} consecutive")
        
        if (self.error_count >= self.max_errors or 
            self.consecutive_errors >= self.max_consecutive_errors):
            print("🔄 Too many errors, initiating auto-restart...")
            self.auto_restart()
        
        return False

    def auto_restart(self):
        """Auto-restart the bot safely"""
        print("🚀 Initiating auto-restart...")
        try:
            if hasattr(self, 'conn'):
                try:
                    self.conn.close()
                except Exception:
                    pass
            
            if self.keep_alive:
                self.keep_alive.stop()
            
            self.error_count = 0
            self.consecutive_errors = 0
            self.last_restart = time.time()
            
            self.setup_database()
            self.verify_database_schema()
            self.update_games_cache()
            
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
                
                response = _tg_session.post(url, data=data, timeout=15)
                result = response.json()
                
                if result.get('ok'):
                    if self.consecutive_errors > 0:
                        self.consecutive_errors = 0
                    return True
                else:
                    error_msg = result.get('description', 'Unknown error')
                    print(f"❌ Telegram API error (attempt {attempt + 1}): {error_msg}")
                    
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
        """Ensure database has correct schema — run migrations for any missing columns"""
        try:
            cursor = self.conn.cursor()

            # channel_games migrations
            cursor.execute("PRAGMA table_info(channel_games)")
            cg_cols = [c[1] for c in cursor.fetchall()]
            if 'bot_message_id' not in cg_cols:
                cursor.execute('ALTER TABLE channel_games ADD COLUMN bot_message_id INTEGER')
                print("✅ Added bot_message_id to channel_games")

            # premium_games migrations
            cursor.execute("PRAGMA table_info(premium_games)")
            pg_cols = [c[1] for c in cursor.fetchall()]
            if 'tokens_price' not in pg_cols:
                cursor.execute('ALTER TABLE premium_games ADD COLUMN tokens_price INTEGER DEFAULT 10')
                print("✅ Added tokens_price to premium_games")
            # Sync tokens_price = stars_price for all games where they differ
            cursor.execute(
                'UPDATE premium_games SET tokens_price = stars_price WHERE tokens_price IS NULL OR tokens_price = 0'
            )

            # users migrations (also done by ReferralSystem but guard here too)
            cursor.execute("PRAGMA table_info(users)")
            u_cols = [c[1] for c in cursor.fetchall()]
            for col, default in [('game_tokens', '0'), ('total_referrals', '0'), ('referred_by', '0'), ('pending_referrer_id', '0')]:
                if col not in u_cols:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT {default}')
                    print(f"✅ Added {col} to users")

            # admin_codes tables — create if missing (safe for existing DBs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_codes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    code        TEXT UNIQUE NOT NULL,
                    created_by  INTEGER NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at  DATETIME NOT NULL,
                    max_uses    INTEGER DEFAULT 1,
                    used_count  INTEGER DEFAULT 0,
                    is_active   INTEGER DEFAULT 1,
                    token_reward INTEGER DEFAULT 5,
                    description TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_code_uses (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    code_id    INTEGER NOT NULL,
                    user_id    INTEGER NOT NULL,
                    used_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code_id, user_id),
                    FOREIGN KEY (code_id) REFERENCES admin_codes(id)
                )
            ''')

            self.conn.commit()
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
        
        if user_id in self.spin_games:
            last_spin = self.spin_games[user_id].get('last_spin', 0)
            if now - last_spin < 3:
                wait_time = 3 - (now - last_spin)
                self.robust_send_message(chat_id, f"⏳ Please wait {wait_time:.1f} seconds before spinning again!")
                return True
        
        symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
        spins = [random.choice(symbols) for _ in range(3)]
        
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
        
        if user_id not in self.spin_games:
            self.spin_games[user_id] = {'spins': 0, 'total_wins': 0}
        
        self.spin_games[user_id]['spins'] += 1
        self.spin_games[user_id]['total_wins'] += win_amount
        self.spin_games[user_id]['last_spin'] = now
        
        stats = self.spin_games[user_id]
        
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
        
        if user_id not in self.spin_games:
            self.spin_games[user_id] = {'spins': 0, 'total_wins': 0}
        
        self.spin_games[user_id]['spins'] += 3
        self.spin_games[user_id]['total_wins'] += total_win
        self.spin_games[user_id]['last_spin'] = time.time()
        
        stats = self.spin_games[user_id]
        
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

    # ==================== IMPROVED ADMIN GAME MANAGEMENT ====================
    
    def scan_bot_uploaded_games(self):
        """
        NOTE: This method previously called getUpdates, which would consume
        messages from the bot's polling queue and cause missed updates.
        It now only counts games already stored in the database that were
        uploaded by admins (is_uploaded=1). To pick up new uploads, admins
        should send files directly to the bot — they are stored automatically.
        """
        try:
            print("🔍 Counting bot-uploaded games from database...")
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1
            ''')
            bot_games_count = cursor.fetchone()[0]
            print(f"✅ Found {bot_games_count} bot-uploaded games in database")
            return bot_games_count
        except Exception as e:
            print(f"❌ Bot games scan error: {e}")
            return 0

    # ==================== SEARCH GAMES METHODS ====================
    
    def search_games(self, search_term, user_id):
        search_term = search_term.lower().strip()
        results = []

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT message_id, file_name, file_type, file_size, upload_date, category, file_id, 
                   bot_message_id, is_uploaded, is_forwarded
            FROM channel_games 
            WHERE LOWER(file_name) LIKE ?
        ''', (f'%{search_term}%',))

        all_games = cursor.fetchall()

        for game in all_games:
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
    
    def create_search_results_buttons(self, results, search_term, user_id, page=0):
        results_per_page = 5
        start_idx = page * results_per_page
        end_idx = start_idx + results_per_page
        page_results = results[start_idx:end_idx]
        
        keyboard = []
        
        for i, game in enumerate(page_results, start_idx + 1):
            button_text = game['file_name']
            if len(button_text) > 30:
                button_text = button_text[:27] + "..."
            
            if game['is_uploaded'] == 1 and game['bot_message_id']:
                message_id_to_send = game['bot_message_id']
                is_bot_file = True
            else:
                message_id_to_send = game['message_id']
                is_bot_file = False
            
            file_id_clean = str(game['file_id']).replace('-', '_').replace('=', 'eq')
            callback_data = f"send_game_{message_id_to_send}_{file_id_clean}_{1 if is_bot_file else 0}"
            
            if len(callback_data) > 64:
                callback_data = f"send_game_{message_id_to_send}_short_{1 if is_bot_file else 0}"
            
            keyboard.append([{
                "text": f"📁 {i}. {button_text}",
                "callback_data": callback_data
            }])
        
        pagination_buttons = []
        if page > 0:
            pagination_buttons.append({
                "text": "⬅️ Previous",
                "callback_data": f"search_page_{search_term}_{page-1}"
            })
        
        if end_idx < len(results):
            pagination_buttons.append({
                "text": "Next ➡️",
                "callback_data": f"search_page_{search_term}_{page+1}"
            })
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
        
        keyboard.append([
            {"text": "🔍 New Search", "callback_data": "search_games"},
            {"text": "📁 Browse All", "callback_data": "game_files"}
        ])
        
        keyboard.append([
            {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
        ])
        
        return {"inline_keyboard": keyboard}
    
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
                        
                        for i, game in enumerate(results[:5], 1):
                            size = self.format_file_size(game['file_size'])
                            source = "🤖 Bot" if game['is_uploaded'] == 1 else "📢 Channel"
                            results_text += f"{i}. <code>{game['file_name']}</code>\n"
                            results_text += f"   📦 {game['file_type']} | 📏 {size} | 🗂️ {game['category']} | {source}\n\n"
                        
                        if len(results) > 5:
                            results_text += f"📋 ... and {len(results) - 5} more files\n\n"
                        
                        results_text += "🔗 Click any file above to download it instantly!"
                        
                        buttons = self.create_search_results_buttons(results, search_term, user_id)
                        print(f"🔍 Sending search results with {len(results)} games")
                        
                        self.robust_send_message(
                            chat_id, 
                            results_text, 
                            buttons
                        )
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
        elif filename_lower.endswith('.xapk'):
            return 'Android Games'
        elif filename_lower.endswith('.apks'):
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
        except Exception:
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
        except Exception:
            return 0

    # ==================== DATABASE & SETUP METHODS ====================
    
    def setup_database(self):
        try:
            db_path = self.get_db_path()
            print(f"📁 Database path: {db_path}")
            
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")   # non-blocking concurrent reads
            self.conn.execute("PRAGMA synchronous=NORMAL") # faster writes, safe with WAL
            self.conn.execute("PRAGMA cache_size=-8000")   # 8 MB page cache
            self.conn.execute("PRAGMA temp_store=MEMORY")
            self.conn.row_factory = None
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
                    game_tokens INTEGER DEFAULT 0,
                    total_referrals INTEGER DEFAULT 0,
                    referred_by INTEGER DEFAULT 0,
                    pending_referrer_id INTEGER DEFAULT 0
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
                    stars_paid INTEGER,
                    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_codes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    code        TEXT UNIQUE NOT NULL,
                    created_by  INTEGER NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at  DATETIME NOT NULL,
                    max_uses    INTEGER DEFAULT 1,
                    used_count  INTEGER DEFAULT 0,
                    is_active   INTEGER DEFAULT 1,
                    token_reward INTEGER DEFAULT 5,
                    description TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_code_uses (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    code_id    INTEGER NOT NULL,
                    user_id    INTEGER NOT NULL,
                    used_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code_id, user_id),
                    FOREIGN KEY (code_id) REFERENCES admin_codes(id)
                )
            ''')

            cursor.execute('INSERT OR IGNORE INTO stars_balance (id) VALUES (1)')

            self.conn.commit()
            print("✅ Database setup successful!")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("⚠️ Falling back to in-memory database")
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            # Re-run schema creation on the in-memory connection directly (no recursion)
            try:
                cursor = self.conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, is_verified INTEGER DEFAULT 0, joined_channel INTEGER DEFAULT 0, verification_code TEXT, code_expires DATETIME, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS channel_games (id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER UNIQUE, file_name TEXT, file_type TEXT, file_size INTEGER, upload_date DATETIME, category TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, added_by INTEGER DEFAULT 0, is_uploaded INTEGER DEFAULT 0, is_forwarded INTEGER DEFAULT 0, file_id TEXT, bot_message_id INTEGER)''')
                self.conn.commit()
                print("✅ In-memory database schema created")
            except Exception as inner_e:
                print(f"❌ In-memory database setup failed: {inner_e}")
    
    def test_bot_connection(self):
        try:
            url = self.base_url + "getMe"
            response = _tg_session.get(url, timeout=10)
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
        """Enhanced scan that includes channel games (using forwarded messages method)"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        try:
            print(f"🔍 Scanning for games in forwarded messages...")
            
            bot_games_found = self.scan_bot_uploaded_games()
            
            self.update_games_cache()
            
            total_games = bot_games_found
            print(f"🔄 Rescan complete! Found {total_games} total games from bot uploads")
            
            self.is_scanning = False
            return total_games
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            self.is_scanning = False
            return 0
    
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
                'zip': [], '7z': [], 'iso': [], 'apk': [], 'xapk': [], 'apks': [],
                'rar': [], 'pkg': [], 'cso': [], 'pbp': [], 'recent': [], 'all': []
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
        except Exception:
            return {'total_games': 0, 'premium_games': 0}
    
    def generate_code(self):
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def save_verification_code(self, user_id, username, first_name, code):
        """
        Save a new verification code for the user.
        Uses INSERT OR IGNORE so existing rows are never reset, then
        updates only the code-related columns.
        Verified users are never touched — the code is simply not saved for them.
        """
        try:
            # Guard: never overwrite a fully-completed user
            if self.is_user_completed(user_id):
                print(f"ℹ️ Skipping code save for already-verified user {user_id}")
                return True

            expires = datetime.now() + timedelta(minutes=10)
            cursor = self.conn.cursor()

            # Ensure the row exists without overwriting any existing columns
            cursor.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                (user_id, username, first_name)
            )

            # Only update the code-specific fields — never touch is_verified,
            # joined_channel, game_tokens, referred_by, pending_referrer_id
            cursor.execute(
                '''UPDATE users
                   SET username = ?,
                       first_name = ?,
                       verification_code = ?,
                       code_expires = ?
                   WHERE user_id = ?''',
                (username, first_name, code, expires, user_id)
            )
            self.conn.commit()
            print(f"✅ Verification code saved for user {user_id}: {code}")
            return True
        except Exception as e:
            print(f"❌ Error saving code: {e}")
            return False
    
    def verify_code(self, user_id, code):
        """
        Returns True on success, 'expired' if code timed out, False if wrong/missing.
        Also sets is_verified=1 on success.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT verification_code, code_expires FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                print(f"❌ No verification code found for user {user_id}")
                return False
                
            stored_code, expires_str = result

            try:
                expires = datetime.fromisoformat(expires_str)
            except (TypeError, ValueError):
                return False

            if datetime.now() > expires:
                print(f"❌ Verification code expired for user {user_id}")
                return 'expired'
                
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
            response = _tg_session.post(url, data=data, timeout=10)
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
    
    def send_message(self, chat_id, text, reply_markup=None):
        return self.robust_send_message(chat_id, text, reply_markup)
    
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
            
            response = _tg_session.post(url, data=data, timeout=15)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"Edit message error: {e}")
            return False
    
    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        try:
            url = self.base_url + "answerCallbackQuery"
            data = {"callback_query_id": callback_query_id}
            if text:
                data["text"] = text
            if show_alert:
                data["show_alert"] = True
            _tg_session.post(url, data=data, timeout=5)
        except Exception as e:
            print(f"⚠️ answer_callback_query error: {e}")
    
    def get_updates(self, offset=None):
        try:
            url = self.base_url + "getUpdates"
            params = {"timeout": 100, "offset": offset}
            response = _tg_session.get(url, params=params, timeout=110)
            data = response.json()
            return data.get('result', []) if data.get('ok') else []
        except Exception as e:
            print(f"Get updates error: {e}")
            return []

    def handle_upload_stats(self, chat_id, message_id, user_id, first_name):
        total_uploads = self.get_upload_stats()
        user_uploads = self.get_upload_stats(user_id)
        total_forwards = self.get_forward_stats()
        user_forwards = self.get_forward_stats(user_id)
        total_games = len(self.games_cache.get('all', []))
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM premium_games')
        premium_games = cursor.fetchone()[0]
        
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

        self.edit_message(chat_id, message_id, stats_text, self.create_admin_buttons())

    def handle_search_games(self, chat_id, message_id, user_id, first_name):
        self.update_games_cache()
        self.search_mode[user_id] = True   # next free-text from this user = search query
        
        search_info = f"""🔍 Game Search

👋 Hello {first_name}!

Search for any game in our database:

📝 How to Search:
1. Simply type the game name
2. The bot will search through {len(self.games_cache.get('all', []))} files
3. Get instant results with download links

💡 Search Tips:
• Use specific game names
• Try different keywords
• Search is case-insensitive

🎮 Example searches:
• "GTA"
• "God of War" 
• "FIFA 2024"
• "Minecraft"

Type your game name now!"""

        self.edit_message(chat_id, message_id, search_info, self.create_search_buttons())

    def format_games_list(self, games, category):
        if not games:
            return f"❌ No {category.upper()} games found."
        
        text = f"📁 <b>{category.upper()} GAMES</b>\n\n"
        text += f"📊 Found: {len(games)} files\n\n"
        
        for i, game in enumerate(games[:8], 1):
            size = self.format_file_size(game['file_size'])
            text += f"{i}. <code>{game['file_name']}</code>\n"
            text += f"   📦 {game['file_type']} | 📏 {size} | 🗂️ {game.get('category', 'Unknown')}\n\n"
        
        text += f"🔗 Visit: {self.REQUIRED_CHANNEL}"
        return text

    def handle_profile(self, chat_id, message_id, user_id, first_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT created_at, is_verified, joined_channel, game_tokens, total_referrals, referred_by FROM users WHERE user_id = ?',
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                created_at, is_verified, joined_channel, tokens, referrals, referred_by = result
                ref_link = self.referral.get_referral_link(user_id)
                profile_text = (
                    f"👤 <b>User Profile</b>\n\n"
                    f"🆔 User ID: <code>{user_id}</code>\n"
                    f"👋 Name: {html.escape(first_name)}\n"
                    f"✅ Verified: {'Yes' if is_verified else 'No'}\n"
                    f"📢 Channel Joined: {'Yes' if joined_channel else 'No'}\n"
                    f"📅 Member Since: {created_at}\n\n"
                    f"💎 Game Tokens: <b>{tokens or 0}</b>\n"
                    f"👥 Referrals: <b>{referrals or 0}</b>\n\n"
                    f"🔗 Your Referral Link:\n"
                    f"<code>{ref_link}</code>"
                )
            else:
                profile_text = (
                    f"👤 <b>User Profile</b>\n\n"
                    f"🆔 User ID: <code>{user_id}</code>\n"
                    f"👋 Name: {html.escape(first_name)}\n"
                    f"✅ Verified: No\n\n"
                    f"Complete verification with /start"
                )

            self.edit_message(chat_id, message_id, profile_text, self.create_main_menu_buttons(user_id))

        except Exception as e:
            print(f"Profile error: {e}")

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

    # ==================== UPDATED MESSAGE PROCESSOR ====================

    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'forward_origin' in message:
                print(f"🔄 Forwarded message received from user {message['from']['id']}")
                user_id = message['from']['id']
                chat_id = message['chat']['id']

                if self.is_admin(user_id) and user_id in self.broadcast_sessions:
                    session = self.broadcast_sessions[user_id]
                    if session['stage'] == 'waiting_message_or_media':
                        if 'photo' in message:
                            photo = message['photo'][-1]
                            caption = message.get('caption', '')
                            return self.handle_broadcast_photo(user_id, chat_id, photo['file_id'], caption)
                        elif 'text' in message:
                            text = message['text']
                            return self.handle_broadcast_message(user_id, chat_id, text)

                if 'document' in message and self.is_admin(user_id):
                    return self.handle_document_upload(message)

                return True
            
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                if text.startswith('/reply_') and self.is_admin(user_id):
                    try:
                        request_id = int(text.replace('/reply_', ''))
                        return self.start_request_reply(user_id, chat_id, request_id)
                    except ValueError:
                        pass

                if text.isdigit() and len(text) == 6:
                    # handle_code_verification tries admin codes first, then verification code
                    return self.handle_code_verification(message)
                
                if user_id in self.upload_sessions:
                    session = self.upload_sessions[user_id]
                    
                    if session['stage'] == 'waiting_stars_price':
                        return self.handle_stars_price(user_id, chat_id, text)
                    elif session['stage'] == 'waiting_description':
                        return self.handle_premium_description(user_id, chat_id, text)
                
                if user_id in self.request_sessions:
                    session = self.request_sessions[user_id]
                    
                    if session['stage'] == 'waiting_game_name':
                        return self.handle_game_request(user_id, chat_id, text)
                    elif session['stage'] == 'waiting_platform':
                        return self.complete_game_request(user_id, chat_id, text)
                
                if user_id in self.reply_sessions:
                    session = self.reply_sessions[user_id]
                    
                    if session['stage'] == 'waiting_reply':
                        return self.handle_request_reply(user_id, chat_id, text)
                
                if user_id in self.stars_sessions:
                    try:
                        stars_amount = int(text.strip())
                        if stars_amount <= 0:
                            self.robust_send_message(chat_id, "❌ Please enter a positive number of Stars.")
                            return True
                        
                        del self.stars_sessions[user_id]
                        return self.process_stars_donation(user_id, chat_id, stars_amount)
                    except ValueError:
                        self.robust_send_message(chat_id, "❌ Please enter a valid number for the Stars amount.")
                        return True
                
                if user_id in self.broadcast_sessions:
                    return self.handle_broadcast_message(user_id, chat_id, text)

                # Admin code creation — waiting for description
                if user_id in self.code_sessions:
                    session = self.code_sessions[user_id]
                    if session.get('stage') == 'waiting_description':
                        description = '' if text.strip().lower() == 'skip' else text.strip()
                        days         = session.get('days')
                        max_uses     = session.get('max_uses', 1)
                        token_reward = session.get('token_reward', 5)
                        try:
                            code = self.admin_codes.create_code(
                                user_id, days, max_uses, description, token_reward
                            )
                            del self.code_sessions[user_id]
                            dur_str  = "No expiry" if days is None else f"{days} day(s)"
                            uses_str = "Unlimited" if max_uses == 0 else str(max_uses)
                            self.robust_send_message(
                                chat_id,
                                f"✅ <b>Code Created!</b>\n\n"
                                f"🔑 Code: <code>{code}</code>\n"
                                f"⏳ Duration: {dur_str}\n"
                                f"👥 Max uses: {uses_str}\n"
                                f"🪙 Token reward: {token_reward}\n"
                                f"📝 Description: {description or 'none'}\n\n"
                                f"Share this code — each user can only use it once.",
                                self.create_admin_buttons()
                            )
                        except Exception as e:
                            self.robust_send_message(chat_id, f"❌ Failed to create code: {e}")
                        return True
                
                # Search mode: user typed after pressing Search Games
                if self.search_mode.get(user_id) and not text.startswith('/'):
                    del self.search_mode[user_id]
                    return self.handle_game_search(message)
                
                if user_id in self.guess_games:
                    if text.strip().isdigit():
                        return self.handle_guess_input(user_id, chat_id, text)
                
                if text.startswith('/'):
                    if text == '/start' or text.startswith('/start '):
                        return self.handle_verification(message)
                    elif text == '/scan' and self.is_admin(user_id):
                        self.robust_send_message(chat_id, "🔄 Scanning for bot-uploaded games...")
                        total_games = self.scan_channel_for_games()
                        self.robust_send_message(chat_id, f"✅ Scan complete! Found {total_games} total games.")
                        return True
                    elif text == '/menu' and self.is_user_completed(user_id):
                        if self.is_admin(user_id):
                            admin_text = f"👑 Admin Menu\n\nWelcome {first_name}!\n\nYou have admin privileges."
                            self.robust_send_message(chat_id, admin_text, self.create_admin_buttons())
                        else:
                            self.robust_send_message(chat_id, f"🏠 Main Menu\n\nWelcome {first_name}!", self.create_main_menu_buttons(user_id))
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
                    elif text == '/stars' and self.is_user_completed(user_id):
                        self.show_stars_menu(user_id, chat_id)
                        return True
                    elif text == '/premium' and self.is_user_completed(user_id):
                        self.show_premium_games_menu(user_id, chat_id)
                        return True
                    elif text == '/request' and self.is_user_completed(user_id):
                        return self.start_game_request(user_id, chat_id)
                    elif text == '/broadcast' and self.is_admin(user_id):
                        return self.start_broadcast_with_photo(user_id, chat_id)
                    elif text == '/cleargames' and self.is_admin(user_id):
                        self.clear_all_games(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/removegames' and self.is_admin(user_id):
                        self.show_remove_game_menu(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/upload' and self.is_admin(user_id):
                        self.show_upload_options(user_id, chat_id, message['message_id'])
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
                        self.show_stars_stats(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/requests' and self.is_admin(user_id):
                        self.show_request_management(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/redeploy' and self.is_admin(user_id):
                        self.redeploy_system.show_redeploy_menu(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/status' and self.is_admin(user_id):
                        self.redeploy_system.show_system_status(user_id, chat_id, message['message_id'])
                        return True
                    elif text == '/backup' and self.is_admin(user_id):
                        self.show_backup_menu(user_id, chat_id, message['message_id'])
                        return True
                
                if self.is_user_verified(user_id):
                    return self.handle_game_search(message)
            
            if 'photo' in message:
                print(f"📸 Photo message received from user {message['from']['id']}")
                user_id = message['from']['id']
                chat_id = message['chat']['id']

                if user_id in self.broadcast_sessions:
                    if self.broadcast_sessions[user_id]['stage'] == 'waiting_message_or_media':
                        photo = message['photo'][-1]
                        caption = message.get('caption', '')
                        return self.handle_broadcast_photo(user_id, chat_id, photo['file_id'], caption)

                if user_id in self.reply_sessions and self.reply_sessions[user_id]['stage'] == 'waiting_photo':
                    photo = message['photo'][-1]
                    caption = message.get('caption', '')
                    return self.handle_photo_reply(user_id, chat_id, photo['file_id'], caption)

            if 'video' in message:
                print(f"🎥 Video message received from user {message['from']['id']}")
                user_id = message['from']['id']
                chat_id = message['chat']['id']

                if user_id in self.broadcast_sessions:
                    if self.broadcast_sessions[user_id]['stage'] == 'waiting_message_or_media':
                        video_file_id = message['video']['file_id']
                        caption = message.get('caption', '')
                        return self.handle_broadcast_video(user_id, chat_id, video_file_id, caption)
            
            if 'document' in message and self.is_admin(message['from']['id']):
                return self.handle_document_upload(message)
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            traceback.print_exc()
            return False

    def handle_verification(self, message):
        """
        Handle /start command.
        - Fully verified users go straight to the main menu (no re-verification).
        - Referral link (?start=ref_ID) stores pending referrer — credited after full verification.
        - Verification is one-time: completed users are never asked to re-verify.
        """
        try:
            user_id    = message['from']['id']
            chat_id    = message['chat']['id']
            username   = message['from'].get('username', '')
            first_name = message['from']['first_name']
            text       = message.get('text', '/start').strip()

            print(f"🔐 /start from {first_name} ({user_id}): '{text}'")

            # ── Parse referral parameter ──────────────────────────────────────
            referrer_id = None
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith('ref_'):
                try:
                    rid = int(parts[1].replace('ref_', ''))
                    if rid != user_id:
                        referrer_id = rid
                except ValueError:
                    pass

            # ── Upsert user row (INSERT OR IGNORE keeps existing data) ────────
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                (user_id, username, first_name)
            )
            cursor.execute(
                'UPDATE users SET username = ?, first_name = ? WHERE user_id = ?',
                (username, first_name, user_id)
            )
            self.conn.commit()

            # Store pending referral — no token yet, awarded after full verification
            if referrer_id:
                self.referral.store_pending_referral(referrer_id, user_id)

            # ── Fully verified — go straight to menu ──────────────────────────
            if self.is_user_completed(user_id):
                self.robust_send_message(
                    chat_id,
                    f"👋 <b>Welcome back {first_name}!</b>\n\n"
                    f"✅ You're already verified — choose an option below:",
                    self.create_main_menu_buttons(user_id)
                )
                return True

            # ── Code verified, channel not yet joined ─────────────────────────
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                self.robust_send_message(
                    chat_id,
                    f"📢 <b>One Last Step!</b>\n\n"
                    f"👋 Hello {first_name}!\n\n"
                    f"✅ Code verification: Complete\n"
                    f"❌ Channel membership: Pending\n\n"
                    f"Join our channel to unlock everything:\n"
                    f"🔗 {self.CHANNEL_LINK}\n\n"
                    f"After joining tap <b>Verify Join</b> below:",
                    self.create_channel_buttons()
                )
                return True

            # ── In channel but code not yet verified ──────────────────────────
            if self.check_channel_membership(user_id) and not self.is_user_verified(user_id):
                self.mark_channel_joined(user_id)
                code = self.generate_code()
                if self.save_verification_code(user_id, username, first_name, code):
                    self.robust_send_message(
                        chat_id,
                        f"🔐 <b>Almost done, {first_name}!</b>\n\n"
                        f"✅ Channel membership: Verified\n"
                        f"❌ Code verification: Pending\n\n"
                        f"Your verification code:\n"
                        f"<code>{code}</code>\n\n"
                        f"Reply with this code.  ⏰ Expires in 10 minutes."
                    )
                else:
                    self.robust_send_message(chat_id, "❌ Error generating code. Please try /start again.")
                return True

            # ── Fresh user — issue verification code ──────────────────────────
            code = self.generate_code()
            if self.save_verification_code(user_id, username, first_name, code):
                referral_note = (
                    "\n\n🎁 <b>You joined via a referral!</b> Complete verification to activate."
                    if referrer_id else ""
                )
                self.robust_send_message(
                    chat_id,
                    f"🔐 <b>Welcome to {BOT_SERVICE_NAME}!</b>\n\n"
                    f"👋 Hello {first_name}!\n\n"
                    f"Two quick steps to access our game collection:\n\n"
                    f"📝 <b>Step 1 — Enter this code:</b>\n"
                    f"<code>{code}</code>\n\n"
                    f"Reply with the code above.\n"
                    f"⏰ Expires in 10 minutes.\n\n"
                    f"You'll join our channel in Step 2.{referral_note}"
                )
            else:
                self.robust_send_message(chat_id, "❌ Error generating code. Please try /start again.")
            return True

        except Exception as e:
            print(f"❌ handle_verification error: {e}")
            traceback.print_exc()
            try:
                self.robust_send_message(message['chat']['id'], "❌ Error. Please try /start again.")
            except Exception:
                pass
            return False

    def handle_code_verification(self, message):
        """
        Handle 6-digit input.
        1. Try admin code redemption first (separate system, works for all users).
        2. If not an admin code, treat as a verification code.
        Awards referral token when user fully completes verification.
        """
        try:
            user_id    = message['from']['id']
            chat_id    = message['chat']['id']
            text       = message.get('text', '').strip()
            first_name = message['from']['first_name']

            if not text.isdigit() or len(text) != 6:
                return False

            print(f"🔐 6-digit input from {first_name} ({user_id}): {text}")

            # ── Try admin code redemption FIRST ──────────────────────────────
            ok, msg, tokens_awarded = self.admin_codes.redeem(text, user_id)
            if ok:
                total = self.referral.get_tokens(user_id)
                self.robust_send_message(
                    chat_id,
                    f"🎉 <b>Code Redeemed!</b>\n\n{msg}\n\n"
                    f"💎 Your token balance: <b>{total}</b>"
                )
                return True

            # ── Fall through to verification code ────────────────────────────
            result = self.verify_code(user_id, text)

            if result == 'expired':
                self.robust_send_message(
                    chat_id,
                    "❌ Code expired. Click /start to get a new code and try again."
                )
                return True

            if result is False:
                # Could be wrong verification code or not a valid admin code either.
                # Only show verification error if the user is mid-verification.
                cursor = self.conn.cursor()
                cursor.execute(
                    'SELECT verification_code FROM users WHERE user_id = ?', (user_id,)
                )
                row = cursor.fetchone()
                if row and row[0]:
                    self.robust_send_message(chat_id, "❌ Invalid or redeemed code.")
                else:
                    self.robust_send_message(chat_id, "❌ Invalid or redeemed code.")
                return True

            # ── result is True — code accepted ───────────────────────────────
            in_channel = self.check_channel_membership(user_id)
            if in_channel:
                self.mark_channel_joined(user_id)
                # Credit referrer now that user is fully verified
                self.referral.complete_referral(user_id)
                self.robust_send_message(
                    chat_id,
                    f"✅ <b>Verification Complete!</b>\n\n"
                    f"👋 Welcome {first_name}!\n\n"
                    f"🎉 You now have full access:\n"
                    f"• 🎮 Game File Browser\n"
                    f"• 💰 Premium Games\n"
                    f"• 🔍 Game Search\n"
                    f"• 🎮 Mini-Games\n"
                    f"• ⭐ Stars Donations\n"
                    f"• 📝 Game Requests\n\n"
                    f"📢 Channel: {self.REQUIRED_CHANNEL}",
                    self.create_main_menu_buttons(user_id)
                )
            else:
                self.robust_send_message(
                    chat_id,
                    f"✅ <b>Code Verified!</b>\n\n"
                    f"👋 Hello {first_name}!\n\n"
                    f"✅ Code verification: Completed\n"
                    f"❌ Channel membership: Pending\n\n"
                    f"📝 <b>Step 2 — Join our channel:</b>\n"
                    f"🔗 {self.CHANNEL_LINK}\n\n"
                    f"Tap <b>Verify Join</b> after joining:",
                    self.create_channel_buttons()
                )
            return True

        except Exception as e:
            print(f"❌ Code verification error: {e}")
            traceback.print_exc()
            return False

    # ==================== STARS PAYMENT WEBHOOKS ====================

    def handle_pre_checkout_query(self, pre_checkout_query):
        """Answer pre-checkout query — must be answered within 10 seconds"""
        try:
            query_id = pre_checkout_query['id']
            url = self.base_url + "answerPreCheckoutQuery"
            data = {"pre_checkout_query_id": query_id, "ok": True}
            response = _tg_session.post(url, data=data, timeout=8)
            result = response.json()
            if result.get('ok'):
                print(f"✅ Pre-checkout approved: {query_id}")
            else:
                print(f"❌ Pre-checkout answer failed: {result.get('description')}")
        except Exception as e:
            print(f"❌ handle_pre_checkout_query error: {e}")

    def handle_successful_payment(self, message):
        """Handle successful Telegram Stars payment"""
        try:
            user_id  = message['from']['id']
            chat_id  = message['chat']['id']
            payment  = message['successful_payment']
            payload  = payment.get('invoice_payload', '')
            stars    = payment.get('total_amount', 0)

            print(f"💰 Successful payment: {stars} Stars from {user_id} | payload={payload}")

            # Premium game purchase
            if payload.startswith('premium_game_'):
                parts = payload.split('_')
                # format: premium_game_GAMEID_USERID_TIMESTAMP
                if len(parts) >= 4:
                    try:
                        game_id = int(parts[2])
                    except (ValueError, IndexError):
                        game_id = None

                    if game_id:
                        # Mark purchase completed
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            UPDATE premium_purchases
                            SET status = 'completed'
                            WHERE transaction_id = ? AND user_id = ?
                        ''', (payload, user_id))
                        if cursor.rowcount == 0:
                            # Insert if no pending row exists
                            cursor.execute('''
                                INSERT OR IGNORE INTO premium_purchases
                                (user_id, game_id, stars_paid, transaction_id, status)
                                VALUES (?, ?, ?, ?, 'completed')
                            ''', (user_id, game_id, stars, payload))
                        self.conn.commit()

                        # Update stars balance
                        self.stars_system.complete_premium_purchase(payload)

                        # Deliver the game
                        self.robust_send_message(chat_id,
                            f"✅ <b>Payment Successful!</b>\n\n"
                            f"⭐ Stars paid: <b>{stars}</b>\n"
                            f"🎮 Your game is being sent now...")
                        self.send_premium_game_file(user_id, chat_id, game_id)
                        return

            # Generic stars donation
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE stars_transactions
                SET payment_status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            ''', (payload,))
            self.conn.commit()

            cursor.execute('''
                UPDATE stars_balance
                SET total_stars_earned = total_stars_earned + ?,
                    total_usd_earned   = total_usd_earned   + ?,
                    available_stars    = available_stars    + ?,
                    available_usd      = available_usd      + ?,
                    last_updated       = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (stars, stars * 0.01, stars, stars * 0.01))
            self.conn.commit()

            self.robust_send_message(chat_id,
                f"⭐ <b>Thank you for your donation!</b>\n\n"
                f"💫 Stars donated: <b>{stars}</b>\n"
                f"💰 Value: <b>${stars * 0.01:.2f}</b>\n\n"
                f"Your support keeps this bot running! 🙏")

        except Exception as e:
            print(f"❌ handle_successful_payment error: {e}")
            traceback.print_exc()

    # ==================== WEBHOOK DISPATCH ====================

    def process_update(self, update):
        """Called by the /webhook Flask route for each incoming Telegram update"""
        try:
            if 'message' in update:
                msg = update['message']
                if 'successful_payment' in msg:
                    self.handle_successful_payment(msg)
                else:
                    self.process_message(msg)
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
            elif 'pre_checkout_query' in update:
                self.handle_pre_checkout_query(update['pre_checkout_query'])
        except Exception as e:
            print(f"❌ process_update error: {e}")

    # ==================== ENHANCED RUN METHOD WITH PERSISTENCE ====================

    def run(self):
        """Enhanced main bot loop with comprehensive crash protection"""
        if not self.initialize_with_persistence():
            print("❌ Bot cannot start. Initialization failed.")
            return
    
        print("🤖 Bot is running with enhanced protection...")
        print("📊 Monitoring: Health checks every 4 minutes")
        print("🛡️ Protection: Auto-restart on failures")
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
                            elif 'callback_query' in update:
                                self.handle_callback_query(update['callback_query'])
                        except Exception as e:
                            print(f"❌ Update processing error: {e}")
                            continue
                # Empty result is normal (no user activity) — do NOT count as failure
                
                current_time = time.time()
                time_since_last_update = current_time - last_successful_update
                
                if time_since_last_update > 300:
                    print(f"🚨 No updates for {time_since_last_update:.0f} seconds, testing connection...")
                    if not self.test_bot_connection():
                        print("❌ Bot connection lost, triggering restart...")
                        raise ConnectionError("Bot connection lost")
                
                if update_failures >= max_update_failures:
                    print("🚨 Too many update failures, triggering restart...")
                    raise ConnectionError("Too many update failures")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                if self.keep_alive:
                    self.keep_alive.stop()
                break
                
            except ConnectionError as e:
                print(f"🔌 Connection issue: {e}")
                self.handle_error(e, "connection_lost")
                raise
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Main loop error: {error_msg}")
                
                if any(keyword in error_msg.lower() for keyword in ['token', 'connection', 'network', 'timeout']):
                    self.handle_error(e, "critical_error")
                    raise
                else:
                    self.handle_error(e, "non_critical_error")
                    time.sleep(5)

# ==================== CHOREO / WEBHOOK ENTRY POINT ====================

def register_webhook(token, public_url):
    """Delete old webhook and register the new one with Telegram"""
    try:
        _tg_session.post(
            f"https://api.telegram.org/bot{token}/deleteWebhook",
            timeout=10
        )
        webhook_url = f"{public_url.rstrip('/')}/webhook"
        r = _tg_session.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            data={"url": webhook_url},
            timeout=10
        )
        result = r.json()
        if result.get('ok'):
            print(f"✅ Webhook registered: {webhook_url}")
        else:
            print(f"⚠️ Webhook registration issue: {result.get('description')}")
    except Exception as e:
        print(f"❌ Webhook registration error: {e}")

if __name__ == "__main__":
    print("🚀 Starting GAMERDROID™ Bot (Choreo / Webhook mode)...")

    # Start Flask server (webhook + health) in background thread
    start_health_check()
    time.sleep(2)

    if BOT_TOKEN:
        # Register webhook with Telegram if a public URL is available
        if PUBLIC_URL:
            register_webhook(BOT_TOKEN, PUBLIC_URL)
        else:
            print("⚠️ No PUBLIC_URL/CHOREO_URL set — webhook not registered automatically.")
            print("   Set CHOREO_URL to your service's public URL in Choreo environment variables.")

        # Initialise bot and expose it to the Flask webhook route
        restart_count = 0
        max_restarts = 10

        while restart_count < max_restarts:
            try:
                restart_count += 1
                print(f"🔄 Bot init attempt #{restart_count}")

                bot_instance = CrossPlatformBot(BOT_TOKEN)

                # Run persistence initialisation (DB restore, cache warm-up, keep-alive)
                if not bot_instance.initialize_with_persistence():
                    print("❌ Persistence init failed — retrying...")
                    time.sleep(10)
                    continue

                print("✅ Bot is live and listening for webhook updates!")
                print(f"📡 Webhook endpoint: POST /webhook")
                print(f"💚 Health endpoint:  GET  /health")

                # Keep the main thread alive — updates arrive via Flask webhook
                while True:
                    time.sleep(60)
                    print(f"💚 Bot alive — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user.")
                break
            except Exception as e:
                print(f"💥 Bot crash (#{restart_count}): {e}")
                if restart_count < max_restarts:
                    delay = min(10 * restart_count, 120)
                    print(f"🔄 Restarting in {delay}s...")
                    time.sleep(delay)
                else:
                    print("❌ Max restarts reached.")
                    break
    else:
        print("❌ No BOT_TOKEN — bot cannot start.")

    print("🔴 Bot service ended.")
