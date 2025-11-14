# 🤖 Telegram Game Bot

A cross-platform Telegram bot for game distribution with mini-games integration.

## ✨ Features

- 🎮 **Game File Management** - Upload, browse, and download games
- 🔐 **User Verification** - Two-step verification system  
- 🎯 **Mini-Games** - Number guess, random generator, lucky spin
- 👑 **Admin Panel** - Game uploads, statistics, management
- 🔍 **Advanced Search** - Real-time game search
- 📱 **Cross-Platform** - Supports multiple game formats
- ⭐ **Star Payment** - Supports donations from users
- 💰 **Premium Games** - Supports Payments For Premium Games
- 💾 **GitHub Backup** - Support data backup and retrieval from GitHub
- 🔄 **Redeploy System** - Redeploy directly from telegram bot

## 🚀 Quick Deployment

### Railway.app (Recommended - Free)
1. Fork this repository
2. Go to [Railway.app](https://railway.app/)
3. Sign up with GitHub
4. Create New Project → Deploy from GitHub
5. Add environment variable:
6. `ADMIN_IDS=your_telegram_id`
7. `BOT_TOKEN=your_bot_token_here`
8. add the rest of the environment variables listed in the environment variables section
9. Deploy! 🎉

### Render.com (Alternative)
1. Go to [Render.com](https://render.com/)
2. Create New Web Service
3. Connect this repository
4. Set start command: `python channel_bot.py`
5. Add `BOT_TOKEN` and `ADMIN_IDS` and other environment variables listed in the environment variables section

## 🛠️ Admin Commands

- `/start` - Begin verification
- `/scan` - Scan for new games (admin only)
- `/menu` - Main menu
- `/minigames` - Mini-games menu
- `/status` - Bot status (admin only)

## 📁 Supported Game Formats

- ZIP, 7Z, RAR - Compressed archives
- ISO - Disc images (PSP, PS1, PS2)
- APK - Android games
- PKG - PS Vita games
- CSO, PBP - PSP compressed formats

## 🔧 Environment Variables

- `BOT_TOKEN` - Your Telegram bot token
- `ADMIN_IDS` - Your Telegram Account ID
- `GITHUB_TOKEN` - ghp_your_copied_token_here
- `GITHUB_REPO_OWNER` - your_github_username
- `GITHUB_REPO_NAME` - your_private_repository_name
- `GITHUB_BACKUP_PATH` - backups/telegram_bot.db
- `GITHUB_BACKUP_BRANCH` - main

## 📞 Support

For issues and questions, please contact me on telegram.
https://t.me/rexoronsaye

---
**⭐ Star this repo if you find it useful!**
