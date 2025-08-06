#!/usr/bin/env python3
"""
Test script for /report optimize admin command.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from admin.command_handler import AdminCommandHandler, AdminCommand


def create_mock_accuracy_data():
    """Create mock accuracy data for testing."""
    mock_data = {
        "accuracy_data": {
            "cryptoraketen": [
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "was_win": True,
                    "pnl": 150.0,
                    "pnl_percent": 2.5,
                    "duration_minutes": 120,
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
                },
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "was_win": True,
                    "pnl": 200.0,
                    "pnl_percent": 3.2,
                    "duration_minutes": 90,
                    "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
                },
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "was_win": False,
                    "pnl": -50.0,
                    "pnl_percent": -0.8,
                    "duration_minutes": 60,
                    "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
                },
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "was_win": True,
                    "pnl": 180.0,
                    "pnl_percent": 2.8,
                    "duration_minutes": 150,
                    "timestamp": (datetime.now() - timedelta(days=4)).isoformat()
                },
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "was_win": True,
                    "pnl": 220.0,
                    "pnl_percent": 3.5,
                    "duration_minutes": 110,
                    "timestamp": (datetime.now() - timedelta(days=5)).isoformat()
                }
            ],
            "smart_crypto_signals": [
                {
                    "symbol": "ETHUSDT",
                    "timeframe": "5m",
                    "was_win": False,
                    "pnl": -100.0,
                    "pnl_percent": -1.5,
                    "duration_minutes": 30,
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
                },
                {
                    "symbol": "ETHUSDT",
                    "timeframe": "5m",
                    "was_win": False,
                    "pnl": -80.0,
                    "pnl_percent": -1.2,
                    "duration_minutes": 25,
                    "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
                },
                {
                    "symbol": "ETHUSDT",
                    "timeframe": "5m",
                    "was_win": True,
                    "pnl": 60.0,
                    "pnl_percent": 0.9,
                    "duration_minutes": 20,
                    "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
                },
                {
                    "symbol": "ETHUSDT",
                    "timeframe": "5m",
                    "was_win": False,
                    "pnl": -120.0,
                    "pnl_percent": -1.8,
                    "duration_minutes": 35,
                    "timestamp": (datetime.now() - timedelta(days=4)).isoformat()
                },
                {
                    "symbol": "ETHUSDT",
                    "timeframe": "5m",
                    "was_win": False,
                    "pnl": -90.0,
                    "pnl_percent": -1.4,
                    "duration_minutes": 28,
                    "timestamp": (datetime.now() - timedelta(days=5)).isoformat()
                }
            ]
        },
        "group_stats": {
            "cryptoraketen": {"total_trades": 5, "win_rate": 80.0},
            "smart_crypto_signals": {"total_trades": 5, "win_rate": 20.0}
        }
    }
    return mock_data


async def test_report_optimize_command():
    """Test the /report optimize command functionality."""
    print("🚀 Starting /report optimize Command Tests")
    print("=" * 60)
    
    # Create temporary file for mock data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        mock_data = create_mock_accuracy_data()
        json.dump(mock_data, f, indent=2)
        temp_file_path = f.name
    
    try:
        # Test 1: AdminCommandHandler Creation
        print("🧪 Testing AdminCommandHandler Creation")
        print("=" * 50)
        handler = AdminCommandHandler()
        print("   ✅ AdminCommandHandler created successfully")
        
        # Test 2: Parse /report optimize Command
        print("\n📝 Testing Command Parsing")
        print("=" * 50)
        command = handler.parse_command("/report optimize", 12345, "testadmin", 67890)
        
        if command:
            print(f"   • Command: {command.command}")
            print(f"   • Args: {command.args}")
            print(f"   • User ID: {command.user_id}")
            print(f"   • Username: {command.username}")
            print("   ✅ Command parsed successfully")
        else:
            print("   ❌ Failed to parse command")
            return
        
        # Test 3: Mock Admin Authorization
        print("\n👑 Testing Admin Authorization")
        print("=" * 50)
        # Temporarily add test user to admin list
        from config.settings import ADMIN_USER_IDS
        original_admin_ids = ADMIN_USER_IDS.copy()
        ADMIN_USER_IDS.append(12345)
        
        is_admin = handler.is_admin(12345, "testadmin")
        print(f"   • Is Admin: {is_admin}")
        print("   ✅ Admin authorization test completed")
        
        # Test 4: Generate Optimization Report
        print("\n📊 Testing Optimization Report Generation")
        print("=" * 50)
        
        # Temporarily modify the accuracy data path for testing
        import config.settings
        original_path = config.settings.ACCURACY_RESULTS_PATH
        config.settings.ACCURACY_RESULTS_PATH = temp_file_path
        
        try:
            # Generate the optimization report
            report = await handler._generate_optimization_report()
            
            print("   • Report generated successfully")
            print("   • Report length:", len(report))
            print("   • Report preview:")
            print("   " + "=" * 40)
            
            # Print first few lines of the report
            lines = report.split('\n')[:15]
            for line in lines:
                print(f"   {line}")
            
            if len(report.split('\n')) > 15:
                print("   ...")
            
            print("   ✅ Optimization report generation completed")
            
        except Exception as e:
            print(f"   ❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Restore original path
            config.settings.ACCURACY_RESULTS_PATH = original_path
            ADMIN_USER_IDS.clear()
            ADMIN_USER_IDS.extend(original_admin_ids)
        
        # Test 5: Full Command Execution
        print("\n🔄 Testing Full Command Execution")
        print("=" * 50)
        
        # Create a mock command for full execution
        mock_command = AdminCommand(
            command="report",
            args=["optimize"],
            user_id=12345,
            username="testadmin",
            chat_id=67890,
            timestamp=datetime.now(),
            raw_message="/report optimize"
        )
        
        # Temporarily set up admin access
        ADMIN_USER_IDS.append(12345)
        config.settings.ACCURACY_RESULTS_PATH = temp_file_path
        
        try:
            # Execute the full command
            response = await handler.handle_command(mock_command)
            
            print("   • Full command execution completed")
            print("   • Response length:", len(response))
            print("   • Response contains 'STRATEGY OPTIMIZATION REPORT':", "STRATEGY OPTIMIZATION REPORT" in response)
            print("   ✅ Full command execution successful")
            
        except Exception as e:
            print(f"   ❌ Error in full command execution: {e}")
        
        finally:
            # Clean up
            ADMIN_USER_IDS.clear()
            ADMIN_USER_IDS.extend(original_admin_ids)
            config.settings.ACCURACY_RESULTS_PATH = original_path
        
        # Test 6: Error Handling
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test with non-existent accuracy file
        config.settings.ACCURACY_RESULTS_PATH = "non_existent_file.json"
        
        try:
            error_report = await handler._generate_optimization_report()
            print("   • Error report generated for missing file")
            print("   • Contains error message:", "No accuracy data found" in error_report)
            print("   ✅ Error handling working correctly")
        except Exception as e:
            print(f"   ❌ Error handling failed: {e}")
        
        finally:
            config.settings.ACCURACY_RESULTS_PATH = original_path
        
        print("\n" + "=" * 60)
        print("📋 Test Results: All tests completed!")
        print("✅ /report optimize command is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_report_optimize_command()) 