from logic.order_executor import place_smart_order
from config.settings import DEFAULT_IM, RISK_PERCENT, OVERRIDE_LEVERAGE, FORCE_MARKET_ENTRY, OverrideConfig
from utils.logger import log_event
from config.strategy_control import is_strategy_enabled, log_strategy_status
from logic.order_router import place_conditional_order
from logic.order_executor import place_smart_order
from core.api import bitget_client as client  # eller rätt klientinstans
from utils.quantity import calculate_quantity
from utils.telegram_logger import send_telegram_log
from utils.leverage import calculate_leverage
from monitor.trade_state import create_trade_state, state

async def check_hedging_conflict(symbol: str, new_side: str, group_name: str = None) -> bool:
    """
    Check if there's a hedging conflict for the given symbol and side.
    
    Args:
        symbol: Trading symbol
        new_side: New trade side ("LONG" or "SHORT")
        group_name: Optional group name for logging
        
    Returns:
        True if hedging is blocked, False if trade can proceed
    """
    try:
        # Check if hedging is enabled
        if OverrideConfig.ENABLE_HEDGING:
            return False  # Hedging allowed, no conflict
        
        # Check for existing positions in the opposite direction
        if symbol in state:
            existing_trade = state[symbol]
            if existing_trade.position_active:
                existing_side = existing_trade.side
                
                # Check if sides are opposite
                if (existing_side.upper() == "LONG" and new_side.upper() == "SHORT") or \
                   (existing_side.upper() == "SHORT" and new_side.upper() == "LONG"):
                    
                    # Hedging conflict detected
                    log_message = f"[Hedging Blocked] Skipped {new_side} for {symbol} — existing {existing_side} position open and ENABLE_HEDGING=False"
                    
                    if group_name:
                        await send_telegram_log(log_message, group_name=group_name, tag="hedging")
                    else:
                        await send_telegram_log(log_message, tag="hedging")
                    
                    log_event(log_message, "WARNING")
                    return True  # Hedging blocked
        
        return False  # No conflict, trade can proceed
        
    except Exception as e:
        log_event(f"[ERROR] Failed to check hedging conflict for {symbol}: {e}", "ERROR")
        return False  # Allow trade to proceed on error

