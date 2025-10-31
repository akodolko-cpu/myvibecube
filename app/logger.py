import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs('logs', exist_ok=True)


def setup_logger(name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


bot_logger = setup_logger('bot', 'logs/bot.log')
user_requests_logger = setup_logger('user_requests', 'logs/user_requests.log')


def log_command_start(telegram_user_id: int, command: str):
    user_requests_logger.info(f"User {telegram_user_id}: executing {command}")


def log_access_denied(telegram_user_id: int, command: str):
    bot_logger.warning(f"Access denied for user {telegram_user_id} to command {command}")


def log_bot_error(error: Exception):
    bot_logger.error(f"Bot error: {str(error)}", exc_info=True)
