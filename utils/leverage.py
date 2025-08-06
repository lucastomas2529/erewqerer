import logging
from config.settings import DEFAULT_BALANCE, RISK_PERCENT, DEFAULT_IM, DEFAULT_LEVERAGE, LEVERAGE_CAP
from utils.telegram_logger import send_telegram_log

async def calculate_leverage(entry_price: float, sl_price: float) -> float:
    """
    Kombinerad modell:
    - Om SL finns → dynamisk hävstångsberäkning (max x50)
    - Om SL saknas → fast x10 (ingen annan logik gäller)
    """
    try:
        if sl_price is None:
            await send_telegram_log("⚠️ SL saknas – använder fast hävstång x10", tag="risk")
            return DEFAULT_LEVERAGE

        sl_percent = abs(entry_price - sl_price) / entry_price
        if sl_percent == 0:
            await send_telegram_log("⚠️ SL-avstånd = 0 – fallback DEFAULT_LEVERAGE används", tag="risk")
            return DEFAULT_LEVERAGE

        risk_usdt = DEFAULT_BALANCE * (RISK_PERCENT / 100)
        leverage = risk_usdt / (DEFAULT_IM * sl_percent)
        return min(round(leverage, 2), LEVERAGE_CAP)

    except Exception as e:
        logging.error(f"❌ Leverage-kalkylfel: {e}")
        await send_telegram_log(f"❌ Leverage fallback pga fel: {e}", tag="risk")
        return DEFAULT_LEVERAGE


