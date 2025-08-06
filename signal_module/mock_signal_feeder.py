import asyncio
from signal_module.signal_queue import signal_queue

async def feed_mock_signals():
    while True:
        mock = {
            "symbol": "BTCUSDT",
            "side": "LONG",
            "entry_price": 27000,
            "sl_price": 26700,
            "tp1": 27200,
            "tp2": 27500,
            "leverage": 10
        }
        await signal_queue.put(mock)
        await asyncio.sleep(60)
