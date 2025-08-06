import pytest
from logic.reentry import check_reentry_conditions

def test_reentry_wait_time_enforced(monkeypatch):
    monkeypatch.setattr("logic.reentry.time", __import__("time"))  # native time

    from logic.reentry import reentry_state
    symbol = "BTCUSDT"
    reentry_state[symbol] = {"last_attempt": time.time() - 1}

    allowed = check_reentry_conditions(symbol, time_limit=10)
    assert not allowed, "Re-entry tillåts för tidigt"

def test_dummy_indicator_pass(monkeypatch):
    from logic.reentry import ema_confirms_reentry, rsi_confirms_reentry
    assert ema_confirms_reentry("BTCUSDT") is True
    assert rsi_confirms_reentry("BTCUSDT") is True