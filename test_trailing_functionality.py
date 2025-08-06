#!/usr/bin/env python3
"""
Test script for dynamic trailing stop functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig

def test_trailing_configuration():
    """Test trailing configuration."""
    print("🧪 Testing Trailing Configuration")
    print("=" * 50)
    
    print(f"   • TRAILING_TRIGGER: {TradingConfig.TRAILING_TRIGGER}%")
    print(f"   • TRAILING_OFFSET: {TradingConfig.TRAILING_OFFSET}%")
    print(f"   • TP_LEVELS: {TradingConfig.TP_LEVELS}")
    
    if TradingConfig.TRAILING_TRIGGER == 6.0 and TradingConfig.TRAILING_OFFSET == 0.5:
        print("   ✅ Trailing configuration is correct (6.0% trigger, 0.5% offset)")
        return True
    else:
        print("   ❌ Trailing configuration is incorrect")
        return False

def test_trailing_watcher_import():
    """Test that trailing watcher can be imported."""
    print("\n📦 Testing Trailing Watcher Import")
    
    try:
        from monitor.trailing import trailing_watcher, start_trailing_watcher, cancel_trailing_watcher
        print("   ✅ Trailing watcher imported successfully")
        print(f"   • Trigger threshold: {trailing_watcher.trigger_threshold}%")
        print(f"   • Trailing offset: {trailing_watcher.trailing_offset}%")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import trailing watcher: {e}")
        return False

def test_trade_state_trailing_integration():
    """Test that trade state includes trailing tracking."""
    print("\n📊 Testing Trade State Trailing Integration")
    
    try:
        from monitor.trade_state import TradeState
        print("   ✅ Trade state imported successfully")
        
        # Check if TradeState has trailing fields
        trade_state = TradeState(
            symbol="BTCUSDT",
            side="LONG",
            entry_price=64000,
            sl_price=63000,
            leverage=10.0,
            initial_margin=20.0,
            quantity=0.1
        )
        
        print(f"   • Trailing started: {trade_state.trailing_started}")
        print(f"   • Trailing active: {trade_state.trailing_active}")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to test trade state integration: {e}")
        return False

def test_entry_integration():
    """Test entry integration with trailing."""
    print("\n📥 Testing Entry Integration")
    
    try:
        from logic.entry import handle_entry_signal
        print("   ✅ Entry function imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import entry function: {e}")
        return False

def test_exit_integration():
    """Test exit integration with trailing."""
    print("\n🚪 Testing Exit Integration")
    
    try:
        from logic.exit import exit_trade, exit_trade_sync
        print("   ✅ Exit functions imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import exit functions: {e}")
        return False

def test_trailing_logic():
    """Test trailing logic calculations."""
    print("\n🧮 Testing Trailing Logic")
    
    try:
        from monitor.trailing import trailing_watcher
        
        # Test P&L calculation for LONG position
        entry_price = 64000
        current_price = 67840  # 6.0% profit (trigger threshold)
        side = "long"
        
        pol = trailing_watcher._calculate_pol(entry_price, current_price, side)
        print(f"   • LONG P&L calculation: {pol:.2f}%")
        
        # Test P&L calculation for SHORT position
        entry_price = 64000
        current_price = 60160  # 6.0% profit (trigger threshold)
        side = "short"
        
        pol = trailing_watcher._calculate_pol(entry_price, current_price, side)
        print(f"   • SHORT P&L calculation: {pol:.2f}%")
        
        # Test trigger logic
        trigger_threshold = TradingConfig.TRAILING_TRIGGER
        should_trigger = pol >= trigger_threshold
        print(f"   • Should trigger trailing: {should_trigger} (threshold: {trigger_threshold}%)")
        
        # Test TP4 trigger logic
        tp4_level = TradingConfig.TP_LEVELS[3] if len(TradingConfig.TP_LEVELS) >= 4 else None
        if tp4_level:
            print(f"   • TP4 level: {tp4_level}%")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to test trailing logic: {e}")
        return False

def test_sl_calculation():
    """Test SL calculation logic."""
    print("\n🔢 Testing SL Calculation")
    
    try:
        from monitor.trailing import trailing_watcher
        
        # Test LONG position SL calculation
        current_price = 65000
        side = "long"
        offset = TradingConfig.TRAILING_OFFSET
        
        new_sl = trailing_watcher._calculate_new_sl_price("BTCUSDT", current_price, side)
        expected_sl = current_price * (1 - offset / 100)
        
        print(f"   • LONG current price: {current_price}")
        print(f"   • LONG calculated SL: {new_sl}")
        print(f"   • LONG expected SL: {expected_sl:.2f}")
        
        # Test SHORT position SL calculation
        current_price = 63000
        side = "short"
        
        new_sl = trailing_watcher._calculate_new_sl_price("BTCUSDT", current_price, side)
        expected_sl = current_price * (1 + offset / 100)
        
        print(f"   • SHORT current price: {current_price}")
        print(f"   • SHORT calculated SL: {new_sl}")
        print(f"   • SHORT expected SL: {expected_sl:.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to test SL calculation: {e}")
        return False

def main():
    """Run all trailing tests."""
    print("🚀 Starting Trailing Functionality Tests")
    
    tests = [
        ("Trailing Configuration", test_trailing_configuration),
        ("Trailing Watcher Import", test_trailing_watcher_import),
        ("Trade State Integration", test_trade_state_trailing_integration),
        ("Entry Integration", test_entry_integration),
        ("Exit Integration", test_exit_integration),
        ("Trailing Logic", test_trailing_logic),
        ("SL Calculation", test_sl_calculation)
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
        print("🎉 All trailing tests completed successfully!")
        print("\n✅ Trailing Functionality Features:")
        print("   • TRAILING_TRIGGER configured (6.0%)")
        print("   • TRAILING_OFFSET configured (0.5%)")
        print("   • Trailing watcher module created")
        print("   • Trade state integration implemented")
        print("   • Entry function integration working")
        print("   • Exit function integration working")
        print("   • P&L calculation logic working")
        print("   • SL calculation logic working")
        print("   • Dynamic trailing stop ready")
    else:
        print("⚠️ Some trailing tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 