#!/usr/bin/env python3
"""
Dynamic Strategy Control System.
Handles per-group, per-symbol, per-timeframe strategy overrides.
"""

from typing import Dict, Any, Optional
from config.settings import STRATEGY_OVERRIDES, OverrideConfig
from utils.logger import log_event

def is_strategy_enabled(
    strategy: str, 
    symbol: str, 
    group: str, 
    timeframe: str = "default"
) -> bool:
    """
    Check if a specific strategy is enabled for the given parameters.
    
    Args:
        strategy: Strategy name (e.g., "ENABLE_TP", "ENABLE_SL", "ENABLE_REENTRY")
        symbol: Trading symbol (e.g., "BTCUSDT", "ETHUSDT")
        group: Signal group name (e.g., "cryptoraketen", "smart_crypto_signals")
        timeframe: Timeframe (e.g., "5m", "1h", "4h", "1d")
        
    Returns:
        bool: True if strategy is enabled, False otherwise
    """
    try:
        # Get the default value from OverrideConfig
        default_value = getattr(OverrideConfig, strategy, True)
        
        # Check for specific override
        override_value = _get_strategy_override(strategy, symbol, group, timeframe)
        
        if override_value is not None:
            # Log the override
            status = "ENABLED" if override_value else "DISABLED"
            log_event(
                f"[StrategyOverride] {status}: {strategy} for {symbol} "
                f"(group={group}, tf={timeframe})",
                "INFO"
            )
            return override_value
        
        # Return default value if no override found
        return default_value
        
    except Exception as e:
        log_event(f"[ERROR] Failed to check strategy {strategy}: {e}", "ERROR")
        # Return True as safe default
        return True

def _get_strategy_override(
    strategy: str, 
    symbol: str, 
    group: str, 
    timeframe: str
) -> Optional[bool]:
    """
    Get strategy override value from the configuration hierarchy.
    
    Args:
        strategy: Strategy name
        symbol: Trading symbol
        group: Signal group name
        timeframe: Timeframe
        
    Returns:
        Optional[bool]: Override value if found, None otherwise
    """
    try:
        # Check if group exists in overrides
        if group not in STRATEGY_OVERRIDES:
            return None
        
        group_overrides = STRATEGY_OVERRIDES[group]
        
        # Check for symbol-specific overrides
        if symbol in group_overrides:
            symbol_overrides = group_overrides[symbol]
            
            # Check for timeframe-specific override
            if timeframe in symbol_overrides:
                timeframe_overrides = symbol_overrides[timeframe]
                if strategy in timeframe_overrides:
                    return timeframe_overrides[strategy]
            
            # Check for default timeframe override
            if "default" in symbol_overrides:
                default_overrides = symbol_overrides["default"]
                if strategy in default_overrides:
                    return default_overrides[strategy]
        
        # Check for default symbol override
        if "default" in group_overrides:
            default_symbol_overrides = group_overrides["default"]
            
            # Check for timeframe-specific override in default symbol
            if timeframe in default_symbol_overrides:
                default_timeframe_overrides = default_symbol_overrides[timeframe]
                if strategy in default_timeframe_overrides:
                    return default_timeframe_overrides[strategy]
            
            # Check for default timeframe in default symbol
            if "default" in default_symbol_overrides:
                default_overrides = default_symbol_overrides["default"]
                if strategy in default_overrides:
                    return default_overrides[strategy]
        
        return None
        
    except Exception as e:
        log_event(f"[ERROR] Failed to get strategy override: {e}", "ERROR")
        return None

def get_all_strategy_overrides(
    symbol: str, 
    group: str, 
    timeframe: str = "default"
) -> Dict[str, bool]:
    """
    Get all strategy overrides for the given parameters.
    
    Args:
        symbol: Trading symbol
        group: Signal group name
        timeframe: Timeframe
        
    Returns:
        Dict[str, bool]: Dictionary of strategy names and their enabled status
    """
    strategies = [
        "ENABLE_TP",
        "ENABLE_SL", 
        "ENABLE_TRAILING_STOP",
        "ENABLE_BREAK_EVEN",
        "ENABLE_REENTRY",
        "ENABLE_PYRAMIDING"
    ]
    
    overrides = {}
    for strategy in strategies:
        overrides[strategy] = is_strategy_enabled(strategy, symbol, group, timeframe)
    
    return overrides

def log_strategy_status(
    symbol: str, 
    group: str, 
    timeframe: str = "default"
):
    """
    Log the status of all strategies for the given parameters.
    
    Args:
        symbol: Trading symbol
        group: Signal group name
        timeframe: Timeframe
    """
    try:
        overrides = get_all_strategy_overrides(symbol, group, timeframe)
        
        log_event(
            f"[StrategyStatus] {symbol} ({group}, {timeframe}): "
            f"{', '.join([f'{k}={v}' for k, v in overrides.items()])}",
            "INFO"
        )
        
    except Exception as e:
        log_event(f"[ERROR] Failed to log strategy status: {e}", "ERROR")

def validate_strategy_overrides() -> bool:
    """
    Validate that all strategy overrides in configuration are valid.
    
    Returns:
        bool: True if all overrides are valid, False otherwise
    """
    try:
        valid_strategies = {
            "ENABLE_TP",
            "ENABLE_SL", 
            "ENABLE_TRAILING_STOP",
            "ENABLE_BREAK_EVEN",
            "ENABLE_REENTRY",
            "ENABLE_PYRAMIDING"
        }
        
        for group, group_overrides in STRATEGY_OVERRIDES.items():
            for symbol, symbol_overrides in group_overrides.items():
                for timeframe, timeframe_overrides in symbol_overrides.items():
                    for strategy, value in timeframe_overrides.items():
                        # Check if strategy name is valid
                        if strategy not in valid_strategies:
                            log_event(
                                f"[ERROR] Invalid strategy name in override: {strategy}",
                                "ERROR"
                            )
                            return False
                        
                        # Check if value is boolean
                        if not isinstance(value, bool):
                            log_event(
                                f"[ERROR] Invalid strategy value for {strategy}: {value} (must be bool)",
                                "ERROR"
                            )
                            return False
        
        log_event("[StrategyControl] All strategy overrides validated successfully", "INFO")
        return True
        
    except Exception as e:
        log_event(f"[ERROR] Failed to validate strategy overrides: {e}", "ERROR")
        return False

def get_override_hierarchy(
    symbol: str, 
    group: str, 
    timeframe: str = "default"
) -> Dict[str, Any]:
    """
    Get the complete override hierarchy for debugging purposes.
    
    Args:
        symbol: Trading symbol
        group: Signal group name
        timeframe: Timeframe
        
    Returns:
        Dict[str, Any]: Complete override hierarchy
    """
    hierarchy = {
        "group": group,
        "symbol": symbol,
        "timeframe": timeframe,
        "overrides": {},
        "applied_from": {}
    }
    
    strategies = [
        "ENABLE_TP",
        "ENABLE_SL", 
        "ENABLE_TRAILING_STOP",
        "ENABLE_BREAK_EVEN",
        "ENABLE_REENTRY",
        "ENABLE_PYRAMIDING"
    ]
    
    for strategy in strategies:
        # Get the override value and track where it came from
        override_value = _get_strategy_override(strategy, symbol, group, timeframe)
        default_value = getattr(OverrideConfig, strategy, True)
        
        if override_value is not None:
            hierarchy["overrides"][strategy] = override_value
            hierarchy["applied_from"][strategy] = f"{group}/{symbol}/{timeframe}"
        else:
            hierarchy["overrides"][strategy] = default_value
            hierarchy["applied_from"][strategy] = "default"
    
    return hierarchy 