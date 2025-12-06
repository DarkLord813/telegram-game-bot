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

print("TELEGRAM BOT - GAME STORAGE & FILE SENDING")
print("Like @manybot with file storage and button-based sending")
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
    """Health check endpoint"""
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
    """Run the health check server"""
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Health server error: {e}")
        time.sleep(5)
        run_health_server()

def start_health_check():
    """Start health check server in background"""
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

# ==================== MAIN BOT CLASS ====================

class TelegramGameBot:
    def __init__(self, token):
        if not token:
            raise ValueError("BOT_TOKEN is required")
        
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
        # ADMIN USER IDs
        self.ADMIN_IDS = [7475473197, 7713987088]
        
        # Session management
        self.user_sessions = {}
        self.temp_files = {}  # Store temporary file info
        
        self.setup_database()
        print("✅ Bot system ready!")
    
    def setup_database(self):
        """Setup database with proper tables"""
        try:
            self.conn = sqlite3.connect('game_bot.db', check_same_thread=False)
            cursor = self.conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Games table - stores ALL uploaded files with file_id
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE,
                    file_unique_id TEXT UNIQUE,
                    file_name TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    category TEXT,
                    description TEXT,
                    added_by INTEGER,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    download_count INTEGER DEFAULT 0,
                    last_downloaded DATETIME
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    emoji TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize default categories
            default_categories = [
                ('PSP Games', '🎮'),
                ('Android Games', '📱'),
                ('PC Games', '💻'),
                ('Emulators', '⚙️'),
                ('Tools', '🛠️'),
                ('Other', '📦')
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
                data["reply_markup"] = json.dumps({"remove_keyboard": True})
            
            response = requests.post(url, data=data, timeout=15)
            return response.json()
            
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return None
    
    def send_document(self, chat_id, file_id, caption=None):
        """Send document using file_id (like @manybot)"""
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
                # Update download count
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE games 
                    SET download_count = download_count + 1,
                        last_downloaded = CURRENT_TIMESTAMP
                    WHERE file_id = ?
                ''', (file_id,))
                self.conn.commit()
                return True
            else:
                print(f"❌ Send document error: {result.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ Send document exception: {e}")
            return False
    
    def send_photo(self, chat_id, file_id, caption=None):
        """Send photo using file_id"""
        try:
            url = self.base_url + "sendPhoto"
            data = {
                "chat_id": chat_id,
                "photo": file_id,
                "caption": caption or "",
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            return response.json().get('ok', False)
                
        except Exception as e:
            print(f"❌ Send photo exception: {e}")
            return False
    
    def send_main_menu(self, chat_id, user_id, first_name):
        """Send main menu"""
        keyboard = [
            ["🎮 Browse Games", "🔍 Search Games"],
            ["📁 My Uploads", "📊 Stats"],
            ["📢 Channel", "ℹ️ Help"]
        ]
        
        # Add admin menu for admins
        if self.is_admin(user_id):
            keyboard.append(["👑 Admin Panel"])
        
        welcome_text = f"""👋 Welcome <b>{first_name}</b>!

🤖 <b>Game Storage Bot</b>
Like @manybot for game files!

📁 <b>Features:</b>
• Browse games by category
• Search for specific games
• Upload your own games
• One-click file downloads
• Fast file sending via file_id

Choose an option:"""
        
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def send_categories_menu(self, chat_id):
        """Send categories menu"""
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
        
        keyboard.append(["🔙 Main Menu"])
        
        categories_text = """🎮 <b>Game Categories</b>

Browse games by category:

"""
        for name, emoji in categories:
            cursor.execute('SELECT COUNT(*) FROM games WHERE category = ? AND is_active = 1', (name,))
            count = cursor.fetchone()[0]
            categories_text += f"{emoji} <b>{name}</b> - {count} games\n"
        
        categories_text += "\nSelect a category to browse games:"
        
        return self.send_message(chat_id, categories_text, keyboard)
    
    def send_games_in_category(self, chat_id, category_name, page=0):
        """Send games list for a category with pagination"""
        cursor = self.conn.cursor()
        
        # Get games in this category
        cursor.execute('''
            SELECT id, file_name, description, download_count 
            FROM games 
            WHERE category = ? AND is_active = 1 
            ORDER BY upload_date DESC 
            LIMIT 10 OFFSET ?
        ''', (category_name, page * 10))
        
        games = cursor.fetchall()
        
        if not games:
            keyboard = [["🔙 Categories"]]
            self.send_message(chat_id, f"❌ No games found in {category_name} category.", keyboard)
            return
        
        # Count total games
        cursor.execute('SELECT COUNT(*) FROM games WHERE category = ? AND is_active = 1', (category_name,))
        total_games = cursor.fetchone()[0]
        
        # Create games list text
        games_text = f"""🎮 <b>{category_name}</b>

📊 Total games: {total_games}
📄 Page {page + 1} of {(total_games + 9) // 10}

"""
        for i, (game_id, file_name, description, download_count) in enumerate(games, 1):
            games_text += f"{i}. <b>{file_name}</b>\n"
            if description:
                games_text += f"   📝 {description}\n"
            games_text += f"   📥 {download_count} downloads\n\n"
        
        # Create keyboard with games as buttons
        keyboard = []
        row = []
        
        for i, (game_id, file_name, description, download_count) in enumerate(games, 1):
            button_text = f"📁 {i}. {file_name[:15]}{'...' if len(file_name) > 15 else ''}"
            row.append(button_text)
            if len(row) == 2 or i == len(games):
                keyboard.append(row.copy())
                row = []
        
        # Add navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append("⬅️ Previous")
        
        if (page + 1) * 10 < total_games:
            nav_buttons.append("Next ➡️")
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append(["🔙 Categories", "🔍 Search"])
        
        # Store games info for this user session
        self.user_sessions[chat_id] = {
            'menu': 'category_games',
            'category': category_name,
            'page': page,
            'games': games
        }
        
        return self.send_message(chat_id, games_text, keyboard)
    
    def send_search_menu(self, chat_id):
        """Send search menu"""
        keyboard = [["🔙 Main Menu"]]
        
        search_text = """🔍 <b>Search Games</b>

Type the name of the game you're looking for.

Examples:
• "GTA"
• "God of War"
• "PSP"
• "Android"

You can search by filename, description, or category.

Type your search query now:"""
        
        self.user_sessions[chat_id] = {'menu': 'search', 'state': 'waiting_query'}
        return self.send_message(chat_id, search_text, keyboard)
    
    def handle_search(self, chat_id, query):
        """Handle game search"""
        cursor = self.conn.cursor()
        
        # Search in filename, description, and category
        cursor.execute('''
            SELECT id, file_name, category, description, download_count 
            FROM games 
            WHERE (file_name LIKE ? OR description LIKE ? OR category LIKE ?) 
            AND is_active = 1 
            ORDER BY download_count DESC 
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        
        if not results:
            keyboard = [["🔍 Search Again", "🔙 Main Menu"]]
            self.send_message(chat_id, f"❌ No games found for: <code>{query}</code>", keyboard)
            return
        
        # Create results text
        results_text = f"""🔍 <b>Search Results for:</b> <code>{query}</code>

📊 Found: {len(results)} games

"""
        for i, (game_id, file_name, category, description, download_count) in enumerate(results[:10], 1):
            results_text += f"{i}. <b>{file_name}</b>\n"
            results_text += f"   📁 {category} | 📥 {download_count} downloads\n"
            if description:
                results_text += f"   📝 {description[:50]}{'...' if len(description) > 50 else ''}\n"
            results_text += f"   └─ Click <b>Game {i}</b> to download\n\n"
        
        if len(results) > 10:
            results_text += f"📋 ... and {len(results) - 10} more games\n\n"
        
        # Create keyboard with results as buttons
        keyboard = []
        row = []
        
        for i, (game_id, file_name, category, description, download_count) in enumerate(results[:10], 1):
            button_text = f"🎮 Game {i}"
            row.append(button_text)
            if len(row) == 2 or i == min(10, len(results)):
                keyboard.append(row.copy())
                row = []
        
        keyboard.append(["🔍 Search Again", "🔙 Main Menu"])
        
        # Store search results
        self.user_sessions[chat_id] = {
            'menu': 'search_results',
            'query': query,
            'results': results
        }
        
        return self.send_message(chat_id, results_text, keyboard)
    
    def send_admin_menu(self, chat_id):
        """Send admin menu"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM games')
        total_games = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM games WHERE added_by = ?', (chat_id,))
        my_games = cursor.fetchone()[0]
        
        keyboard = [
            ["📤 Upload Game", "🗑️ My Games"],
            ["📊 All Games", "🏷️ Categories"],
            ["🔙 Main Menu"]
        ]
        
        admin_text = f"""👑 <b>Admin Panel</b>

📊 <b>Statistics:</b>
• Total games in database: {total_games}
• Your uploaded games: {my_games}

⚡ <b>Features:</b>
• 📤 Upload Game - Add new game files
• 🗑️ My Games - Manage your uploads
• 📊 All Games - View all games
• 🏷️ Categories - Manage categories

Choose an option:"""
        
        return self.send_message(chat_id, admin_text, keyboard)
    
    def send_upload_menu(self, chat_id):
        """Send upload menu"""
        keyboard = [
            ["🎮 Game File", "📷 Screenshot"],
            ["📝 Add Description", "🔙 Admin Menu"]
        ]
        
        upload_text = """📤 <b>Upload Game</b>

How to upload:

1. Click <b>Game File</b> to upload game file
   Supported: ZIP, 7Z, ISO, APK, RAR, etc.
   
2. (Optional) Click <b>Screenshot</b> to add preview
   
3. (Optional) Click <b>Add Description</b> to add description

4. The file will be saved permanently with file_id
   Users can download it instantly with one click!

📁 <b>Current upload:</b>"""
        
        if chat_id in self.temp_files:
            file_info = self.temp_files[chat_id]
            upload_text += f"\n• File: {file_info.get('file_name', 'None')}"
            upload_text += f"\n• Description: {file_info.get('description', 'None')}"
            upload_text += f"\n• Screenshots: {len(file_info.get('screenshots', []))}"
        
        upload_text += "\n\nStart by uploading a game file:"
        
        return self.send_message(chat_id, upload_text, keyboard)
    
    def save_game_to_database(self, chat_id, file_info):
        """Save uploaded game to database"""
        try:
            cursor = self.conn.cursor()
            
            # Get category from description or use default
            category = file_info.get('category', 'Other')
            if not category:
                category = 'Other'
            
            # Insert game into database
            cursor.execute('''
                INSERT INTO games 
                (file_id, file_unique_id, file_name, file_type, file_size, mime_type, 
                 category, description, added_by, upload_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_info['file_id'],
                file_info.get('file_unique_id', ''),
                file_info['file_name'],
                file_info.get('file_type', ''),
                file_info.get('file_size', 0),
                file_info.get('mime_type', ''),
                category,
                file_info.get('description', ''),
                chat_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            self.conn.commit()
            game_id = cursor.lastrowid
            
            # Save screenshots if any
            screenshots = file_info.get('screenshots', [])
            for i, screenshot_id in enumerate(screenshots):
                cursor.execute('''
                    INSERT INTO game_screenshots 
                    (game_id, file_id, position)
                    VALUES (?, ?, ?)
                ''', (game_id, screenshot_id, i))
            
            self.conn.commit()
            
            # Clear temp data
            if chat_id in self.temp_files:
                del self.temp_files[chat_id]
            
            return game_id
            
        except Exception as e:
            print(f"❌ Error saving game to database: {e}")
            return None
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
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
    
    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name}: {text}")
                
                # Save/update user in database
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name)
                    VALUES (?, ?, ?)
                ''', (user_id, message['from'].get('username', ''), first_name))
                self.conn.commit()
                
                # Handle session states
                if chat_id in self.user_sessions:
                    session = self.user_sessions[chat_id]
                    
                    # Handle search query
                    if session.get('state') == 'waiting_query':
                        return self.handle_search(chat_id, text)
                    
                    # Handle description input
                    elif session.get('state') == 'waiting_description':
                        if chat_id in self.temp_files:
                            self.temp_files[chat_id]['description'] = text
                        
                        self.user_sessions[chat_id]['state'] = None
                        self.send_upload_menu(chat_id)
                        return True
                    
                    # Handle category input
                    elif session.get('state') == 'waiting_category':
                        if chat_id in self.temp_files:
                            self.temp_files[chat_id]['category'] = text
                        
                        # Complete upload
                        if chat_id in self.temp_files:
                            game_id = self.save_game_to_database(chat_id, self.temp_files[chat_id])
                            if game_id:
                                self.send_message(chat_id, f"✅ Game saved successfully! ID: {game_id}")
                                self.send_main_menu(chat_id, user_id, first_name)
                            else:
                                self.send_message(chat_id, "❌ Failed to save game.")
                        
                        del self.user_sessions[chat_id]
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
                
                elif text == '🔍 Search Games':
                    self.send_search_menu(chat_id)
                    return True
                
                elif text == '🔍 Search Again':
                    self.send_search_menu(chat_id)
                    return True
                
                elif text == '📁 My Uploads':
                    self.send_my_uploads(chat_id, user_id)
                    return True
                
                elif text == '📊 Stats':
                    self.send_stats(chat_id, user_id)
                    return True
                
                elif text == '📢 Channel':
                    self.send_message(chat_id, "📢 Join our channel: @pspgamers5")
                    return True
                
                elif text == 'ℹ️ Help':
                    self.send_help(chat_id)
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
                
                elif text == '🎮 Game File' and self.is_admin(user_id):
                    self.send_message(chat_id, "📤 Please send the game file now.\n\nSupported formats: ZIP, 7Z, ISO, APK, RAR, PKG, CSO, PBP")
                    return True
                
                elif text == '📝 Add Description' and self.is_admin(user_id):
                    self.user_sessions[chat_id] = {'state': 'waiting_description'}
                    self.send_message(chat_id, "📝 Please enter a description for this game:")
                    return True
                
                elif text == '🔙 Admin Menu' and self.is_admin(user_id):
                    self.send_admin_menu(chat_id)
                    return True
                
                elif text == '📊 All Games' and self.is_admin(user_id):
                    self.send_all_games(chat_id)
                    return True
                
                elif text == '🏷️ Categories' and self.is_admin(user_id):
                    self.send_categories_management(chat_id)
                    return True
                
                # Handle category selection
                elif text.startswith(('🎮 ', '📱 ', '💻 ', '⚙️ ', '🛠️ ', '📦 ')):
                    category_name = text[2:]  # Remove emoji
                    self.send_games_in_category(chat_id, category_name)
                    return True
                
                # Handle game selection from category
                elif chat_id in self.user_sessions and self.user_sessions[chat_id].get('menu') == 'category_games':
                    if text.startswith('📁 '):
                        try:
                            # Extract game number from button text
                            game_num = int(text.split('.')[0].replace('📁 ', '')) - 1
                            session = self.user_sessions[chat_id]
                            games = session.get('games', [])
                            
                            if 0 <= game_num < len(games):
                                game_id, file_name, description, download_count = games[game_num]
                                
                                # Get file_id from database
                                cursor = self.conn.cursor()
                                cursor.execute('SELECT file_id FROM games WHERE id = ?', (game_id,))
                                result = cursor.fetchone()
                                
                                if result:
                                    file_id = result[0]
                                    caption = f"🎮 <b>{file_name}</b>"
                                    if description:
                                        caption += f"\n\n📝 {description}"
                                    caption += f"\n\n📥 Sent via Game Storage Bot"
                                    
                                    # Send the file
                                    if self.send_document(chat_id, file_id, caption):
                                        # Show success message with options
                                        keyboard = [
                                            ["📁 Send Again", "🎮 Browse More"],
                                            ["🔙 Categories", "🔍 Search"]
                                        ]
                                        self.send_message(chat_id, f"✅ <b>{file_name}</b> sent successfully!", keyboard)
                                    else:
                                        self.send_message(chat_id, "❌ Failed to send file.")
                                else:
                                    self.send_message(chat_id, "❌ File not found.")
                            else:
                                self.send_message(chat_id, "❌ Invalid game selection.")
                        except:
                            self.send_message(chat_id, "❌ Error processing game selection.")
                        return True
                
                # Handle game selection from search results
                elif chat_id in self.user_sessions and self.user_sessions[chat_id].get('menu') == 'search_results':
                    if text.startswith('🎮 Game '):
                        try:
                            # Extract game number from button text
                            game_num = int(text.replace('🎮 Game ', '')) - 1
                            session = self.user_sessions[chat_id]
                            results = session.get('results', [])
                            
                            if 0 <= game_num < len(results):
                                game_id, file_name, category, description, download_count = results[game_num]
                                
                                # Get file_id from database
                                cursor = self.conn.cursor()
                                cursor.execute('SELECT file_id FROM games WHERE id = ?', (game_id,))
                                result = cursor.fetchone()
                                
                                if result:
                                    file_id = result[0]
                                    caption = f"🎮 <b>{file_name}</b>\n📁 {category}"
                                    if description:
                                        caption += f"\n\n📝 {description}"
                                    caption += f"\n\n📥 Sent via Game Storage Bot"
                                    
                                    # Send the file
                                    if self.send_document(chat_id, file_id, caption):
                                        keyboard = [
                                            ["📁 Send Again", "🔍 Search Again"],
                                            ["🎮 Browse Games", "🔙 Main Menu"]
                                        ]
                                        self.send_message(chat_id, f"✅ <b>{file_name}</b> sent successfully!", keyboard)
                                    else:
                                        self.send_message(chat_id, "❌ Failed to send file.")
                                else:
                                    self.send_message(chat_id, "❌ File not found.")
                            else:
                                self.send_message(chat_id, "❌ Invalid game selection.")
                        except:
                            self.send_message(chat_id, "❌ Error processing game selection.")
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
                
                # Handle "Send Again"
                elif text == '📁 Send Again':
                    # This would need to track the last sent file
                    self.send_message(chat_id, "Please select a game from the categories or search results.")
                    return True
            
            # Handle document uploads
            if 'document' in message:
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                
                if self.is_admin(user_id):
                    return self.handle_document_upload(message, chat_id)
            
            # Handle photo uploads (for screenshots)
            if 'photo' in message:
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                
                if self.is_admin(user_id) and chat_id in self.temp_files:
                    photo = message['photo'][-1]  # Get highest resolution
                    file_id = photo['file_id']
                    
                    if 'screenshots' not in self.temp_files[chat_id]:
                        self.temp_files[chat_id]['screenshots'] = []
                    
                    self.temp_files[chat_id]['screenshots'].append(file_id)
                    self.send_message(chat_id, f"✅ Screenshot added! Total: {len(self.temp_files[chat_id]['screenshots'])}")
                    self.send_upload_menu(chat_id)
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Process message error: {e}")
            traceback.print_exc()
            return False
    
    def handle_document_upload(self, message, chat_id):
        """Handle document upload from admin"""
        try:
            doc = message['document']
            file_id = doc.get('file_id')
            file_unique_id = doc.get('file_unique_id')
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            mime_type = doc.get('mime_type', '')
            
            print(f"📥 Upload received: {file_name} (ID: {file_id})")
            
            # Determine file type
            if '.' in file_name:
                file_type = file_name.split('.')[-1].upper()
            else:
                file_type = 'UNKNOWN'
            
            # Store in temp files
            self.temp_files[chat_id] = {
                'file_id': file_id,
                'file_unique_id': file_unique_id,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': file_size,
                'mime_type': mime_type,
                'screenshots': []
            }
            
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
            
            categories_text = """✅ <b>File received!</b>

📁 File: <code>{}</code>
📦 Type: {}
📏 Size: {}

Now select a category for this game:""".format(
                file_name, file_type, self.format_file_size(file_size)
            )
            
            self.user_sessions[chat_id] = {'state': 'waiting_category'}
            return self.send_message(chat_id, categories_text, keyboard)
            
        except Exception as e:
            print(f"❌ Document upload error: {e}")
            traceback.print_exc()
            return False
    
    def send_my_uploads(self, chat_id, user_id):
        """Show user's uploaded games"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, file_name, category, download_count, upload_date 
            FROM games 
            WHERE added_by = ? 
            ORDER BY upload_date DESC 
            LIMIT 20
        ''', (user_id,))
        
        games = cursor.fetchall()
        
        if not games:
            keyboard = [["🔙 Main Menu"]]
            self.send_message(chat_id, "📭 You haven't uploaded any games yet.", keyboard)
            return
        
        games_text = """📁 <b>My Uploaded Games</b>

"""
        for i, (game_id, file_name, category, download_count, upload_date) in enumerate(games, 1):
            games_text += f"{i}. <b>{file_name}</b>\n"
            games_text += f"   📁 {category} | 📥 {download_count} downloads\n"
            games_text += f"   📅 {upload_date[:10]}\n\n"
        
        keyboard = [["🔙 Main Menu"]]
        self.send_message(chat_id, games_text, keyboard)
    
    def send_stats(self, chat_id, user_id):
        """Show bot statistics"""
        cursor = self.conn.cursor()
        
        # Total games
        cursor.execute('SELECT COUNT(*) FROM games WHERE is_active = 1')
        total_games = cursor.fetchone()[0]
        
        # Total downloads
        cursor.execute('SELECT SUM(download_count) FROM games')
        total_downloads = cursor.fetchone()[0] or 0
        
        # Your downloads
        cursor.execute('SELECT COUNT(*) FROM games WHERE added_by = ?', (user_id,))
        your_games = cursor.fetchone()[0]
        
        # Most popular category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM games 
            WHERE is_active = 1 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        popular_category = cursor.fetchone()
        
        stats_text = f"""📊 <b>Bot Statistics</b>

🎮 Total Games: {total_games}
📥 Total Downloads: {total_downloads}
👤 Your Uploads: {your_games}"""

        if popular_category:
            cat_name, cat_count = popular_category
            stats_text += f"\n🏆 Popular Category: {cat_name} ({cat_count} games)"
        
        stats_text += "\n\n📈 <b>Top Categories:</b>\n"
        
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM games 
            WHERE is_active = 1 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        
        for category, count in cursor.fetchall():
            stats_text += f"• {category}: {count} games\n"
        
        keyboard = [["🔙 Main Menu"]]
        self.send_message(chat_id, stats_text, keyboard)
    
    def send_help(self, chat_id):
        """Show help information"""
        help_text = """ℹ️ <b>Help & Information</b>

🤖 <b>How to use this bot:</b>

1. <b>Browse Games</b>
   • Select a category
   • Click on any game to download it instantly
   
2. <b>Search Games</b>
   • Type the game name
   • Click on results to download
   
3. <b>Upload Games (Admins)</b>
   • Go to Admin Panel
   • Upload game files
   • Files are saved permanently
   
4. <b>Fast Downloads</b>
   • Uses Telegram's file_id system
   • Instant file sending
   • No re-uploads needed

📱 <b>Features:</b>
• One-click file downloads
• Permanent file storage
• Search functionality
• Download statistics
• Category organization

📢 <b>Channel:</b> @pspgamers5

For admin access, contact bot owner."""
        
        keyboard = [["🔙 Main Menu"]]
        self.send_message(chat_id, help_text, keyboard)
    
    def send_all_games(self, chat_id):
        """Show all games for admin"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM games WHERE is_active = 1')
        total_games = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(download_count) FROM games')
        total_downloads = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM games 
            WHERE is_active = 1 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        
        stats_text = f"""📊 <b>All Games - Admin View</b>

🎮 Total Games: {total_games}
📥 Total Downloads: {total_downloads}

📈 <b>Games by Category:</b>\n"""
        
        for category, count in cursor.fetchall():
            stats_text += f"• {category}: {count} games\n"
        
        # Recent uploads
        cursor.execute('''
            SELECT file_name, added_by, upload_date, download_count 
            FROM games 
            WHERE is_active = 1 
            ORDER BY upload_date DESC 
            LIMIT 5
        ''')
        
        stats_text += "\n📅 <b>Recent Uploads:</b>\n"
        for file_name, added_by, upload_date, download_count in cursor.fetchall():
            stats_text += f"• {file_name} ({download_count} downloads)\n"
        
        keyboard = [
            ["📤 Upload Game", "🗑️ Manage Games"],
            ["🔙 Admin Menu"]
        ]
        
        self.send_message(chat_id, stats_text, keyboard)
    
    def send_categories_management(self, chat_id):
        """Manage categories"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, emoji FROM categories ORDER BY name')
        categories = cursor.fetchall()
        
        categories_text = """🏷️ <b>Categories Management</b>

Current categories:
"""
        for name, emoji in categories:
            cursor.execute('SELECT COUNT(*) FROM games WHERE category = ? AND is_active = 1', (name,))
            count = cursor.fetchone()[0]
            categories_text += f"{emoji} {name} - {count} games\n"
        
        categories_text += "\nTo add a category, type: /addcategory Name Emoji"
        categories_text += "\nExample: /addcategory Nintendo 🎮"
        
        keyboard = [["🔙 Admin Menu"]]
        self.send_message(chat_id, categories_text, keyboard)
    
    def run(self):
        """Main bot loop"""
        print("🤖 Game Storage Bot is running...")
        
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
    print("🚀 Starting Game Storage Bot...")
    
    # Start health check server
    start_health_check()
    
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
                bot = TelegramGameBot(BOT_TOKEN)
                bot.run()
            else:
                print(f"❌ Invalid bot token: {data.get('description')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    else:
        print("❌ ERROR: BOT_TOKEN environment variable not set!")
        
        # Keep running for health checks
        while True:
            time.sleep(60)
