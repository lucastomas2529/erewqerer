import pytest
from logic.hedge import open_hedge_position

def test_open_hedge_position(monkeypatch):
    captured_orders = []
    monkeypatch.setattr("logic.hedge.place_order", lambda *args, **kwargs: captured_orders.append((args, kwargs)))
    monkeypatch.setattr("utils.telegram_logger.send_telegram_log", lambda msg, tag=None: None)

    open_hedge_position("BTCUSDT", entry_price=28000, sl_price=27500, qty=0.05, lev=10)
    assert captured_orders, "Ingen hedge-order registrerad"
    assert captured_orders[0][1]["side"] == "Sell"