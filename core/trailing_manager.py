#!/usr/bin/env python3
"""
Trailing stop manager for dynamic stop-loss adjustment.
Implements "riding to heaven" trailing stops that follow price movement.
"""

import asyncio
from typing import Dict, Optional, Tuple
from core.api import get_current_price_async, place_stop_loss_order, cancel_order
from core.exchange_api import OrderResult
from config.settings import TradingConfig

class TrailingManager:
    """Manages trailing stop logic for active trades."""
    
    def __init__(self):
        self.active_trades = {}  # symbol -> trade_info
        self.trailing_threshold = TradingConfig.TRAILING_THRESHOLD  # Default 3% profit
        self.trailing_distance = TradingConfig.TRAILING_DISTANCE  # Default 1% trailing distance
        self.trailing_step = TradingConfig.TRAILING_STEP  # Default 0.5% step size
    
    async def register_trade(self, symbol: str, side: str, entry_price: float, 
                           sl_price: float, tp_prices: list, order_ids: list) -> None:
        """Register a new trade for trailing stop monitoring."""
        trade_info = {
            "symbol": symbol,
            "side": side.lower(),
            "entry_price": entry_price,
            "original_sl": sl_price,
            "current_sl": sl_price,
            "tp_prices": tp_prices,
            "order_ids": order_ids,
            "trailing_active": False,
            "trailing_order_id": None,
            "highest_price": entry_price if side == "buy" else entry_price,
            "lowest_price": entry_price if side == "sell" else entry_price,
            "status": "active"
        }
        self.active_trades[symbol] = trade_info
        print(f"📊 Trailing stop monitoring started for {symbol}")
    
    async def check_trailing_conditions(self, symbol: str) -> bool:
        """Check if trailing stop should be activated."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["trailing_active"]:
            return True  # Already trailing
        
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
            
            # Activate trailing if TP2 hit OR profit threshold reached
            if tp2_hit or profit_pct >= self.trailing_threshold:
                print(f"🎯 Trailing conditions met for {symbol}:")
                print(f"   Current Price: ${current_price:,.2f}")
                print(f"   Entry Price: ${entry_price:,.2f}")
                print(f"   Profit: {profit_pct:.2f}%")
                print(f"   TP2 Hit: {tp2_hit}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking trailing for {symbol}: {e}")
            return False
    
    async def update_trailing_stop(self, symbol: str) -> bool:
        """Update trailing stop based on current price movement."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if not trade["trailing_active"]:
            return False
        
        try:
            current_price = await get_current_price_async(symbol)
            side = trade["side"]
            
            # Update highest/lowest prices
            if side == "buy":
                if current_price > trade["highest_price"]:
                    trade["highest_price"] = current_price
                # Calculate new trailing stop
                new_sl = current_price * (1 - self.trailing_distance)
            else:  # sell
                if current_price < trade["lowest_price"]:
                    trade["lowest_price"] = current_price
                # Calculate new trailing stop
                new_sl = current_price * (1 + self.trailing_distance)
            
            # Check if we need to move the stop-loss
            current_sl = trade["current_sl"]
            should_move = False
            
            if side == "buy":
                # For buy trades, only move SL up
                should_move = new_sl > current_sl + (current_sl * self.trailing_step)
            else:
                # For sell trades, only move SL down
                should_move = new_sl < current_sl - (current_sl * self.trailing_step)
            
            if should_move:
                # Cancel existing trailing order
                if trade["trailing_order_id"]:
                    try:
                        await cancel_order(symbol, trade["trailing_order_id"])
                    except:
                        pass  # Order might already be filled
                
                # Place new trailing stop order
                sl_order = await place_stop_loss_order(
                    symbol=symbol,
                    side="sell" if side == "buy" else "buy",
                    quantity=trade.get("quantity", 0.001),  # Default quantity
                    stop_price=new_sl
                )
                
                if sl_order and sl_order.get("order_id"):
                    trade["current_sl"] = new_sl
                    trade["trailing_order_id"] = sl_order["order_id"]
                    
                    print(f"📈 Trailing stop updated for {symbol}:")
                    print(f"   New SL: ${new_sl:,.2f}")
                    print(f"   Current Price: ${current_price:,.2f}")
                    print(f"   Order ID: {sl_order['order_id']}")
                    return True
                else:
                    print(f"❌ Failed to update trailing stop for {symbol}")
                    return False
            
            return True  # No update needed
                
        except Exception as e:
            print(f"❌ Error updating trailing stop for {symbol}: {e}")
            return False
    
    async def activate_trailing(self, symbol: str) -> bool:
        """Activate trailing stop for a trade."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["trailing_active"]:
            return True  # Already active
        
        try:
            current_price = await get_current_price_async(symbol)
            side = trade["side"]
            
            # Calculate initial trailing stop
            if side == "buy":
                initial_sl = current_price * (1 - self.trailing_distance)
            else:  # sell
                initial_sl = current_price * (1 + self.trailing_distance)
            
            # Place initial trailing stop order
            sl_order = await place_stop_loss_order(
                symbol=symbol,
                side="sell" if side == "buy" else "buy",
                quantity=trade.get("quantity", 0.001),  # Default quantity
                stop_price=initial_sl
            )
            
            if sl_order and sl_order.get("order_id"):
                trade["trailing_active"] = True
                trade["current_sl"] = initial_sl
                trade["trailing_order_id"] = sl_order["order_id"]
                
                print(f"🚀 Trailing stop activated for {symbol}:")
                print(f"   Initial SL: ${initial_sl:,.2f}")
                print(f"   Current Price: ${current_price:,.2f}")
                print(f"   Order ID: {sl_order['order_id']}")
                return True
            else:
                print(f"❌ Failed to activate trailing stop for {symbol}")
                return False
                
        except Exception as e:
            print(f"❌ Error activating trailing for {symbol}: {e}")
            return False
    
    async def monitor_trailing(self) -> None:
        """Main monitoring loop for trailing stops."""
        while True:
            try:
                for symbol in list(self.active_trades.keys()):
                    trade = self.active_trades[symbol]
                    if trade["status"] != "active":
                        continue
                    
                    # Check if trailing should be activated
                    if not trade["trailing_active"]:
                        if await self.check_trailing_conditions(symbol):
                            await self.activate_trailing(symbol)
                    else:
                        # Update existing trailing stop
                        await self.update_trailing_stop(symbol)
                
                await asyncio.sleep(3)  # Check every 3 seconds for trailing
                
            except Exception as e:
                print(f"❌ Error in trailing monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_trade_status(self, symbol: str) -> Optional[Dict]:
        """Get current status of a trade."""
        return self.active_trades.get(symbol)
    
    def close_trade(self, symbol: str) -> None:
        """Close a trade and remove from monitoring."""
        if symbol in self.active_trades:
            self.active_trades[symbol]["status"] = "closed"
            print(f"📊 Trailing stop monitoring stopped for {symbol}")

# Global instance
trailing_manager = TrailingManager()

# Test function
async def test_trailing_logic():
    """Test the trailing stop logic with mock data."""
    print("🧪 TESTING TRAILING STOP LOGIC")
    print("=" * 40)
    
    # Mock trade registration
    await trailing_manager.register_trade(
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
    print(f"   Trailing threshold: {trailing_manager.trailing_threshold}%")
    print(f"   Trailing distance: {trailing_manager.trailing_distance}%")
    
    # Test trailing conditions
    result = await trailing_manager.check_trailing_conditions("BTCUSDT")
    print(f"   Trailing conditions met: {result}")
    
    print("✅ Trailing stop test completed!")

if __name__ == "__main__":
    asyncio.run(test_trailing_logic()) 