from utils.logger import log_event

async def handle_tp_hit(symbol, tp_level_hit, tp_prices, current_sl):
    try:
        if tp_level_hit == 2:
            new_sl = tp_prices[0]
            log_event(f"[SL-MOVE] Flyttar SL till TP1 på {symbol} → {new_sl}", "INFO")
            return new_sl
        elif tp_level_hit == 3:
            new_sl = tp_prices[1]
            log_event(f"[SL-MOVE] Flyttar SL till TP2 på {symbol} → {new_sl}", "INFO")
            return new_sl
        elif tp_level_hit == 4:
            new_sl = tp_prices[2]
            log_event(f"[SL-MOVE] Flyttar SL till TP3 på {symbol} → {new_sl}", "INFO")
            return new_sl
        else:
            return current_sl
    except Exception as e:
        log_event(f"[ERROR] TP-hantering misslyckades för {symbol}: {e}", "ERROR")
        return current_sl