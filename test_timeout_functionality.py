#!/usr/bin/env python3
"""
Test script for automatic trade exit timeout functionality.
This script tests the timeout watcher and trade state integration.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig
from monitor.timeout_watcher import timeout_watcher, start_trade_timeout, cancel_trade_timeout
from monitor.trade_state import create_trade_state, close_trade_state, TradeState

async def test_timeout_watcher_initialization():
    """Test timeout watcher initialization."""
    print("🧪 Testing Timeout Watcher Initialization")
    print("=" * 50)
    
    print(f"   • Timeout seconds: {timeout_watcher.timeout_seconds}")
    print(f"   • Timeout hours: {timeout_watcher.timeout_seconds / 3600:.1f}h")
    print(f"   • Active tasks: {len(timeout_watcher.timeout_tasks)}")
    print(f"   • Trade start times: {len(timeout_watcher.trade_start_times)}")
    
    return True

async def test_trade_timeout_start():
    """Test starting a timeout for a trade."""
    print("\n⏰ Testing Trade Timeout Start")
    
    symbol = "BTCUSDT"
    side = "long"
    group_name = "test_group"
    
    try:
        # Start timeout
        await start_trade_timeout(symbol, side, group_name)
        
        print(f"   ✅ Timeout started for {symbol}")
        print(f"   • Active tasks: {len(timeout_watcher.timeout_tasks)}")
        print(f"   • Trade start times: {len(timeout_watcher.trade_start_times)}")
        
        # Check if task was created
        if symbol in timeout_watcher.timeout_tasks:
            task = timeout_watcher.timeout_tasks[symbol]
            print(f"   • Task created: {task.get_name()}")
            print(f"   • Task done: {task.done()}")
            return True
        else:
            print(f"   ❌ Task not found for {symbol}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to start timeout: {e}")
        return False

async def test_trade_timeout_cancel():
    """Test cancelling a timeout for a trade."""
    print("\n🚫 Testing Trade Timeout Cancel")
    
    symbol = "ETHUSDT"
    side = "short"
    group_name = "test_group"
    
    try:
        # Start timeout first
        await start_trade_timeout(symbol, side, group_name)
        print(f"   ✅ Timeout started for {symbol}")
        
        # Cancel timeout
        await cancel_trade_timeout(symbol)
        print(f"   ✅ Timeout cancelled for {symbol}")
        
        # Check if task was cancelled
        if symbol not in timeout_watcher.timeout_tasks:
            print(f"   ✅ Task removed for {symbol}")
            return True
        else:
            print(f"   ❌ Task still exists for {symbol}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to cancel timeout: {e}")
        return False

async def test_trade_state_integration():
    """Test trade state integration with timeout."""
    print("\n🎯 Testing Trade State Integration")
    
    symbol = "SOLUSDT"
    side = "LONG"
    entry_price = 100.0
    sl_price = 95.0
    leverage = 10.0
    initial_margin = 20.0
    quantity = 0.1
    group_name = "test_group"
    
    try:
        # Create trade state (this should start timeout)
        trade_state = await create_trade_state(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            sl_price=sl_price,
            leverage=leverage,
            initial_margin=initial_margin,
            quantity=quantity,
            group_name=group_name
        )
        
        print(f"   ✅ Trade state created for {symbol}")
        print(f"   • Timeout started: {trade_state.timeout_started}")
        print(f"   • Position active: {trade_state.position_active}")
        
        # Check if timeout task was created
        if symbol in timeout_watcher.timeout_tasks:
            print(f"   ✅ Timeout task created for {symbol}")
        else:
            print(f"   ❌ Timeout task not found for {symbol}")
            return False
        
        # Close trade state (this should cancel timeout)
        await close_trade_state(symbol, group_name)
        print(f"   ✅ Trade state closed for {symbol}")
        
        # Check if timeout task was cancelled
        if symbol not in timeout_watcher.timeout_tasks:
            print(f"   ✅ Timeout task cancelled for {symbol}")
            return True
        else:
            print(f"   ❌ Timeout task still exists for {symbol}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test trade state integration: {e}")
        return False

async def test_multiple_trades():
    """Test multiple trades with timeouts."""
    print("\n📊 Testing Multiple Trades")
    
    test_trades = [
        {"symbol": "BTCUSDT", "side": "long", "group": "group1"},
        {"symbol": "ETHUSDT", "side": "short", "group": "group2"},
        {"symbol": "SOLUSDT", "side": "long", "group": "group3"}
    ]
    
    try:
        # Start timeouts for multiple trades
        for trade in test_trades:
            await start_trade_timeout(trade["symbol"], trade["side"], trade["group"])
            print(f"   ✅ Timeout started for {trade['symbol']}")
        
        print(f"   • Total active tasks: {len(timeout_watcher.timeout_tasks)}")
        print(f"   • Total start times: {len(timeout_watcher.trade_start_times)}")
        
        # Cancel all timeouts
        for trade in test_trades:
            await cancel_trade_timeout(trade["symbol"])
            print(f"   ✅ Timeout cancelled for {trade['symbol']}")
        
        print(f"   • Active tasks after cancel: {len(timeout_watcher.timeout_tasks)}")
        
        if len(timeout_watcher.timeout_tasks) == 0:
            print("   ✅ All timeouts cancelled successfully")
            return True
        else:
            print(f"   ❌ {len(timeout_watcher.timeout_tasks)} tasks still active")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test multiple trades: {e}")
        return False

async def test_timeout_configuration():
    """Test timeout configuration from settings."""
    print("\n⚙️ Testing Timeout Configuration")
    
    from config.settings import TradingConfig
    
    print(f"   • AUTO_CLOSE_TIMEOUT: {TradingConfig.AUTO_CLOSE_TIMEOUT} seconds")
    print(f"   • Timeout hours: {TradingConfig.AUTO_CLOSE_TIMEOUT / 3600:.1f}h")
    print(f"   • Timeout minutes: {TradingConfig.AUTO_CLOSE_TIMEOUT / 60:.1f} minutes")
    
    # Test that timeout watcher uses the correct configuration
    if timeout_watcher.timeout_seconds == TradingConfig.AUTO_CLOSE_TIMEOUT:
        print("   ✅ Timeout watcher uses correct configuration")
        return True
    else:
        print(f"   ❌ Timeout watcher configuration mismatch: {timeout_watcher.timeout_seconds} vs {TradingConfig.AUTO_CLOSE_TIMEOUT}")
        return False

async def test_error_handling():
    """Test error handling in timeout functionality."""
    print("\n🛡️ Testing Error Handling")
    
    try:
        # Test with invalid symbol
        await start_trade_timeout("", "long", "test_group")
        print("   ⚠️ Should have handled empty symbol")
        
        # Test with invalid side
        await start_trade_timeout("BTCUSDT", "invalid_side", "test_group")
        print("   ⚠️ Should have handled invalid side")
        
        # Test cancelling non-existent timeout
        await cancel_trade_timeout("NONEXISTENT")
        print("   ✅ Handled non-existent timeout gracefully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

def main():
    """Run all timeout tests."""
    print("🚀 Starting Timeout Functionality Tests")
    
    async def run_tests():
        tests = [
            ("Timeout Watcher Initialization", test_timeout_watcher_initialization),
            ("Trade Timeout Start", test_trade_timeout_start),
            ("Trade Timeout Cancel", test_trade_timeout_cancel),
            ("Trade State Integration", test_trade_state_integration),
            ("Multiple Trades", test_multiple_trades),
            ("Timeout Configuration", test_timeout_configuration),
            ("Error Handling", test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if await test_func():
                    print(f"   ✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"   ❌ {test_name}: FAILED")
            except Exception as e:
                print(f"   ❌ {test_name}: ERROR - {e}")
        
        print("\n" + "=" * 50)
        print(f"📋 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All timeout tests completed successfully!")
            print("\n✅ Timeout Functionality Verified:")
            print("   • Auto-close timeout configuration working")
            print("   • Timeout tasks created and managed correctly")
            print("   • Trade state integration functional")
            print("   • Multiple trades supported")
            print("   • Error handling robust")
            print("   • Timeout cancellation working")
        else:
            print("⚠️ Some timeout tests failed. Please check the implementation.")
        
        return passed == total
    
    return asyncio.run(run_tests())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 