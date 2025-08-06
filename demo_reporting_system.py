#!/usr/bin/env python3
"""
Demo script showing the complete reporting system in action.
Demonstrates logging, reporting, and notifications.
"""

import asyncio
from datetime import datetime, timedelta
from core.reporting_system import reporting_system
from core.admin_commands import admin_handler

async def demo_reporting_system():
    """Demonstrate the complete reporting system."""
    
    print("📊 REPORTING SYSTEM DEMO")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    # Demo 1: Signal Processing
    print("📊 DEMO 1: Signal Processing")
    print("-" * 40)
    
    # Simulate signal processing
    signals = [
        {
            'group_name': 'Premium Signals',
            'signal_text': 'BTCUSDT LONG 67000 65000 70000',
            'parsed_data': {
                'symbol': 'BTCUSDT',
                'side': 'long',
                'entry': 67000,
                'sl': 65000,
                'tp': [70000]
            },
            'processing_time': 0.2,
            'status': 'processed'
        },
        {
            'group_name': 'VIP Signals',
            'signal_text': 'ETHUSDT SHORT 3750 3800 3700',
            'parsed_data': {
                'symbol': 'ETHUSDT',
                'side': 'short',
                'entry': 3750,
                'sl': 3800,
                'tp': [3700]
            },
            'processing_time': 0.1,
            'status': 'processed'
        }
    ]
    
    for i, signal_data in enumerate(signals, 1):
        signal_id = await reporting_system.log_signal(signal_data)
        print(f"✅ Signal {i} processed: {signal_id}")
    
    # Demo 2: Trade Execution
    print("\n📊 DEMO 2: Trade Execution")
    print("-" * 40)
    
    # Simulate trade execution
    trades = [
        {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'quantity': 0.001,
            'entry_price': 67000,
            'sl_price': 65000,
            'tp_prices': [70000],
            'order_ids': ['order_1'],
            'group_name': 'Premium Signals',
            'signal_source': 'telegram',
            'processing_time': 0.5,
            'admin_command': False
        },
        {
            'symbol': 'ETHUSDT',
            'side': 'sell',
            'quantity': 0.1,
            'entry_price': 3750,
            'sl_price': 3800,
            'tp_prices': [3700],
            'order_ids': ['order_2'],
            'group_name': 'VIP Signals',
            'signal_source': 'telegram',
            'processing_time': 0.3,
            'admin_command': False
        }
    ]
    
    trade_ids = []
    for i, trade_data in enumerate(trades, 1):
        trade_id = await reporting_system.log_trade(trade_data)
        trade_ids.append(trade_id)
        print(f"✅ Trade {i} executed: {trade_id}")
    
    # Demo 3: Admin Commands
    print("\n📊 DEMO 3: Admin Commands")
    print("-" * 40)
    
    # Simulate admin commands
    admin_trades = [
        {
            'symbol': 'SOLUSDT',
            'side': 'buy',
            'quantity': 1.0,
            'entry_price': 150,
            'sl_price': 145,
            'tp_prices': [160],
            'order_ids': ['admin_order_1'],
            'group_name': 'Admin Command',
            'signal_source': 'admin_command',
            'processing_time': 0.8,
            'admin_command': True
        }
    ]
    
    for i, trade_data in enumerate(admin_trades, 1):
        trade_id = await reporting_system.log_trade(trade_data)
        print(f"✅ Admin trade {i} executed: {trade_id}")
    
    # Demo 4: Error Handling
    print("\n📊 DEMO 4: Error Handling")
    print("-" * 40)
    
    # Simulate errors
    errors = [
        {
            'error_type': 'API_ERROR',
            'error_message': 'Failed to place order',
            'context': {'symbol': 'BTCUSDT', 'action': 'place_order'},
            'severity': 'medium'
        },
        {
            'error_type': 'NETWORK_ERROR',
            'error_message': 'Connection timeout',
            'context': {'endpoint': '/api/v1/order', 'timeout': 30},
            'severity': 'high'
        }
    ]
    
    for i, error_data in enumerate(errors, 1):
        error_id = await reporting_system.log_error(error_data)
        print(f"⚠️ Error {i} logged: {error_id}")
    
    # Demo 5: Daily Report
    print("\n📊 DEMO 5: Daily Report")
    print("-" * 40)
    
    daily_report = await reporting_system.generate_daily_report()
    
    print("📋 Daily Report Summary:")
    summary = daily_report.get('summary', {})
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Closed Trades: {summary.get('closed_trades', 0)}")
    print(f"   Total PnL: ${summary.get('total_pnl', 0):,.2f}")
    print(f"   Win Rate: {summary.get('win_rate', 0):.1f}%")
    print(f"   Signals Received: {summary.get('signals_received', 0)}")
    print(f"   Errors Occurred: {summary.get('errors_occurred', 0)}")
    
    # Demo 6: Weekly Report
    print("\n📊 DEMO 6: Weekly Report")
    print("-" * 40)
    
    weekly_report = await reporting_system.generate_weekly_report()
    
    print("📋 Weekly Report Summary:")
    period = weekly_report.get('period', {})
    summary = weekly_report.get('summary', {})
    print(f"   Period: {period.get('start_date', 'Unknown')} to {period.get('end_date', 'Unknown')}")
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Closed Trades: {summary.get('closed_trades', 0)}")
    print(f"   Total PnL: ${summary.get('total_pnl', 0):,.2f}")
    print(f"   Win Rate: {summary.get('win_rate', 0):.1f}%")
    print(f"   Avg PnL per Trade: ${summary.get('avg_pnl_per_trade', 0):,.2f}")
    
    # Demo 7: Group Performance
    print("\n📊 DEMO 7: Group Performance")
    print("-" * 40)
    
    group_stats = daily_report.get('group_stats', {})
    print("📋 Group Performance Analysis:")
    for group, stats in group_stats.items():
        print(f"   {group}:")
        print(f"     Trades: {stats['trades']}")
        print(f"     Total PnL: ${stats['total_pnl']:,.2f}")
        print(f"     Winning Trades: {stats['winning_trades']}")
        print(f"     Losing Trades: {stats['losing_trades']}")
        if stats['trades'] > 0:
            win_rate = (stats['winning_trades'] / stats['trades'] * 100)
            print(f"     Win Rate: {win_rate:.1f}%")
    
    # Demo 8: Telegram Notifications
    print("\n📊 DEMO 8: Telegram Notifications")
    print("-" * 40)
    
    print("📱 Sending reports to Telegram...")
    await reporting_system.send_daily_report_to_telegram(daily_report)
    await reporting_system.send_weekly_report_to_telegram(weekly_report)
    print("✅ Reports sent to Telegram")
    
    # Demo 9: File Storage
    print("\n📊 DEMO 9: File Storage")
    print("-" * 40)
    
    # Save reports to files
    await reporting_system.save_report_to_file(daily_report, "demo_daily_report.json")
    await reporting_system.save_report_to_file(weekly_report, "demo_weekly_report.json")
    
    print("✅ Daily report saved to: reports/demo_daily_report.json")
    print("✅ Weekly report saved to: reports/demo_weekly_report.json")
    
    # Demo 10: Statistics Overview
    print("\n📊 DEMO 10: Statistics Overview")
    print("-" * 40)
    
    print("📋 Real-time Statistics:")
    daily_stats = reporting_system.daily_stats
    print(f"   Trades Executed: {daily_stats['trades_executed']}")
    print(f"   Signals Received: {daily_stats['signals_received']}")
    print(f"   Errors Occurred: {daily_stats['errors_occurred']}")
    print(f"   Total PnL: ${daily_stats['total_pnl']:,.2f}")
    print(f"   Winning Trades: {daily_stats['winning_trades']}")
    print(f"   Losing Trades: {daily_stats['losing_trades']}")
    
    print("\n📋 Group Statistics:")
    group_stats = reporting_system.group_stats
    for group, stats in group_stats.items():
        print(f"   {group}: {stats['trades']} trades, ${stats['total_pnl']:,.2f} PnL")
    
    print("\n📊 DEMO SUMMARY")
    print("=" * 60)
    print("✅ Signal processing and logging")
    print("✅ Trade execution and logging")
    print("✅ Admin command logging")
    print("✅ Error handling and logging")
    print("✅ Daily report generation")
    print("✅ Weekly report generation")
    print("✅ Group performance analysis")
    print("✅ Telegram notifications")
    print("✅ File storage")
    print("✅ Real-time statistics")
    
    print(f"\n🎉 REPORTING SYSTEM DEMO COMPLETED!")
    print(f"⚡ Demo completed at: {datetime.now()}")

