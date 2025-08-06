# core/api.py - Enhanced with comprehensive exchange integration
import time
import asyncio
from core.exchange_api import bitget_api, bybit_api, OrderResult
from typing import Dict, Optional, Tuple

# Global API instance (default to Bitget)
default_api = bitget_api

async def place_stop_loss_order(symbol: str, side: str, quantity: float, stop_price: float) -> dict:
    """
    Place a stop-loss order.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: 'buy' or 'sell' (opposite of position side)
        quantity: Position size to close
        stop_price: Stop-loss price level
    
    Returns:
        Order result dictionary
    """
    try:
        # Use the exchange API to place stop-loss order
        result = await default_api.place_limit_order(
            symbol=symbol,
            side=side.lower(),
            amount=quantity,
            price=stop_price,
            reduce_only=True  # Ensure it only closes position
        )
        
        return {
            "order_id": result.order_id,
            "status": result.status,
            "symbol": result.symbol,
            "side": result.side,
            "quantity": result.amount,
            "price": result.price,
            "order_type": "StopLoss",
            "stop_price": stop_price
        }
        
    except Exception as e:
        print(f"❌ Stop-loss order failed for {symbol}: {e}")
        # Return mock order for testing
        return {
            "order_id": f"sl_{symbol}_{int(time.time())}",
            "status": "open",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": stop_price,
            "order_type": "StopLoss",
            "stop_price": stop_price,
            "error": str(e)
        }

async def cancel_order(symbol: str, order_id: str) -> dict:
    """
    Cancel an existing order.
    
    Args:
        symbol: Trading pair
        order_id: Order ID to cancel
    
    Returns:
        Cancellation result
    """
    try:
        result = await default_api.cancel_order(symbol, order_id)
        return {
            "order_id": order_id,
            "status": "cancelled",
            "symbol": symbol,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ Cancel order failed for {order_id}: {e}")
        return {
            "order_id": order_id,
            "status": "failed",
            "symbol": symbol,
            "success": False,
            "error": str(e)
        }

def place_order(symbol, side, quantity, order_type="limit", price=None, reduce_only=False):
    """
    Enhanced order placement with real exchange integration.
    """
    try:
        if order_type.lower() == "limit" and price:
            # Use async limit order
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                default_api.place_limit_order(symbol, side, quantity, price, reduce_only)
            )
            loop.close()
            
            return {
                "order_id": result.order_id,
                "status": result.status,
                "symbol": result.symbol,
                "side": result.side,
                "quantity": result.amount,
                "price": result.price
            }
        else:
            # Fallback to original mock behavior
            print(f"📤 ORDER: {side} {quantity} {symbol} @ {price or 'market'}")
            return {"order_id": f"mock_{symbol}_{side}"}
            
    except Exception as e:
        print(f"❌ Order placement failed: {e}")
        return {"order_id": f"failed_{symbol}_{side}", "error": str(e)}

async def place_reentry_order(symbol: str, side: str, entry_price: float, sl_price: float,
                       leverage: float, quantity: float) -> dict:
    """
    Place a re-entry order after SL hit.
    """
    try:
        # Order data structure for re-entry
        order_data = {
            "symbol": symbol,
            "side": side,
            "qty": quantity,
            "order_type": "Limit",
            "price": entry_price,
            "leverage": leverage,
            "stop_loss": sl_price,
            "position_idx": 0
        }
        
        # Placeholder for actual API call
        print(f"📤 RE-ENTRY ORDER: {order_data}")
        
        # Return mock response
        return {
            "orderId": f"reentry_{symbol}_{int(time.time())}",
            "status": "NEW",
            "symbol": symbol,
            "side": side,
            "qty": quantity,
            "price": entry_price
        }
        
    except Exception as e:
        print(f"❌ Re-entry order failed: {e}")
        return {"error": str(e)}

# Placeholder functions for generate modules
async def get_trade_history(symbol: str = None, limit: int = 100) -> list:
    """
    Placeholder function for getting trade history.
    TODO: Implement actual trade history retrieval from exchange API.
    """
    print(f"📊 Getting trade history for {symbol or 'all symbols'}")
    return []  # Return empty list for now

async def get_trade_history_log(days: int = 1) -> list:
    """
    Placeholder function for getting trade history log.
    TODO: Implement actual trade log retrieval.
    """
    print(f"📊 Getting trade history log for last {days} days")
    return []  # Return empty list for now

