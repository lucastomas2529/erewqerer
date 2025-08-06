import random
import asyncio
import time
from config.settings import REENTRY_DELAY_SEC as REENTRY_DELAY_RANGE, MAX_REENTRIES, DEFAULT_IM, LEVERAGE_CAP
from utils.logger import log_event
from utils.leverage import calculate_leverage
from utils.quantity import calculate_quantity
from logic.order_router import place_conditional_order
from utils.telegram_logger import send_telegram_log
from config.strategy_control import is_strategy_enabled

# Global re-entry tracking
reentry_state = {}

# EMA-baserad bekräftelse för re-entry
async def ema_confirms_reentry(symbol: str, timeframe: str = "1m", period: int = 21) -> bool:
    """
    Kontrollera om EMA21 bekräftar riktning för re-entry.
    """
    try:
        # Placeholder logic for EMA confirmation
        print(f"📊 EMA21 bekräftelse för {symbol} på {timeframe}")
        return True  # Mock confirmation
    except Exception as e:
        await send_telegram_log(f"❌ EMA-fel för {symbol}: {e}")
        return False

async def rsi_confirms_reentry(symbol: str, timeframe: str = "1m", period: int = 14) -> bool:
    """
    Kontrollera RSI-nivå för re-entry-bekräftelse.
    """
    try:
        # Placeholder logic for RSI confirmation
        print(f"📊 RSI bekräftelse för {symbol}")
        return True  # Mock confirmation
    except Exception as e:
        await send_telegram_log(f"❌ Fel vid RSI-kontroll för {symbol}: {e}")
        return False

async def check_reentry_conditions(symbol, entry_price, sl_price, side, reentry_count, current_price, group_name: str = None, timeframe: str = "default"):
    """
    Kontrollera om re-entry kan genomföras.
    ✅ Tidsgräns (90-180s)
    ✅ Max 3 re-entries
    ✅ Pris inte rört sig för mycket
    ✅ Strategy control override
    """
    
    # Check if re-entry is enabled for this symbol/group/timeframe
    if group_name and not is_strategy_enabled("ENABLE_REENTRY", symbol, group_name, timeframe):
        await send_telegram_log(f"❌ [StrategyOverride] Re-entry disabled for {symbol} ({group_name}, {timeframe})", tag="reentry")
        return False
    
    if reentry_count >= MAX_REENTRIES:
        await send_telegram_log(f"❌ Max re-entries nått för {symbol} ({reentry_count})", tag="reentry")
        return False
    
    # Kontrollera tidsgräns
    last_attempt = reentry_state.get(symbol, {}).get("last_attempt", 0)
    time_since_last = time.time() - last_attempt
    min_delay = REENTRY_DELAY_RANGE[0]
    
    if time_since_last < min_delay:
        remaining = min_delay - time_since_last
        await send_telegram_log(f"⏰ Re-entry för {symbol} väntar {remaining:.0f}s", tag="reentry")
        return False
    
    # Kontrollera prisavvikelse
    price_change = abs(current_price - entry_price) / entry_price
    if price_change > 0.05:  # 5% max avvikelse
        await send_telegram_log(f"❌ Pris rört sig för mycket för {symbol}: {price_change:.1%}", tag="reentry")
        return False
    
    # EMA & RSI bekräftelse
    ema_ok = await ema_confirms_reentry(symbol)
    rsi_ok = await rsi_confirms_reentry(symbol)
    
    if not (ema_ok and rsi_ok):
        await send_telegram_log(f"❌ Tekniska indikatorer avråder re-entry för {symbol}", tag="reentry")
        return False
    
    return True

async def place_reentry_order(symbol: str, side: str, entry_price: float, sl_price: float, leverage: float, quantity: float) -> dict:
    """
    Placera re-entry order efter SL träffad.
    """
    try:
        await send_telegram_log(f"📤 REENTRY: {side} {quantity} {symbol} @ {entry_price}", tag="reentry")
        
        # Update reentry tracking
        if symbol not in reentry_state:
            reentry_state[symbol] = {"count": 0}
        
        reentry_state[symbol]["count"] += 1
        reentry_state[symbol]["last_attempt"] = time.time()
        
        # Calculate new leverage
        new_leverage = await calculate_leverage(entry_price, sl_price)
        leverage = min(new_leverage, LEVERAGE_CAP)
        
        # Calculate quantity
        new_quantity = calculate_quantity(DEFAULT_IM, leverage, entry_price)
        
        # Mock order placement
        order_data = {
            "symbol": symbol,
            "side": side,
            "quantity": new_quantity,
            "price": entry_price,
            "leverage": leverage,
            "stop_loss": sl_price
        }
        
        print(f"📤 RE-ENTRY ORDER: {order_data}")
        
        result = {
            "order_id": f"reentry_{symbol}_{int(time.time())}",
            "status": "NEW",
            "symbol": symbol,
            "side": side,
            "quantity": new_quantity,
            "price": entry_price
        }
        
        await send_telegram_log(f"✅ Re-entry #{reentry_state[symbol]['count']} placerad för {symbol}", tag="reentry")
        return result
        
    except Exception as e:
        log_event(f"[ERROR] Re-entry-fel för {symbol}: {e}", "ERROR")
        return {"error": str(e)}