async def demo_integration_scenarios():
    """Demonstrate integration scenarios."""
    
    print("\n🔗 INTEGRATION SCENARIOS DEMO")
    print("=" * 40)
    
    # Scenario 1: Signal to Trade Pipeline
    print("📊 Scenario 1: Signal to Trade Pipeline")
    print("-" * 40)
    
    # Simulate signal processing
    signal_data = {
        'group_name': 'Premium Signals',
        'signal_text': 'BTCUSDT LONG 67000 65000 70000',
        'parsed_data': {
            'symbol': 'BTCUSDT',
            'side': 'long',
            'entry': 67000,
            'sl': 65000,
            'tp': [70000]
        },
        'processing_time': 0.2,
        'status': 'processed'
    }
    
    signal_id = await reporting_system.log_signal(signal_data)
    print(f"✅ Signal processed: {signal_id}")
    
    # Simulate trade execution
    trade_data = {
        'symbol': 'BTCUSDT',
        'side': 'buy',
        'quantity': 0.001,
        'entry_price': 67000,
        'sl_price': 65000,
        'tp_prices': [70000],
        'order_ids': ['order_1'],
        'group_name': 'Premium Signals',
        'signal_source': 'telegram',
        'processing_time': 0.5,
        'admin_command': False
    }
    
    trade_id = await reporting_system.log_trade(trade_data)
    print(f"✅ Trade executed: {trade_id}")
    
    # Scenario 2: Admin Command Pipeline
    print("\n📊 Scenario 2: Admin Command Pipeline")
    print("-" * 40)
    
    # Simulate admin command
    admin_trade_data = {
        'symbol': 'ETHUSDT',
        'side': 'sell',
        'quantity': 0.1,
        'entry_price': 3750,
        'sl_price': 3800,
        'tp_prices': [3700],
        'order_ids': ['admin_order_1'],
        'group_name': 'Admin Command',
        'signal_source': 'admin_command',
        'processing_time': 0.8,
        'admin_command': True
    }
    
    admin_trade_id = await reporting_system.log_trade(admin_trade_data)
    print(f"✅ Admin trade executed: {admin_trade_id}")
    
    # Scenario 3: Error Handling Pipeline
    print("\n📊 Scenario 3: Error Handling Pipeline")
    print("-" * 40)
    
    # Simulate error
    error_data = {
        'error_type': 'API_ERROR',
        'error_message': 'Failed to place order',
        'context': {'symbol': 'BTCUSDT', 'action': 'place_order'},
        'severity': 'medium'
    }
    
    error_id = await reporting_system.log_error(error_data)
    print(f"⚠️ Error logged: {error_id}")
    
    # Generate final report
    print("\n📊 Final Integration Report")
    print("-" * 40)
    
    daily_report = await reporting_system.generate_daily_report()
    summary = daily_report.get('summary', {})
    
    print(f"📋 Integration Summary:")
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Signals Processed: {summary.get('signals_received', 0)}")
    print(f"   Errors Handled: {summary.get('errors_occurred', 0)}")
    
    print("✅ Integration scenarios completed!")

if __name__ == "__main__":
    print("📊 Starting Reporting System Demo...")
    asyncio.run(demo_reporting_system())
    asyncio.run(demo_integration_scenarios()) 