# breakeven_ws.py

import asyncio
import websockets
import json

from utils.telegram_logger import send_telegram_log
from utils.constants import BE_TRIGGER_THRESHOLD, BE_OFFSET_PCT
from core.api import move_sl_to_be


# ... resten av din befintliga kod ...

async def breakeven_watcher(symbol: str, side: str, entry_price: float, client, state):
    """
    Startar WebSocket som lyssnar på marknadspris.
    Flyttar SL till BE när prisrörelse > BE_TRIGGER_THRESHOLD.
    """
    if state.entry_in_progress or state.is_ws_processing:
        return

    state.is_ws_processing = True

    ws_url = f"wss://stream.bybit.com/v5/public/linear"
    topic = f"tickers.{symbol}"

    try:
        async with websockets.connect(ws_url, ping_interval=None) as ws:
            await ws.send(json.dumps({
                "op": "subscribe",
                "args": [topic]
            }))
            await send_telegram_log(f"🟢 BE WebSocket aktiv för {symbol}", tag="info")

            while True:
                msg = await ws.recv()
                data = json.loads(msg)

                if "data" not in data:
                    continue

                price = float(data["data"].get("lastPrice", 0))
                if price == 0:
                    continue

                move_pct = ((price - entry_price) / entry_price) * 100
                if side.upper() == "SHORT":
                    move_pct *= -1

                if move_pct >= BE_TRIGGER_THRESHOLD and not state.sl_moved_to_be:
                    await move_sl_to_be(client, symbol, side, entry_price, offset_pct=BE_OFFSET_PCT)
                    state.sl_moved_to_be = True
                    await send_telegram_log(f"🔐 SL flyttat till BE +{BE_OFFSET_PCT}% för {symbol}", tag="sl")
                    break

                await asyncio.sleep(1)

    except Exception as e:
        await send_telegram_log(f"❌ BE WebSocket fel: {e}", tag="error")

    finally:
        state.is_ws_processing = False
