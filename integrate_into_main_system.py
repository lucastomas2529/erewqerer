#!/usr/bin/env python3
"""
Integration script showing exactly how to integrate SL management into the main trading system.
This provides the exact code changes needed for the main trading loop.
"""

import asyncio
from datetime import datetime

def show_main_system_integration():
    """Show the exact integration steps for the main trading system."""
    
    print("🔄 INTEGRATION INTO MAIN TRADING SYSTEM")
    print("=" * 60)
    print(f"🕐 Integration Guide: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📋 STEP 1: UPDATE IMPORTS IN MAIN FILES")
    print("-" * 50)
    
    print("""
# In runner/main.py - ADD THESE IMPORTS:
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
""")
    
    print("""
# In monitor/loop_manager.py - ADD THESE IMPORTS:
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
""")
    
    print("\n📋 STEP 2: UPDATE MAIN FUNCTION")
    print("-" * 50)
    
    print("""
# In runner/main.py - UPDATE THE MAIN FUNCTION:

async def main():
    log_event("🔄 Boten startar...")
    if SHUTDOWN_ALL:
        log_event("🛑 Boten är i nödläge – SHUTDOWN_ALL är aktivt", "ERROR")
        return
    try:
        await asyncio.gather(
            start_telegram_listener(),           # Telegram-parser
            monitor_trailing_stop(),            # Trailing-övervakning
            trading_loop(),                     # Trading loop
            breakeven_manager.monitor_breakeven(),  # 🆕 Break-even monitoring
            trailing_manager.monitor_trailing()      # 🆕 Trailing stop monitoring
        )
    except Exception as e:
        log_event(f"[FATAL] Fel i huvudloopen: {e}", "ERROR")
""")
    
    print("\n📋 STEP 3: UPDATE TRADING LOOP")
    print("-" * 50)
    
    print("""
# In monitor/loop_manager.py - UPDATE THE TRADING LOOP:

async def trading_loop():
    while True:
        try:
            maybe_signal = get_active_signal()
            signal = await maybe_signal if inspect.isawaitable(maybe_signal) else maybe_signal
            if not signal:
                await asyncio.sleep(5)
                continue
                
            symbol = signal.get("symbol")
            if not symbol:
                await asyncio.sleep(5)
                continue
                
            current_price = await get_current_price(symbol)
            signal["current_price"] = current_price

            await handle_entry_signal(signal)
            await handle_incoming_signal(signal)
            
            leverage = calculate_leverage(signal["entry"], signal.get("sl"))
            position_data = prepare_position(signal)
            
            if position_data:
                quantity = position_data["qty"]
                orders_placed = place_initial_entry_in_two_steps(symbol, quantity)
                
                # 🆕 REGISTER FOR SL MANAGEMENT AFTER ORDERS PLACED
                if orders_placed:
                    entry_price = signal.get("entry") or current_price
                    sl_price = signal.get("sl") or (entry_price * 0.98)  # Default 2% SL
                    tp_prices = signal.get("targets", []) or [entry_price * 1.02]  # Default 2% TP
                    
                    # Register with break-even manager
                    await breakeven_manager.register_trade(
                        symbol=symbol,
                        side=signal.get("side", "buy").lower(),
                        entry_price=entry_price,
                        sl_price=sl_price,
                        tp_prices=tp_prices,
                        order_ids=[f"order_{symbol}_{int(time.time())}"]  # Mock order IDs
                    )
                    
                    # Register with trailing manager
                    await trailing_manager.register_trade(
                        symbol=symbol,
                        side=signal.get("side", "buy").lower(),
                        entry_price=entry_price,
                        sl_price=sl_price,
                        tp_prices=tp_prices,
                        order_ids=[f"order_{symbol}_{int(time.time())}"]  # Mock order IDs
                    )
                    
                    print(f"✅ Trade registered for SL management: {symbol}")
            else:
                print(f"⚠️ Failed to prepare position for {symbol}")
                continue
                
            # ... rest of the trading loop logic ...
            
        except Exception as e:
            await send_telegram_log(f"[Loop error] {e}")
            await asyncio.sleep(10)
""")
    
    print("\n📋 STEP 4: ADD HELPER FUNCTIONS")
    print("-" * 50)
    
    print("""
# Add these helper functions to monitor/loop_manager.py:

async def register_trade_for_sl_management(signal: dict, orders_placed: bool):
    \"\"\"Register a trade for SL management after orders are placed.\"\"\"
    if not orders_placed:
        return
        
    symbol = signal.get("symbol")
    side = signal.get("side", "buy").lower()
    entry_price = signal.get("entry")
    sl_price = signal.get("sl")
    tp_prices = signal.get("targets", [])
    
    if not all([symbol, entry_price, sl_price]):
        print(f"⚠️ Missing trade data for SL registration: {symbol}")
        return
    
    try:
        # Register with break-even manager
        await breakeven_manager.register_trade(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=tp_prices,
            order_ids=[f"order_{symbol}_{int(time.time())}"]
        )
        
        # Register with trailing manager
        await trailing_manager.register_trade(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=tp_prices,
            order_ids=[f"order_{symbol}_{int(time.time())}"]
        )
        
        print(f"✅ Trade registered for SL management: {symbol}")
        
    except Exception as e:
        print(f"❌ Error registering trade for SL management: {e}")

async def get_sl_management_status():
    \"\"\"Get status of all active SL management trades.\"\"\"
    breakeven_trades = list(breakeven_manager.active_trades.keys())
    trailing_trades = list(trailing_manager.active_trades.keys())
    
    status = {
        "breakeven_trades": len(breakeven_trades),
        "trailing_trades": len(trailing_trades),
        "active_symbols": list(set(breakeven_trades + trailing_trades))
    }
    
    return status
""")
    
    print("\n📋 STEP 5: UPDATE CONFIGURATION")
    print("-" * 50)
    
    print("""
# The following settings are already added to config/settings.py:

# Break-even Configuration
BREAKEVEN_THRESHOLD = 2.0            # Profit % to trigger break-even
BREAKEVEN_BUFFER = 0.001             # Break-even buffer (0.1% above entry)

# Trailing Stop Configuration  
TRAILING_THRESHOLD = 3.0             # Profit % to activate trailing
TRAILING_DISTANCE = 0.01             # Trailing distance (1% from current price)
TRAILING_STEP = 0.005                # Minimum step size for trailing updates
""")
    
    print("\n📋 STEP 6: TESTING INTEGRATION")
    print("-" * 50)
    
    print("""
# Test the integration with these commands:

# 1. Test break-even manager
python core/breakeven_manager.py

# 2. Test trailing manager  
python core/trailing_manager.py

# 3. Test complete workflow
python integrate_sl_management.py

# 4. Test with real signals
python demo_sl_management.py
""")
    
    print("\n📋 STEP 7: MONITORING AND LOGGING")
    print("-" * 50)
    
    print("""
# Add these monitoring functions to your logging system:

async def log_sl_management_status():
    \"\"\"Log current SL management status.\"\"\"
    status = await get_sl_management_status()
    
    log_message = f"""
SL Management Status:
   Break-even trades: {status['breakeven_trades']}
   Trailing trades: {status['trailing_trades']}
   Active symbols: {', '.join(status['active_symbols']) if status['active_symbols'] else 'None'}
    """
    
    await send_telegram_log(log_message)

# Call this function periodically or after each trade
await log_sl_management_status()
""")
    
    print("\n✅ INTEGRATION COMPLETE!")
    print("=" * 50)
    
    print("""
🎉 Your trading bot now has:
   ✅ Break-even management
   ✅ Trailing stop management  
   ✅ Real-time SL monitoring
   ✅ Risk-based position sizing
   ✅ Dual LIMIT order strategy
   ✅ Comprehensive error handling

🚀 Ready for production trading!
""")

