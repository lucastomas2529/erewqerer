# utils/symbol_data.py

# ✅ Anpassad för Bitget – ingen Bybit-referens

# Tick size och minsta orderstorlek per symbol
SYMBOL_INFO = {
    "BTCUSDT": {
        "tick_size": 0.1,
        "min_qty": 0.001
    },
    "ETHUSDT": {
        "tick_size": 0.01,
        "min_qty": 0.01
    },
    "XRPUSDT": {
        "tick_size": 0.0001,
        "min_qty": 10
    },
    "SOLUSDT": {
        "tick_size": 0.01,
        "min_qty": 0.1
    },
    "DOGEUSDT": {
        "tick_size": 0.00001,
        "min_qty": 100
    },
    "BNBUSDT": {
        "tick_size": 0.01,
        "min_qty": 0.05
    },
    "ADAUSDT": {
        "tick_size": 0.0001,
        "min_qty": 10
    },
    "AVAXUSDT": {
        "tick_size": 0.01,
        "min_qty": 0.1
    },
    "MATICUSDT": {
        "tick_size": 0.0001,
        "min_qty": 10
    },
    "LINKUSDT": {
        "tick_size": 0.01,
        "min_qty": 0.1
    }
    # 🔁 Lägg till fler symboler om du vill
}


def get_tick_size(symbol: str) -> float:
    """Returnerar tick size för angiven symbol."""
    return SYMBOL_INFO.get(symbol.upper(), {}).get("tick_size", 0.01)


def get_min_qty(symbol: str) -> float:
    """Returnerar minsta kvantitet för angiven symbol."""
    return SYMBOL_INFO.get(symbol.upper(), {}).get("min_qty", 0.001)

def get_symbol_precision(symbol: str) -> int:
    """
    Get decimal precision for symbol.
    TODO: Implement actual precision retrieval from exchange.
    """
    # Default precision mapping
    precision_map = {
        "BTCUSDT": 2,
        "ETHUSDT": 2,
        "XRPUSDT": 4,
        "SOLUSDT": 3,
        "DOGEUSDT": 5,
        "IOTAUSDT": 5,
        "ADAUSDT": 4,
    }
    return precision_map.get(symbol.upper(), 4)  # Default to 4 decimals

# core/symbol_data.py
from core.api import client  # Din riktiga API-klient
from utils.telegram_logger import send_telegram_log

async def get_current_price(symbol: str) -> float | None:
    try:
        ticker = await client.get_ticker(symbol=symbol)
        return float(ticker["lastPrice"])  # Anpassa beroende på klientens struktur
    except Exception as e:
        await send_telegram_log(f"❌ Kunde inte hämta pris för {symbol}: {e}", tag="error")
        return None