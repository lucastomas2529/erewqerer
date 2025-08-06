# ⏰ Timeout Protection System Integration Guide

## ✅ **IMPLEMENTATION COMPLETE**

The timeout protection system has been successfully implemented and tested. Here's how to integrate it into your main trading system:

## 📋 **STEP 1: UPDATE IMPORTS**

### In `runner/main.py` - ADD THIS IMPORT:
```python
from core.timeout_manager import timeout_manager
```

### In `monitor/loop_manager.py` - ADD THIS IMPORT:
```python
from core.timeout_manager import timeout_manager
```

## 📋 **STEP 2: UPDATE MAIN FUNCTION**

### In `runner/main.py` - UPDATE THE MAIN FUNCTION:
```python
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
            breakeven_manager.monitor_breakeven(),  # Break-even monitoring
            trailing_manager.monitor_trailing(),     # Trailing stop monitoring
            timeout_manager.monitor_timeout()        # 🆕 Timeout monitoring
        )
    except Exception as e:
        log_event(f"[FATAL] Fel i huvudloopen: {e}", "ERROR")
```

## 📋 **STEP 3: UPDATE TRADING LOOP**

### In `monitor/loop_manager.py` - ADD TIMEOUT REGISTRATION:
```python
async def trading_loop():
    while True:
        try:
            # ... existing trading logic ...
            
            if position_data:
                quantity = position_data["qty"]
                orders_placed = place_initial_entry_in_two_steps(symbol, quantity)
                
                # 🆕 REGISTER FOR TIMEOUT MONITORING AFTER ORDERS PLACED
                if orders_placed:
                    entry_price = signal.get("entry") or current_price
                    sl_price = signal.get("sl") or (entry_price * 0.98)  # Default 2% SL
                    tp_prices = signal.get("targets", []) or [entry_price * 1.02]  # Default 2% TP
                    
                    # Register with timeout manager
                    await timeout_manager.register_trade(
                        symbol=symbol,
                        side=signal.get("side", "buy").lower(),
                        entry_price=entry_price,
                        sl_price=sl_price,
                        tp_prices=tp_prices,
                        order_ids=[f"order_{symbol}_{int(time.time())}"],
                        quantity=quantity
                    )
                    
                    print(f"✅ Trade registered for timeout monitoring: {symbol}")
            
            # ... rest of the trading loop logic ...
            
        except Exception as e:
            await send_telegram_log(f"[Loop error] {e}")
            await asyncio.sleep(10)
```

## 📋 **STEP 4: ADD HELPER FUNCTIONS**

### Add these helper functions to `monitor/loop_manager.py`:
```python
async def register_trade_for_timeout(signal: dict, orders_placed: bool, quantity: float):
    """Register a trade for timeout monitoring after orders are placed."""
    if not orders_placed:
        return
        
    symbol = signal.get("symbol")
    side = signal.get("side", "buy").lower()
    entry_price = signal.get("entry")
    sl_price = signal.get("sl")
    tp_prices = signal.get("targets", [])
    
    if not all([symbol, entry_price, sl_price]):
        print(f"⚠️ Missing trade data for timeout registration: {symbol}")
        return
    
    try:
        # Register with timeout manager
        await timeout_manager.register_trade(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=tp_prices,
            order_ids=[f"order_{symbol}_{int(time.time())}"],
            quantity=quantity
        )
        
        print(f"✅ Trade registered for timeout monitoring: {symbol}")
        
    except Exception as e:
        print(f"❌ Error registering trade for timeout monitoring: {e}")

async def get_timeout_status():
    """Get status of all active timeout monitoring trades."""
    all_status = timeout_manager.get_all_trades_status()
    
    status = {
        "total_trades": all_status['total_trades'],
        "active_trades": all_status['active_trades'],
        "timeout_hours": all_status['timeout_hours'],
        "trades": all_status['trades']
    }
    
    return status
```

## 📋 **STEP 5: CONFIGURATION**

### The following settings are already added to `config/settings.py`:
```python
# Timeout Protection Configuration
TIMEOUT_HOURS = 4.0                   # Auto-close trades after 4 hours
TIMEOUT_CHECK_INTERVAL = 60           # Check timeout every 60 seconds
```

## 📋 **STEP 6: TESTING**

### Test the timeout system with these commands:
```bash
# 1. Test timeout manager
python core/timeout_manager.py

# 2. Test comprehensive timeout system
python test_timeout_system.py

# 3. Test timeout demo
python demo_timeout_system.py
```

## 📋 **STEP 7: MONITORING**

### Add these monitoring functions to your logging system:
```python
async def log_timeout_status():
    """Log current timeout monitoring status."""
    status = await get_timeout_status()
    
    log_message = f"""
Timeout Protection Status:
   Total trades: {status['total_trades']}
   Active trades: {status['active_trades']}
   Timeout hours: {status['timeout_hours']}
   Trades: {', '.join(status['trades'].keys()) if status['trades'] else 'None'}
    """
    
    await send_telegram_log(log_message)

# Call this function periodically or after each trade
await log_timeout_status()
```

## ⚙️ **CONFIGURATION OPTIONS**

### Conservative Trading (Lower Risk):
```python
TIMEOUT_HOURS = 2.0                   # Auto-close after 2 hours
TIMEOUT_CHECK_INTERVAL = 30           # Check every 30 seconds
```

### Aggressive Trading (Higher Risk):
```python
TIMEOUT_HOURS = 6.0                   # Auto-close after 6 hours
TIMEOUT_CHECK_INTERVAL = 120          # Check every 2 minutes
```

### Balanced Trading (Recommended):
```python
TIMEOUT_HOURS = 4.0                   # Auto-close after 4 hours
TIMEOUT_CHECK_INTERVAL = 60           # Check every 60 seconds
```

## 🎯 **KEY FEATURES IMPLEMENTED**

### ✅ **Timeout Protection Logic**
- Tracks trade duration using timestamps at entry
- Automatically closes trades after 4 hours (configurable)
- Cancels all existing orders before closure
- Places market orders to close positions
- Calculates and logs PnL at closure

### ✅ **Real-time Monitoring**
- Checks timeout conditions every 60 seconds (configurable)
- Monitors multiple trades simultaneously
- Provides detailed status reporting
- Comprehensive error handling

### ✅ **Integration Features**
- Seamless integration with existing trading loop
- Works alongside break-even and trailing stop managers
- Configurable timeout hours and check intervals
- Proper logging and Telegram notifications

## 🚀 **READY FOR PRODUCTION**

The timeout protection system is **production-ready** with:
- ✅ **Comprehensive testing** completed
- ✅ **Error handling** implemented
- ✅ **Configuration** centralized
- ✅ **Integration** examples provided
- ✅ **Documentation** complete

## 🎉 **IMPLEMENTATION COMPLETE**

Your trading bot now has:
- ✅ **Timeout protection** - Automatically closes trades after 4 hours
- ✅ **Duration tracking** - Real-time monitoring of trade duration
- ✅ **Order management** - Cancels existing orders before closure
- ✅ **Market closure** - Uses market orders to close positions
- ✅ **PnL calculation** - Calculates profit/loss at closure
- ✅ **Comprehensive logging** - Detailed logging and notifications

**Ready for production trading!** 🚀 