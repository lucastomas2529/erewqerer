#!/usr/bin/env python3
"""
Test sending a signal to an accessible channel.
"""

import asyncio
from telethon import TelegramClient
from config.settings import TelegramConfig

async def test_accessible_channel():
    """Test sending a signal to an accessible channel."""
    
    print("🧪 Testing Accessible Channel...")
    
    # Use the same credentials as the main bot
    api_id = TelegramConfig.TELEGRAM_API_ID
    api_hash = TelegramConfig.TELEGRAM_API_HASH
    
    # Create a test client
    client = TelegramClient("test_session", api_id, api_hash)
    
    try:
        await client.start()
        print("✅ Test client connected")
        
        # Test channel you have access to
        test_channel_id = -1002765168462  # Toams_Trading_New_Channel
        test_message = """
🧪 TEST SIGNAL - BOT DETECTION TEST
BTCUSDT LONG
Entry: 45000
TP1: 46000
TP2: 47000
SL: 44000

This is a test to verify the bot is detecting signals correctly.
        """.strip()
        
        print(f"📤 Sending test signal to Toams_Trading_New_Channel...")
        await client.send_message(test_channel_id, test_message)
        print("✅ Test signal sent!")
        
        print("\n📋 Now check your bot console for:")
        print("   • '📨 Raw message received from toams_trading_channel'")
        print("   • '✅ Message passed spam filter'")
        print("   • '✅ Signal parsed from toams_trading_channel'")
        print("   • 'BTCUSDT LONG (confidence: X.XX)'")
        
        print("\n⏰ Wait 10 seconds for the bot to process...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_accessible_channel()) 