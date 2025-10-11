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

print("TELEGRAM BOT - CROSS PLATFORM")
print("Code Verification + Channel Join + Game Scanner")
print("Admin Game Uploads Enabled + Forward Support + Game Search")
print("Mini-Games Integration: Number Guess, Random Number, Lucky Spin")
print("=" * 50)

class CrossPlatformBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
        # YOUR CHANNEL DETAILS
        self.REQUIRED_CHANNEL = "@pspgamers5"
        self.CHANNEL_LINK = "https://t.me/pspgamers5"
        
        # ADMIN USER IDs - Replace these with actual user IDs
        self.ADMIN_IDS = [1234567890, 0987654321]
        
        # Mini-games state management
        self.guess_games = {}  # {user_id: {'target': number, 'attempts': count}}
        self.spin_games = {}   # {user_id: {'spins': count, 'last_spin': timestamp}}
        
        self.setup_database()
        self.verify_database_schema()  # Add schema verification
        self.games_cache = {}
        self.is_scanning = False
        self.search_sessions = {}
        self.search_results = {}
        
        print("✅ Bot system ready!")
        print(f"📊 Monitoring channel: {self.REQUIRED_CHANNEL}")
        print(f"👑 Admin uploads enabled for {len(self.ADMIN_IDS)} users")
        print("📤 Forwarded files support enabled")
        print("🔍 Game search feature enabled")
        print("🎮 Mini-games integrated: Number Guess, Random Number, Lucky Spin")
    
    def is_admin(self, user_id):
        return user_id in self.ADMIN_IDS
    
    def create_progress_bar(self, percentage, length=10):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    # ==================== DATABASE SCHEMA VERIFICATION ====================
    
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
        
        self.send_message(chat_id, game_text, keyboard)
        return True
    
    def handle_guess_input(self, user_id, chat_id, guess_text):
        """Handle user's number guess"""
        if user_id not in self.guess_games:
            self.send_message(chat_id, "❌ No active number guess game. Start a new one from Mini-Games!")
            return False
        
        try:
            guess = int(guess_text.strip())
            if guess < 1 or guess > 10:
                self.send_message(chat_id, "❌ Please enter a number between 1 and 10!")
                return True
        except ValueError:
            self.send_message(chat_id, "❌ Please enter a valid number!")
            return True
        
        game = self.guess_games[user_id]
        game['attempts'] += 1
        target = game['target']
        
        # Create quick number buttons
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
            
            self.send_message(chat_id, win_text, keyboard)
            del self.guess_games[user_id]
            
        elif game['attempts'] >= game['max_attempts']:
            lose_text = f"""😔 <b>Game Over!</b>

🎯 The number was: <b>{target}</b>
📊 Your attempts: <b>{game['attempts']}</b>
💡 Better luck next time!

🔄 Want to try again?"""
            
            self.send_message(chat_id, lose_text, keyboard)
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
            
            self.send_message(chat_id, progress_text, keyboard)
        
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
        
        self.send_message(chat_id, random_text, keyboard)
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
        
        self.send_message(chat_id, custom_text, keyboard)
        return True
    
    def lucky_spin(self, user_id, chat_id):
        """Perform a lucky spin"""
        now = time.time()
        
        # Rate limiting: 1 spin per 3 seconds
        if user_id in self.spin_games:
            last_spin = self.spin_games[user_id].get('last_spin', 0)
            if now - last_spin < 3:
                wait_time = 3 - (now - last_spin)
                self.send_message(chat_id, f"⏳ Please wait {wait_time:.1f} seconds before spinning again!")
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
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎰 Spin Again", "callback_data": "game_spin"}],
                [{"text": "🎯 Big Spin (3x)", "callback_data": "big_spin"}],
                [{"text": "🔙 Back to Mini-Games", "callback_data": "mini_games"}]
            ]
        }
        
        self.send_message(chat_id, spin_text, keyboard)
        return True
    
    def big_spin(self, user_id, chat_id):
        """Perform 3 spins at once"""
        spin_results = []
        total_win = 0
        
        for spin_num in range(3):
            symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🔔"]
            spins = [random.choice(symbols) for _ in range(3)]
            
            # Calculate win for this spin
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
        
        # Update stats
        if user_id not in self.spin_games:
            self.spin_games[user_id] = {'spins': 0, 'total_wins': 0}
        
        self.spin_games[user_id]['spins'] += 3
        self.spin_games[user_id]['total_wins'] += total_win
        self.spin_games[user_id]['last_spin'] = time.time()
        
        stats = self.spin_games[user_id]
        
        # Create big spin result text
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
        
        self.send_message(chat_id, big_spin_text, keyboard)
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

    # ==================== IMPROVED ADMIN GAME MANAGEMENT ====================
    
    def clear_all_games(self, user_id, chat_id, message_id):
        """Clear all games from database (admin only)"""
        if not self.is_admin(user_id):
            self.answer_callback_query(message_id, "❌ Access denied. Admin only.", True)
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Count games before deletion
            cursor.execute('SELECT COUNT(*) FROM channel_games')
            total_games_before = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1')
            uploaded_games_before = cursor.fetchone()[0]
            
            # Delete all games
            cursor.execute('DELETE FROM channel_games')
            self.conn.commit()
            
            # Update cache
            self.update_games_cache()
            
            clear_text = f"""🗑️ <b>All Games Cleared Successfully!</b>

📊 Before clearing:
• Total games: {total_games_before}
• Admin uploaded: {uploaded_games_before}

✅ After clearing:
• All games removed from database
• Cache updated
• Ready for fresh start

🔄 You can now upload new games or rescan the channel."""
            
            self.edit_message(chat_id, message_id, clear_text, self.create_admin_buttons())
            
            print(f"🗑️ Admin {user_id} cleared all games from database")
            
        except Exception as e:
            error_text = f"❌ Error clearing games: {str(e)}"
            self.edit_message(chat_id, message_id, error_text, self.create_admin_buttons())
            print(f"❌ Clear games error: {e}")

    # ==================== IMPROVED DOCUMENT UPLOAD METHODS ====================
    
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
            
            doc = message['document']
            file_name = doc.get('file_name', 'Unknown File')
            file_size = doc.get('file_size', 0)
            file_id = doc.get('file_id', '')
            bot_message_id = message['message_id']
            
            print(f"📥 Admin {user_id} uploading: {file_name} (Size: {file_size}, Message ID: {bot_message_id})")
            
            # Check if it's a supported game file
            game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
            if not any(file_name.lower().endswith(ext) for ext in game_extensions):
                self.send_message(chat_id, f"❌ File type not supported: {file_name}")
                print(f"❌ Unsupported file type: {file_name}")
                return False
            
            file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
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
                'file_id': file_id,
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
            
            self.send_message(chat_id, confirm_text)
            
            print(f"✅ Successfully stored: {file_name} (Storage ID: {storage_message_id}, Bot Message ID: {bot_message_id})")
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def handle_forwarded_message(self, message):
        try:
            user_id = message['from']['id']
            
            if not self.is_admin(user_id):
                print(f"❌ Non-admin user {user_id} attempted forwarded upload")
                return False
            
            # Check if this is a forwarded document
            if 'forward_origin' not in message:
                return False
                
            if 'document' not in message:
                print("❌ Forwarded message has no document")
                return False
            
            print(f"📨 Processing forwarded file from admin {user_id}")
            return self.handle_document_upload(message)
            
        except Exception as e:
            print(f"❌ Forwarded message processing error: {e}")
            return False

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
                        
                        game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
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
            
            return bot_games_found
            
        except Exception as e:
            print(f"❌ Bot games scan error: {e}")
            return 0

    # ==================== IMPROVED FILE SENDING METHODS ====================
    
    def send_game_file(self, chat_id, message_id, file_id=None, is_bot_file=False):
        try:
            print(f"📤 Sending game file: msg_id={message_id}, is_bot_file={is_bot_file}, file_id={file_id}")
            
            if is_bot_file:
                # For bot-uploaded files, forward from the bot's chat
                url = self.base_url + "forwardMessage"
                data = {
                    "chat_id": chat_id,
                    "from_chat_id": chat_id,  # Important: forward from current chat
                    "message_id": message_id
                }
                
                response = requests.post(url, data=data, timeout=30)
                result = response.json()
                
                if result.get('ok'):
                    print(f"✅ Successfully forwarded bot file {message_id}")
                    return True
                else:
                    print(f"❌ Bot file forward failed: {result.get('description')}")
                    # Fallback to direct send
                    if file_id:
                        return self.send_document_directly(chat_id, file_id)
                    return False
            else:
                # For channel files, forward from channel
                url = self.base_url + "forwardMessage"
                data = {
                    "chat_id": chat_id,
                    "from_chat_id": self.REQUIRED_CHANNEL,
                    "message_id": message_id
                }
                
                response = requests.post(url, data=data, timeout=30)
                result = response.json()
                
                if result.get('ok'):
                    print(f"✅ Successfully forwarded channel file {message_id}")
                    return True
                else:
                    print(f"❌ Channel forward failed: {result.get('description')}")
                    # Fallback to direct send
                    if file_id and file_id != 'short':
                        return self.send_document_directly(chat_id, file_id)
                    else:
                        # Try to get file_id from database
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT file_id FROM channel_games WHERE message_id = ?', (message_id,))
                        result_db = cursor.fetchone()
                        if result_db and result_db[0]:
                            return self.send_document_directly(chat_id, result_db[0])
                    
                    return False
                
        except Exception as e:
            print(f"❌ Error sending game file: {e}")
            return False

    def send_document_directly(self, chat_id, file_id):
        """Send document directly using file_id"""
        try:
            print(f"📤 Sending document directly with file_id: {file_id}")
            
            url = self.base_url + "sendDocument"
            data = {
                "chat_id": chat_id,
                "document": file_id
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Sent document directly using file_id to user {chat_id}")
                return True
            else:
                print(f"❌ Direct send failed: {result.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending document directly: {e}")
            return False

    # ==================== SEARCH GAMES METHODS ====================
    
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
            
            # Use bot_message_id for uploaded files, channel message_id for channel files
            if game['is_uploaded'] == 1 and game['bot_message_id']:
                # This is a file uploaded directly to the bot
                message_id_to_send = game['bot_message_id']
                is_bot_file = True
            else:
                # This is a file from the channel
                message_id_to_send = game['message_id']
                is_bot_file = False
            
            file_id_clean = str(game['file_id']).replace('-', '_').replace('=', 'eq')
            callback_data = f"send_game_{message_id_to_send}_{file_id_clean}_{1 if is_bot_file else 0}"
            
            # Validate callback data length
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
                self.send_message(chat_id, "🔐 Please complete verification first with /start")
                return True
            
            print(f"🔍 User {user_id} searching for: '{search_term}'")
            
            # Show initial search message
            search_msg = self.send_message(chat_id, 
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
                        
                        self.send_message(
                            chat_id, 
                            results_text, 
                            buttons
                        )
                    else:
                        results_text = f"❌ No results found for: <code>{search_term}</code>\n\n"
                        results_text += "💡 Try:\n• Different keywords\n• Shorter search terms\n• Check spelling"
                        results_text += "\n\n🔍 Try a new search:"
                        
                        self.send_message(chat_id, results_text, self.create_search_buttons())
                    
                    if user_id in self.search_sessions:
                        del self.search_sessions[user_id]
                        
                except Exception as e:
                    print(f"❌ Search error: {e}")
                    self.send_message(chat_id, "❌ Search failed. Please try again.")
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

    # ==================== DATABASE & SETUP METHODS ====================
    
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
                
                game_extensions = ['.zip', '.7z', '.iso', '.rar', '.pkg', '.cso', '.pbp', '.cs0', '.apk']
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
            
            return {'total_games': total_games}
        except:
            return {'total_games': 0}
    
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
    
    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = self.base_url + "sendMessage"
            data = {
                "chat_id": chat_id, 
                "text": text, 
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            if result.get('ok'):
                print(f"✅ Message sent to {chat_id}")
                return True
            else:
                print(f"❌ Failed to send message: {result.get('description')}")
                return False
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return False
    
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
            
            response = requests.post(url, data=data, timeout=10)
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
            requests.post(url, data=data, timeout=5)
        except:
            pass
    
    def get_updates(self, offset=None):
        try:
            url = self.base_url + "getUpdates"
            params = {"timeout": 100, "offset": offset}
            response = requests.get(url, params=params, timeout=100)
            data = response.json()
            return data.get('result', []) if data.get('ok') else []
        except Exception as e:
            print(f"Get updates error: {e}")
            return []
    
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
                    {"text": "🔍 Search Games", "callback_data": "search_games"}
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
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": f"📦 ZIP ({len(self.games_cache.get('zip', []))})", "callback_data": "game_zip"},
                    {"text": f"🗜️ 7Z ({len(self.games_cache.get('7z', []))})", "callback_data": "game_7z"}
                ],
                [
                    {"text": f"💿 ISO ({len(self.games_cache.get('iso', []))})", "callback_data": "game_iso"},
                    {"text": f"📱 APK ({len(self.games_cache.get('apk', []))})", "callback_data": "game_apk"}
                ],
                [
                    {"text": f"🎮 PSP ({psp_count})", "callback_data": "game_psp"},
                    {"text": f"📋 All ({stats['total_games']})", "callback_data": "game_all"}
                ],
                [
                    {"text": "🔍 Search Games", "callback_data": "search_games"}
                ],
                [
                    {"text": "🔄 Rescan", "callback_data": "rescan_games"}
                ],
                [
                    {"text": "🔙 Back to Games", "callback_data": "games"}
                ]
            ]
        }
        return keyboard
    
    def create_main_menu_buttons(self):
        stats = self.get_channel_stats()
        keyboard = [
            [
                {"text": "📊 Profile", "callback_data": "profile"},
                {"text": "🕒 Time", "callback_data": "time"}
            ],
            [
                {"text": "📢 Channel", "callback_data": "channel_info"},
                {"text": f"🎮 Games ({stats['total_games']})", "callback_data": "games"}
            ],
            [
                {"text": "🔍 Search Games", "callback_data": "search_games"}
            ]
        ]
        
        keyboard.append([
            {"text": "🔧 Admin Panel", "callback_data": "admin_panel"}
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
                    {"text": "📤 Upload Games", "callback_data": "upload_games_info"},
                    {"text": "🗑️ Clear All Games", "callback_data": "clear_all_games"}
                ],
                [
                    {"text": "📊 Profile", "callback_data": "profile"},
                    {"text": "🔍 Scan Bot Games", "callback_data": "scan_bot_games"}
                ],
                [
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
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
                    {"text": "🔙 Back to Menu", "callback_data": "back_to_menu"}
                ]
            ]
        }
    
    def handle_upload_stats(self, chat_id, message_id, user_id, first_name):
        total_uploads = self.get_upload_stats()
        user_uploads = self.get_upload_stats(user_id)
        total_forwards = self.get_forward_stats()
        user_forwards = self.get_forward_stats(user_id)
        total_games = len(self.games_cache.get('all', []))
        
        # Count bot-uploaded games
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM channel_games WHERE is_uploaded = 1 AND bot_message_id IS NOT NULL')
        bot_uploaded = cursor.fetchone()[0]
        
        stats_text = f"""👑 Admin Panel

📊 Upload Statistics:
• Your uploads: {user_uploads} files
• Your forwarded: {user_forwards} files
• Total bot uploads: {total_uploads} files
• Bot-uploaded games: {bot_uploaded} files
• Total forwarded: {total_forwards} files
• Total games in database: {total_games}

📤 Upload Methods:
1. Send files directly to bot
2. Forward files from channels/chats
3. Use rescan to find existing bot uploads"""

        self.edit_message(chat_id, message_id, stats_text, self.create_admin_buttons())

    def handle_upload_games_info(self, chat_id, message_id, user_id, first_name):
        upload_info = f"""📤 Upload Games - Admin Guide

👋 Hello {first_name}!

As an admin, you can upload game files in multiple ways:

📁 Supported Formats:
• ZIP files (.zip)
• 7Z files (.7z) 
• ISO files (.iso) - PSP, PS1, PS2 games
• APK files (.apk) - Android games
• RAR files (.rar)
• PKG files (.pkg) - PS Vita games
• CSO files (.cso) - PSP compressed ISO
• PSP files (.pbp, .cs0)

🔄 Method 1: Direct Upload
1. Send the game file as a document to this bot
2. The bot will automatically process and add it

🔄 Method 2: Forward Files
1. Find game files in any channel or chat
2. Forward them to this bot
3. The bot will process forwarded files automatically

🔄 Method 3: Rescan Existing
1. Click "Scan Bot Games" to find existing uploads
2. The bot will scan recent messages for game files

📊 Your stats:
• Total uploads: {self.get_upload_stats(user_id)} files
• Forwarded files: {self.get_forward_stats(user_id)} files"""

        self.edit_message(chat_id, message_id, upload_info, self.create_admin_buttons())

    def handle_search_games(self, chat_id, message_id, user_id, first_name):
        # Update cache first to ensure we have latest data
        self.update_games_cache()
        
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
        
        text += "🔗 Visit: @pspgamers5"
        return text

    def handle_profile(self, chat_id, message_id, user_id, first_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT created_at, is_verified, joined_channel FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
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

            self.edit_message(chat_id, message_id, profile_text, self.create_main_menu_buttons())
            
        except Exception as e:
            print(f"Profile error: {e}")

    # ==================== UPDATED CALLBACK HANDLER ====================

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
            
            # Mini-games callbacks
            if data == "game_guess":
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
                # Show quick number buttons
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

            # Handle game file sending with proper message ID handling
            if data.startswith('send_game_'):
                parts = data.replace('send_game_', '').split('_')
                if len(parts) >= 3:
                    message_id_to_send = int(parts[0])
                    file_id = parts[1] if len(parts) > 1 else None
                    is_bot_file = int(parts[2]) == 1  # 1 for bot files, 0 for channel files
                    
                    # Clean file_id if it was shortened
                    if file_id == 'short':
                        file_id = None
                    else:
                        file_id = file_id.replace('_', '-').replace('eq', '=')
                    
                    self.answer_callback_query(callback_query['id'], "📥 Sending file...", False)
                    
                    if self.send_game_file(chat_id, message_id_to_send, file_id, is_bot_file):
                        self.answer_callback_query(callback_query['id'], "✅ File sent!", False)
                    else:
                        self.answer_callback_query(callback_query['id'], "❌ Failed to send file. Please try again or contact admin.", True)
                return
            
            elif data.startswith('search_page_'):
                parts = data.replace('search_page_', '').split('_')
                if len(parts) >= 2:
                    search_term = parts[0]
                    page = int(parts[1])
                    
                    user_results = self.search_results.get(user_id, {})
                    if user_results and user_results.get('search_term') == search_term:
                        results = user_results.get('results', [])
                        
                        results_text = f"🔍 Search Results: <code>{search_term}</code>\n\n"
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
            if data == "profile":
                self.handle_profile(chat_id, message_id, user_id, first_name)
                
            elif data == "time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_text = f"🕒 <b>Current Time</b>\n\n📅 {current_time}\n\n⏰ Server Time (UTC)"
                self.edit_message(chat_id, message_id, time_text, self.create_main_menu_buttons())
                
            elif data == "channel_info":
                channel_info = f"""📢 <b>Channel Information</b>

🏷️ Channel: @pspgamers5
🔗 Link: https://t.me/pspgamers5
📝 Description: PSP Games & More!

🎮 Available Games:
• PSP Games (ISO/CSO)
• PS1 Games
• Android Games (APK)
• Emulator Games
• And much more!

📥 How to Download:
1. Join our channel
2. Browse available games
3. Click on files to download

⚠️ Note: You need to join channel and complete verification to access games."""
                self.edit_message(chat_id, message_id, channel_info, self.create_main_menu_buttons())
                
            elif data == "games":
                if not self.is_user_completed(user_id):
                    self.edit_message(chat_id, message_id, 
                                    "🔐 Please complete verification first with /start", 
                                    self.create_main_menu_buttons())
                    return
                
                stats = self.get_channel_stats()
                games_text = f"""🎮 <b>Games Section</b>

📊 Total Games: {stats['total_games']}

🎯 Choose an option below:

• 📁 Game Files - Browse all available games
• 🎮 Mini Games - Fun mini-games to play
• 🔍 Search Games - Search for specific games

🔗 Channel: @pspgamers5"""
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
                                    self.create_main_menu_buttons())
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
                self.edit_message(chat_id, message_id, f"✅ Rescan complete! Found {total_games} total games. Database now has {stats['total_games']} games.", self.create_game_files_buttons())
            
            elif data == "back_to_menu":
                welcome_text = f"""👋 Welcome {first_name}!

🤖 <b>Cross-Platform Telegram Bot</b>

📊 Features:
• 🎮 Game File Browser
• 🔍 Advanced Game Search  
• 📱 Cross-Platform Support
• 📤 Admin Upload System
• 🔄 Forward Support
• 🕒 Real-time Updates
• 🎮 Mini-Games Entertainment

Choose an option below:"""
                self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons())
            
            elif data == "verify_channel":
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    welcome_text = f"""✅ <b>Verification Complete!</b>

👋 Welcome {first_name}!

🎉 You now have full access to:
• 🎮 Game File Browser  
• 🔍 Game Search
• 📁 All Game Categories
• 🕒 Real-time Updates
• 🎮 Mini-Games

📢 Channel: @pspgamers5
Choose an option below:"""
                    self.edit_message(chat_id, message_id, welcome_text, self.create_main_menu_buttons())
                else:
                    self.edit_message(chat_id, message_id, 
                                    "❌ You haven't joined the channel yet!\n\n"
                                    "Please join @pspgamers5 first, then click Verify Join again.",
                                    self.create_channel_buttons())
            
            elif data == "admin_panel":
                if not self.is_admin(user_id):
                    self.edit_message(chat_id, message_id, "❌ Access denied. Admin only.", self.create_main_menu_buttons())
                    return
                
                admin_text = f"""👑 <b>Admin Panel</b>

👋 Welcome {first_name}!

🛠️ Admin Features:
• 📤 Upload game files directly
• 🔄 Process forwarded files  
• 📊 View upload statistics
• 🗃️ Update games cache
• 🗑️ Clear all games
• 🔍 Scan bot-uploaded games
• 🔍 Monitor system status

📊 Your Stats:
• Total uploads: {self.get_upload_stats(user_id)}
• Forwarded files: {self.get_forward_stats(user_id)}
• Total games: {len(self.games_cache.get('all', []))}

Choose an option:"""
                self.edit_message(chat_id, message_id, admin_text, self.create_admin_buttons())
            
            elif data == "upload_stats":
                if not self.is_admin(user_id):
                    return
                self.handle_upload_stats(chat_id, message_id, user_id, first_name)
            
            elif data == "upload_games_info":
                if not self.is_admin(user_id):
                    return
                self.handle_upload_games_info(chat_id, message_id, user_id, first_name)
            
            elif data == "update_cache":
                if not self.is_admin(user_id):
                    return
                self.edit_message(chat_id, message_id, "🔄 Updating games cache...", self.create_admin_buttons())
                self.update_games_cache()
                self.edit_message(chat_id, message_id, f"✅ Cache updated! {len(self.games_cache.get('all', []))} games loaded.", self.create_admin_buttons())
                
        except Exception as e:
            print(f"Callback error: {e}")

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
                welcome_text = f"""👋 Welcome back {first_name}!

✅ You're already verified!
📢 Channel membership: Active

Choose an option below:"""
                self.send_message(chat_id, welcome_text, self.create_main_menu_buttons())
                return True
            
            # Check if user is verified but not joined channel
            if self.is_user_verified(user_id) and not self.check_channel_membership(user_id):
                channel_text = f"""📢 <b>Channel Verification Required</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:"""
                self.send_message(chat_id, channel_text, self.create_channel_buttons())
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
                    self.send_message(chat_id, verify_text)
                    return True
                else:
                    self.send_message(chat_id, "❌ Error generating verification code. Please try again.")
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
                # Check if user has already joined channel
                if self.check_channel_membership(user_id):
                    self.mark_channel_joined(user_id)
                    welcome_text = f"""✅ <b>Verification Complete!</b>

👋 Welcome {first_name}!

🎉 You now have full access to:
• 🎮 Game File Browser  
• 🔍 Game Search
• 📁 All Game Categories
• 🕒 Real-time Updates
• 🎮 Mini-Games

📢 Channel: @pspgamers5
Choose an option below:"""
                    self.send_message(chat_id, welcome_text, self.create_main_menu_buttons())
                else:
                    channel_text = f"""✅ <b>Code Verified!</b>

👋 Hello {first_name}!

✅ Code verification: Completed
❌ Channel membership: Pending

📝 <b>Step 2: Join Our Channel</b>

To access all features, please join our channel:

🔗 {self.CHANNEL_LINK}

After joining, click the button below:"""
                    self.send_message(chat_id, channel_text, self.create_channel_buttons())
                return True
            else:
                self.send_message(chat_id, "❌ Invalid or expired code. Please use /start to get a new code.")
                return True
                
        except Exception as e:
            print(f"❌ Code verification error: {e}")
            return False

    # ==================== UPDATED MESSAGE PROCESSOR ====================

    def process_message(self, message):
        """Main message processing function"""
        try:
            if 'text' in message:
                text = message['text']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from']['first_name']
                
                print(f"💬 Message from {first_name} ({user_id}): {text}")
                
                # Handle mini-games input first
                if user_id in self.guess_games:
                    # Check if it's a number guess for an active game
                    if text.strip().isdigit():
                        return self.handle_guess_input(user_id, chat_id, text)
                
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
                        if self.is_admin(user_id):
                            admin_text = f"👑 Admin Menu\n\nWelcome {first_name}!\n\nYou have admin privileges."
                            self.send_message(chat_id, admin_text, self.create_admin_buttons())
                        else:
                            self.send_message(chat_id, f"🏠 Main Menu\n\nWelcome {first_name}!", self.create_main_menu_buttons())
                        return True
                    elif text == '/minigames' and self.is_user_completed(user_id):
                        games_text = """🎮 <b>Mini Games</b>

Available games:
• /guess - Start number guess game
• /random - Generate random number
• /spin - Lucky spin game
• /minigames - Show this menu

Have fun! 🎉"""
                        self.send_message(chat_id, games_text, self.create_mini_games_buttons())
                        return True
                    elif text == '/guess' and self.is_user_completed(user_id):
                        return self.start_number_guess_game(user_id, chat_id)
                    elif text == '/random' and self.is_user_completed(user_id):
                        return self.generate_random_number(user_id, chat_id)
                    elif text == '/spin' and self.is_user_completed(user_id):
                        return self.lucky_spin(user_id, chat_id)
                    elif text == '/cleargames' and self.is_admin(user_id):
                        self.clear_all_games(user_id, chat_id, message['message_id'])
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
                        
                        self.send_message(chat_id, debug_text)
                        return True
                
                # Handle code verification
                if text.isdigit() and len(text) == 6:
                    return self.handle_code_verification(message)
                
                # Handle game search
                if self.is_user_verified(user_id):
                    return self.handle_game_search(message)
            
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

    def run(self):
        if not self.test_bot_connection():
            print("❌ Bot cannot start. Please check your token.")
            return
        
        print("🤖 Bot is running...")
        print("📝 Send /start to begin")
        print("🎮 Mini-games available: /minigames")
        print("👑 Admin commands: /scan, /cleargames, /debug_uploads")
        print("🛑 Press Ctrl+C to stop")
        
        offset = 0
        while True:
            try:
                updates = self.get_updates(offset)
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        self.process_message(update['message'])
                    elif 'callback_query' in update:
                        self.handle_callback_query(update['callback_query'])
                        
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

if __name__ == "__main__":
    bot = CrossPlatformBot(BOT_TOKEN)
    bot.run()