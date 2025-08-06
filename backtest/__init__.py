"""
Backtest framework for simulating trade signals through the entire system.
"""

from .runner import BacktestRunner
from .mock_data import generate_test_signals

__all__ = ['BacktestRunner', 'generate_test_signals'] 