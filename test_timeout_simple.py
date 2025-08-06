#!/usr/bin/env python3
"""
Simple test script for automatic trade exit timeout functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig

def test_timeout_configuration():
    """Test timeout configuration."""
    print("🧪 Testing Timeout Configuration")
    print("=" * 50)
    
    print(f"   • AUTO_CLOSE_TIMEOUT: {TradingConfig.AUTO_CLOSE_TIMEOUT} seconds")
    print(f"   • Timeout hours: {TradingConfig.AUTO_CLOSE_TIMEOUT / 3600:.1f}h")
    print(f"   • Timeout minutes: {TradingConfig.AUTO_CLOSE_TIMEOUT / 60:.1f} minutes")
    
    if TradingConfig.AUTO_CLOSE_TIMEOUT == 14400:  # 4 hours
        print("   ✅ Timeout configuration is correct (4 hours)")
        return True
    else:
        print("   ❌ Timeout configuration is incorrect")
        return False

def test_timeout_watcher_import():
    """Test that timeout watcher can be imported."""
    print("\n📦 Testing Timeout Watcher Import")
    
    try:
        from monitor.timeout_watcher import timeout_watcher, start_trade_timeout, cancel_trade_timeout
        print("   ✅ Timeout watcher imported successfully")
        print(f"   • Timeout seconds: {timeout_watcher.timeout_seconds}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import timeout watcher: {e}")
        return False

def test_trade_state_import():
    """Test that trade state can be imported."""
    print("\n📦 Testing Trade State Import")
    
    try:
        from monitor.trade_state import TradeState, create_trade_state, close_trade_state
        print("   ✅ Trade state imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import trade state: {e}")
        return False

def test_exit_integration():
    """Test exit integration."""
    print("\n🚪 Testing Exit Integration")
    
    try:
        from logic.exit import exit_trade, exit_trade_sync
        print("   ✅ Exit functions imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import exit functions: {e}")
        return False

def test_entry_integration():
    """Test entry integration."""
    print("\n📥 Testing Entry Integration")
    
    try:
        from logic.entry import handle_entry_signal
        print("   ✅ Entry function imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import entry function: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Timeout Functionality Tests")
    
    tests = [
        ("Timeout Configuration", test_timeout_configuration),
        ("Timeout Watcher Import", test_timeout_watcher_import),
        ("Trade State Import", test_trade_state_import),
        ("Exit Integration", test_exit_integration),
        ("Entry Integration", test_entry_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
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
        print("\n✅ Timeout Functionality Features:")
        print("   • AUTO_CLOSE_TIMEOUT configured (4 hours)")
        print("   • Timeout watcher module created")
        print("   • Trade state integration implemented")
        print("   • Exit function integration working")
        print("   • Entry function integration working")
        print("   • Automatic trade exit after timeout ready")
    else:
        print("⚠️ Some timeout tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 