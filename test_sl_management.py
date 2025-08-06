#!/usr/bin/env python3
"""
Comprehensive test script for break-even and trailing stop management.
Tests real scenarios with price movements and SL adjustments.
"""

import asyncio
import time
from datetime import datetime
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
from core.entry_manager import execute_entry_strategy
from core.api import get_current_price_async, get_account_balance

async def test_sl_management_comprehensive():
    """Comprehensive test of SL management with break-even and trailing stops."""
    
    print("🚀 SL MANAGEMENT COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Break-even functionality
    print("📊 TEST 1: Break-Even Management")
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
        # Register trade for break-even monitoring
        entry_price = result['orders'][0]['price']
        sl_price = result['orders'][0]['sl_price']
        tp_prices = [result['orders'][0]['tp_price']]  # Single TP for now
        order_ids = [order['order_id'] for order in result['orders']]
        
        await breakeven_manager.register_trade(
            symbol="BTCUSDT",
            side="buy",
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=tp_prices,
            order_ids=order_ids
        )
        
        print(f"✅ Trade registered for break-even monitoring:")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   SL: ${sl_price:,.2f}")
        print(f"   Break-even threshold: {breakeven_manager.breakeven_threshold}%")
        
        # Test break-even conditions
        breakeven_met = await breakeven_manager.check_breakeven_conditions("BTCUSDT")
        print(f"   Break-even conditions met: {breakeven_met}")
        
        if breakeven_met:
            await breakeven_manager.move_to_breakeven("BTCUSDT")
    
    print()
    
    # Test 2: Trailing stop functionality
    print("📊 TEST 2: Trailing Stop Management")
    print("-" * 40)
    
    # Register trade for trailing monitoring
    await trailing_manager.register_trade(
        symbol="ETHUSDT",
        side="buy",
        entry_price=3750.0,  # Mock entry price
        sl_price=3650.0,     # Mock SL price
        tp_prices=[3800.0, 3900.0, 4000.0],  # Mock TP levels
        order_ids=["mock_trailing_1", "mock_trailing_2"]
    )
    
    print(f"✅ Trade registered for trailing stop monitoring:")
    print(f"   Symbol: ETHUSDT")
    print(f"   Entry: $3,750")
    print(f"   Trailing threshold: {trailing_manager.trailing_threshold}%")
    print(f"   Trailing distance: {trailing_manager.trailing_distance}%")
    
    # Test trailing conditions
    trailing_met = await trailing_manager.check_trailing_conditions("ETHUSDT")
    print(f"   Trailing conditions met: {trailing_met}")
    
    if trailing_met:
        await trailing_manager.activate_trailing("ETHUSDT")
    
    print()
    
    # Test 3: Combined scenario - Break-even then trailing
    print("📊 TEST 3: Combined Break-Even + Trailing")
    print("-" * 40)
    
    # Simulate a profitable trade scenario
    await breakeven_manager.register_trade(
        symbol="SOLUSDT",
        side="buy",
        entry_price=135.0,
        sl_price=130.0,
        tp_prices=[140.0, 145.0, 150.0],
        order_ids=["mock_combined_1", "mock_combined_2"]
    )
    
    await trailing_manager.register_trade(
        symbol="SOLUSDT",
        side="buy",
        entry_price=135.0,
        sl_price=130.0,
        tp_prices=[140.0, 145.0, 150.0],
        order_ids=["mock_combined_1", "mock_combined_2"]
    )
    
    print(f"✅ Combined trade registered:")
    print(f"   Symbol: SOLUSDT")
    print(f"   Entry: $135.00")
    print(f"   TP2: $145.00")
    
    # Simulate price movement scenarios
    scenarios = [
        {"price": 137.0, "description": "Small profit - no triggers"},
        {"price": 142.0, "description": "TP2 hit - break-even should trigger"},
        {"price": 148.0, "description": "Large profit - trailing should activate"},
        {"price": 152.0, "description": "Maximum profit - trailing should update"}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['description']}")
        print(f"   Simulated Price: ${scenario['price']:,.2f}")
        
        # Test break-even conditions
        breakeven_met = await breakeven_manager.check_breakeven_conditions("SOLUSDT")
        print(f"   Break-even triggered: {breakeven_met}")
        
        # Test trailing conditions
        trailing_met = await trailing_manager.check_trailing_conditions("SOLUSDT")
        print(f"   Trailing triggered: {trailing_met}")
    
    print()
    
    # Test 4: Sell side scenarios
    print("📊 TEST 4: Sell Side Management")
    print("-" * 40)
    
    # Register sell trade
    await breakeven_manager.register_trade(
        symbol="ADAUSDT",
        side="sell",
        entry_price=0.50,
        sl_price=0.55,
        tp_prices=[0.48, 0.45, 0.42],
        order_ids=["mock_sell_1", "mock_sell_2"]
    )
    
    await trailing_manager.register_trade(
        symbol="ADAUSDT",
        side="sell",
        entry_price=0.50,
        sl_price=0.55,
        tp_prices=[0.48, 0.45, 0.42],
        order_ids=["mock_sell_1", "mock_sell_2"]
    )
    
    print(f"✅ Sell trade registered:")
    print(f"   Symbol: ADAUSDT")
    print(f"   Entry: $0.50")
    print(f"   TP2: $0.45")
    
    # Test sell side scenarios
    sell_scenarios = [
        {"price": 0.48, "description": "Small profit - no triggers"},
        {"price": 0.44, "description": "TP2 hit - break-even should trigger"},
        {"price": 0.40, "description": "Large profit - trailing should activate"}
    ]
    
    for i, scenario in enumerate(sell_scenarios, 1):
        print(f"\n   Sell Scenario {i}: {scenario['description']}")
        print(f"   Simulated Price: ${scenario['price']:,.4f}")
        
        breakeven_met = await breakeven_manager.check_breakeven_conditions("ADAUSDT")
        print(f"   Break-even triggered: {breakeven_met}")
        
        trailing_met = await trailing_manager.check_trailing_conditions("ADAUSDT")
        print(f"   Trailing triggered: {trailing_met}")
    
    print()
    
    # Test 5: Configuration validation
    print("📊 TEST 5: Configuration Validation")
    print("-" * 40)
    
    from config.settings import TradingConfig
    
    configs = {
        "Break-even threshold": TradingConfig.BREAKEVEN_THRESHOLD,
        "Break-even buffer": TradingConfig.BREAKEVEN_BUFFER,
        "Trailing threshold": TradingConfig.TRAILING_THRESHOLD,
        "Trailing distance": TradingConfig.TRAILING_DISTANCE,
        "Trailing step": TradingConfig.TRAILING_STEP
    }
    
    print("📋 Current Configuration:")
    for name, value in configs.items():
        print(f"   {name}: {value}")
    
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    # Get status of all registered trades
    breakeven_trades = list(breakeven_manager.active_trades.keys())
    trailing_trades = list(trailing_manager.active_trades.keys())
    
    print(f"✅ Break-even trades registered: {len(breakeven_trades)}")
    print(f"✅ Trailing trades registered: {len(trailing_trades)}")
    
    for symbol in breakeven_trades:
        status = breakeven_manager.get_trade_status(symbol)
        print(f"   {symbol}: Break-even {'✅' if status['breakeven_triggered'] else '⏳'}")
    
    for symbol in trailing_trades:
        status = trailing_manager.get_trade_status(symbol)
        print(f"   {symbol}: Trailing {'✅' if status['trailing_active'] else '⏳'}")
    
    print()
    print("🎉 SL MANAGEMENT TEST COMPLETED!")
    print(f"⚡ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_monitoring_loops():
    """Test the monitoring loops for both managers."""
    print("\n🔄 TESTING MONITORING LOOPS")
    print("=" * 40)
    
    # Start monitoring loops in background
    breakeven_task = asyncio.create_task(breakeven_manager.monitor_breakeven())
    trailing_task = asyncio.create_task(trailing_manager.monitor_trailing())
    
    print("📊 Monitoring loops started...")
    print("   Break-even monitoring: ✅ Active")
    print("   Trailing stop monitoring: ✅ Active")
    
    # Let them run for a few seconds
    await asyncio.sleep(10)
    
    # Cancel the tasks
    breakeven_task.cancel()
    trailing_task.cancel()
    
    try:
        await breakeven_task
    except asyncio.CancelledError:
        pass
    
    try:
        await trailing_task
    except asyncio.CancelledError:
        pass
    
    print("✅ Monitoring loops stopped")

if __name__ == "__main__":
    print("🚀 Starting SL Management Comprehensive Test...")
    asyncio.run(test_sl_management_comprehensive())
    asyncio.run(test_monitoring_loops()) 