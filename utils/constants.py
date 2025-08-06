
# utils/constants.py
# 
# ⚠️  DEPRECATED: All constants moved to config/settings.py
# This file now imports from centralized configuration.

from config.settings import (
    SUPPORTED_SYMBOLS as BITGET_SYMBOLS,
    MAX_LEVERAGE,
    RISK_PER_TRADE,
    FALLBACK_SL_PERCENTAGE,
    TP_LEVELS,
    LEVERAGE_BOOST_THRESHOLD,
    ENTRY_SL_OFFSET,
    FALLBACK_SL_OFFSET,
    TradingConfig
)

# Convert TP_LEVELS to old PYRAMIDING_THRESHOLDS format for backward compatibility
PYRAMIDING_THRESHOLDS = {
    "tp1": TradingConfig.TP_LEVELS[0] / 100,  # Convert % to decimal
    "tp2": TradingConfig.TP_LEVELS[1] / 100,
    "tp3": TradingConfig.TP_LEVELS[2] / 100,
    "tp4": TradingConfig.TP_LEVELS[3] / 100
}

ENABLE_TRAILING_AFTER = TradingConfig.ENABLE_TRAILING_AFTER

# Order settings for trading operations
ORDER_SETTINGS = {
    "order_type": "limit",
    "time_in_force": "GTC",  # Good Till Cancelled
    "reduce_only": False,
    "post_only": True,  # Use post-only orders by default
    "base_price_type": "LastPrice"
}

# Breakeven settings
BE_TRIGGER_THRESHOLD = TradingConfig.BREAK_EVEN_TRIGGER  # 0.5%
BE_OFFSET_PCT = 0.1  # Break-even offset percentage
