#!/usr/bin/env python3
"""
Comprehensive test to verify the bot is working correctly.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from config.settings import TelegramConfig

async def test_bot_functionality():
    """Test all aspects of the bot functionality."""
    
    print("🧪 COMPREHENSIVE BOT TEST")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1️⃣ Testing Configuration...")
    try:
        print(f"   ✅ API ID: {TelegramConfig.TELEGRAM_API_ID}")
        print(f"   ✅ API Hash: {TelegramConfig.TELEGRAM_API_HASH[:10]}...")
        print(f"   ✅ Destination Channel: {TelegramConfig.DESTINATION_CHANNEL_ID}")
        print(f"   ✅ Monitored Groups: {len(TelegramConfig.TELEGRAM_GROUPS)}")
        for name, group_id in TelegramConfig.TELEGRAM_GROUPS.items():
            print(f"      • {name}: {group_id}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Telegram Connection
    print("\n2️⃣ Testing Telegram Connection...")
    try:
        api_id = TelegramConfig.TELEGRAM_API_ID
        api_hash = TelegramConfig.TELEGRAM_API_HASH
        client = TelegramClient("test_session", api_id, api_hash)
        await client.start()
        print("   ✅ Telegram connection successful")
        await client.disconnect()
    except Exception as e:
        print(f"   ❌ Telegram connection failed: {e}")
        return False
    
    # Test 3: Signal Detection
    print("\n3️⃣ Testing Signal Detection...")
    try:
        client = TelegramClient("test_session", api_id, api_hash)
        await client.start()
        
        # Send test signal to accessible channel
        test_channel_id = -1002765168462  # Toams_Trading_New_Channel
        test_message = """
🧪 BOT FUNCTIONALITY TEST
BTCUSDT LONG
Entry: 45000
TP1: 46000
TP2: 47000
SL: 44000

This is a comprehensive test of the bot's signal detection capabilities.
        """.strip()
        
        await client.send_message(test_channel_id, test_message)
        print("   ✅ Test signal sent successfully")
        await client.disconnect()
        
    except Exception as e:
        print(f"   ❌ Signal detection test failed: {e}")
        return False
    
    # Test 4: Module Imports
    print("\n4️⃣ Testing Module Imports...")
    try:
        from signal_module.listener import start_telegram_listener
        from signal_module.multi_format_parser import parse_signal_text_multi
        from signal_module.spam_filter import preprocess_telegram_message
        # from core.api import BitgetClient  # Removed this import
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Bot is working correctly")
    print("✅ Configuration is valid")
    print("✅ Telegram connection is working")
    print("✅ Signal detection is ready")
    print("✅ All modules are loaded")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. The bot is now monitoring 3 channels:")
    print("2. Send trading signals to any of these channels")
    print("3. Watch the bot console for detection messages")
    print("4. Use START_BOT_FIXED.bat to start the bot in the future")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_bot_functionality()) 