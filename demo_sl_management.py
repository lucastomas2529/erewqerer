#!/usr/bin/env python3
"""
Comprehensive demo of SL management with break-even and trailing stops.
Shows real-world scenarios with price movements and SL adjustments.
"""

import asyncio
import time
from datetime import datetime
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
from core.entry_manager import execute_entry_strategy
from core.api import get_current_price_async

async def demo_sl_management_workflow():
    """Demonstrate the complete SL management workflow."""
    
    print("🚀 SL MANAGEMENT WORKFLOW DEMO")
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
        
        print(f"✅ Trade placed successfully:")
        print(f"   Symbol: BTCUSDT")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   SL: ${sl_price:,.2f}")
        print(f"   TP: ${tp_price:,.2f}")
        print(f"   Orders: {len(result['orders'])}")
        
        # Step 2: Register for SL management
        print("\n📊 STEP 2: REGISTER FOR SL MANAGEMENT")
        print("-" * 40)
        
        # Register for break-even monitoring
        await breakeven_manager.register_trade(
            symbol="BTCUSDT",
            side="buy",
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=[tp_price],  # Single TP for demo
            order_ids=order_ids
        )
        
        # Register for trailing stop monitoring
        await trailing_manager.register_trade(
            symbol="BTCUSDT",
            side="buy",
            entry_price=entry_price,
            sl_price=sl_price,
            tp_prices=[tp_price],  # Single TP for demo
            order_ids=order_ids
        )
        
        print(f"✅ Trade registered for SL management:")
        print(f"   Break-even monitoring: ✅ Active")
        print(f"   Trailing stop monitoring: ✅ Active")
        
        # Step 3: Simulate price movements and SL adjustments
        print("\n📊 STEP 3: SIMULATE PRICE MOVEMENTS")
        print("-" * 40)
        
        # Simulate different price scenarios
        scenarios = [
            {"price": entry_price * 0.99, "description": "Price drops - no triggers"},
            {"price": entry_price * 1.01, "description": "Small profit - no triggers"},
            {"price": entry_price * 1.025, "description": "2.5% profit - break-even should trigger"},
            {"price": entry_price * 1.035, "description": "3.5% profit - trailing should activate"},
            {"price": entry_price * 1.05, "description": "5% profit - trailing should update"}
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   Scenario {i}: {scenario['description']}")
            print(f"   Simulated Price: ${scenario['price']:,.2f}")
            
            # Test break-even conditions
            breakeven_met = await breakeven_manager.check_breakeven_conditions("BTCUSDT")
            print(f"   Break-even triggered: {breakeven_met}")
            
            if breakeven_met:
                await breakeven_manager.move_to_breakeven("BTCUSDT")
            
            # Test trailing conditions
            trailing_met = await trailing_manager.check_trailing_conditions("BTCUSDT")
            print(f"   Trailing triggered: {trailing_met}")
            
            if trailing_met:
                await trailing_manager.activate_trailing("BTCUSDT")
            
            # Small delay to simulate real-time monitoring
            await asyncio.sleep(1)
        
        # Step 4: Show final status
        print("\n📊 STEP 4: FINAL STATUS")
        print("-" * 40)
        
        breakeven_status = breakeven_manager.get_trade_status("BTCUSDT")
        trailing_status = trailing_manager.get_trade_status("BTCUSDT")
        
        print(f"📊 Break-even Status:")
        print(f"   Triggered: {'✅' if breakeven_status['breakeven_triggered'] else '⏳'}")
        print(f"   Current SL: ${breakeven_status['current_sl']:,.2f}")
        print(f"   Original SL: ${breakeven_status['original_sl']:,.2f}")
        
        print(f"\n📊 Trailing Status:")
        print(f"   Active: {'✅' if trailing_status['trailing_active'] else '⏳'}")
        print(f"   Current SL: ${trailing_status['current_sl']:,.2f}")
        print(f"   Highest Price: ${trailing_status['highest_price']:,.2f}")
        
        print("\n✅ SL Management Demo Completed!")
    
    else:
        print("❌ Failed to place trade")

async def demo_multiple_trades():
    """Demonstrate SL management with multiple trades."""
    
    print("\n🔄 MULTIPLE TRADES DEMO")
    print("=" * 40)
    
    # Register multiple trades with different scenarios
    trades = [
        {
            "symbol": "ETHUSDT",
            "side": "buy",
            "entry": 3750.0,
            "sl": 3650.0,
            "tp": 3900.0,
            "description": "ETH Long"
        },
        {
            "symbol": "SOLUSDT", 
            "side": "sell",
            "entry": 135.0,
            "sl": 140.0,
            "tp": 130.0,
            "description": "SOL Short"
        },
        {
            "symbol": "ADAUSDT",
            "side": "buy",
            "entry": 0.50,
            "sl": 0.48,
            "tp": 0.55,
            "description": "ADA Long"
        }
    ]
    
    for trade in trades:
        # Register for both managers
        await breakeven_manager.register_trade(
            symbol=trade["symbol"],
            side=trade["side"],
            entry_price=trade["entry"],
            sl_price=trade["sl"],
            tp_prices=[trade["tp"]],
            order_ids=[f"mock_{trade['symbol']}_1", f"mock_{trade['symbol']}_2"]
        )
        
        await trailing_manager.register_trade(
            symbol=trade["symbol"],
            side=trade["side"],
            entry_price=trade["entry"],
            sl_price=trade["sl"],
            tp_prices=[trade["tp"]],
            order_ids=[f"mock_{trade['symbol']}_1", f"mock_{trade['symbol']}_2"]
        )
        
        print(f"✅ {trade['description']} registered")
    
    # Check all trades
    print(f"\n📊 Monitoring {len(trades)} trades:")
    for trade in trades:
        symbol = trade["symbol"]
        breakeven_status = breakeven_manager.get_trade_status(symbol)
        trailing_status = trailing_manager.get_trade_status(symbol)
        
        print(f"   {symbol}: Break-even {'✅' if breakeven_status['breakeven_triggered'] else '⏳'} | "
              f"Trailing {'✅' if trailing_status['trailing_active'] else '⏳'}")

async def demo_configuration():
    """Show the current configuration settings."""
    
    print("\n⚙️ CONFIGURATION DEMO")
    print("=" * 40)
    
    from config.settings import TradingConfig
    
    configs = {
        "Break-even threshold": f"{TradingConfig.BREAKEVEN_THRESHOLD}%",
        "Break-even buffer": f"{TradingConfig.BREAKEVEN_BUFFER * 100}%",
        "Trailing threshold": f"{TradingConfig.TRAILING_THRESHOLD}%",
        "Trailing distance": f"{TradingConfig.TRAILING_DISTANCE * 100}%",
        "Trailing step": f"{TradingConfig.TRAILING_STEP * 100}%"
    }
    
    print("📋 Current SL Management Configuration:")
    for name, value in configs.items():
        print(f"   {name}: {value}")
    
    print("\n💡 Configuration Notes:")
    print("   • Break-even triggers at 2% profit or when TP2 is hit")
    print("   • Trailing activates at 3% profit or when TP2 is hit")
    print("   • Trailing follows price with 1% distance")
    print("   • SL updates only when price moves 0.5% or more")

if __name__ == "__main__":
    print("🚀 Starting SL Management Workflow Demo...")
    asyncio.run(demo_sl_management_workflow())
    asyncio.run(demo_multiple_trades())
    asyncio.run(demo_configuration())
    print(f"\n⚡ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 