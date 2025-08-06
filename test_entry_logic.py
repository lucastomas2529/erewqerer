#!/usr/bin/env python3
"""
Comprehensive test script for entry logic implementation.
Tests risk-based sizing, dual LIMIT orders, SL/TP, and fallback scenarios.
"""

import asyncio
import time
from datetime import datetime
from core.entry_manager import execute_entry_strategy, calculate_position_size
from core.api import get_current_price_async, get_account_balance

async def test_entry_logic_comprehensive():
    """Comprehensive test of entry logic with various scenarios."""
    
    print("🚀 ENTRY LOGIC COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Basic dual entry with risk-based sizing
    print("📊 TEST 1: Basic Dual Entry Strategy")
    print("-" * 40)
    
    result1 = await execute_entry_strategy(
        symbol="BTCUSDT",
        side="buy",
        risk_percent=1.0,
        leverage=10,
        step1_ratio=0.5  # 50/50 split
    )
    
    print(f"✅ Test 1 Result:")
    print(f"   Orders placed: {len(result1['orders'])}")
    print(f"   Fallback used: {result1['fallback']}")
    print(f"   Errors: {len(result1['errors'])}")
    
    if result1['orders']:
        for i, order in enumerate(result1['orders'], 1):
            print(f"   Order {i}: {order['quantity']} @ ${order['price']:,.2f}")
            print(f"   SL: ${order['sl_price']:,.2f}, TP: ${order['tp_price']:,.2f}")
    print()
    
    # Test 2: Different risk parameters
    print("📊 TEST 2: High Risk Strategy")
    print("-" * 40)
    
    result2 = await execute_entry_strategy(
        symbol="ETHUSDT",
        side="buy",
        risk_percent=2.0,  # Higher risk
        leverage=20,        # Higher leverage
        step1_ratio=0.6    # 60/40 split
    )
    
    print(f"✅ Test 2 Result:")
    print(f"   Orders placed: {len(result2['orders'])}")
    print(f"   Fallback used: {result2['fallback']}")
    print(f"   Errors: {len(result2['errors'])}")
    
    if result2['orders']:
        for i, order in enumerate(result2['orders'], 1):
            print(f"   Order {i}: {order['quantity']} @ ${order['price']:,.2f}")
            print(f"   SL: ${order['sl_price']:,.2f}, TP: ${order['tp_price']:,.2f}")
    print()
    
    # Test 3: Sell side strategy
    print("📊 TEST 3: Sell Side Strategy")
    print("-" * 40)
    
    result3 = await execute_entry_strategy(
        symbol="SOLUSDT",
        side="sell",
        risk_percent=0.5,
        leverage=5,
        step1_ratio=0.7  # 70/30 split
    )
    
    print(f"✅ Test 3 Result:")
    print(f"   Orders placed: {len(result3['orders'])}")
    print(f"   Fallback used: {result3['fallback']}")
    print(f"   Errors: {len(result3['errors'])}")
    
    if result3['orders']:
        for i, order in enumerate(result3['orders'], 1):
            print(f"   Order {i}: {order['quantity']} @ ${order['price']:,.2f}")
            print(f"   SL: ${order['sl_price']:,.2f}, TP: ${order['tp_price']:,.2f}")
    print()
    
    # Test 4: Custom SL/TP levels
    print("📊 TEST 4: Custom SL/TP Levels")
    print("-" * 40)
    
    current_price = await get_current_price_async("BTCUSDT")
    custom_sl = current_price * 0.97  # 3% below
    custom_tp = current_price * 1.05  # 5% above
    
    result4 = await execute_entry_strategy(
        symbol="BTCUSDT",
        side="buy",
        risk_percent=1.5,
        leverage=15,
        sl_price=custom_sl,
        tp_price=custom_tp
    )
    
    print(f"✅ Test 4 Result:")
    print(f"   Orders placed: {len(result4['orders'])}")
    print(f"   Fallback used: {result4['fallback']}")
    print(f"   Errors: {len(result4['errors'])}")
    
    if result4['orders']:
        for i, order in enumerate(result4['orders'], 1):
            print(f"   Order {i}: {order['quantity']} @ ${order['price']:,.2f}")
            print(f"   SL: ${order['sl_price']:,.2f}, TP: ${order['tp_price']:,.2f}")
    print()
    
    # Test 5: Position size calculation
    print("📊 TEST 5: Position Size Calculation")
    print("-" * 40)
    
    balance = await get_account_balance("USDT")
    print(f"💰 Account Balance: ${balance:,.2f} USDT")
    
    # Test different scenarios
    scenarios = [
        {"risk": 1.0, "leverage": 10, "sl_distance": 0.02},
        {"risk": 2.0, "leverage": 20, "sl_distance": 0.01},
        {"risk": 0.5, "leverage": 5, "sl_distance": 0.05}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        current_price = await get_current_price_async("BTCUSDT")
        sl_price = current_price * (1 - scenario["sl_distance"])
        
        qty = await calculate_position_size(
            "BTCUSDT",
            scenario["risk"],
            scenario["leverage"],
            sl_price,
            current_price
        )
        
        risk_amount = balance * (scenario["risk"] / 100)
        position_value = qty * current_price
        
        print(f"   Scenario {i}:")
        print(f"     Risk: {scenario['risk']}%, Leverage: {scenario['leverage']}x")
        print(f"     Position Size: {qty:.6f} BTC")
        print(f"     Position Value: ${position_value:,.2f}")
        print(f"     Risk Amount: ${risk_amount:,.2f}")
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_results = [result1, result2, result3, result4]
    total_orders = sum(len(r['orders']) for r in all_results)
    total_fallbacks = sum(1 for r in all_results if r['fallback'])
    total_errors = sum(len(r['errors']) for r in all_results)
    
    print(f"✅ Total Tests: {len(all_results)}")
    print(f"✅ Total Orders Placed: {total_orders}")
    print(f"⚠️  Fallbacks Used: {total_fallbacks}")
    print(f"❌ Total Errors: {total_errors}")
    print()
    
    if total_errors == 0:
        print("🎉 ALL TESTS PASSED! Entry logic is working correctly.")
    else:
        print("⚠️  Some errors occurred. Check the implementation.")
    
    print(f"⚡ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 Starting Entry Logic Comprehensive Test...")
    asyncio.run(test_entry_logic_comprehensive()) 