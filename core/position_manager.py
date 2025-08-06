# position_manager.py

from typing import Dict, Optional
from utils.telegram_logger import send_telegram_log
from config.settings import TradingConfig
from utils.leverage import calculate_leverage


def prepare_position(signal: Dict) -> Optional[Dict]:
    """
    Förbereder position baserat på signalens entry, SL, risk mm.
    Returnerar dict med qty, lev, IM mm. Returnerar None vid fel.
    """
    try:
        symbol = signal["symbol"]
        entry = signal["entry"]
        sl = signal["sl"]
        direction = signal["direction"]
        tp = signal.get("tp", [])
        signal_text = signal.get("raw_text", "").lower()  # för att hitta "x75" eller "swing"

        if sl is None:
            send_telegram_log("❌ Kan ej beräkna position – SL saknas.", tag="error")
            return None

        # Riskkalkyl enligt strategi
        risk_amount = TradingConfig.RISK_PERCENT
        initial_margin = TradingConfig.DEFAULT_IM  # fallback IM
        distance = abs(entry - sl)

        leverage = calculate_leverage(entry, sl)

        # x75 = strategi-flagga, betyder 10x leverage (ej bokstavlig 75x)
        if "x75" in signal_text:
            leverage = 10.0

        # swing = strategi-flagga, betyder 6x leverage
        if "swing" in signal_text:
            leverage = 6.0

        # Beräkna qty från IM och leverage
        qty = calculate_position_size(entry, leverage, initial_margin)

        return {
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "qty": qty,
            "leverage": leverage,
            "initial_margin": initial_margin,
            "direction": direction
        }

    except Exception as e:
        send_telegram_log(f"❌ Fel vid prepare_position: {e}", tag="error")
        return None

def calculate_position_size(entry_price: float, leverage: float, im_amount: float) -> float:
    """
    Enkel beräkning av positionens storlek.
    """
    try:
        if entry_price == 0:
            return 0
        return round((im_amount * leverage) / entry_price, 4)
    except Exception as e:
        send_telegram_log(f"❌ Fel vid beräkning av position size: {e}", tag="error")
        return 0


