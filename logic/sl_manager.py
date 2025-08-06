from config.settings import SL_MOVE_THRESHOLDS, SL_MOVE_OFFSETS
from utils.logger import log_event
from core.api import client

async def check_and_adjust_sl(symbol, entry_price, current_price, pol, current_sl):
    try:
        # Flytta till BE +0.15% vid PoL ≥ 2.4%
        if pol >= SL_MOVE_THRESHOLDS['to_BE']:
            new_sl = round(entry_price * (1 + SL_MOVE_OFFSETS['BE']), 2)
            if new_sl > current_sl:
                log_event(f"[SL-MOVE] Flyttar SL till BE +0.15% på {symbol} → {new_sl}", "INFO")
                return new_sl

        # Fallback-SL vid PoL ≥ 4% → entry + 0.3%
        if pol >= SL_MOVE_THRESHOLDS['to_BE_fallback']:
            new_sl = round(entry_price * (1 + SL_MOVE_OFFSETS['fallback']), 2)
            if new_sl > current_sl:
                log_event(f"[SL-MOVE] Fallback SL aktiverad på {symbol} → {new_sl}", "INFO")
                return new_sl

        return current_sl  # Ingen förändring
    except Exception as e:
        log_event(f"[ERROR] Fel i SL-flytt för {symbol}: {e}", "ERROR")
        return current_sl
    
    # logic/sl_manager.py
from utils.telegram_logger import send_telegram_log
from core.api import client  # ✅ Din riktiga Bitget-klient

async def update_sl(symbol: str, side: str, new_sl: float, quantity: float, order_id: str):
    """
    Uppdaterar SL genom att modifiera en existerande order via Bitget API.
    """
    try:
        payload = {
            "symbol": symbol,
            "orderId": order_id,
            "stopLoss": new_sl
        }

        await send_telegram_log(
            f"🔐 SL uppdateras via Bitget modify_order till {new_sl} för {symbol} ({side})",
            tag="sl"
        )

        await client.modify_order(payload)

    except Exception as e:
        await send_telegram_log(
            f"❌ SL-uppdatering misslyckades för {symbol}: {e}",
            tag="error"
        )

