import re
from typing import Dict, Optional, List
from config.settings import TelegramConfig, OverrideConfig
from utils.telegram_logger import send_telegram_log, send_group_specific_log
from datetime import datetime, timedelta
from signal_module.multi_format_parser import parse_signal

# ========================
# SignalTracker & parserfunktioner
# ========================

class SignalTracker:
    def __init__(self, coin=None, direction=None, leverage=None, group_name=None):
        self.coin = coin
        self.direction = direction
        self.leverage = leverage
        self.group_name = group_name
        self.timestamp = datetime.now()

    def get_signal(self):
        if self.coin and self.direction and self.leverage:
            return {
                "symbol": self.coin,
                "direction": self.direction,
                "leverage": self.leverage,
                "group_name": self.group_name,
                "timestamp": self.timestamp.isoformat()
            }
        return None

# ========================
# SignalHandler – Enhanced for multi-group support
# ========================

class SignalHandler:
    def __init__(self):
        self.active_signals: Dict[str, List[Dict]] = {}  # group_name -> list of signals
        self.signal_stats: Dict[str, Dict] = {}  # group_name -> stats
        print("✅ SignalHandler initialized with multi-group support")

    def add_signal(self, signal_data: Dict):
        """Add a signal to the handler with group tracking."""
        group_name = signal_data.get("group_name", "unknown")
        
        if group_name not in self.active_signals:
            self.active_signals[group_name] = []
            self.signal_stats[group_name] = {
                "total_signals": 0,
                "successful_parses": 0,
                "failed_parses": 0,
                "last_signal_time": None
            }
        
        self.active_signals[group_name].append(signal_data)
        self.signal_stats[group_name]["total_signals"] += 1
        self.signal_stats[group_name]["last_signal_time"] = datetime.now()
        
        print(f"📨 Signal added from {group_name}: {signal_data.get('symbol', 'Unknown')}")

    def get_signals_by_group(self, group_name: str) -> List[Dict]:
        """Get all signals from a specific group."""
        return self.active_signals.get(group_name, [])

    def get_group_stats(self, group_name: str) -> Dict:
        """Get statistics for a specific group."""
        return self.signal_stats.get(group_name, {})

    def get_all_group_stats(self) -> Dict[str, Dict]:
        """Get statistics for all groups."""
        return self.signal_stats

    def clear_group_signals(self, group_name: str):
        """Clear all signals from a specific group."""
        if group_name in self.active_signals:
            self.active_signals[group_name] = []
            print(f"🗑️ Cleared signals for {group_name}")

from signal_module.signal_queue import signal_queue

def get_active_signal():
    try:
        return signal_queue.get_nowait()
    except:
        return None

# ========================
# Signal Inversion Logic
# ========================

async def invert_signal_if_enabled(signal_data: Dict) -> Dict:
    """
    Invert signal side if ENABLE_SIGNAL_INVERSION is enabled.
    
    Args:
        signal_data: Original signal data
        
    Returns:
        Modified signal data with inverted side if enabled
    """
    if not OverrideConfig.ENABLE_SIGNAL_INVERSION:
        return signal_data
    
    # Check if signal has a side to invert
    if "side" not in signal_data or signal_data["side"] is None:
        return signal_data
    
    original_side = signal_data["side"]
    
    # Invert the side
    if original_side.upper() == "LONG":
        signal_data["side"] = "SHORT"
        inverted_side = "SHORT"
    elif original_side.upper() == "SHORT":
        signal_data["side"] = "LONG"
        inverted_side = "LONG"
    else:
        # Unknown side, don't invert
        return signal_data
    
    # Add inversion metadata
    signal_data["is_inverted"] = True
    signal_data["original_side"] = original_side
    
    # Log the inversion
    symbol = signal_data.get("symbol", "Unknown")
    group_name = signal_data.get("group_name", "unknown")
    
    log_message = f"[Signal Inversion] {symbol} signal flipped: {original_side} → {inverted_side}"
    
    await send_group_specific_log(
        group_name,
        log_message,
        tag="inversion"
    )
    
    print(f"🔄 {log_message}")
    
    return signal_data

# Global signal handler instance
signal_handler = SignalHandler()

# Ensure SignalHandler class is instantiated
if __name__ == '__main__':
    handler = SignalHandler()

# Force SignalHandler init execution
if __name__ == '__main__':
    h = SignalHandler()

# Enhanced functions for multi-group support
async def handle_incoming_signal(signal_data: Dict):
    """Handle incoming signals with group tracking and inversion."""
    group_name = signal_data.get("group_name", "unknown")
    
    # Apply signal inversion if enabled
    signal_data = await invert_signal_if_enabled(signal_data)
    
    # Add to signal handler
    signal_handler.add_signal(signal_data)
    
    # Log the signal
    symbol = signal_data.get("symbol", "Unknown")
    side = signal_data.get("side", "Unknown")
    is_inverted = signal_data.get("is_inverted", False)
    
    log_message = f"Signal processed: {symbol} {side}"
    if is_inverted:
        log_message += " (INVERTED)"
    
    await send_group_specific_log(
        group_name,
        log_message,
        tag="signal"
    )
    
    print(f"📨 Incoming signal from {group_name}: {signal_data}")
    return {"status": "processed", "group_name": group_name, "is_inverted": is_inverted}

def match_signal_update(signal_text: str, group_name: str = None):
    """Match signal updates with group context."""
    print(f"🔍 Matching signal from {group_name}: {signal_text}")
    return None

def parse_partial_close(signal_text: str, group_name: str = None):
    """Parse partial close signals with group context."""
    print(f"📝 Parse partial close from {group_name}: {signal_text}")
    return None

async def start_trade_from_incomplete_signal(signal_data: Dict):
    """Start trades from incomplete signals with group tracking."""
    group_name = signal_data.get("group_name", "unknown")
    print(f"🚀 Start incomplete trade from {group_name}: {signal_data}")
    return {"status": "started", "group_name": group_name}

async def get_group_performance_report(group_name: str = None):
    """Generate performance report for specific group or all groups."""
    if group_name:
        stats = signal_handler.get_group_stats(group_name)
        return {group_name: stats}
    else:
        return signal_handler.get_all_group_stats()

