#!/usr/bin/env python3
"""
Mock data generator for backtest signals.
Generates realistic test signals for backtesting the trading system.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class MockSignal:
    """Mock signal data structure."""
    timestamp: str
    group_name: str
    symbol: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit: List[float]
    leverage: int
    message_text: str
    message_id: int

def generate_realistic_price(base_price: float, volatility: float = 0.02) -> float:
    """Generate realistic price with volatility."""
    change = random.uniform(-volatility, volatility)
    return base_price * (1 + change)

def generate_test_signals(
    num_signals: int = 100,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    symbols: List[str] = None,
    groups: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate realistic test signals for backtesting.
    
    Args:
        num_signals: Number of signals to generate
        start_date: Start date for signal generation
        end_date: End date for signal generation
        symbols: List of symbols to use (default: common crypto pairs)
        groups: List of group names to use (default: configured groups)
        
    Returns:
        List of signal dictionaries
    """
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    
    if groups is None:
        groups = ["cryptoraketen", "smart_crypto_signals", "own_channel"]
    
    # Base prices for symbols
    base_prices = {
        "BTCUSDT": 64000,
        "ETHUSDT": 3200,
        "SOLUSDT": 100,
        "XRPUSDT": 0.5,
        "ADAUSDT": 0.4,
        "DOGEUSDT": 0.08,
        "AVAXUSDT": 35,
        "DOTUSDT": 7,
        "LINKUSDT": 15,
        "MATICUSDT": 0.8
    }
    
    signals = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    for i in range(num_signals):
        # Generate random timestamp within date range
        days_diff = (end_dt - start_dt).days
        random_days = random.randint(0, days_diff)
        timestamp = start_dt + timedelta(days=random_days)
        timestamp = timestamp.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Select random symbol and group
        symbol = random.choice(symbols)
        group_name = random.choice(groups)
        side = random.choice(["LONG", "SHORT"])
        
        # Generate realistic prices
        base_price = base_prices.get(symbol, 100)
        entry_price = generate_realistic_price(base_price)
        
        # Generate SL and TP based on side
        if side == "LONG":
            sl_distance = random.uniform(0.01, 0.03)  # 1-3% below entry
            tp1_distance = random.uniform(0.015, 0.025)  # 1.5-2.5% above entry
            tp2_distance = random.uniform(0.03, 0.05)   # 3-5% above entry
            tp3_distance = random.uniform(0.06, 0.10)   # 6-10% above entry
            tp4_distance = random.uniform(0.10, 0.15)   # 10-15% above entry
            
            stop_loss = entry_price * (1 - sl_distance)
            take_profit = [
                entry_price * (1 + tp1_distance),
                entry_price * (1 + tp2_distance),
                entry_price * (1 + tp3_distance),
                entry_price * (1 + tp4_distance)
            ]
        else:  # SHORT
            sl_distance = random.uniform(0.01, 0.03)  # 1-3% above entry
            tp1_distance = random.uniform(0.015, 0.025)  # 1.5-2.5% below entry
            tp2_distance = random.uniform(0.03, 0.05)   # 3-5% below entry
            tp3_distance = random.uniform(0.06, 0.10)   # 6-10% below entry
            tp4_distance = random.uniform(0.10, 0.15)   # 10-15% below entry
            
            stop_loss = entry_price * (1 + sl_distance)
            take_profit = [
                entry_price * (1 - tp1_distance),
                entry_price * (1 - tp2_distance),
                entry_price * (1 - tp3_distance),
                entry_price * (1 - tp4_distance)
            ]
        
        # Generate leverage
        leverage = random.choice([10, 20, 25, 50])
        
        # Generate message text
        message_text = f"#{symbol} {side} Entry: {entry_price:.2f} SL: {stop_loss:.2f} TP1: {take_profit[0]:.2f} TP2: {take_profit[1]:.2f} TP3: {take_profit[2]:.2f} TP4: {take_profit[3]:.2f}"
        
        # Create signal
        signal = MockSignal(
            timestamp=timestamp.isoformat(),
            group_name=group_name,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            leverage=leverage,
            message_text=message_text,
            message_id=i + 1
        )
        
        signals.append(asdict(signal))
    
    # Sort signals by timestamp
    signals.sort(key=lambda x: x["timestamp"])
    
    return signals

def generate_historical_signals_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load historical signals from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing historical signals
        
    Returns:
        List of signal dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        # Validate signal structure
        required_fields = ["timestamp", "group_name", "symbol", "side", "entry_price"]
        for signal in signals:
            for field in required_fields:
                if field not in signal:
                    raise ValueError(f"Signal missing required field: {field}")
        
        return signals
    except FileNotFoundError:
        print(f"⚠️ Historical signals file not found: {file_path}")
        print("   Generating mock signals instead...")
        return generate_test_signals()
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file: {e}")
        print("   Generating mock signals instead...")
        return generate_test_signals()
    except Exception as e:
        print(f"❌ Error loading historical signals: {e}")
        print("   Generating mock signals instead...")
        return generate_test_signals()

def save_test_signals(signals: List[Dict[str, Any]], file_path: str):
    """
    Save test signals to a JSON file.
    
    Args:
        signals: List of signal dictionaries
        file_path: Path to save the signals
    """
    try:
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test signals saved to: {file_path}")
        print(f"   Total signals: {len(signals)}")
    except Exception as e:
        print(f"❌ Error saving test signals: {e}")

def generate_scenario_signals(scenario: str = "mixed") -> List[Dict[str, Any]]:
    """
    Generate signals for specific testing scenarios.
    
    Args:
        scenario: Scenario type ("bull", "bear", "mixed", "volatile", "trending")
        
    Returns:
        List of signal dictionaries
    """
    if scenario == "bull":
        # Mostly long signals with upward bias
        signals = generate_test_signals(num_signals=50)
        for signal in signals:
            signal["side"] = "LONG"
            # Increase entry prices over time
            signal["entry_price"] *= (1 + random.uniform(0.001, 0.005))
        return signals
    
    elif scenario == "bear":
        # Mostly short signals with downward bias
        signals = generate_test_signals(num_signals=50)
        for signal in signals:
            signal["side"] = "SHORT"
            # Decrease entry prices over time
            signal["entry_price"] *= (1 - random.uniform(0.001, 0.005))
        return signals
    
    elif scenario == "volatile":
        # High volatility scenario
        signals = generate_test_signals(num_signals=100)
        for signal in signals:
            # Add more volatility to prices
            signal["entry_price"] = generate_realistic_price(signal["entry_price"], volatility=0.05)
        return signals
    
    elif scenario == "trending":
        # Trending market scenario
        signals = generate_test_signals(num_signals=80)
        trend_direction = random.choice([1, -1])
        for i, signal in enumerate(signals):
            # Add trend component
            trend_factor = 1 + (trend_direction * 0.001 * i)
            signal["entry_price"] *= trend_factor
        return signals
    
    else:  # "mixed"
        # Default mixed scenario
        return generate_test_signals(num_signals=100)

if __name__ == "__main__":
    # Generate and save test signals
    print("🧪 Generating test signals...")
    
    # Create different scenarios
    scenarios = ["mixed", "bull", "bear", "volatile", "trending"]
    
    for scenario in scenarios:
        signals = generate_scenario_signals(scenario)
        file_path = f"data/test_signals_{scenario}.json"
        save_test_signals(signals, file_path)
    
    print("✅ All test signal files generated!") 