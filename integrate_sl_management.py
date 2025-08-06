#!/usr/bin/env python3
"""
Integration script showing how to integrate SL management into the main trading system.
This demonstrates the complete workflow from signal to SL management.
"""

import asyncio
import time
from datetime import datetime
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
from core.entry_manager import execute_entry_strategy
from signal_module.multi_format_parser import parse_signal
from core.api import get_current_price_async

async def process_signal_with_sl_management(signal_text: str):
    """Process a signal and integrate SL management."""
    
    print(f"📡 Processing Signal: {signal_text}")
    print("-" * 50)
    
    # Step 1: Parse the signal
    parsed = await parse_signal(signal_text)
    if not parsed:
        print("❌ Failed to parse signal")
        return
    
    print(f"✅ Signal parsed:")
    print(f"   Symbol: {parsed.get('symbol', 'N/A')}")
    print(f"   Side: {parsed.get('side', 'N/A')}")
    print(f"   Entry: {parsed.get('entry', 'N/A')}")
    print(f"   SL: {parsed.get('sl', 'N/A')}")
    print(f"   TPs: {parsed.get('targets', [])}")
    
    # Step 2: Execute entry strategy
    symbol = parsed.get('symbol')
    side = parsed.get('side', 'buy').lower()
    
    if not symbol:
        print("❌ No symbol found in signal")
        return
    
    result = await execute_entry_strategy(
        symbol=symbol,
        side=side,
        risk_percent=1.0,
        leverage=10,
        step1_ratio=0.5
    )
    
    if not result['orders']:
        print("❌ Failed to place orders")
        return
    
    # Step 3: Register for SL management
    entry_price = result['orders'][0]['price']
    sl_price = result['orders'][0]['sl_price']
    tp_prices = [result['orders'][0]['tp_price']]  # Single TP for demo
    order_ids = [order['order_id'] for order in result['orders']]
    
    # Register for break-even monitoring
    await breakeven_manager.register_trade(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        sl_price=sl_price,
        tp_prices=tp_prices,
        order_ids=order_ids
    )
    
    # Register for trailing stop monitoring
    await trailing_manager.register_trade(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        sl_price=sl_price,
        tp_prices=tp_prices,
        order_ids=order_ids
    )
    
    print(f"✅ Trade registered for SL management:")
    print(f"   Break-even monitoring: ✅ Active")
    print(f"   Trailing stop monitoring: ✅ Active")
    
    return {
        "symbol": symbol,
        "side": side,
        "entry_price": entry_price,
        "sl_price": sl_price,
        "tp_prices": tp_prices,
        "order_ids": order_ids
    }

async def monitor_active_trades():
    """Monitor all active trades for SL adjustments."""
    
    print("\n📊 MONITORING ACTIVE TRADES")
    print("=" * 40)
    
    # Get all active trades
    breakeven_trades = list(breakeven_manager.active_trades.keys())
    trailing_trades = list(trailing_manager.active_trades.keys())
    
    print(f"📈 Active Trades:")
    print(f"   Break-even monitoring: {len(breakeven_trades)} trades")
    print(f"   Trailing monitoring: {len(trailing_trades)} trades")
    
    for symbol in breakeven_trades:
        breakeven_status = breakeven_manager.get_trade_status(symbol)
        trailing_status = trailing_manager.get_trade_status(symbol)
        
        print(f"\n   {symbol}:")
        print(f"     Break-even: {'✅' if breakeven_status['breakeven_triggered'] else '⏳'}")
        print(f"     Trailing: {'✅' if trailing_status['trailing_active'] else '⏳'}")
        print(f"     Current SL: ${breakeven_status['current_sl']:,.2f}")
        
        # Check for SL adjustments
        if await breakeven_manager.check_breakeven_conditions(symbol):
            await breakeven_manager.move_to_breakeven(symbol)
            print(f"     🎯 Break-even triggered!")
        
        if await trailing_manager.check_trailing_conditions(symbol):
            await trailing_manager.activate_trailing(symbol)
            print(f"     📈 Trailing activated!")
        
        if trailing_status['trailing_active']:
            await trailing_manager.update_trailing_stop(symbol)
            print(f"     📊 Trailing updated!")

async def demo_complete_workflow():
    """Demonstrate the complete workflow from signal to SL management."""
    
    print("🚀 COMPLETE SL MANAGEMENT WORKFLOW")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Sample signals to process
    signals = [
        "BTCUSDT LONG Entry: 67000 SL: 65000 TP: 69000, 70000, 72000",
        "ETHUSDT SHORT Entry: 3750 SL: 3850 TP: 3650, 3550, 3450",
        "SOLUSDT LONG Entry: 135 SL: 130 TP: 140, 145, 150"
    ]
    
    active_trades = []
    
    # Process each signal
    for i, signal in enumerate(signals, 1):
        print(f"📡 Processing Signal {i}:")
        trade_info = await process_signal_with_sl_management(signal)
        if trade_info:
            active_trades.append(trade_info)
        print()
    
    # Monitor trades for a few cycles
    print("🔄 MONITORING TRADES FOR SL ADJUSTMENTS")
    print("=" * 50)
    
    for cycle in range(3):
        print(f"\n📊 Monitoring Cycle {cycle + 1}:")
        await monitor_active_trades()
        await asyncio.sleep(2)  # Simulate real-time monitoring
    
    # Final status
    print("\n📊 FINAL STATUS")
    print("=" * 30)
    
    for trade in active_trades:
        symbol = trade['symbol']
        breakeven_status = breakeven_manager.get_trade_status(symbol)
        trailing_status = trailing_manager.get_trade_status(symbol)
        
        print(f"   {symbol}:")
        print(f"     Break-even: {'✅' if breakeven_status['breakeven_triggered'] else '⏳'}")
        print(f"     Trailing: {'✅' if trailing_status['trailing_active'] else '⏳'}")
        print(f"     Current SL: ${breakeven_status['current_sl']:,.2f}")
    
    print("\n✅ Complete workflow demo finished!")

async def demo_integration_with_main_loop():
    """Show how to integrate SL management into the main trading loop."""
    
    print("\n🔄 INTEGRATION WITH MAIN TRADING LOOP")
    print("=" * 50)
    
    print("📋 Integration Steps:")
    print("   1. Import SL managers in main loop")
    print("   2. Register trades after entry execution")
    print("   3. Add monitoring tasks to asyncio.gather()")
    print("   4. Handle SL adjustments in real-time")
    
    print("\n💻 Code Example:")
    print("""
# In runner/main.py or monitor/loop_manager.py:

from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager

async def trading_loop():
    while True:
        # ... existing trading logic ...
        
        # After placing orders, register for SL management
        if orders_placed:
            await breakeven_manager.register_trade(...)
            await trailing_manager.register_trade(...)
        
        await asyncio.sleep(5)

async def main():
    await asyncio.gather(
        start_telegram_listener(),
        trading_loop(),
        breakeven_manager.monitor_breakeven(),  # Add this
        trailing_manager.monitor_trailing()      # Add this
    )
    """)
    
    print("\n✅ Integration guide completed!")

if __name__ == "__main__":
    print("🚀 Starting SL Management Integration Demo...")
    asyncio.run(demo_complete_workflow())
    asyncio.run(demo_integration_with_main_loop())
    print(f"\n⚡ Integration demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 