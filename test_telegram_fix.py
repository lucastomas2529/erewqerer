#!/usr/bin/env python3
"""
Test script to verify Telegram notifications work correctly.
"""

import asyncio
import os
from utils.telegram_logger import send_telegram_log
from config.settings import TelegramConfig

async def test_telegram_configuration():
    """Test Telegram configuration."""
    print("🔧 Testing Telegram Configuration...")
    
    # Check if bot token is set
    if not TelegramConfig.TELEGRAM_BOT_TOKEN or TelegramConfig.TELEGRAM_BOT_TOKEN == "DIN_TELEGRAM_BOT_TOKEN":
        print("❌ Bot token not configured")
        print("   Set TELEGRAM_BOT_TOKEN environment variable")
        return False
    
    # Check if chat ID is set
    if not TelegramConfig.TELEGRAM_CHAT_ID:
        print("❌ Chat ID not configured")
        print("   Set TELEGRAM_CHAT_ID environment variable")
        return False
    
    print("✅ Configuration looks good")
    return True

async def test_telegram_connection():
    """Test Telegram API connection."""
    print("📡 Testing Telegram Connection...")
    
    try:
        result = await send_telegram_log(
            "🧪 Test message from trading bot",
            group_name="Test Group",
            tag="connection_test"
        )
        
        if result:
            print("✅ Telegram connection successful")
            return True
        else:
            print("❌ Telegram connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test error: {e}")
        return False

async def test_multiple_messages():
    """Test sending multiple messages."""
    print("📨 Testing Multiple Messages...")
    
    messages = [
        ("Signal received: BTCUSDT LONG", "Signal Group", "signal"),
        ("Trade executed: BTCUSDT 0.1 @ 45000", "Trade Group", "trade"),
        ("Error occurred: API timeout", "Error Group", "error")
    ]
    
    success_count = 0
    for message, group, tag in messages:
        try:
            result = await send_telegram_log(message, group, tag)
            if result:
                success_count += 1
                print(f"✅ Sent: {message[:30]}...")
            else:
                print(f"❌ Failed: {message[:30]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"📊 Success rate: {success_count}/{len(messages)}")
    return success_count == len(messages)

async def main():
    """Run all Telegram tests."""
    print("🚀 Starting Telegram Fix Tests...\n")
    
    # Test 1: Configuration
    config_ok = await test_telegram_configuration()
    if not config_ok:
        print("\n❌ Configuration failed. Please fix settings first.")
        return
    
    print()
    
    # Test 2: Connection
    connection_ok = await test_telegram_connection()
    if not connection_ok:
        print("\n❌ Connection failed. Check bot token and chat ID.")
        return
    
    print()
    
    # Test 3: Multiple messages
    messages_ok = await test_multiple_messages()
    
    print("\n" + "="*50)
    if config_ok and connection_ok and messages_ok:
        print("🎉 All Telegram tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main()) 