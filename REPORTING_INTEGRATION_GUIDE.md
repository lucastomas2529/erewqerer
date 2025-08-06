# Reporting System Integration Guide

## Overview

The reporting system provides comprehensive logging, monitoring, and reporting capabilities for the trading bot. This guide explains how to integrate it into the main trading system and resolve any issues.

## Features

- **Real-time Logging**: Logs trades, signals, and errors with detailed metadata
- **Database Storage**: SQLite database for persistent data storage
- **In-memory Statistics**: Fast access to current trading statistics
- **Telegram Notifications**: Real-time alerts for important events
- **Daily/Weekly Reports**: Comprehensive performance summaries
- **JSON Export**: Structured data export for analysis

## Integration Steps

### 1. Import the Reporting System

Add to your main files:

```python
from core.reporting_system import reporting_system
```

### 2. Initialize the Database

Add to your startup code:

```python
# In runner/main.py or startup.py
async def initialize_system():
    # Initialize reporting system
    await reporting_system.initialize_database()
    print("✅ Reporting system initialized")
```

### 3. Integrate with Signal Processing

Update your signal listener to log signals:

```python
# In signal_module/listener.py
async def handle_signal_message(message, group_name):
    # ... existing signal processing ...
    
    # Log the signal
    await reporting_system.log_signal({
        'group_name': group_name,
        'signal_text': signal_text,
        'parsed_data': parsed_data,
        'processing_time': processing_time,
        'status': 'processed'
    })
```

### 4. Integrate with Trade Execution

Update your trade execution to log trades:

```python
# In monitor/loop_manager.py or core/entry_manager.py
async def execute_trade(signal_data):
    # ... existing trade execution ...
    
    # Log the trade
    await reporting_system.log_trade({
        'symbol': symbol,
        'side': side,
        'quantity': quantity,
        'entry_price': entry_price,
        'sl_price': sl_price,
        'tp_prices': tp_prices,
        'order_ids': order_ids,
        'group_name': group_name,
        'signal_source': signal_source,
        'processing_time': processing_time,
        'admin_command': False
    })
```

### 5. Integrate with Error Handling

Update your error handling to log errors:

```python
# In any error handling block
try:
    # ... your code ...
except Exception as e:
    await reporting_system.log_error({
        'error_type': 'trade_execution',
        'error_message': str(e),
        'context': {
            'symbol': symbol,
            'side': side,
            'group_name': group_name
        },
        'severity': 'high'
    })
``` 