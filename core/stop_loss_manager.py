import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core.api import get_current_price_async, place_market_order
from core.exchange_api import bitget_api, bybit_api

class StopLossManager:
    """
    Advanced stop-loss management with break-even, trailing stops, and dynamic adjustment.
    """
    
    def __init__(self):
        self.active_positions = {}  # Track active positions and their SL states
        self.config = {
            "break_even_trigger": 0.02,  # 2% profit to move SL to break-even
            "trailing_start": 0.05,      # 5% profit to start trailing
            "trailing_distance": 0.01,   # 1% trailing distance
            "tp2_break_even": True,      # Move to break-even after TP2
            "max_trailing_distance": 0.05  # Maximum trailing distance (5%)
        }
    
    async def calculate_break_even_sl(self, entry_price: float, side: str) -> float:
        """Calculate break-even stop-loss level."""
        if side.lower() == "buy":
            return entry_price * 1.001  # Slight buffer above entry for buy
        else:
            return entry_price * 0.999  # Slight buffer below entry for sell
    
    async def calculate_trailing_sl(self, current_price: float, side: str, 
                                   trailing_distance: float) -> float:
        """Calculate trailing stop-loss level."""
        if side.lower() == "buy":
            return current_price * (1 - trailing_distance)
        else:
            return current_price * (1 + trailing_distance)
    
    async def should_move_to_break_even(self, position: Dict) -> bool:
        """Check if SL should move to break-even."""
        current_price = await get_current_price_async(position['symbol'])
        entry_price = position['entry_price']
        side = position['side']
        
        if side.lower() == "buy":
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        return profit_pct >= self.config["break_even_trigger"]
    
    async def should_start_trailing(self, position: Dict) -> bool:
        """Check if trailing stop should start."""
        current_price = await get_current_price_async(position['symbol'])
        entry_price = position['entry_price']
        side = position['side']
        
        if side.lower() == "buy":
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        return profit_pct >= self.config["trailing_start"]
    
    async def update_stop_loss(self, position_id: str, new_sl: float, 
                              reason: str = "manual") -> Dict:
        """Update stop-loss for a position."""
        try:
            # In real implementation, this would call the exchange API
            # For now, we'll simulate the update
            position = self.active_positions.get(position_id, {})
            old_sl = position.get('current_sl', 0)
            
            # Simulate API call to update SL
            print(f"📤 UPDATING SL: {position.get('symbol', 'UNKNOWN')}")
            print(f"   Old SL: ${old_sl:,.2f}")
            print(f"   New SL: ${new_sl:,.2f}")
            print(f"   Reason: {reason}")
            
            # Update position data
            position['current_sl'] = new_sl
            position['sl_history'].append({
                'timestamp': datetime.now(),
                'old_sl': old_sl,
                'new_sl': new_sl,
                'reason': reason
            })
            
            self.active_positions[position_id] = position
            
            return {
                'success': True,
                'position_id': position_id,
                'old_sl': old_sl,
                'new_sl': new_sl,
                'reason': reason
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'position_id': position_id
            }
    
    async def check_and_update_sl(self, position_id: str) -> Dict:
        """Check current position and update SL if needed."""
        position = self.active_positions.get(position_id)
        if not position:
            return {'success': False, 'error': 'Position not found'}
        
        current_price = await get_current_price_async(position['symbol'])
        entry_price = position['entry_price']
        current_sl = position.get('current_sl', position['initial_sl'])
        side = position['side']
        
        # Calculate current profit
        if side.lower() == "buy":
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        updates = []
        
        # Check for break-even trigger
        if profit_pct >= self.config["break_even_trigger"] and not position.get('break_even_hit'):
            break_even_sl = await self.calculate_break_even_sl(entry_price, side)
            if (side.lower() == "buy" and break_even_sl > current_sl) or \
               (side.lower() == "sell" and break_even_sl < current_sl):
                
                result = await self.update_stop_loss(position_id, break_even_sl, "break_even")
                if result['success']:
                    position['break_even_hit'] = True
                    updates.append(result)
        
        # Check for trailing start
        if profit_pct >= self.config["trailing_start"] and not position.get('trailing_active'):
            position['trailing_active'] = True
            position['trailing_start_price'] = current_price
        
        # Update trailing stop if active
        if position.get('trailing_active'):
            trailing_sl = await self.calculate_trailing_sl(
                current_price, side, self.config["trailing_distance"]
            )
            
            # Check if we should update trailing SL
            should_update = False
            if side.lower() == "buy":
                should_update = trailing_sl > current_sl
            else:
                should_update = trailing_sl < current_sl
            
            if should_update:
                result = await self.update_stop_loss(position_id, trailing_sl, "trailing")
                if result['success']:
                    updates.append(result)
        
        return {
            'success': True,
            'updates': updates,
            'current_price': current_price,
            'profit_pct': profit_pct,
            'break_even_hit': position.get('break_even_hit', False),
            'trailing_active': position.get('trailing_active', False)
        }
    
    async def add_position(self, position_id: str, symbol: str, side: str, 
                          entry_price: float, initial_sl: float, 
                          tp1: float = None, tp2: float = None) -> Dict:
        """Add a new position to track."""
        position = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'initial_sl': initial_sl,
            'current_sl': initial_sl,
            'tp1': tp1,
            'tp2': tp2,
            'break_even_hit': False,
            'trailing_active': False,
            'trailing_start_price': None,
            'sl_history': [],
            'created_at': datetime.now()
        }
        
        self.active_positions[position_id] = position
        
        return {
            'success': True,
            'position_id': position_id,
            'position': position
        }
    
    async def remove_position(self, position_id: str) -> Dict:
        """Remove a position from tracking."""
        if position_id in self.active_positions:
            del self.active_positions[position_id]
            return {'success': True, 'position_id': position_id}
        return {'success': False, 'error': 'Position not found'}

