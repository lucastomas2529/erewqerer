from config.settings import HEDGE_TRIGGER, HEDGE_SL
from utils.logger import log_event

async def check_and_open_hedge(symbol, direction, entry_price, current_price):
    try:
        price_change_pct = ((current_price - entry_price) / entry_price) * 100
        if direction == "long" and price_change_pct <= HEDGE_TRIGGER:
            log_event(f"[HEDGE] Trigger för hedge SHORT på {symbol} → prisfall {price_change_pct:.2f}%", "INFO")
            # await place_hedge_order(symbol, "short", sl=HEDGE_SL)
            return True
        elif direction == "short" and price_change_pct >= -HEDGE_TRIGGER:
            log_event(f"[HEDGE] Trigger för hedge LONG på {symbol} → prisökning {price_change_pct:.2f}%", "INFO")
            # await place_hedge_order(symbol, "long", sl=HEDGE_SL)
            return True
        return False
    except Exception as e:
        log_event(f"[ERROR] Hedge-logik misslyckades för {symbol}: {e}", "ERROR")
        return False