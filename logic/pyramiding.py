# pyramiding.py – PoL-övervakning och IM-hantering
from config.settings import DEFAULT_LEVERAGE, PYRAMID_STEPS, LEVERAGE_CAP
from utils.telegram_logger import send_telegram_log
from config.strategy_control import is_strategy_enabled


def evaluate_pyramiding_actions(pol_percent: float, sl_price: float, entry_price: float, symbol: str = None, group_name: str = None, timeframe: str = "default") -> dict:
    """
    Returnerar en åtgärdsplan baserat på aktuell profit-nivå (PoL).
    Resultat innehåller:
    - im_top_up: IM att lägga till (None om ingen ökning)
    - new_leverage: Ny hävstång (None om oförändrad)
    - move_sl_to: Ny SL-nivå (None om oförändrad)
    - trigger_trailing: True om trailing ska aktiveras
    """
    
    # Check if pyramiding is enabled for this symbol/group/timeframe
    if symbol and group_name and not is_strategy_enabled("ENABLE_PYRAMIDING", symbol, group_name, timeframe):
        send_telegram_log(f"❌ [StrategyOverride] Pyramiding disabled for {symbol} ({group_name}, {timeframe})", tag="pyramiding")
        return {
            "im_top_up": None,
            "new_leverage": None,
            "move_sl_to": None,
            "trigger_trailing": False
        }

    actions = {
        "im_top_up": None,
        "new_leverage": None,
        "move_sl_to": None,
        "trigger_trailing": False
    }

    # Use centralized pyramid configuration
    level_1 = PYRAMID_STEPS["level_1"]
    level_2 = PYRAMID_STEPS["level_2"] 
    level_3 = PYRAMID_STEPS["level_3"]
    
    # Level 1 - Reset IM and adjust leverage if configured
    if pol_percent >= level_1["trigger_pol"]:
        actions["im_top_up"] = level_1["topup_im"]
        send_telegram_log(f"🔁 PoL ≥ {level_1['trigger_pol']}% → återställer IM till {level_1['topup_im']} USDT", tag="pyramiding")
        
        # Adjust leverage to max if configured and SL is safe
        if level_1.get("adjust_leverage_to_max") and sl_price >= entry_price * (1 + level_1["min_sl_to_raise_leverage"]):
            actions["new_leverage"] = LEVERAGE_CAP
            send_telegram_log(f"⚡️ Höjer hävstång till x{LEVERAGE_CAP}", tag="pyramiding")

    # Move SL to safe level when configured
    min_sl_offset = level_1.get("min_sl_to_raise_leverage", 0.0015)
    if pol_percent >= (level_1["trigger_pol"] - 0.1):  # Slightly before level 1
        new_sl = round(entry_price * (1 + min_sl_offset), 6)
        if sl_price < new_sl:
            actions["move_sl_to"] = new_sl
            send_telegram_log(f"🔐 PoL ≥ {level_1['trigger_pol'] - 0.1}% → Flyttar SL till Entry +{min_sl_offset*100:.2f}%: {new_sl}", tag="sl")

    # Level 2 - Higher IM
    if pol_percent >= level_2["trigger_pol"]:
        actions["im_top_up"] = level_2["topup_im"]
        send_telegram_log(f"💥 PoL ≥ {level_2['trigger_pol']}% → IM = {level_2['topup_im']} USDT", tag="pyramiding")

    # Level 3 - Maximum IM + trailing stop
    if pol_percent >= level_3["trigger_pol"]:
        actions["im_top_up"] = level_3["topup_im"]
        actions["trigger_trailing"] = True
        send_telegram_log(f"🚀 PoL ≥ {level_3['trigger_pol']}% → IM = {level_3['topup_im']} USDT + aktivera trailing stop", tag="pyramiding")

    return actions

