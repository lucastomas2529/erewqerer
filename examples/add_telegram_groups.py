#!/usr/bin/env python3
"""
Example script showing how to add multiple Telegram groups for signal monitoring.

Usage:
    python examples/add_telegram_groups.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TelegramConfig
from utils.telegram_groups import add_multiple_groups, get_group_stats

def main():
    print("🔧 Telegram Groups Configuration Example")
    print("=" * 50)
    
    # Show current status
    print("\n📊 Current Status:")
    get_group_stats()
    
    # Example: Add multiple groups at once
    new_groups = {
        "premium_crypto_signals": -1234567890,
        "altcoin_alerts": -1234567891,  
        "futures_trading": -1234567892,
        "scalping_signals": -1234567893,
        "whale_alerts": -1234567894,
        # Add more groups as needed (up to 20 total)
    }
    
    print(f"\n➕ Adding {len(new_groups)} new groups...")
    # Uncomment the line below to actually add the groups
    # add_multiple_groups(new_groups)
    
    print("\n💡 To add groups in your code:")
    print("from config.settings import TelegramConfig")
    print("TelegramConfig.add_telegram_group('group_name', -1234567890)")
    
    print("\n💡 To add multiple groups:")
    print("from utils.telegram_groups import add_multiple_groups")
    print("add_multiple_groups({'group1': -123, 'group2': -456})")
    
    print("\n📋 Example group configuration:")
    for name, group_id in new_groups.items():
        print(f"  • {name}: {group_id}")
    
    print("\n✅ Configuration ready! The bot will monitor all groups in TelegramConfig.TELEGRAM_GROUPS")

if __name__ == "__main__":
    main()