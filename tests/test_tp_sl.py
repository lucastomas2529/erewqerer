import pytest
from logic.sl_manager import update_sl
from logic.trailing import monitor_trailing_stop

def test_update_sl_moves_sl_level(monkeypatch):
    logs = []
    monkeypatch.setattr("utils.telegram_logger.send_telegram_log", lambda msg, tag=None: logs.append(msg))

    update_sl("BTCUSDT", 29000.5)
    assert any("SL flyttad till 29000.5" in log for log in logs)

def test_trailing_stop_activates(monkeypatch):
    logs = []
    monkeypatch.setattr("utils.telegram_logger.send_telegram_log", lambda msg, tag=None: logs.append(msg))

    monitor_trailing_stop("ETHUSDT", 2000, trail_percent=0.5)
    assert any("Trailing Stop aktiverad" in log for log in logs)