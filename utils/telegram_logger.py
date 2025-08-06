import aiohttp
from config.settings import TelegramConfig

async def send_telegram_log(message: str, group_name: str = None, tag: str = None):
    """
    Send log message to Telegram with optional group name and tag.
    
    Args:
        message: The message to send
        group_name: Optional group name for context
        tag: Optional tag for message categorization
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Check if bot token is configured
        if not TelegramConfig.TELEGRAM_BOT_TOKEN or TelegramConfig.TELEGRAM_BOT_TOKEN == "DIN_TELEGRAM_BOT_TOKEN":
            print(f"⚠️ Telegram bot token not configured")
            return False
            
        # Check if chat ID is configured
        if not TelegramConfig.TELEGRAM_CHAT_ID:
            print(f"⚠️ Telegram chat ID not configured")
            return False
        
        # Format message
        formatted_message = f"📊 {message}"
        if group_name:
            formatted_message += f"\n📁 Group: {group_name}"
        if tag:
            formatted_message += f"\n🏷️ Tag: {tag}"
        
        # Send message
        url = f"https://api.telegram.org/bot{TelegramConfig.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TelegramConfig.TELEGRAM_CHAT_ID,
            "text": formatted_message,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
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

async def send_group_specific_log(group_name: str, message: str, tag: str = None):
    """
    Send a log message specifically for a group.
    
    Args:
        group_name: The group name for context
        message: The message to send
        tag: Optional tag for message categorization
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    return await send_telegram_log(message, group_name=group_name, tag=tag)

async def send_error_log(group_name: str, error_message: str):
    """
    Send an error log message for a specific group.
    
    Args:
        group_name: The group name for context
        error_message: The error message to send
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    return await send_telegram_log(f"❌ {error_message}", group_name=group_name, tag="error")

async def send_success_log(group_name: str, success_message: str):
    """
    Send a success log message for a specific group.
    
    Args:
        group_name: The group name for context
        success_message: The success message to send
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    return await send_telegram_log(f"✅ {success_message}", group_name=group_name, tag="success")
