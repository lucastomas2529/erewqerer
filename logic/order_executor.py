# order_executor.py

import logging
import asyncio
from typing import Optional
from utils.constants import ORDER_SETTINGS
from utils.quantity import calculate_quantity
from utils.telegram_logger import send_telegram_log
from utils.price import round_price
from config.settings import DEFAULT_BALANCE, RISK_PERCENT, DEFAULT_IM, DEFAULT_LEVERAGE
from utils.leverage import calculate_leverage

async def check_existing_position(client, symbol: str) -> bool:
    """
    Kontrollera om en öppen position redan finns för detta symbol.
    Returnerar True om en aktiv position finns.
    """
    try:
        positions = await client.get_positions(symbol=symbol)
        for pos in positions:
            if pos["symbol"] == symbol and float(pos["size"]) > 0:
                await send_telegram_log(f"⚠️ Position redan öppen för {symbol}. Hoppar över ny trade.")
                return True
        return False
    except Exception as e:
        await send_telegram_log(f"❌ Fel vid kontroll av öppen position: {e}")
        return False


async def close_position(client, symbol: str, side: str, quantity: float, order_type: str = "Market", base_price_type: str = "LastPrice") -> dict:
    """
    Stänger del av en position med angiven ordertyp och prisbas.
    Används vid TP1–TP6, anpassar LIMIT vs MARKET.
    """
    try:
        order_data = {
            "symbol": symbol,
            "side": "Sell" if side.upper() == "LONG" else "Buy",
            "order_type": order_type,
            "qty": quantity,
            "reduce_only": True,
            "base_price_type": base_price_type
        }

        logging.info(f"📤 CLOSE POSITION ORDER: {order_data}")
        await send_telegram_log(f"📤 CLOSE POSITION – {order_data['side']} {quantity} {symbol} ({order_type}, {base_price_type})", tag="tp")

        # Här kallas API (denna måste finnas i client-objektet)
        result = await client.place_order(**order_data)

        if result.get("retCode") == 0:
            await send_telegram_log(f"✅ Position stängd: {result}")
            return result
        else:
            await send_telegram_log(f"❌ Stäng position misslyckades: {result}")
            return result

    except Exception as e:
        await send_telegram_log(f"❌ Stäng position exception: {e}")
        return {"error": str(e)}

# Additional placeholder functions for imports
async def update_sl_tp(symbol: str, sl_price: float = None, tp_price: float = None) -> dict:
    """Update stop loss and take profit for existing position."""
    print(f"📝 UPDATE SL/TP: {symbol}")
    return {"status": "mock"}

async def handle_reverse_logic(*args, **kwargs):
    """Placeholder for reverse logic handling."""
    print("🔄 Reverse logic placeholder")
    return {"status": "mock"}

async def place_initial_entry_in_two_steps(*args, **kwargs):
    """Placeholder for two-step entry logic."""
    print("📤 Two-step entry placeholder")
    return {"status": "mock"}

async def place_market_order(*args, **kwargs):
    """Placeholder for market orders."""
    print("📤 Market order placeholder") 
    return {"status": "mock"}

async def partial_close(*args, **kwargs):
    """Placeholder for partial close logic."""
    print("📤 Partial close placeholder")
    return {"status": "mock"}

def place_smart_order(*args, **kwargs):
    """Placeholder for smart order logic."""
    print("📤 Smart order placeholder")
    return {"status": "mock"}