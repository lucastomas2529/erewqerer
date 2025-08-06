import asyncio
from signal_module.listener import start_telegram_listener
from monitor.loop_manager import trading_loop                    # ⬅️ ny
from logic.entry import handle_entry_signal
from logic.trailing import monitor_trailing_stop
from monitor.trade_state import monitor_pol_and_adjust
from utils.logger import log_event
from config.settings import SHUTDOWN_ALL

async def main():
    log_event("🔄 Boten startar...")

    if SHUTDOWN_ALL:
        log_event("🛑 Boten är i nödläge – SHUTDOWN_ALL är aktivt", "ERROR")
        return

    try:
        await asyncio.gather(
            start_telegram_listener(handle_entry_signal),  # Telegram-parser
            monitor_trailing_stop(),                       # Trailing-övervakning
            trading_loop()                                 # ✅ Kör direkt som async-funktion
    )
    except Exception as e:
        log_event(f"[FATAL] Fel i huvudloopen: {e}", "ERROR")


if __name__ == "__main__":
    asyncio.run(main())

# Säkerställ att SignalHandler instansieras
from signal_module.signal_handler import SignalHandler
handler = SignalHandler()

