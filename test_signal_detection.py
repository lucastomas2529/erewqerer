#!/usr/bin/env python3
"""
Quick test to verify signal detection is working.
"""

import asyncio
from telethon import TelegramClient
from config.settings import TelegramConfig

async def test_signal_detection():
    """Test if the bot can detect signals."""
    
    print("🧪 Testing Signal Detection...")
    
    # Use the same credentials as the main bot
    api_id = TelegramConfig.TELEGRAM_API_ID
    api_hash = TelegramConfig.TELEGRAM_API_HASH
    
    # Create a test client
    client = TelegramClient("test_session", api_id, api_hash)
    
    try:
        await client.start()
        print("✅ Test client connected")
        
        # Get user's dialogs (chats they have access to)
        print("\n📋 Checking accessible channels...")
        async for dialog in client.iter_dialogs():
            if dialog.is_channel:
                print(f"  • {dialog.title}: {dialog.id}")
        
        print(f"\n🎯 Monitored channels in config:")
        for name, channel_id in TelegramConfig.TELEGRAM_GROUPS.items():
            print(f"  • {name}: {channel_id}")
        
        print("\n💡 To test the bot:")
        print("1. Join one of the monitored channels with your Telegram account")
        print("2. Send a test signal like: 'BTCUSDT LONG Entry: 45000 TP1: 46000 SL: 44000'")
        print("3. Watch the bot console for detection messages")
        
        # Try to send to the first accessible channel
        print("\n📤 Trying to send test signal...")
        test_message = """
🧪 TEST SIGNAL
BTCUSDT LONG
Entry: 45000
TP1: 46000
TP2: 47000
SL: 44000
        """.strip()
        
        # Try to send to yourself first
        me = await client.get_me()
        await client.send_message(me, test_message)
        print("✅ Test signal sent to yourself!")
        
        print("\n📋 What to look for in the main bot console:")
        print("   • '📨 Raw message received from [channel_name]'")
        print("   • '✅ Message passed spam filter'")
        print("   • '✅ Signal parsed from [channel_name]'")
        print("   • 'BTCUSDT LONG (confidence: X.XX)'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_signal_detection()) 