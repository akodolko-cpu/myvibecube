from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from app.middleware.access_middleware import require_access

@require_access("/start")
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    welcome_text = (
        f"👋 Добро пожаловать, {user.first_name}!\n\n"
        "🤖 Это MyVibe Bot - система управления продажами.\n\n"
        "Используйте /help для просмотра доступных команд."
    )
    await update.effective_chat.send_message(welcome_text)

def get_handler():
    """Return the command handler for /start."""
    return CommandHandler("start", start_command)
