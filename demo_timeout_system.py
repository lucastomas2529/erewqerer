#!/usr/bin/env python3
"""
Demo script showing timeout protection system in action.
Demonstrates trade registration, duration tracking, and auto-closure scenarios.
"""

import asyncio
import time
from datetime import datetime, timedelta
from core.timeout_manager import timeout_manager
from core.entry_manager import execute_entry_strategy
from core.api import get_current_price_async

async def demo_timeout_workflow():
    """Demonstrate the complete timeout protection workflow."""
    
    print("⏰ TIMEOUT PROTECTION SYSTEM DEMO")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Place a real trade using entry strategy
    print("📊 STEP 1: PLACE TRADE WITH ENTRY STRATEGY")
    print("-" * 40)
    
    result = await execute_entry_strategy(
        symbol="BTCUSDT",
        side="buy",
        risk_percent=1.0,
        leverage=10,
        step1_ratio=0.5
    )
    
    if result['orders']:
        entry_price = result['orders'][0]['price']
        sl_price = result['orders'][0]['sl_price']
        tp_price = result['orders'][0]['tp_price']
        order_ids = [order['order_id'] for order in result['orders']]
        quantity = 0.001  # Mock quantity
        
        print(f"✅ Trade placed successfully:")
        print(f"   Symbol: BTCUSDT")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   SL: ${sl_price:,.2f}")
        print(f"   TP: ${tp_price:,.2f}")
        print(f"   Orders: {len(result['orders'])}")
        
        # Step 2: Register for timeout monitoring
        print("\n📊 STEP 2: REGISTER FOR TIMEOUT MONITORING")
        print("-" * 40)
        
        await timeout_manager.register_trade(
            symbol="BTCUSDT",
            side="buy",
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=[tp_price],
            order_ids=order_ids,
            quantity=quantity
        )
        
        print(f"✅ Trade registered for timeout monitoring:")
        print(f"   Timeout: {timeout_manager.timeout_hours} hours")
        print(f"   Check interval: {timeout_manager.check_interval} seconds")
        
        # Step 3: Simulate time passage and monitoring
        print("\n📊 STEP 3: SIMULATE TIME PASSAGE")
        print("-" * 40)
        
        # Simulate different time scenarios
        scenarios = [
            {"hours": 0.1, "description": "Just started - no timeout"},
            {"hours": 2.0, "description": "Halfway through - no timeout"},
            {"hours": 3.5, "description": "Almost timeout - warning"},
            {"hours": 4.5, "description": "Timeout exceeded - should close"}
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   Scenario {i}: {scenario['description']}")
            print(f"   Simulated Duration: {scenario['hours']:.1f} hours")
            
            # Simulate time passage by modifying the entry timestamp
            if "BTCUSDT" in timeout_manager.active_trades:
                trade = timeout_manager.active_trades["BTCUSDT"]
                trade["entry_timestamp"] = time.time() - (scenario["hours"] * 3600)
                trade["entry_datetime"] = datetime.now() - timedelta(hours=scenario["hours"])
            
            # Test timeout conditions
            timeout_met = await timeout_manager.check_timeout_conditions("BTCUSDT")
            print(f"   Timeout triggered: {timeout_met}")
            
            # Show current status
            status = timeout_manager.get_trade_status("BTCUSDT")
            if status:
                duration = status['duration_hours']
                remaining = timeout_manager.timeout_hours - duration
                print(f"   Duration: {duration:.2f} hours")
                print(f"   Remaining: {remaining:.2f} hours")
                
                if timeout_met:
                    print("   ⏰ TIMEOUT TRIGGERED - Trade should be closed!")
                    # Note: We won't actually close it in the demo
                    print("   (Skipping actual closure for demo purposes)")
            
            # Small delay to simulate real-time monitoring
            await asyncio.sleep(1)
        
        # Step 4: Show final status
        print("\n📊 STEP 4: FINAL STATUS")
        print("-" * 40)
        
        status = timeout_manager.get_trade_status("BTCUSDT")
        if status:
            print(f"📊 Trade Status:")
            print(f"   Symbol: {status['symbol']}")
            print(f"   Side: {status['side']}")
            print(f"   Entry: ${status['entry_price']:,.2f}")
            print(f"   Entry Time: {status['entry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duration: {status['duration_hours']:.2f} hours")
            print(f"   Timeout Hours: {status['timeout_hours']}")
            print(f"   Status: {status['status']}")
        
        print("\n✅ Timeout Protection Demo Completed!")
    
    else:
        print("❌ Failed to place trade")

async def demo_multiple_trades():
    """Demonstrate timeout protection with multiple trades."""
    
    print("\n🔄 MULTIPLE TRADES DEMO")
    print("=" * 40)
    
    # Register multiple trades with different entry times
    trades = [
        {
            "symbol": "ETHUSDT",
            "side": "buy",
            "entry": 3750.0,
            "sl": 3650.0,
            "tp": 3900.0,
            "quantity": 0.1,
            "hours_ago": 1.5  # 1.5 hours ago
        },
        {
            "symbol": "SOLUSDT",
            "side": "sell",
            "entry": 135.0,
            "sl": 140.0,
            "tp": 130.0,
            "quantity": 10.0,
            "hours_ago": 3.0  # 3 hours ago
        },
        {
            "symbol": "ADAUSDT",
            "side": "buy",
            "entry": 0.50,
            "sl": 0.48,
            "tp": 0.55,
            "quantity": 1000.0,
            "hours_ago": 4.5  # 4.5 hours ago - should timeout
        }
    ]
    
    for trade in trades:
        # Register trade
        await timeout_manager.register_trade(
            symbol=trade["symbol"],
            side=trade["side"],
            entry_price=trade["entry"],
            sl_price=trade["sl"],
            tp_prices=[trade["tp"]],
            order_ids=[f"mock_{trade['symbol']}_1", f"mock_{trade['symbol']}_2"],
            quantity=trade["quantity"]
        )
        
        # Simulate entry time
        if trade["symbol"] in timeout_manager.active_trades:
            trade_obj = timeout_manager.active_trades[trade["symbol"]]
            trade_obj["entry_timestamp"] = time.time() - (trade["hours_ago"] * 3600)
            trade_obj["entry_datetime"] = datetime.now() - timedelta(hours=trade["hours_ago"])
        
        print(f"✅ {trade['symbol']} registered ({trade['hours_ago']}h ago)")
    
    # Check all trades
    print(f"\n📊 Monitoring {len(trades)} trades:")
    all_status = timeout_manager.get_all_trades_status()
    
    for symbol, trade_info in all_status['trades'].items():
        duration = trade_info['duration_hours']
        remaining = trade_info['remaining_hours']
        timeout_warning = "⚠️" if duration > 3.5 else "✅"
        timeout_status = "TIMEOUT" if duration >= 4.0 else "ACTIVE"
        
        print(f"   {symbol}: {duration:.2f}h elapsed, {remaining:.2f}h remaining {timeout_warning} {timeout_status}")

async def demo_configuration():
    """Show the current timeout configuration settings."""
    
    print("\n⚙️ CONFIGURATION DEMO")
    print("=" * 40)
    
    from config.settings import TradingConfig
    
    configs = {
        "Timeout hours": f"{TradingConfig.TIMEOUT_HOURS} hours",
        "Check interval": f"{TradingConfig.TIMEOUT_CHECK_INTERVAL} seconds",
        "Check frequency": f"Every {TradingConfig.TIMEOUT_CHECK_INTERVAL} seconds"
    }
    
    print("📋 Current Timeout Configuration:")
    for name, value in configs.items():
        print(f"   {name}: {value}")
    
    print("\n💡 Configuration Notes:")
    print("   • Trades are automatically closed after 4 hours")
    print("   • System checks for timeouts every 60 seconds")
    print("   • All existing orders are cancelled before closure")
    print("   • Market orders are used to close positions")
    print("   • PnL is calculated and logged at closure")

if __name__ == "__main__":
    print("⏰ Starting Timeout Protection System Demo...")
    asyncio.run(demo_timeout_workflow())
    asyncio.run(demo_multiple_trades())
    asyncio.run(demo_configuration())
    print(f"\n⚡ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 