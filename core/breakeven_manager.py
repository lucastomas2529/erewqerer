#!/usr/bin/env python3
"""
Break-even manager for moving stop-loss to break-even after TP2 or profit threshold.
"""

import asyncio
from typing import Dict, Optional, Tuple
from core.api import get_current_price_async, place_stop_loss_order, cancel_order
from core.exchange_api import OrderResult
from config.settings import TradingConfig

class BreakEvenManager:
    """Manages break-even logic for active trades."""
    
    def __init__(self):
        self.active_trades = {}  # symbol -> trade_info
        self.breakeven_threshold = TradingConfig.BREAKEVEN_THRESHOLD  # Default 2% profit
        self.breakeven_buffer = TradingConfig.BREAKEVEN_BUFFER  # Default 0.1% buffer
    
    async def register_trade(self, symbol: str, side: str, entry_price: float, 
                           sl_price: float, tp_prices: list, order_ids: list) -> None:
        """Register a new trade for break-even monitoring."""
        trade_info = {
            "symbol": symbol,
            "side": side.lower(),
            "entry_price": entry_price,
            "original_sl": sl_price,
            "current_sl": sl_price,
            "tp_prices": tp_prices,
            "order_ids": order_ids,
            "breakeven_triggered": False,
            "breakeven_order_id": None,
            "status": "active"
        }
        self.active_trades[symbol] = trade_info
        print(f"📊 Break-even monitoring started for {symbol}")
    
    async def check_breakeven_conditions(self, symbol: str) -> bool:
        """Check if break-even conditions are met."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["breakeven_triggered"]:
            return False
        
        try:
            current_price = await get_current_price_async(symbol)
            entry_price = trade["entry_price"]
            side = trade["side"]
            
            # Calculate current profit percentage
            if side == "buy":
                profit_pct = (current_price - entry_price) / entry_price * 100
            else:  # sell
                profit_pct = (entry_price - current_price) / entry_price * 100
            
            # Check if TP2 is hit (if we have TP2)
            tp2_hit = False
            if len(trade["tp_prices"]) >= 2:
                tp2 = trade["tp_prices"][1]  # Second TP
                if side == "buy" and current_price >= tp2:
                    tp2_hit = True
                elif side == "sell" and current_price <= tp2:
                    tp2_hit = True
            
            # Break-even if TP2 hit OR profit threshold reached
            if tp2_hit or profit_pct >= self.breakeven_threshold:
                print(f"🎯 Break-even conditions met for {symbol}:")
                print(f"   Current Price: ${current_price:,.2f}")
                print(f"   Entry Price: ${entry_price:,.2f}")
                print(f"   Profit: {profit_pct:.2f}%")
                print(f"   TP2 Hit: {tp2_hit}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking break-even for {symbol}: {e}")
            return False
    
    async def move_to_breakeven(self, symbol: str) -> bool:
        """Move stop-loss to break-even level."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["breakeven_triggered"]:
            return False
        
        try:
            entry_price = trade["entry_price"]
            side = trade["side"]
            
            # Calculate break-even price with buffer
            if side == "buy":
                breakeven_price = entry_price * (1 + self.breakeven_buffer)
            else:  # sell
                breakeven_price = entry_price * (1 - self.breakeven_buffer)
            
            # Cancel original SL order if it exists
            if trade["current_sl"] != trade["original_sl"]:
                # This means we already have a break-even order
                try:
                    await cancel_order(symbol, trade["breakeven_order_id"])
                except:
                    pass  # Order might already be filled
            
            # Place new SL order at break-even
            sl_order = await place_stop_loss_order(
                symbol=symbol,
                side="sell" if side == "buy" else "buy",
                quantity=trade.get("quantity", 0.001),  # Default quantity
                stop_price=breakeven_price
            )
            
            if sl_order and sl_order.get("order_id"):
                trade["current_sl"] = breakeven_price
                trade["breakeven_triggered"] = True
                trade["breakeven_order_id"] = sl_order["order_id"]
                
                print(f"✅ Break-even SL placed for {symbol}:")
                print(f"   New SL: ${breakeven_price:,.2f}")
                print(f"   Order ID: {sl_order['order_id']}")
                return True
            else:
                print(f"❌ Failed to place break-even SL for {symbol}")
                return False
                
        except Exception as e:
            print(f"❌ Error moving to break-even for {symbol}: {e}")
            return False
    
    async def monitor_breakeven(self) -> None:
        """Main monitoring loop for break-even conditions."""
        while True:
            try:
                for symbol in list(self.active_trades.keys()):
                    trade = self.active_trades[symbol]
                    if trade["status"] != "active":
                        continue
                    
                    # Check if break-even conditions are met
                    if await self.check_breakeven_conditions(symbol):
                        await self.move_to_breakeven(symbol)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"❌ Error in break-even monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_trade_status(self, symbol: str) -> Optional[Dict]:
        """Get current status of a trade."""
        return self.active_trades.get(symbol)
    
    def close_trade(self, symbol: str) -> None:
        """Close a trade and remove from monitoring."""
        if symbol in self.active_trades:
            self.active_trades[symbol]["status"] = "closed"
            print(f"📊 Break-even monitoring stopped for {symbol}")

# Global instance
breakeven_manager = BreakEvenManager()

# Test function
async def test_breakeven_logic():
    """Test the break-even logic with mock data."""
    print("🧪 TESTING BREAK-EVEN LOGIC")
    print("=" * 40)
    
    # Mock trade registration
    await breakeven_manager.register_trade(
        symbol="BTCUSDT",
        side="buy",
        entry_price=67000.0,
        sl_price=65000.0,
        tp_prices=[68000.0, 69000.0, 70000.0],
        order_ids=["mock_order_1", "mock_order_2"]
    )
    
    # Simulate price movement
    print("📊 Trade registered:")
    print(f"   Symbol: BTCUSDT")
    print(f"   Entry: $67,000")
    print(f"   TP2: $69,000")
    print(f"   Break-even threshold: {breakeven_manager.breakeven_threshold}%")
    
    # Test break-even conditions
    result = await breakeven_manager.check_breakeven_conditions("BTCUSDT")
    print(f"   Break-even conditions met: {result}")
    
    print("✅ Break-even test completed!")

if __name__ == "__main__":
    asyncio.run(test_breakeven_logic()) 