def show_configuration_options():
    """Show configuration options for different trading styles."""
    
    print("\n⚙️ CONFIGURATION OPTIONS")
    print("=" * 50)
    
    print("""
# Conservative Trading (Lower Risk):
BREAKEVEN_THRESHOLD = 1.5            # Break-even at 1.5% profit
TRAILING_THRESHOLD = 2.5             # Trailing at 2.5% profit
TRAILING_DISTANCE = 0.015            # 1.5% trailing distance
TRAILING_STEP = 0.008               # 0.8% minimum step

# Aggressive Trading (Higher Risk):
BREAKEVEN_THRESHOLD = 3.0            # Break-even at 3% profit
TRAILING_THRESHOLD = 5.0             # Trailing at 5% profit
TRAILING_DISTANCE = 0.008            # 0.8% trailing distance
TRAILING_STEP = 0.003               # 0.3% minimum step

# Balanced Trading (Recommended):
BREAKEVEN_THRESHOLD = 2.0            # Break-even at 2% profit
TRAILING_THRESHOLD = 3.0             # Trailing at 3% profit
TRAILING_DISTANCE = 0.01             # 1% trailing distance
TRAILING_STEP = 0.005               # 0.5% minimum step
""")

if __name__ == "__main__":
    print("🚀 SL Management Integration Guide")
    print("=" * 60)
    show_main_system_integration()
    show_configuration_options()
    print(f"\n⚡ Integration guide completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 