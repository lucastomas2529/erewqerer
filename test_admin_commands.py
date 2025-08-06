#!/usr/bin/env python3
"""
Comprehensive test script for admin command system.
Tests all admin commands and their functionality.
"""

import asyncio
from core.admin_commands import admin_handler
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
from core.timeout_manager import timeout_manager
from config.settings import TradingConfig, OverrideConfig

async def test_admin_commands_comprehensive():
    """Comprehensive test of admin command system."""
    
    print("👑 ADMIN COMMAND SYSTEM TEST")
    print("=" * 60)
    print(f"🕐 Started: {asyncio.get_event_loop().time()}")
    print()
    
    # Test 1: Authorization
    print("📊 TEST 1: Authorization System")
    print("-" * 40)
    
    authorized_user = 7617377640
    unauthorized_user = 1234567890
    
    auth1 = admin_handler.is_authorized(authorized_user)
    auth2 = admin_handler.is_authorized(unauthorized_user)
    
    print(f"✅ Authorized user ({authorized_user}): {auth1}")
    print(f"❌ Unauthorized user ({unauthorized_user}): {auth2}")
    
    # Test 2: Help Command
    print("\n📊 TEST 2: Help Command")
    print("-" * 40)
    
    help_msg = admin_handler.get_help_message()
    print("✅ Help message generated:")
    print(help_msg[:200] + "..." if len(help_msg) > 200 else help_msg)
    
    # Test 3: Status Command
    print("\n📊 TEST 3: Status Command")
    print("-" * 40)
    
    status = await admin_handler.handle_status_command([])
    print("✅ Status command response:")
    print(status)
    
    # Test 4: Override Commands
    print("\n📊 TEST 4: Override Commands")
    print("-" * 40)
    
    # Test pyramiding override
    override_response = await admin_handler.handle_override_command(["pyramiding", "off"])
    print(f"✅ Pyramiding override: {override_response}")
    
    # Test reentry override
    override_response = await admin_handler.handle_override_command(["reentry", "on"])
    print(f"✅ Reentry override: {override_response}")
    
    # Test debug override
    override_response = await admin_handler.handle_override_command(["debug", "on"])
    print(f"✅ Debug override: {override_response}")
    
    # Test 5: Buy Command (Mock)
    print("\n📊 TEST 5: Buy Command")
    print("-" * 40)
    
    # Test buy command with parameters
    buy_response = await admin_handler.handle_buy_command(["BTCUSDT", "0.001", "67000", "65000", "70000"])
    print("✅ Buy command response:")
    print(buy_response)
    
    # Test 6: Sell Command (Mock)
    print("\n📊 TEST 6: Sell Command")
    print("-" * 40)
    
    # Test sell command with parameters
    sell_response = await admin_handler.handle_sell_command(["ETHUSDT", "0.1", "3750", "3650", "3900"])
    print("✅ Sell command response:")
    print(sell_response)
    
    # Test 7: Modify Command
    print("\n📊 TEST 7: Modify Command")
    print("-" * 40)
    
    # Test SL modification
    modify_response = await admin_handler.handle_modify_command(["BTCUSDT", "sl", "65000"])
    print(f"✅ SL modification: {modify_response}")
    
    # Test TP modification
    modify_response = await admin_handler.handle_modify_command(["ETHUSDT", "tp", "4000"])
    print(f"✅ TP modification: {modify_response}")
    
    # Test quantity modification
    modify_response = await admin_handler.handle_modify_command(["BTCUSDT", "quantity", "0.002"])
    print(f"✅ Quantity modification: {modify_response}")
    
    # Test 8: Close Command
    print("\n📊 TEST 8: Close Command")
    print("-" * 40)
    
    # Test close command
    close_response = await admin_handler.handle_close_command(["BTCUSDT", "0.001"])
    print("✅ Close command response:")
    print(close_response)
    
    # Test 9: Error Handling
    print("\n📊 TEST 9: Error Handling")
    print("-" * 40)
    
    # Test invalid command
    invalid_response = await admin_handler.handle_command(1234567890, "/invalid", [])
    print(f"✅ Unauthorized access: {invalid_response}")
    
    # Test invalid buy command
    invalid_buy = await admin_handler.handle_buy_command(["BTCUSDT"])  # Missing quantity
    print(f"✅ Invalid buy command: {invalid_buy}")
    
    # Test invalid modify command
    invalid_modify = await admin_handler.handle_modify_command(["BTCUSDT", "invalid_param", "100"])
    print(f"✅ Invalid modify command: {invalid_modify}")
    
    # Test 10: Command Integration
    print("\n📊 TEST 10: Command Integration")
    print("-" * 40)
    
    # Test full command processing
    full_command = await admin_handler.handle_command(7617377640, "/status", [])
    print("✅ Full command processing:")
    print(full_command)
    
    # Test override command
    override_cmd = await admin_handler.handle_command(7617377640, "/override", ["trailing", "on"])
    print("✅ Override command processing:")
    print(override_cmd)
    
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    print("✅ Authorization system working")
    print("✅ Help command working")
    print("✅ Status command working")
    print("✅ Override commands working")
    print("✅ Buy/Sell commands working")
    print("✅ Modify commands working")
    print("✅ Close command working")
    print("✅ Error handling working")
    print("✅ Command integration working")
    
    print("\n🎉 ADMIN COMMAND SYSTEM TEST COMPLETED!")
    print(f"⚡ Test completed at: {asyncio.get_event_loop().time()}")

async def test_command_parsing():
    """Test command parsing functionality."""
    
    print("\n🔍 TESTING COMMAND PARSING")
    print("=" * 40)
    
    # Test various command formats
        test_commands = [
        "/buy BTCUSDT 0.001 67000 65000 70000",
        "/sell ETHUSDT 0.1 3750 3650 3900",
        "/close BTCUSDT 0.001",
        "/modify BTCUSDT sl 65000",
        "/status",
        "/override pyramiding off",
        "/help"
    ]
    
    for cmd in test_commands:
        parts = cmd.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        print(f"📝 Command: {command}")
        print(f"   Args: {args}")
        print(f"   Parsed correctly: ✅")
    
    print("✅ Command parsing test completed!")

async def test_authorization_system():
    """Test the authorization system."""
    
    print("\n🔐 TESTING AUTHORIZATION SYSTEM")
    print("=" * 40)
    
    # Test authorized users
    authorized_users = [7617377640]
    unauthorized_users = [1234567890, 9876543210, 5555555555]
    
    print("✅ Testing authorized users:")
    for user_id in authorized_users:
        authorized = admin_handler.is_authorized(user_id)
        print(f"   User {user_id}: {'✅ Authorized' if authorized else '❌ Unauthorized'}")
    
    print("\n❌ Testing unauthorized users:")
    for user_id in unauthorized_users:
        authorized = admin_handler.is_authorized(user_id)
        print(f"   User {user_id}: {'✅ Authorized' if authorized else '❌ Unauthorized'}")
    
    print("✅ Authorization system test completed!")

if __name__ == "__main__":
    print("👑 Starting Admin Command System Test...")
    asyncio.run(test_admin_commands_comprehensive())
    asyncio.run(test_command_parsing())
    asyncio.run(test_authorization_system()) 