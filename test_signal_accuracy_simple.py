#!/usr/bin/env python3
"""
Simple test script for Signal Accuracy Tracking System.
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_accuracy_configuration():
    """Test accuracy tracking configuration."""
    print("🧪 Testing Accuracy Tracking Configuration")
    print("=" * 50)
    
    try:
        from config.settings import (
            ENABLE_SIGNAL_ACCURACY_TRACKING,
            ACCURACY_TRACKING_TIMEFRAME,
            SAVE_ACCURACY_TO_FILE,
            ACCURACY_RESULTS_PATH
        )
        
        print(f"   • ENABLE_SIGNAL_ACCURACY_TRACKING: {ENABLE_SIGNAL_ACCURACY_TRACKING}")
        print(f"   • ACCURACY_TRACKING_TIMEFRAME: {ACCURACY_TRACKING_TIMEFRAME}")
        print(f"   • SAVE_ACCURACY_TO_FILE: {SAVE_ACCURACY_TO_FILE}")
        print(f"   • ACCURACY_RESULTS_PATH: {ACCURACY_RESULTS_PATH}")
        
        assert ENABLE_SIGNAL_ACCURACY_TRACKING == True
        assert ACCURACY_TRACKING_TIMEFRAME == "1d"
        assert SAVE_ACCURACY_TO_FILE == True
        assert ACCURACY_RESULTS_PATH == "data/signal_accuracy.json"
        
        print("   ✅ Accuracy configuration is correct")
        return True
        
    except Exception as e:
        print(f"   ❌ Accuracy configuration test failed: {e}")
        return False

def test_reporting_integration():
    """Test integration with reporting module."""
    print("\n🔗 Testing Integration with Reporting")
    print("=" * 50)
    
    try:
        from monitor.reporting import TradeReporter
        
        reporter = TradeReporter()
        
        # Create mock trade state
        class MockTradeState:
            def __init__(self):
                self.symbol = "BTCUSDT"
                self.side = "LONG"
                self.entry_price = 64000.0
                self.quantity = 0.1
                self.leverage = 20.0
                self.tp_hits = [64500, 65000]
                self.pyramid_steps_completed = []
                self.reentry_attempts = 0
                self.breakeven_triggered = True
                self.trailing_active = False
                self.sl_price = 63500.0
        
        trade_state = MockTradeState()
        
        # Generate report
        report = asyncio.run(reporter.generate_trade_report(
            trade_state=trade_state,
            exit_price=65000.0,
            exit_reason="TP",
            group_name="cryptoraketen"
        ))
        
        print(f"   ✅ Report generated: {report is not None}")
        print(f"   ✅ Report symbol: {report.symbol}")
        print(f"   ✅ Report group: {report.group_name}")
        print(f"   ✅ Report P&L: {report.pnl_percentage:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to test reporting integration: {e}")
        return False

def test_daily_summary_with_accuracy():
    """Test daily summary with accuracy tracking."""
    print("\n📊 Testing Daily Summary with Accuracy")
    print("=" * 50)
    
    try:
        from monitor.reporting import TradeReporter
        
        reporter = TradeReporter()
        
        # Generate daily summary
        summary = reporter.get_daily_summary()
        
        print(f"   ✅ Daily summary generated: {len(summary)} characters")
        print(f"   • Summary contains 'DAILY TRADING SUMMARY': {'DAILY TRADING SUMMARY' in summary}")
        
        # Check if accuracy tracking is mentioned
        if "SIGNAL ACCURACY REPORT" in summary:
            print("   • Signal accuracy report included in daily summary")
        else:
            print("   • No signal accuracy report in daily summary (expected if no trades)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to test daily summary: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Signal Accuracy Tracking Tests")
    print("=" * 60)
    
    tests = [
        test_accuracy_configuration,
        test_reporting_integration,
        test_daily_summary_with_accuracy
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SIGNAL ACCURACY TRACKING TESTS COMPLETED SUCCESSFULLY!")
        return True
    else:
        print("⚠️ Some signal accuracy tracking tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 