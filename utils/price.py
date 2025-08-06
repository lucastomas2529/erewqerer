# utils/price.py
from __future__ import annotations

import asyncio
from decimal import Decimal, ROUND_DOWN
from functools import lru_cache
from typing import Optional

# Vi låter core.symbol_data vara sanningen för pris (async).
# Den här modulen fungerar som adapter + hjälpfunktioner.
try:
    from core.symbol_data import (
        get_current_price as _get_current_price,  # async källa för live-pris
    )
except Exception as _e:  # pragma: no cover
    _get_current_price = None  # type: ignore

__all__ = [
    "get_current_price",
    "get_current_price_sync",
    "get_latest_price",
    "get_volume_24h",
    "round_price",
]

# ---------- Precision & rundning ----------

# Säker fallback om core.symbol_data inte exponerar symbol-precision.
from config.settings import SymbolConfig

_DEFAULT_DECIMALS = SymbolConfig.DEFAULT_DECIMALS
_FALLBACK_DECIMALS_MAP = SymbolConfig.FALLBACK_DECIMALS_MAP

@lru_cache(maxsize=256)
def _decimals_for_symbol_cached(symbol: str) -> int:
    """
    Hämta decimal-precision för symbol och cacha resultatet.
    Först: försök via core.symbol_data.get_symbol_precision.
    Annars: fallback-tabell → annars _DEFAULT_DECIMALS.
    """
    sym = (symbol or "").upper()
    if not sym:
        return _DEFAULT_DECIMALS

    # Försök via core.symbol_data om funktionen finns
    try:
        from core.symbol_data import get_symbol_precision  # type: ignore
        dec = get_symbol_precision(sym)
        return int(dec)
    except Exception:
        # gå vidare till fallback
        pass

    return int(_FALLBACK_DECIMALS_MAP.get(sym, _DEFAULT_DECIMALS))


def round_price(price: float, symbol: Optional[str] = None) -> float:
    """
    Avrunda pris till korrekt precision för symbolen (ROUND_DOWN).
    Defensivt: tvingar float.
    """
    price = float(price)
    decimals = _decimals_for_symbol_cached(symbol or "")
    quant = Decimal(10) ** (-decimals)
    return float(Decimal(str(price)).quantize(quant, rounding=ROUND_DOWN))


# ---------- Live-pris: async + sync wrappers ----------

async def get_current_price(symbol: str) -> float:
    """
    Hämta live-pris för symbol från den ENDA källan (core.symbol_data).
    """
    if _get_current_price is None:
        raise RuntimeError("core.symbol_data.get_current_price saknas – kan inte hämta pris.")
    return float(await _get_current_price(symbol))


def get_current_price_sync(symbol: str) -> float:
    """
    Synk wrapper: använd INTE inne i en redan-asynk kontext.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # ingen loop → kör synchronously
        return asyncio.run(get_current_price(symbol))
    else:
        # loop kör redan; vi kan inte blocka/åter-entrera den här.
        raise RuntimeError("get_current_price_sync() anropad inifrån en aktiv event loop.")


# ---------- Hjälpmetoder med robust loggning ----------

async def get_latest_price(symbol: str) -> Optional[float]:
    """
    Hämta senaste pris; returnera None om något går fel.
    """
    try:
        return await get_current_price(symbol)
    except Exception as e:
        # Logga asynkront – förutsätter att loggfunktionen är async-kompatibel
        try:
            from utils.telegram_logger import send_telegram_log  # async
            await send_telegram_log(
                f"❌ Misslyckades att hämta pris för {symbol}: {e!r}",
                tag="error",
            )
        except Exception:
            pass
        return None


async def get_volume_24h(symbol: str) -> Optional[float]:
    """
    Försök hämta 24h-volym via Bitget-klienten om metod finns; annars None.
    Gör inte antaganden om exakt endpoint-namn.
    """
    sym = (symbol or "").upper()
    try:
        from core.bitget_client import get_client  # din fabrik som returnerar en klient
        client = get_client()

        # Pröva några vanliga namn i ordning – anpassa till din klient när du vet exakta metoder.
        for attr in ("get_24h_volume", "get_ticker_24h_volume", "get_ticker"):
            if hasattr(client, attr):
                fn = getattr(client, attr)
                val = fn(sym)  # kan vara sync eller async beroende på din klient-impl
                if asyncio.iscoroutine(val):
                    val = await val

                # Om dict → plocka ett känt fält
                if isinstance(val, dict):
                    for k in ("vol", "volume", "baseVolume", "quoteVolume"):
                        if k in val:
                            try:
                                return float(val[k])  # type: ignore[arg-type]
                            except Exception:
                                return None
                    # om inget passade
                    return None

                # Om redan numeriskt
                try:
                    return float(val)  # type: ignore[arg-type]
                except Exception:
                    return None

        return None

    except Exception as e:
        try:
            from utils.telegram_logger import send_telegram_log
            await send_telegram_log(
                f"❌ Volymhämtning misslyckades för {sym}: {e!r}",
                tag="error",
            )
        except Exception:
            pass
        return None