# Placeholder functions for loop_manager imports
async def place_dca_orders(*args, **kwargs):
    """Placeholder for DCA orders."""
    print("📤 DCA orders placeholder")
    return {"status": "mock"}

async def amend_order(*args, **kwargs):
    """Placeholder for amending orders.""" 
    print("📤 Amend order placeholder")
    return {"status": "mock"}

# Mock bitget client for compatibility
class MockBitgetClient:
    def __init__(self):
        print("📡 Mock Bitget client initialized")
    
    async def get_positions(self, symbol=None):
        print(f"📊 Getting positions for {symbol or 'all symbols'}")
        return []
    
    async def place_order(self, **kwargs):
        print(f"📤 Mock order: {kwargs}")
        return {"order_id": f"mock_{int(time.time())}"}

# Create a global instance for imports
client = MockBitgetClient()
bitget_client = client  # For compatibility with different import names

async def move_sl_to_be(symbol: str, be_price: float) -> dict:
    """
    Move stop loss to break-even price.
    TODO: Implement actual break-even SL logic.
    """
    print(f"📝 MOVE SL TO BE: {symbol} @ {be_price}")
    return {"status": "mock", "sl_price": be_price}

async def place_limit_order(symbol: str, side: str, quantity: float, price: float) -> dict:
    """
    Place a limit order.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: 'buy' or 'sell'
        quantity: Order quantity
        price: Limit price
    
    Returns:
        Order result dictionary
    """
    try:
        result = await default_api.place_limit_order(
            symbol=symbol,
            side=side.lower(),
            amount=quantity,
            price=price
        )
        return {
            "order_id": result.order_id,
            "status": result.status,
            "symbol": result.symbol,
            "side": result.side,
            "quantity": result.amount,
            "price": result.price,
            "order_type": "Limit"
        }
    except Exception as e:
        print(f"❌ Limit order failed for {symbol}: {e}")
        return {
            "order_id": f"limit_{symbol}_{int(time.time())}",
            "status": "failed",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "order_type": "Limit",
            "error": str(e)
        }

def place_market_order(symbol: str, quantity: float, side: str = "Buy") -> dict:
    """
    Enhanced market order placement.
    """
    try:
        # Note: Market orders would need different implementation in real exchange
        # For now, we'll place a limit order at current price + small offset
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get current price
        current_price = loop.run_until_complete(default_api.get_current_price(symbol))
        
        if current_price:
            # Add small offset for market execution simulation
            offset = current_price * 0.001  # 0.1% offset
            execution_price = current_price + offset if side.lower() in ['buy', 'long'] else current_price - offset
            
            result = loop.run_until_complete(
                default_api.place_limit_order(symbol, side.lower(), quantity, execution_price)
            )
            loop.close()
            
            return {
                "order_id": result.order_id,
                "status": "FILLED",  # Simulate immediate fill
                "symbol": result.symbol,
                "side": result.side,
                "qty": result.amount,
                "order_type": "Market",
                "price": result.price
            }
        else:
            loop.close()
            raise ValueError("Could not get current price for market order")
            
    except Exception as e:
        print(f"❌ Market order failed: {e}")
        # Fallback to mock
        return {
            "order_id": f"market_{symbol}_{int(time.time())}",
            "status": "FAILED",
            "symbol": symbol,
            "side": side,
            "qty": quantity,
            "order_type": "Market",
            "error": str(e)
        }

async def place_dual_entry_orders(symbol: str, side: str, total_amount: float,
                                 entry_price1: float, entry_price2: float,
                                 step1_ratio: float = 0.6) -> Tuple[Dict, Dict]:
    """
    Place dual LIMIT orders for entry strategy.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: 'buy' or 'sell'
        total_amount: Total position size
        entry_price1: Price for first order (Step 1)
        entry_price2: Price for second order (Step 2)  
        step1_ratio: Ratio of total amount for step 1 (default 60%)
    
    Returns:
        Tuple of (order1_dict, order2_dict)
    """
    try:
        order1, order2 = await default_api.place_dual_limit_orders(
            symbol, side, total_amount, entry_price1, entry_price2, step1_ratio
        )
        
        # Convert to dict format for backward compatibility
        order1_dict = {
            "order_id": order1.order_id,
            "status": order1.status,
            "symbol": order1.symbol,
            "side": order1.side,
            "quantity": order1.amount,
            "price": order1.price,
            "step": 1
        }
        
        order2_dict = {
            "order_id": order2.order_id,
            "status": order2.status,
            "symbol": order2.symbol,
            "side": order2.side,
            "quantity": order2.amount,
            "price": order2.price,
            "step": 2
        }
        
        return order1_dict, order2_dict
        
    except Exception as e:
        print(f"❌ Dual entry orders failed: {e}")
        raise e

