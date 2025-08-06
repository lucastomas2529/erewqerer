import time
import asyncio
import inspect
from datetime import datetime
from utils.price import get_current_price
from core.position_manager import prepare_position, calculate_position_size
from generate.daily_report import analyze_trades as analyze_daily
from generate.weekly_report import analyze_trades as analyze_weekly
from logic.entry import handle_entry_signal
from utils.leverage import calculate_leverage
from logic.hedge import check_and_open_hedge
from logic.reentry import check_reentry_conditions, place_reentry_order
from logic.order_executor import (
    check_existing_position,
    close_position,
    handle_reverse_logic,
    place_initial_entry_in_two_steps,
    place_market_order,
    update_sl_tp,
    partial_close
)
from logic.order_router import (
    place_conditional_order,
    fallback_to_limit_order,
    modify_order,
    cancel_order,
)
from logic.breakeven_ws import breakeven_watcher
from logic.sl_manager import check_and_adjust_sl
from logic.tp_manager import handle_tp_hit
from logic.trailing import (
    should_activate_trailing,
    calculate_trailing_sl,
    monitor_trailing_stop,
)
from signal_module.signal_handler import (
    get_active_signal,
    parse_signal,
    handle_incoming_signal,
    match_signal_update,
    parse_partial_close,
    start_trade_from_incomplete_signal,
)
from signal_module.forward_signals_userbot import forward_handler
from utils.telegram_logger import send_telegram_log
from core.api import (
    place_order,
    place_dca_orders,
    amend_order
)
import asyncio
from monitor.trade_state import TradeState
from monitor.loop_helpers import monitor_pol_and_adjust
from core.bitget_client import BitgetClient

client = BitgetClient()

async def trading_loop():
    while True:
        try:
            # Hämta signal – fungerar både om get_active_signal är async eller sync
            maybe_signal = get_active_signal()
            signal = await maybe_signal if inspect.isawaitable(maybe_signal) else maybe_signal

            if not signal:
                await asyncio.sleep(5)
                continue

            symbol = signal.get("symbol")
            if not symbol:
                await asyncio.sleep(5)
                continue

            # Hämta pris via ENDA källan (utils.price) – ingen client-parameter
            current_price = await get_current_price(symbol)
            signal["current_price"] = current_price

            # SIGNAL & ENTRY
            await handle_entry_signal(signal)
            await handle_incoming_signal(signal)
            leverage = calculate_leverage(signal["entry"], signal.get("sl"))
            position_data = prepare_position(signal)
            if position_data:
                quantity = position_data["qty"]
                place_initial_entry_in_two_steps(symbol, quantity)
            else:
                print(f"⚠️ Failed to prepare position for {symbol}")
                continue

            # Starta PoL-övervakning i bakgrunden
            state = TradeState(
                symbol=symbol,
                side=signal["direction"].upper(),
                entry_price=signal["entry"],
                sl_price=signal.get("sl"),
                leverage=leverage,
                initial_margin=signal.get("initial_margin", 20),
                quantity=quantity
            )
            asyncio.create_task(monitor_pol_and_adjust(state, signal))

            # SL/TP
            check_and_adjust_sl(symbol, current_price)
            handle_tp_hit(symbol, current_price)

            # RE-ENTRY & DCA
            if check_reentry_conditions(symbol, current_price):
                place_reentry_order(
                    client=client,
                    symbol=symbol,
                    side=signal["direction"],
                    entry_price=signal["entry"],
                    sl_price=signal.get("sl"),
                    leverage=leverage,
                    initial_margin=signal.get("initial_margin", 20),
                    qty=quantity
                )
            place_dca_orders(symbol, signal)

            # PYRAMIDING
            if signal.get("pol", 0) >= 2.5:
                pyramid_qty = calculate_position_size(current_price, leverage, 20)  # entry_price, leverage, im_amount
                place_market_order(symbol, pyramid_qty)

            # TRAILING STOP
            if should_activate_trailing(symbol):
                trailing_sl = calculate_trailing_sl(symbol)
                monitor_trailing_stop(symbol, trailing_sl)

            # HEDGE STRATEGY
            signal.setdefault("entry_price", signal.get("entry"))
            signal.setdefault("sl_price",   signal.get("sl"))
            check_and_open_hedge(symbol, signal["entry_price"], current_price, signal["sl_price"])

            # ORDER LOGIC
            check_existing_position(symbol)
            modify_order(symbol, current_price)
            cancel_order(symbol)
            handle_reverse_logic(symbol)
            close_position(symbol)

            # ADVANCED SIGNAL HANDLING
            update_sl_tp(symbol, current_price)
            partial_close(symbol, 0.25)
            match_signal_update(signal)
            parse_partial_close(signal)
            start_trade_from_incomplete_signal(signal)
            parse_signal(signal)

            # BREAKEVEN LIVE WATCHER
            breakeven_watcher()

            # REPORTING
            if datetime.utcnow().hour == 22:
                analyze_daily()
            if datetime.utcnow().weekday() == 6 and datetime.utcnow().hour == 23:
                analyze_weekly()

            await asyncio.sleep(15)

        except Exception as e:
            await send_telegram_log(f"[Loop error] {e}")
            await asyncio.sleep(10)

