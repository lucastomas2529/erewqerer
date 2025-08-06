#!/usr/bin/env python3
"""
Timeout protection system for automatically closing trades after 4 hours.
Tracks trade duration and closes positions if no exit has occurred.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from core.api import get_current_price_async, place_market_order, cancel_order
from core.exchange_api import OrderResult
from config.settings import TradingConfig
from utils.logger import log_event

class TimeoutManager:
    """Manages timeout protection for active trades."""
    
    def __init__(self):
        self.active_trades = {}  # symbol -> trade_info
        self.timeout_hours = TradingConfig.TIMEOUT_HOURS  # From config
        self.check_interval = TradingConfig.TIMEOUT_CHECK_INTERVAL  # From config
        
    async def register_trade(self, symbol: str, side: str, entry_price: float, 
                           sl_price: float, tp_prices: list, order_ids: list, 
                           quantity: float = None) -> None:
        """Register a new trade for timeout monitoring."""
        trade_info = {
            "symbol": symbol,
            "side": side.lower(),
            "entry_price": entry_price,
            "sl_price": sl_price,
            "tp_prices": tp_prices,
            "order_ids": order_ids,
            "quantity": quantity,
            "entry_timestamp": time.time(),
            "entry_datetime": datetime.now(),
            "timeout_triggered": False,
            "status": "active"
        }
        self.active_trades[symbol] = trade_info
        log_event(f"⏰ Timeout monitoring started for {symbol} (4 hours)", "INFO")
        print(f"⏰ Timeout monitoring started for {symbol}")
        print(f"   Entry time: {trade_info['entry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Timeout: {self.timeout_hours} hours")
    
    def get_trade_duration(self, symbol: str) -> Optional[float]:
        """Get the duration of a trade in hours."""
        if symbol not in self.active_trades:
            return None
        
        trade = self.active_trades[symbol]
        if trade["status"] != "active":
            return None
        
        duration_seconds = time.time() - trade["entry_timestamp"]
        duration_hours = duration_seconds / 3600
        return duration_hours
    
    async def check_timeout_conditions(self, symbol: str) -> bool:
        """Check if timeout conditions are met."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["timeout_triggered"] or trade["status"] != "active":
            return False
        
        duration_hours = self.get_trade_duration(symbol)
        if duration_hours is None:
            return False
        
        # Check if trade has exceeded timeout
        if duration_hours >= self.timeout_hours:
            log_event(f"⏰ Timeout triggered for {symbol} after {duration_hours:.2f} hours", "WARNING")
            print(f"⏰ Timeout triggered for {symbol}:")
            print(f"   Duration: {duration_hours:.2f} hours")
            print(f"   Timeout limit: {self.timeout_hours} hours")
            print(f"   Entry time: {trade['entry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        
        return False
    
    async def close_trade_timeout(self, symbol: str) -> bool:
        """Close a trade due to timeout."""
        if symbol not in self.active_trades:
            return False
        
        trade = self.active_trades[symbol]
        if trade["timeout_triggered"]:
            return False
        
        try:
            side = trade["side"]
            quantity = trade.get("quantity", 0.001)  # Default quantity
            
            # Determine exit side (opposite of entry)
            exit_side = "sell" if side == "buy" else "buy"
            
            # Cancel any existing orders
            for order_id in trade["order_ids"]:
                try:
                    await cancel_order(symbol, order_id)
                    print(f"   ✅ Cancelled order: {order_id}")
                except Exception as e:
                    print(f"   ⚠️ Failed to cancel order {order_id}: {e}")
            
            # Place market order to close position
            current_price = await get_current_price_async(symbol)
            exit_order = place_market_order(symbol, quantity, exit_side)
            
            if exit_order and exit_order.get("order_id"):
                trade["timeout_triggered"] = True
                trade["status"] = "closed"
                trade["exit_price"] = current_price
                trade["exit_timestamp"] = time.time()
                trade["exit_datetime"] = datetime.now()
                trade["exit_order_id"] = exit_order["order_id"]
                
                # Calculate PnL
                entry_price = trade["entry_price"]
                if side == "buy":
                    pnl_pct = (current_price - entry_price) / entry_price * 100
                else:  # sell
                    pnl_pct = (entry_price - current_price) / entry_price * 100
                
                log_event(f"⏰ Trade {symbol} closed due to timeout", "WARNING")
                print(f"✅ Trade closed due to timeout:")
                print(f"   Symbol: {symbol}")
                print(f"   Entry: ${entry_price:,.2f}")
                print(f"   Exit: ${current_price:,.2f}")
                print(f"   PnL: {pnl_pct:.2f}%")
                print(f"   Duration: {self.get_trade_duration(symbol):.2f} hours")
                print(f"   Order ID: {exit_order['order_id']}")
                
                return True
            else:
                print(f"❌ Failed to close trade {symbol} due to timeout")
                return False
                
        except Exception as e:
            log_event(f"❌ Error closing trade {symbol} due to timeout: {e}", "ERROR")
            print(f"❌ Error closing trade {symbol} due to timeout: {e}")
            return False
    
    async def monitor_timeout(self) -> None:
        """Main monitoring loop for timeout conditions."""
        while True:
            try:
                for symbol in list(self.active_trades.keys()):
                    trade = self.active_trades[symbol]
                    if trade["status"] != "active":
                        continue
                    
                    # Check if timeout conditions are met
                    if await self.check_timeout_conditions(symbol):
                        await self.close_trade_timeout(symbol)
                
                await asyncio.sleep(self.check_interval)  # Check every 60 seconds
                
            except Exception as e:
                log_event(f"❌ Error in timeout monitoring: {e}", "ERROR")
                print(f"❌ Error in timeout monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_trade_status(self, symbol: str) -> Optional[Dict]:
        """Get current status of a trade."""
        if symbol not in self.active_trades:
            return None
        
        trade = self.active_trades[symbol]
        duration_hours = self.get_trade_duration(symbol)
        
        status = {
            "symbol": symbol,
            "side": trade["side"],
            "entry_price": trade["entry_price"],
            "entry_datetime": trade["entry_datetime"],
            "duration_hours": duration_hours,
            "timeout_hours": self.timeout_hours,
            "timeout_triggered": trade["timeout_triggered"],
            "status": trade["status"]
        }
        
        if trade["timeout_triggered"]:
            status.update({
                "exit_price": trade.get("exit_price"),
                "exit_datetime": trade.get("exit_datetime"),
                "exit_order_id": trade.get("exit_order_id")
            })
        
        return status
    
    def close_trade(self, symbol: str) -> None:
        """Close a trade and remove from monitoring."""
        if symbol in self.active_trades:
            self.active_trades[symbol]["status"] = "closed"
            print(f"⏰ Timeout monitoring stopped for {symbol}")
    
    def get_all_trades_status(self) -> Dict:
        """Get status of all active trades."""
        active_trades = {}
        for symbol, trade in self.active_trades.items():
            if trade["status"] == "active":
                duration_hours = self.get_trade_duration(symbol)
                active_trades[symbol] = {
                    "duration_hours": duration_hours,
                    "timeout_hours": self.timeout_hours,
                    "remaining_hours": max(0, self.timeout_hours - duration_hours) if duration_hours else None
                }
        
        return {
            "total_trades": len(self.active_trades),
            "active_trades": len(active_trades),
            "timeout_hours": self.timeout_hours,
            "trades": active_trades
        }

# Global instance
timeout_manager = TimeoutManager()

# Test function
async def test_timeout_logic():
    """Test the timeout logic with mock data."""
    print("🧪 TESTING TIMEOUT LOGIC")
    print("=" * 40)
    
    # Mock trade registration
    await timeout_manager.register_trade(
        symbol="BTCUSDT",
        side="buy",
        entry_price=67000.0,
        sl_price=65000.0,
        tp_prices=[68000.0, 69000.0, 70000.0],
        order_ids=["mock_order_1", "mock_order_2"],
        quantity=0.001
    )
    
    # Simulate trade status
    print("📊 Trade registered:")
    print(f"   Symbol: BTCUSDT")
    print(f"   Entry: $67,000")
    print(f"   Timeout: {timeout_manager.timeout_hours} hours")
    
    # Test timeout conditions
    result = await timeout_manager.check_timeout_conditions("BTCUSDT")
    print(f"   Timeout conditions met: {result}")
    
    # Show trade status
    status = timeout_manager.get_trade_status("BTCUSDT")
    print(f"   Duration: {status['duration_hours']:.2f} hours")
    print(f"   Remaining: {timeout_manager.timeout_hours - status['duration_hours']:.2f} hours")
    
    print("✅ Timeout test completed!")

if __name__ == "__main__":
    asyncio.run(test_timeout_logic()) 