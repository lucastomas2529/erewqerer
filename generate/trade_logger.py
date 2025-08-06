
import logging
import os
from datetime import datetime

# Skapa loggmapp om den inte finns
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logger setup
logger = logging.getLogger("TradeLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Loggfil per dag
log_filename = datetime.now().strftime("%Y-%m-%d_trades.log")
file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_entry(symbol: str, side: str, price: float, quantity: float, leverage: float, sl: float, tp: float):
    logger.info(f"ENTRY | {symbol} | {side} | Price: {price} | Qty: {quantity} | Lev: {leverage}x | SL: {sl} | TP: {tp}")

def log_exit(symbol: str, exit_price: float, pnl_percent: float, reason: str):
    logger.info(f"EXIT  | {symbol} | Price: {exit_price} | PnL: {pnl_percent}% | Reason: {reason}")

def log_error(message: str):
    logger.error(f"ERROR | {message}")

def log_im_addition(symbol: str, added_im: float, new_total_im: float, reason: str):
    logger.info(f"IM++  | {symbol} | Added: {added_im} USDT | New Total IM: {new_total_im} USDT | Reason: {reason}")

def log_sl_update(symbol: str, new_sl: float, reason: str):
    logger.info(f"SL-UPD| {symbol} | New SL: {new_sl} | Reason: {reason}")

def log_trailing_activation(symbol: str, trailing_start: float):
    logger.info(f"TRAIL | {symbol} | Activated from: {trailing_start}")
