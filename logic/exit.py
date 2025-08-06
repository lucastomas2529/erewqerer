# exit.py – avsluta aktiv position på Bitget

from core.api import place_market_order, get_position
from core.symbol_data import get_symbol_precision
from config.settings import DEFAULT_SL_BUFFER
from monitor.trade_state import close_trade_state, state
from monitor.reporting import generate_trade_report
from config.strategy_control import is_strategy_enabled

import logging

logger = logging.getLogger(__name__)

async def exit_trade(symbol: str, side: str, group_name: str = None, timeframe: str = "default"):
    """
    Stänger en aktiv position på Bitget genom att placera en market-order i motsatt riktning.
    :param symbol: T.ex. 'BTCUSDT'
    :param side: 'long' eller 'short'
    :param group_name: Optional group name for logging
    :param timeframe: Timeframe for strategy control
    """
    try:
        # Check if manual exit is allowed for this symbol/group/timeframe
        if group_name and not is_strategy_enabled("ENABLE_MANUAL_EXIT", symbol, group_name, timeframe):
            logger.warning(f"[StrategyOverride] Manual exit disabled for {symbol} ({group_name}, {timeframe})")
            return
        
        position = get_position(symbol)
        if not position or float(position['total']) == 0:
            logger.info(f"Ingen öppen position för {symbol} att stänga.")
            return

        close_side = "close_long" if side == "long" else "close_short"
        qty = float(position['total'])
        precision = get_symbol_precision(symbol)
        qty = round(qty, precision['quantity'])

        logger.info(f"Stänger {side.upper()} position på {symbol} med qty={qty}")
        place_market_order(symbol=symbol, side=close_side, size=qty)
        
        # Get current price for reporting (placeholder - would need actual price)
        exit_price = 0  # Placeholder - would need to get actual exit price
        
        # Generate trade report before closing trade state
        try:
            if symbol in state:
                trade_state = state[symbol]
                # Get current price for accurate P&L calculation
                # This would need to be implemented with actual price fetching
                current_price = exit_price or trade_state.entry_price  # Fallback to entry price
                
                # Generate and send trade report
                await generate_trade_report(
                    trade_state=trade_state,
                    exit_price=current_price,
                    exit_reason="MANUAL",
                    group_name=group_name
                )
                logger.info(f"[REPORT] Trade report generated for {symbol}")
        except Exception as e:
            logger.warning(f"[REPORT] Failed to generate trade report for {symbol}: {e}")
        
        # Cancel timeout timer and break-even watcher for this trade
        try:
            await close_trade_state(symbol, group_name)
            logger.info(f"[Auto-Close] Timeout cancelled for {symbol} (position closed manually)")
            logger.info(f"[Break-Even] Watcher cancelled for {symbol} (position closed manually)")
            logger.info(f"[Trailing] Watcher cancelled for {symbol} (position closed manually)")
            logger.info(f"[Pyramiding] Watcher cancelled for {symbol} (position closed manually)")
            
            # Start re-entry watcher if re-entry is enabled
            from config.settings import TradingConfig
            if TradingConfig.REENTRY_ENABLED:
                from monitor.reentry_watcher import start_reentry_watcher
                # Note: We would need the original signal data here
                # For now, we'll create a basic signal structure
                original_signal = {
                    "symbol": symbol,
                    "side": side,
                    "entry": [0],  # Placeholder - would need actual entry price
                    "sl": 0,       # Placeholder - would need actual SL price
                    "tp": [1.5, 3.0, 6.0, 10.0]  # Default TP levels
                }
                await start_reentry_watcher(symbol, original_signal, 0, "manual", group_name)
                logger.info(f"[Re-entry] Re-entry watcher started for {symbol} after manual exit")
        except Exception as e:
            logger.warning(f"[Auto-Close] Failed to cancel timers for {symbol}: {e}")

    except Exception as e:
        logger.error(f"Fel vid stängning av {symbol} position: {e}")

# Backward compatibility function
def exit_trade_sync(symbol: str, side: str):
    """
    Synchronous version of exit_trade for backward compatibility.
    """
    try:
        position = get_position(symbol)
        if not position or float(position['total']) == 0:
            logger.info(f"Ingen öppen position för {symbol} att stänga.")
            return

        close_side = "close_long" if side == "long" else "close_short"
        qty = float(position['total'])
        precision = get_symbol_precision(symbol)
        qty = round(qty, precision['quantity'])

        logger.info(f"Stänger {side.upper()} position på {symbol} med qty={qty}")
        place_market_order(symbol=symbol, side=close_side, size=qty)

    except Exception as e:
        logger.error(f"Fel vid stängning av {symbol} position: {e}")

# Alias for backward compatibility
exit_trade = exit_trade_sync

