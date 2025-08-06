# pol_monitor.py – övervakning av PoL och pyramiding
import logging
from config.settings import DEFAULT_BALANCE, RISK_PERCENT, DEFAULT_IM, DEFAULT_LEVERAGE, PYRAMID_STEPS, LEVERAGE_CAP
from core.symbol_data import get_symbol_precision
from utils.telegram_logger import send_telegram_log
from utils.leverage import calculate_leverage
async def monitor_pol_and_adjust(state, signal): ...


async def get_pyramiding_im_and_leverage(pol_percent: float, current_sl: float, entry_price: float) -> dict:
    """
    Returnerar IM och leverage beroende på aktuell profit-nivå (PoL).
    """
    result = {"new_im": None, "new_leverage": None, "sl_adjusted": False}

    # Level 1: 1.5% - 2.5% profit
    if pol_percent >= PYRAMID_STEPS["level_1"]["trigger_pol"] and pol_percent < 2.5:
        result["new_im"] = PYRAMID_STEPS["level_1"]["topup_im"]
        await send_telegram_log(f"🔁 PoL ≥ {PYRAMID_STEPS['level_1']['trigger_pol']}% → återställer IM till {PYRAMID_STEPS['level_1']['topup_im']} USDT", tag="pyramiding")

    # Break-even logic
    if pol_percent >= 2.4:
        new_sl = round(entry_price * 1.0015, 6)
        if current_sl < new_sl:
            result["sl_adjusted"] = True
            await send_telegram_log(f"🔐 PoL ≥ 2.4% → Flyttar SL till Entry +0.15%: {new_sl}", tag="sl")
    
    # Level 2: 2.5% profit
    if pol_percent >= PYRAMID_STEPS["level_2"]["trigger_pol"]:
        result["new_im"] = PYRAMID_STEPS["level_2"]["topup_im"]
        result["new_leverage"] = LEVERAGE_CAP
        await send_telegram_log(f"⚡️ PoL ≥ {PYRAMID_STEPS['level_2']['trigger_pol']}% → IM = {PYRAMID_STEPS['level_2']['topup_im']} USDT & hävstång till max x{LEVERAGE_CAP}", tag="pyramiding")

    # Level 3: 4.0% profit
    if pol_percent >= PYRAMID_STEPS["level_3"]["trigger_pol"]:
        result["new_im"] = PYRAMID_STEPS["level_3"]["topup_im"]
        await send_telegram_log(f"💥 PoL ≥ {PYRAMID_STEPS['level_3']['trigger_pol']}% → IM = {PYRAMID_STEPS['level_3']['topup_im']} USDT", tag="pyramiding")

    # Additional level: 6.0% profit
    if pol_percent >= 6.0:
        result["new_im"] = 200
        await send_telegram_log("🚀 PoL ≥ 6.0% → IM = 200 USDT", tag="pyramiding")

    return result

