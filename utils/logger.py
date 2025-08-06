import logging
import asyncio
from utils.telegram_logger import send_telegram_log

def log_event(message: str, level: str = "INFO"):
    full_msg = f"[{level}] {message}"
    print(full_msg)
    try:
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule the coroutine
                asyncio.create_task(send_telegram_log(full_msg))
            else:
                # If loop is not running, run the coroutine
                loop.run_until_complete(send_telegram_log(full_msg))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(send_telegram_log(full_msg))
    except Exception:
        print("[WARN] Kunde inte skicka till Telegram")