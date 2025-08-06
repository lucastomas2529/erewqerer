from config.settings import TRAILING_ACTIVATION, TRAILING_SL_PERCENT
from utils.logger import log_event

def should_activate_trailing(pol, tp4_hit):
    return tp4_hit or pol >= TRAILING_ACTIVATION['after_pol']

def calculate_trailing_sl(current_price, direction):
    if direction == "long":
        return round(current_price * (1 - TRAILING_SL_PERCENT), 2)
    elif direction == "short":
        return round(current_price * (1 + TRAILING_SL_PERCENT), 2)
    else:
        raise ValueError("Felaktig riktning angiven")

async def monitor_trailing_stop():
    # Placeholder-loop, här ska koppling till prisfeed ske
    log_event("[TRAILING] Trailing-stop monitor är aktiv", "INFO")
    # while True:
    #     await asyncio.sleep(30)
    #     kontrollera om SL ska flyttas ytterligare

    # logic/trailing.py
from utils.telegram_logger import send_telegram_log

async def activate_trailing_stop(symbol: str, side: str):
    """
    Aktiverar trailing stop i marknaden.
    """
    try:
        trailing_percent = 0.3  # t.ex. 0.3% trailing
        direction = "Sell" if side.upper() == "LONG" else "Buy"

        await send_telegram_log(
            f"📉 Trailing SL aktiverad för {symbol} ({side}) – {trailing_percent}%",
            tag="trailing"
        )

        # Exekvera via din klient
        # await client.set_trailing_stop(symbol=symbol, side=direction, trailingStop=trailing_percent)

    except Exception as e:
        await send_telegram_log(f"❌ Fel vid aktivering av trailing SL för {symbol}: {e}", tag="error")
