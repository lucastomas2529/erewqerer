#!/usr/bin/env python3
"""
Comprehensive test script for timeout protection system.
Tests trade registration, duration tracking, and auto-closure.
"""

import asyncio
import time
from datetime import datetime, timedelta
from core.timeout_manager import timeout_manager
from core.entry_manager import execute_entry_strategy
from core.api import get_current_price_async

async def test_timeout_system_comprehensive():
    """Comprehensive test of timeout protection system."""
    
    print("⏰ TIMEOUT PROTECTION SYSTEM TEST")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Basic timeout functionality
    print("📊 TEST 1: Basic Timeout Functionality")
    print("-" * 40)
    
    # Place a test trade
    result = await execute_entry_strategy(
        symbol="BTCUSDT",
        side="buy",
        risk_percent=1.0,
        leverage=10,
        step1_ratio=0.5
    )
    
    if result['orders']:
        # Register trade for timeout monitoring
        entry_price = result['orders'][0]['price']
        sl_price = result['orders'][0]['sl_price']
        tp_prices = [result['orders'][0]['tp_price']]
        order_ids = [order['order_id'] for order in result['orders']]
        quantity = 0.001  # Mock quantity
        
        await timeout_manager.register_trade(
            symbol="BTCUSDT",
            side="buy",
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=tp_prices,
            order_ids=order_ids,
            quantity=quantity
        )
        
        print(f"✅ Trade registered for timeout monitoring:")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   Timeout: {timeout_manager.timeout_hours} hours")
        print(f"   Check interval: {timeout_manager.check_interval} seconds")
        
        # Test timeout conditions
        timeout_met = await timeout_manager.check_timeout_conditions("BTCUSDT")
        print(f"   Timeout conditions met: {timeout_met}")
        
        # Show trade status
        status = timeout_manager.get_trade_status("BTCUSDT")
        print(f"   Duration: {status['duration_hours']:.4f} hours")
        print(f"   Remaining: {timeout_manager.timeout_hours - status['duration_hours']:.4f} hours")
    
    print()
    
    # Test 2: Multiple trades with different scenarios
    print("📊 TEST 2: Multiple Trades Scenario")
    print("-" * 40)
    
    # Register multiple trades
    trades = [
        {
            "symbol": "ETHUSDT",
            "side": "buy",
            "entry": 3750.0,
            "sl": 3650.0,
            "tp": 3900.0,
            "quantity": 0.1
        },
        {
            "symbol": "SOLUSDT",
            "side": "sell",
            "entry": 135.0,
            "sl": 140.0,
            "tp": 130.0,
            "quantity": 10.0
        },
        {
            "symbol": "ADAUSDT",
            "side": "buy",
            "entry": 0.50,
            "sl": 0.48,
            "tp": 0.55,
            "quantity": 1000.0
        }
    ]
    
    for trade in trades:
        await timeout_manager.register_trade(
            symbol=trade["symbol"],
            side=trade["side"],
            entry_price=trade["entry"],
            sl_price=trade["sl"],
            tp_prices=[trade["tp"]],
            order_ids=[f"mock_{trade['symbol']}_1", f"mock_{trade['symbol']}_2"],
            quantity=trade["quantity"]
        )
        print(f"✅ {trade['symbol']} registered for timeout monitoring")
    
    print()
    
    # Test 3: Duration tracking
    print("📊 TEST 3: Duration Tracking")
    print("-" * 40)
    
    # Wait a bit to simulate time passing
    print("⏳ Simulating time passage...")
    await asyncio.sleep(2)
    
    # Check all trades
    all_status = timeout_manager.get_all_trades_status()
    print(f"📈 Active Trades: {all_status['active_trades']}")
    print(f"⏰ Timeout: {all_status['timeout_hours']} hours")
    
    for symbol, trade_info in all_status['trades'].items():
        print(f"\n   {symbol}:")
        print(f"     Duration: {trade_info['duration_hours']:.4f} hours")
        print(f"     Remaining: {trade_info['remaining_hours']:.4f} hours")
        print(f"     Status: Active")
    
    print()
    
    # Test 4: Simulate timeout scenario
    print("📊 TEST 4: Simulate Timeout Scenario")
    print("-" * 40)
    
    # Create a trade that's already "old" for testing
    old_trade = {
        "symbol": "TESTUSDT",
        "side": "buy",
        "entry_price": 100.0,
        "sl_price": 95.0,
        "tp_prices": [105.0],
        "order_ids": ["old_order_1", "old_order_2"],
        "quantity": 1.0,
        "entry_timestamp": time.time() - (5 * 3600),  # 5 hours ago
        "entry_datetime": datetime.now() - timedelta(hours=5),
        "timeout_triggered": False,
        "status": "active"
    }
    
    timeout_manager.active_trades["TESTUSDT"] = old_trade
    
    print(f"📊 Created old trade TESTUSDT (5 hours old)")
    print(f"   Entry time: {old_trade['entry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Duration: {timeout_manager.get_trade_duration('TESTUSDT'):.2f} hours")
    
    # Test timeout conditions
    timeout_met = await timeout_manager.check_timeout_conditions("TESTUSDT")
    print(f"   Timeout conditions met: {timeout_met}")
    
    if timeout_met:
        print("   ⏰ Trade should be closed due to timeout!")
        # Note: We won't actually close it in the test to avoid API calls
        print("   (Skipping actual closure for test purposes)")
    
    print()
    
    # Test 5: Configuration validation
    print("📊 TEST 5: Configuration Validation")
    print("-" * 40)
    
    from config.settings import TradingConfig
    
    configs = {
        "Timeout hours": TradingConfig.TIMEOUT_HOURS,
        "Check interval": TradingConfig.TIMEOUT_CHECK_INTERVAL,
        "Check interval (seconds)": TradingConfig.TIMEOUT_CHECK_INTERVAL
    }
    
    print("📋 Current Configuration:")
    for name, value in configs.items():
        print(f"   {name}: {value}")
    
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    # Get status of all registered trades
    all_status = timeout_manager.get_all_trades_status()
    
    print(f"✅ Total trades registered: {all_status['total_trades']}")
    print(f"✅ Active trades: {all_status['active_trades']}")
    print(f"✅ Timeout hours: {all_status['timeout_hours']}")
    
    for symbol in timeout_manager.active_trades.keys():
        status = timeout_manager.get_trade_status(symbol)
        duration = status['duration_hours']
        remaining = timeout_manager.timeout_hours - duration
        print(f"   {symbol}: {duration:.4f}h elapsed, {remaining:.4f}h remaining")
    
    print()
    print("🎉 TIMEOUT PROTECTION TEST COMPLETED!")
    print(f"⚡ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_monitoring_loop():
    """Test the monitoring loop for timeout protection."""
    print("\n🔄 TESTING MONITORING LOOP")
    print("=" * 40)
    
    # Start monitoring loop in background
    timeout_task = asyncio.create_task(timeout_manager.monitor_timeout())
    
    print("⏰ Timeout monitoring loop started...")
    print("   Monitoring: ✅ Active")
    print("   Check interval: 60 seconds")
    
    # Let it run for a few seconds
    await asyncio.sleep(10)
    
    # Cancel the task
    timeout_task.cancel()
    
    try:
        await timeout_task
    except asyncio.CancelledError:
        pass
    
    print("✅ Timeout monitoring loop stopped")

if __name__ == "__main__":
    print("⏰ Starting Timeout Protection System Test...")
    asyncio.run(test_timeout_system_comprehensive())
    asyncio.run(test_monitoring_loop()) 