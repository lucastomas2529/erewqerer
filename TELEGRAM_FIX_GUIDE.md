# Telegram Notification Fix Guide

## Issues Identified

1. **RuntimeWarning**: `coroutine 'send_telegram_log' was never awaited`
2. **404 Error**: `Telegram log failed: 404, message='Not Found'`

## Root Causes

1. **Unawaited Coroutines**: Async functions called without `await`
2. **Invalid Bot Token**: Using placeholder token "DIN_TELEGRAM_BOT_TOKEN"
3. **Missing Chat ID**: No valid chat ID configured

## Fix 1: Update Telegram Logger

Update `utils/telegram_logger.py`:

```python
import asyncio
import aiohttp
from config.settings import TelegramConfig

async def send_telegram_log(message: str, group_name: str = None, tag: str = None):
    """Send log message to Telegram with error handling."""
    try:
        # Check if bot token is configured
        if not TelegramConfig.BOT_TOKEN or TelegramConfig.BOT_TOKEN == "DIN_TELEGRAM_BOT_TOKEN":
            print(f"⚠️ Telegram bot token not configured")
            return False
            
        # Check if chat ID is configured
        if not TelegramConfig.CHAT_ID:
            print(f"⚠️ Telegram chat ID not configured")
            return False
        
        # Format message
        formatted_message = f"📊 {message}"
        if group_name:
            formatted_message += f"\n📁 Group: {group_name}"
        if tag:
            formatted_message += f"\n🏷️ Tag: {tag}"
        
        # Send message
        url = f"https://api.telegram.org/bot{TelegramConfig.BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TelegramConfig.CHAT_ID,
            "text": formatted_message,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    print(f"✅ Telegram log sent: {message[:50]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Telegram log failed: {response.status}, {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Telegram log error: {e}")
        return False
```

## Fix 2: Update Settings Configuration

Update `config/settings.py`:

```python
import os

class TelegramConfig:
    # Use environment variables with fallbacks
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "DIN_TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Validation
    @classmethod
    def is_configured(cls):
        return (cls.BOT_TOKEN and 
                cls.BOT_TOKEN != "DIN_TELEGRAM_BOT_TOKEN" and 
                cls.CHAT_ID)
```

## Fix 3: Create Environment Template

Create `.env` file:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Other settings...
```

## Fix 4: Update All Telegram Calls

Ensure all `send_telegram_log` calls use `await`:

```python
# ❌ Wrong - in any file
send_telegram_log("Message", group_name="test")

# ✅ Correct - in any file
await send_telegram_log("Message", group_name="test")
```

## Fix 5: Add Telegram Test Script

Create `test_telegram_fix.py`:

```python
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
    if not TelegramConfig.BOT_TOKEN or TelegramConfig.BOT_TOKEN == "DIN_TELEGRAM_BOT_TOKEN":
        print("❌ Bot token not configured")
        print("   Set TELEGRAM_BOT_TOKEN environment variable")
        return False
    
    # Check if chat ID is set
    if not TelegramConfig.CHAT_ID:
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
```

## Fix 6: Update Reporting System Integration

Update `core/reporting_system.py` to handle Telegram errors gracefully:

```python
# In the send_trade_notification method
async def send_trade_notification(self, trade_data):
    """Send trade notification to Telegram."""
    try:
        message = f"💰 Trade Executed\n"
        message += f"Symbol: {trade_data['symbol']}\n"
        message += f"Side: {trade_data['side'].upper()}\n"
        message += f"Quantity: {trade_data['quantity']}\n"
        message += f"Entry: ${trade_data['entry_price']:,.2f}\n"
        
        if trade_data.get('sl_price'):
            message += f"SL: ${trade_data['sl_price']:,.2f}\n"
        
        if trade_data.get('tp_prices'):
            tp_list = ", ".join([f"${tp:,.2f}" for tp in trade_data['tp_prices']])
            message += f"TP: {tp_list}\n"
        
        # Try to send to Telegram
        telegram_result = await send_telegram_log(
            message,
            group_name=trade_data.get('group_name', 'Unknown'),
            tag="trade_executed"
        )
        
        if not telegram_result:
            print("⚠️ Trade notification sent to database only (Telegram failed)")
        else:
            print("✅ Trade notification sent to Telegram")
            
    except Exception as e:
        print(f"❌ Trade notification error: {e}")
```

## Testing the Fix

1. **Set up environment variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

2. **Run the test script**:
   ```bash
   python test_telegram_fix.py
   ```

3. **Check the output**:
   - ✅ Configuration looks good
   - ✅ Telegram connection successful
   - ✅ All messages sent successfully

## Common Issues and Solutions

### Issue: "Bot token is invalid"
**Solution**: Get a new bot token from @BotFather on Telegram

### Issue: "Chat not found"
**Solution**: 
1. Start a chat with your bot
2. Send `/start` to the bot
3. Get your chat ID from @userinfobot

### Issue: "Forbidden"
**Solution**: Make sure your bot has permission to send messages to the chat

### Issue: "Network error"
**Solution**: Check your internet connection and firewall settings

## Verification Steps

1. **Check configuration**:
   ```python
   from config.settings import TelegramConfig
   print(f"Bot token: {TelegramConfig.BOT_TOKEN[:10]}...")
   print(f"Chat ID: {TelegramConfig.CHAT_ID}")
   ```

2. **Test simple message**:
   ```python
   import asyncio
   from utils.telegram_logger import send_telegram_log
   
   async def test():
       result = await send_telegram_log("Test message")
       print(f"Result: {result}")
   
   asyncio.run(test())
   ```

3. **Check database logs**:
   ```python
   # The reporting system should still work even if Telegram fails
   from core.reporting_system import reporting_system
   # ... test logging ...
   ```

This fix guide addresses the specific Telegram notification issues identified in the testing and provides a comprehensive solution. 