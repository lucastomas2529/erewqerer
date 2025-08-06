# utils/telegram_groups.py
"""
Utility functions for managing Telegram groups dynamically.
"""

from config.settings import TelegramConfig

def add_multiple_groups(groups_dict: dict):
    """
    Add multiple Telegram groups at once.
    
    Usage:
    add_multiple_groups({
        "premium_signals": -1234567890,
        "crypto_alerts": -1234567891,
        "trading_channel": -1234567892
    })
    """
    for name, group_id in groups_dict.items():
        TelegramConfig.add_telegram_group(name, group_id)
    
    print(f"✅ Added {len(groups_dict)} new groups")
    TelegramConfig.list_monitored_groups()

def remove_group(name: str):
    """Remove a group from monitoring."""
    if name in TelegramConfig.TELEGRAM_GROUPS:
        group_id = TelegramConfig.TELEGRAM_GROUPS.pop(name)
        TelegramConfig.TELEGRAM_SIGNAL_CHANNEL_IDS = list(TelegramConfig.TELEGRAM_GROUPS.values())
        print(f"✅ Removed group: {name} ({group_id})")
    else:
        print(f"❌ Group '{name}' not found")

def get_group_stats():
    """Get statistics about monitored groups."""
    total_groups = len(TelegramConfig.TELEGRAM_GROUPS)
    max_groups = 20
    remaining = max_groups - total_groups
    
    print(f"📊 Group Statistics:")
    print(f"  • Total monitored: {total_groups}/{max_groups}")
    print(f"  • Remaining slots: {remaining}")
    print(f"  • Group IDs: {list(TelegramConfig.TELEGRAM_GROUPS.values())}")
    
    return {
        "total": total_groups,
        "max": max_groups,
        "remaining": remaining,
        "groups": TelegramConfig.TELEGRAM_GROUPS.copy()
    }

# Example usage and group templates
EXAMPLE_GROUPS = {
    "premium_crypto_signals": -1234567890,
    "altcoin_alerts": -1234567891,
    "futures_trading": -1234567892,
    "scalping_signals": -1234567893,
    "whale_alerts": -1234567894,
    "technical_analysis": -1234567895,
    "defi_signals": -1234567896,
    "nft_trading": -1234567897,
    "arbitrage_opportunities": -1234567898,
    "leverage_trading": -1234567899,
}

if __name__ == "__main__":
    # Demo the functionality
    print("🔧 Telegram Groups Manager")
    get_group_stats()
    TelegramConfig.list_monitored_groups()