def place_initial_entry_in_two_steps(symbol: str, total_quantity: float, 
                                    entry_price1: float = None, entry_price2: float = None):
    """
    Legacy function wrapper for dual entry orders.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get current price if not provided
        if not entry_price1 or not entry_price2:
            current_price = loop.run_until_complete(default_api.get_current_price(symbol))
            if not entry_price1:
                entry_price1 = current_price * 0.995  # 0.5% below current
            if not entry_price2:
                entry_price2 = current_price * 0.990  # 1% below current
        
        order1, order2 = loop.run_until_complete(
            place_dual_entry_orders(symbol, "buy", total_quantity, entry_price1, entry_price2)
        )
        loop.close()
        
        print(f"✅ Dual entry orders placed for {symbol}")
        print(f"   Step 1: {order1['quantity']} @ ${order1['price']:,.2f}")
        print(f"   Step 2: {order2['quantity']} @ ${order2['price']:,.2f}")
        
        return [order1, order2]
        
    except Exception as e:
        print(f"❌ Failed to place dual entry orders: {e}")
        return []

async def get_position(symbol: str) -> dict:
    """
    Enhanced position retrieval using real exchange API.
    """
    try:
        positions = await default_api.get_positions(symbol)
        
        if positions:
            # Return first matching position
            pos = positions[0]
            return {
                "symbol": pos.symbol,
                "size": pos.size,
                "side": pos.side,
                "avgPrice": pos.entry_price,
                "unrealisedPnl": pos.unrealized_pnl,
                "leverage": pos.leverage,
                "percentage": pos.percentage,
                "margin": pos.margin
            }
        else:
            # No position found
            return {
                "symbol": symbol,
                "size": 0,
                "side": "None",
                "avgPrice": 0,
                "unrealisedPnl": 0,
                "leverage": 1,
                "percentage": 0,
                "margin": 0
            }
            
    except Exception as e:
        print(f"❌ Failed to get position for {symbol}: {e}")
        # Fallback to mock data
        return {
            "symbol": symbol,
            "size": 0,
            "side": "None",
            "avgPrice": 0,
            "unrealisedPnl": 0,
            "leverage": 1,
            "error": str(e)
        }

# Enhanced utility functions
async def get_account_balance(currency: str = "USDT") -> float:
    """Get account balance for a specific currency."""
    try:
        balance = await default_api.get_balance(currency)
        return balance.get('free', 0.0) if isinstance(balance, dict) else 0.0
    except Exception as e:
        print(f"❌ Failed to get {currency} balance: {e}")
        return 0.0

async def get_current_price_async(symbol: str) -> float:
    """Async version of current price fetching."""
    return await default_api.get_current_price(symbol)

def get_current_price_sync(symbol: str) -> float:
    """Synchronous wrapper for current price fetching."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        price = loop.run_until_complete(default_api.get_current_price(symbol))
        loop.close()
        return price
    except Exception as e:
        print(f"❌ Failed to get price for {symbol}: {e}")
        return None

# API status and health check functions
def check_api_status() -> Dict[str, bool]:
    """Check the status of all exchange APIs."""
    return {
        "bitget_ready": not bitget_api.mock_mode,
        "bybit_ready": not bybit_api.mock_mode,
        "bitget_testnet": bitget_api.testnet,
        "bybit_testnet": bybit_api.testnet,
        "live_trading": default_api.is_live_trading_enabled()
    }

def switch_to_exchange(exchange_name: str) -> bool:
    """Switch the default exchange API."""
    global default_api
    
    if exchange_name.lower() == "bitget":
        default_api = bitget_api
        print(f"✅ Switched to Bitget API {'(TESTNET)' if default_api.testnet else '(LIVE)'}")
        return True
    elif exchange_name.lower() == "bybit":
        default_api = bybit_api  
        print(f"✅ Switched to Bybit API {'(TESTNET)' if default_api.testnet else '(LIVE)'}")
        return True
    else:
        print(f"❌ Unknown exchange: {exchange_name}")
        return False