#!/usr/bin/env python3
"""
Test script for multi-group Telegram support functionality.
This script tests the enhanced listener, signal handler, and reporting capabilities.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TelegramConfig
from signal_module.signal_handler import signal_handler, handle_incoming_signal
from utils.telegram_logger import send_telegram_log, send_group_specific_log
from generate.daily_report import generate_daily_report, generate_group_specific_report

async def test_multi_group_functionality():
    """Test the multi-group support functionality."""
    print("🧪 Testing Multi-Group Telegram Support")
    print("=" * 50)
    
    # Test 1: Check Telegram configuration
    print("\n1. 📡 Testing Telegram Configuration")
    print(f"   • Total groups configured: {len(TelegramConfig.TELEGRAM_GROUPS)}")
    print(f"   • Groups: {list(TelegramConfig.TELEGRAM_GROUPS.keys())}")
    
    # Test 2: Test signal handler initialization
    print("\n2. 🎯 Testing Signal Handler")
    print(f"   • Signal handler initialized: {signal_handler is not None}")
    print(f"   • Active signals: {len(signal_handler.active_signals)}")
    
    # Test 3: Simulate signals from different groups
    print("\n3. 📨 Testing Signal Processing")
    
    test_signals = [
        {
            "symbol": "BTCUSDT",
            "side": "LONG",
            "entry": [64000],
            "tp": [66000],
            "sl": 63000,
            "group_name": "cryptoraketen",
            "timestamp": "2024-01-15T10:30:00",
            "message_id": 12345
        },
        {
            "symbol": "ETHUSDT",
            "side": "SHORT",
            "entry": [3200],
            "tp": [3100],
            "sl": 3300,
            "group_name": "smart_crypto_signals",
            "timestamp": "2024-01-15T10:35:00",
            "message_id": 12346
        },
        {
            "symbol": "SOLUSDT",
            "side": "LONG",
            "entry": [100],
            "tp": [110],
            "sl": 95,
            "group_name": "own_channel",
            "timestamp": "2024-01-15T10:40:00",
            "message_id": 12347
        }
    ]
    
    for signal in test_signals:
        await handle_incoming_signal(signal)
        print(f"   ✅ Processed signal from {signal['group_name']}: {signal['symbol']} {signal['side']}")
    
    # Test 4: Check signal tracking
    print("\n4. 📊 Testing Signal Tracking")
    for group_name in TelegramConfig.TELEGRAM_GROUPS.keys():
        signals = signal_handler.get_signals_by_group(group_name)
        stats = signal_handler.get_group_stats(group_name)
        print(f"   • {group_name}: {len(signals)} signals, {stats.get('total_signals', 0)} total")
    
    # Test 5: Test group-specific reporting
    print("\n5. 📈 Testing Group-Specific Reporting")
    for group_name in TelegramConfig.TELEGRAM_GROUPS.keys():
        await generate_group_specific_report(group_name)
        print(f"   ✅ Generated report for {group_name}")
    
    # Test 6: Test daily report
    print("\n6. 📅 Testing Daily Report")
    await generate_daily_report()
    print("   ✅ Generated daily report")
    
    # Test 7: Test telegram logging with group context
    print("\n7. 📱 Testing Telegram Logging")
    for group_name in TelegramConfig.TELEGRAM_GROUPS.keys():
        await send_group_specific_log(
            group_name,
            f"Test message from {group_name}",
            tag="test"
        )
        print(f"   ✅ Sent test log to {group_name}")
    
    print("\n" + "=" * 50)
    print("✅ All multi-group tests completed successfully!")
    print(f"📊 Final stats: {len(signal_handler.active_signals)} groups with signals")

async def test_signal_metadata():
    """Test signal metadata handling."""
    print("\n🔍 Testing Signal Metadata")
    
    # Test signal with complete metadata
    test_signal = {
        "symbol": "BTCUSDT",
        "side": "LONG",
        "entry": [64000],
        "tp": [66000],
        "sl": 63000,
        "group_name": "cryptoraketen",
        "source_group": "cryptoraketen",  # Backward compatibility
        "source_chat_id": -1002290339976,
        "timestamp": "2024-01-15T10:30:00",
        "message_id": 12345
    }
    
    print(f"   • Original signal: {test_signal['symbol']} {test_signal['side']}")
    print(f"   • Group name: {test_signal['group_name']}")
    print(f"   • Source chat ID: {test_signal['source_chat_id']}")
    print(f"   • Message ID: {test_signal['message_id']}")
    print(f"   • Timestamp: {test_signal['timestamp']}")
    
    # Process the signal
    result = await handle_incoming_signal(test_signal)
    print(f"   • Processing result: {result}")
    
    # Verify it was stored correctly
    stored_signals = signal_handler.get_signals_by_group("cryptoraketen")
    if stored_signals:
        last_signal = stored_signals[-1]
        print(f"   • Stored signal group: {last_signal.get('group_name')}")
        print(f"   • Stored signal symbol: {last_signal.get('symbol')}")

async def test_concurrent_group_handling():
    """Test concurrent handling of multiple groups."""
    print("\n⚡ Testing Concurrent Group Handling")
    
    # Simulate concurrent signals from different groups
    concurrent_signals = []
    for i, group_name in enumerate(TelegramConfig.TELEGRAM_GROUPS.keys()):
        signal = {
            "symbol": f"TEST{i+1}USDT",
            "side": "LONG" if i % 2 == 0 else "SHORT",
            "entry": [100 + i],
            "tp": [110 + i],
            "sl": 90 + i,
            "group_name": group_name,
            "timestamp": f"2024-01-15T10:{30+i}:00",
            "message_id": 20000 + i
        }
        concurrent_signals.append(signal)
    
    # Process all signals concurrently
    tasks = [handle_incoming_signal(signal) for signal in concurrent_signals]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"   • Processed {len(results)} concurrent signals")
    print(f"   • Successful: {len([r for r in results if not isinstance(r, Exception)])}")
    print(f"   • Failed: {len([r for r in results if isinstance(r, Exception)])}")

if __name__ == "__main__":
    print("🚀 Starting Multi-Group Support Tests")
    
    async def main():
        try:
            await test_multi_group_functionality()
            await test_signal_metadata()
            await test_concurrent_group_handling()
            
            print("\n🎉 All tests completed successfully!")
            print("📋 Summary:")
            print(f"   • Groups configured: {len(TelegramConfig.TELEGRAM_GROUPS)}")
            print(f"   • Groups with signals: {len(signal_handler.active_signals)}")
            print(f"   • Total signals processed: {sum(len(signals) for signals in signal_handler.active_signals.values())}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main()) 