# Global instance
sl_manager = StopLossManager()

# Demo/test functions
async def test_stop_loss_manager():
    """Test the stop-loss manager with various scenarios."""
    
    print("🧪 STOP-LOSS MANAGER TEST")
    print("=" * 50)
    
    # Test 1: Add position and check break-even
    print("\n📊 TEST 1: Break-Even Logic")
    print("-" * 30)
    
    # Simulate a BTC long position
    position_id = "test_btc_long_001"
    result = await sl_manager.add_position(
        position_id=position_id,
        symbol="BTCUSDT",
        side="buy",
        entry_price=67000.0,
        initial_sl=65000.0,
        tp1=68000.0,
        tp2=69000.0
    )
    
    print(f"✅ Position added: {result['success']}")
    print(f"   Entry: ${67000:,.2f}")
    print(f"   Initial SL: ${65000:,.2f}")
    print(f"   TP1: ${68000:,.2f}")
    print(f"   TP2: ${69000:,.2f}")
    
    # Simulate price movement and check SL updates
    test_prices = [67000, 67500, 68000, 68500, 69000, 69500, 70000]
    
    for price in test_prices:
        # Temporarily override current price for testing
        original_get_price = get_current_price_async
        get_current_price_async = lambda symbol: asyncio.Future()
        get_current_price_async.set_result(price)
        
        result = await sl_manager.check_and_update_sl(position_id)
        
        print(f"💰 Price: ${price:,.2f} | Profit: {result['profit_pct']:.2%}")
        print(f"   Break-even hit: {result['break_even_hit']}")
        print(f"   Trailing active: {result['trailing_active']}")
        
        if result['updates']:
            for update in result['updates']:
                print(f"   📤 SL Updated: ${update['old_sl']:,.2f} → ${update['new_sl']:,.2f}")
        
        # Restore original function
        get_current_price_async = original_get_price
    
    # Test 2: Trailing stop logic
    print("\n📊 TEST 2: Trailing Stop Logic")
    print("-" * 30)
    
    position_id2 = "test_eth_short_001"
    result = await sl_manager.add_position(
        position_id=position_id2,
        symbol="ETHUSDT",
        side="sell",
        entry_price=3800.0,
        initial_sl=3900.0,
        tp1=3700.0,
        tp2=3600.0
    )
    
    print(f"✅ Short position added: {result['success']}")
    print(f"   Entry: ${3800:,.2f}")
    print(f"   Initial SL: ${3900:,.2f}")
    
    # Simulate price movement for short position
    test_prices_short = [3800, 3750, 3700, 3650, 3600, 3550, 3500]
    
    for price in test_prices_short:
        # Temporarily override current price for testing
        original_get_price = get_current_price_async
        get_current_price_async = lambda symbol: asyncio.Future()
        get_current_price_async.set_result(price)
        
        result = await sl_manager.check_and_update_sl(position_id2)
        
        print(f"💰 Price: ${price:,.2f} | Profit: {result['profit_pct']:.2%}")
        print(f"   Break-even hit: {result['break_even_hit']}")
        print(f"   Trailing active: {result['trailing_active']}")
        
        if result['updates']:
            for update in result['updates']:
                print(f"   📤 SL Updated: ${update['old_sl']:,.2f} → ${update['new_sl']:,.2f}")
        
        # Restore original function
        get_current_price_async = original_get_price
    
    print("\n✅ Stop-loss manager test completed!")

if __name__ == "__main__":
    asyncio.run(test_stop_loss_manager()) 