async def handle_entry_signal(signal):
    from monitor.trade_state import state
    from logic.sl_manager import update_sl
    from utils.telegram_logger import log_to_telegram

    symbol = signal.get("symbol")
    entry = signal.get("entry")
    sl = signal.get("sl")
    tp1 = signal.get("tp1")
    signal_side = signal.get("side", "").upper()  # "LONG" or "SHORT"
    side = "Buy" if signal_side == "LONG" else "Sell"
    group_name = signal.get("group_name")

    if not symbol or not entry or not sl or not tp1:
        log_event(f"[SKIPPED] Signal saknar nödvändig data: {signal}", "ERROR")
        return

    # Check for hedging conflicts
    hedging_blocked = await check_hedging_conflict(symbol, signal_side, group_name)
    if hedging_blocked:
        return  # Exit early if hedging is blocked

    # Get timeframe from signal or use default
    timeframe = signal.get("timeframe", "default")
    
    # Log strategy status for this trade
    log_strategy_status(symbol, group_name, timeframe)
    
    # Check if TP is enabled for this symbol/group/timeframe
    if not is_strategy_enabled("ENABLE_TP", symbol, group_name, timeframe):
        log_event(f"[StrategyOverride] TP disabled for {symbol} ({group_name}, {timeframe}) - skipping entry", "WARNING")
        return
    
    # Check if SL is enabled for this symbol/group/timeframe
    if not is_strategy_enabled("ENABLE_SL", symbol, group_name, timeframe):
        log_event(f"[StrategyOverride] SL disabled for {symbol} ({group_name}, {timeframe}) - skipping entry", "WARNING")
        return

    if isinstance(entry, str) and ("-" in entry or "–" in entry):
        delimiter = "-" if "-" in entry else "–"
        parts = entry.split(delimiter)
        try:
            entry = [float(parts[0].strip()), float(parts[1].strip())]
            log_event(f"[INFO] Konverterade entry-sträng till lista: {entry}", "INFO")
        except Exception as e:
            log_event(f"[SKIPPED] Kunde inte tolka entry-sträng: {entry} – {e}", "ERROR")
            return

    if isinstance(entry, list):
        if len(entry) != 2:
            log_event(f"[SKIPPED] Ogiltigt entry-format (lista måste ha 2 värden): {entry}", "ERROR")
            return
        entry1, entry2 = entry
    else:
        entry1 = round(entry * 0.998, 2)
        entry2 = round(entry * 1.002, 2)
        state.entry1 = entry1
        state.entry2 = entry2
        state.entry_price = (entry1 + entry2) / 2
        log_event(f"[INFO] Entry med ett värde, beräknar 2 nivåer: {entry1}, {entry2}", "INFO")

    lev = await calculate_leverage(entry1, sl)
    qty = calculate_quantity(DEFAULT_IM, lev, entry1)
    half_qty = qty / 2

    async def place_dual_limit_orders(symbol, side, entry1, entry2, half_qty, sl, tp1, lev):
        log_event(f"[LIMIT ORDER 1] {side} {half_qty} @ {entry1}", "INFO")
        log_event(f"[LIMIT ORDER 2] {side} {half_qty} @ {entry2}", "INFO")
        await send_telegram_log(f"📥 Limit Entry 1: {side} {half_qty:.4f} @ {entry1}")
        await send_telegram_log(f"📥 Limit Entry 2: {side} {half_qty:.4f} @ {entry2}")

        order_id1 = await place_smart_order(symbol, side, half_qty, entry1, sl, tp1, lev, "limit")
        if order_id1:
            await send_telegram_log(f"✅ Order 1 placerad: ID {order_id1}")
        else:
            await send_telegram_log("❌ Order 1 misslyckades")


        order_id2 = await place_smart_order(symbol, side, half_qty, entry2, sl, tp1, lev, "limit")
        if order_id2:
            await send_telegram_log(f"✅ Order 2 placerad: ID {order_id2}")
        else:
            await send_telegram_log("❌ Order 2 misslyckades")

        return order_id1, order_id2

    # 🔄 Kör båda ordrarna och hämta order-id
    order_id1, order_id2 = await place_dual_limit_orders(symbol, side, entry1, entry2, half_qty, sl, tp1, lev)

    # 🧠 Spara ID:n till state
    state.order_id = [order_id1, order_id2]

    # 🔒 Uppdatera SL för båda ordrarna
    await update_sl(symbol=symbol, side=side, new_sl=sl, quantity=qty, order_id=order_id1)
    await update_sl(symbol=symbol, side=side, new_sl=sl, quantity=qty, order_id=order_id2)

    # ⏰ Start timeout timer and break-even watcher for this trade
    side_for_timeout = "long" if signal_side == "LONG" else "short"
    tp_levels = signal.get("tp", [])
    
    try:
        await create_trade_state(
            symbol=symbol,
            side=side_for_timeout.upper(),
            entry_price=entry1,
            sl_price=sl,
            leverage=lev,
            initial_margin=DEFAULT_IM,
            quantity=qty,
            group_name=group_name
        )
        log_event(f"[TIMEOUT] Auto-close timer started for {symbol} (4h timeout)", "INFO")
        log_event(f"[BREAKEVEN] Break-even watcher started for {symbol} (trigger: {TradingConfig.BREAK_EVEN_TRIGGER}%)", "INFO")
        log_event(f"[TRAILING] Trailing watcher started for {symbol} (trigger: {TradingConfig.TRAILING_TRIGGER}%, offset: {TradingConfig.TRAILING_OFFSET}%)", "INFO")
        log_event(f"[PYRAMIDING] Pyramiding watcher started for {symbol} (max steps: {TradingConfig.MAX_PYRAMID_STEPS}, thresholds: {TradingConfig.PYRAMID_POL_THRESHOLDS}%)", "INFO")
    except Exception as e:
        log_event(f"[WARNING] Failed to start timers for {symbol}: {e}", "WARNING")

    log_event(f"[ENTRY] Signal mottagen för {symbol} @ {entry1}/{entry2} SL: {sl} Lev: x{lev}", "INFO")






