import asyncio
from core.api import (
    place_dual_entry_orders, place_market_order, get_current_price_async, get_account_balance
)
from core.exchange_api import OrderResult
from typing import Dict, Tuple

async def calculate_position_size(symbol: str, risk_percent: float, leverage: float, sl_price: float, entry_price: float) -> float:
    """
    Calculate position size based on risk, leverage, and stop-loss distance.
    """
    balance = await get_account_balance("USDT")
    risk_amount = balance * (risk_percent / 100)
    risk_per_unit = abs(entry_price - sl_price)
    if risk_per_unit == 0:
        return 0.0
    qty = (risk_amount * leverage) / risk_per_unit
    return round(qty, 6)

async def execute_entry_strategy(
    symbol: str,
    side: str,
    risk_percent: float,
    leverage: float,
    entry_price1: float = None,
    entry_price2: float = None,
    sl_price: float = None,
    tp_price: float = None,
    step1_ratio: float = 0.5
) -> Dict:
    """
    Execute entry logic with two-step LIMIT orders and fallback to market order if needed.
    """
    results = {"orders": [], "fallback": False, "errors": []}
    try:
        # Get current price if not provided
        if not entry_price1 or not entry_price2:
            current_price = await get_current_price_async(symbol)
            entry_price1 = entry_price1 or current_price * 0.995
            entry_price2 = entry_price2 or current_price * 0.990
        
        # Calculate SL/TP if not provided
        if not sl_price:
            sl_price = entry_price1 * (0.98 if side.lower() == "buy" else 1.02)
        if not tp_price:
            tp_price = entry_price1 * (1.02 if side.lower() == "buy" else 0.98)
        
        # Calculate position size
        qty = await calculate_position_size(symbol, risk_percent, leverage, sl_price, entry_price1)
        if qty <= 0:
            results["errors"].append("Position size is zero. Check risk or SL settings.")
            return results
        
        # Place dual LIMIT orders (50/50 split)
        try:
            order1, order2 = await place_dual_entry_orders(
                symbol, side, qty, entry_price1, entry_price2, step1_ratio
            )
            results["orders"].extend([order1, order2])
            results["fallback"] = False
        except Exception as e:
            # Fallback: Place market order for first entry
            results["errors"].append(f"Dual LIMIT order failed: {e}. Fallback to market order.")
            market_order = place_market_order(symbol, qty, side)
            results["orders"].append(market_order)
            results["fallback"] = True
        
        # Attach SL/TP info to orders (for logging/demo)
        for order in results["orders"]:
            order["sl_price"] = sl_price
            order["tp_price"] = tp_price
        
        return results
    except Exception as e:
        results["errors"].append(f"Entry strategy failed: {e}")
        return results

# Demo/test function
async def test_entry_manager():
    print("\n=== ENTRY STRATEGY TEST ===")
    symbol = "BTCUSDT"
    side = "buy"
    risk_percent = 1.0
    leverage = 10
    # Simulate a trade
    result = await execute_entry_strategy(
        symbol=symbol,
        side=side,
        risk_percent=risk_percent,
        leverage=leverage
    )
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_entry_manager())