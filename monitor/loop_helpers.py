# loop_helpers.py – hanterar realtids-övervakning av PoL och pyramiding
import asyncio
from monitor.trade_state import TradeState
from logic.pyramiding import evaluate_pyramiding_actions
from logic.sl_manager import update_sl
from logic.trailing import activate_trailing_stop
from core.api import place_reentry_order
from utils.price import get_current_price, round_price
from utils.telegram_logger import send_telegram_log
from logic.order_router import place_conditional_order  
from core.api import client
from logic.pol_monitor import monitor_pol_and_adjust


async def monitor_pol_and_adjust(state: TradeState, signal: dict):
    """
    Övervakar PoL och utför åtgärder enligt strategi:
    - IM-upplägg vid +2.5%, +4%, +6%
    - SL-flytt vid +2.4% eller TP
    - Trailing vid TP4 eller +6%
    """
    from monitor.lock_manager import get_symbol_lock

    lock = get_symbol_lock(state.symbol)
    async with lock:
        try:
            while state.position_active:
                await asyncio.sleep(15)

                price = await get_current_price(state.symbol)
                if not price:
                    await send_telegram_log(f"⚠️ Kunde inte hämta pris för {state.symbol}", tag="error")
                    continue 

                state.update_pol(price)

                await send_telegram_log(
                    f"📊 PoL {state.symbol} ({state.side}): {state.current_pol:.2f}%",
                    tag="pol"
                )

        except Exception as e:
            print(f"⚠️ Fel i monitor_pol_and_adjust: {e}")
            await send_telegram_log(f"Fel i monitor_pol_and_adjust: {e}", tag="error")


            # Kontrollera åtgärder
            actions = evaluate_pyramiding_actions(
                pol_percent=state.current_pol,
                sl_price=state.sl_price or 0,
                entry_price=state.entry_price
            )

            # SL-flytt
            if actions["move_sl_to"] and not state.sl_updated:
                await update_sl(
                     symbol=state.symbol,
                    side=state.side,
                    new_sl=actions["move_sl_to"],
                    quantity=state.quantity,
                    order_id=state.order_id
                )

                state.sl_price = actions["move_sl_to"]
                state.sl_updated = True

                # 📈 IM-top-up och re-entry-logik
                if actions["im_top_up"]:
                    await place_reentry_order(
                        symbol=state.symbol,
                        side=state.side,
                        entry_price=state.entry_price,
                        sl_price=state.sl_price,
                        leverage=actions.get("new_leverage", state.leverage),
                        initial_margin=actions["im_top_up"],
                        qty=state.quantity,
                        is_pyramiding=True
                    )

                

                    # 🆕 Villkorad order efter re-entry (t.ex. TP1-nivå)
                    try:
                        tp_price = state.entry_price * 1.015  # Justera till riktig TP1 om tillgänglig
                        place_conditional_order(
                            client=client,
                            symbol=state.symbol,
                            side="SELL" if state.side == "LONG" else "BUY",
                            trigger_price=tp_price,
                            entry_price=tp_price,
                            qty=state.quantity,
                            leverage=state.leverage,
                            sl=state.sl_price,
                            tp=None
                        )

                    except Exception as e:
                        await send_telegram_log(
                            f"⚠️ Kunde inte lägga villkorad order för {state.symbol}: {e}",
                            tag="order"
                        )

            # Trailing stop
            if actions["trigger_trailing"] and not state.trailing_active:
                await activate_trailing_stop(state.symbol, state.side)
                state.trailing_active = True


