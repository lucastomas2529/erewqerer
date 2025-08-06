# 🤖 Advanced Crypto Trading Bot

A sophisticated automated cryptocurrency trading bot with real-time signal processing, advanced risk management, and comprehensive monitoring systems.

## 🚀 **Features**

### ✅ **Core Trading System**
- **Real-time Signal Processing** - Monitors up to 20 Telegram groups simultaneously
- **Multi-format Signal Parsing** - Supports various signal formats with confidence scoring
- **Dual-step Entry Strategy** - Places LIMIT orders in two steps (50/50 distribution)
- **Market Order Fallback** - Automatic fallback to market orders if LIMIT orders fail
- **Risk Management** - Position sizing based on risk percentage and leverage
- **Exchange Integration** - Unified API for Bitget and Bybit with rate limiting

### ✅ **Advanced Risk Management**
- **Break-even Protection** - Automatically moves SL to break-even after TP2 or profit threshold
- **Trailing Stop System** - Dynamic trailing stops that "ride to heaven" as price moves favorably
- **Timeout Protection** - Auto-closes trades after 4 hours if no exit occurs
- **Order Management** - Comprehensive order cancellation and modification
- **PnL Tracking** - Real-time profit/loss calculation and logging

### ✅ **Monitoring & Logging**
- **Real-time Monitoring** - Concurrent monitoring of all active trades
- **Telegram Notifications** - Instant alerts for trade events and system status
- **Comprehensive Logging** - Detailed logs for debugging and analysis
- **Error Handling** - Robust error handling with graceful degradation
- **System Health Monitoring** - Continuous monitoring of bot performance

## 📁 **Project Structure**

```
tg trading bot/
├── core/                          # Core trading logic
│   ├── api.py                     # Unified exchange API wrapper
│   ├── exchange_api.py            # Exchange-specific API implementation
│   ├── entry_manager.py           # Entry strategy and order placement
│   ├── breakeven_manager.py       # Break-even protection system
│   ├── trailing_manager.py        # Trailing stop management
│   └── timeout_manager.py         # Timeout protection system
├── signal_module/                 # Signal processing
│   ├── listener.py                # Telegram message listener
│   ├── multi_format_parser.py     # Multi-format signal parsing
│   ├── spam_filter.py             # Message filtering and preprocessing
│   └── group_monitor.py           # Group monitoring and statistics
├── monitor/                       # Trade monitoring
│   ├── loop_manager.py            # Main trading loop
│   └── trade_state.py             # Trade state management
├── config/                        # Configuration
│   └── settings.py                # Centralized configuration
├── runner/                        # Bot execution
│   ├── main.py                    # Main entry point
│   └── startup.py                 # Startup procedures
├── utils/                         # Utilities
│   ├── logger.py                  # Logging system
│   └── telegram_logger.py         # Telegram notification system
└── tests/                         # Testing and demos
    ├── test_timeout_system.py     # Timeout system tests
    ├── demo_timeout_system.py     # Timeout system demo
    └── test_api_integration.py    # API integration tests
```

## 🛠️ **Installation**

### Prerequisites
- Python 3.8+
- Telegram Bot Token
- Exchange API credentials (Bitget/Bybit)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd tg-trading-bot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_template.txt .env
# Edit .env with your API credentials
```

### Environment Variables
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Exchange API Keys
BITGET_API_KEY=your_bitget_key
BITGET_API_SECRET=your_bitget_secret
BITGET_API_PASSPHRASE=your_bitget_passphrase

BYBIT_API_KEY=your_bybit_key
BYBIT_API_SECRET=your_bybit_secret
```

## ⚙️ **Configuration**

### Trading Parameters (`config/settings.py`)
```python
# Risk Management
RISK_PERCENT = 2.0                 # Risk percentage per trade
LEVERAGE_CAP = 50                  # Maximum leverage allowed
TIMEOUT_HOURS = 4.0               # Auto-close trades after 4 hours

# Break-even Protection
BREAKEVEN_THRESHOLD = 2.0         # Profit % to trigger break-even
BREAKEVEN_BUFFER = 0.001          # Break-even buffer (0.1% above entry)

# Trailing Stop Configuration
TRAILING_THRESHOLD = 3.0          # Profit % to activate trailing
TRAILING_DISTANCE = 0.01          # Trailing distance (1% from current price)
TRAILING_STEP = 0.005             # Minimum step size for trailing updates
```

## 🚀 **Usage**

### Start the Bot
```bash
# Run the main trading bot
python runner/main.py

# Or run with specific configuration
python -c "from runner.main import main; import asyncio; asyncio.run(main())"
```

### Testing Individual Components
```bash
# Test timeout protection system
python test_timeout_system.py

# Test API integration
python test_api_integration.py

# Demo timeout system
python demo_timeout_system.py
```

## 📊 **Signal Processing**

### Supported Signal Formats
The bot supports multiple signal formats:

```
# Format 1: Standard
BTCUSDT LONG Entry: 67000 SL: 65000 TP: 68000, 69000, 70000

# Format 2: Compact
BTC LONG 67000 SL 65000 TP 68000 69000 70000

# Format 3: With targets
BNB Position: LONG Open: 620 Exit: 640,660 Cut: 610

# Format 4: Simple
ETHUSDT BUY @ 3750 SL: 3650 TP: 3900
```

### Signal Parsing Features
- **Multi-format Support** - Handles various signal formats
- **Confidence Scoring** - Rates signal quality and completeness
- **Fallback Logic** - Calculates missing SL/TP levels
- **Symbol Translation** - Converts various symbol formats
- **Spam Filtering** - Filters out irrelevant messages

## 🔄 **Trading Workflow**

### 1. Signal Reception
- Monitors up to 20 Telegram groups simultaneously
- Filters and preprocesses incoming messages
- Parses signals with confidence scoring

### 2. Entry Execution
- Calculates position size based on risk percentage
- Places dual LIMIT orders (50/50 distribution)
- Falls back to market orders if needed
- Sets initial SL and TP levels

### 3. Risk Management
- **Break-even Protection**: Moves SL to break-even after TP2 or profit threshold
- **Trailing Stops**: Dynamic trailing that follows price movement
- **Timeout Protection**: Auto-closes trades after 4 hours

### 4. Monitoring
- Real-time monitoring of all active trades
- Continuous SL/TP adjustments
- Comprehensive logging and notifications

## 🛡️ **Risk Management Systems**

### Break-even Protection
- Automatically moves stop-loss to break-even
- Triggers after TP2 or configurable profit threshold
- Includes buffer above entry price for safety

### Trailing Stop System
- Activates after reaching profit threshold
- Dynamically adjusts SL to follow price movement
- "Rides to heaven" as price moves favorably
- Configurable trailing distance and step size

### Timeout Protection
- Tracks trade duration using timestamps
- Auto-closes trades after 4 hours (configurable)
- Cancels existing orders before closure
- Places market orders to close positions
- Calculates and logs final PnL

## 📈 **Monitoring & Analytics**

### Real-time Monitoring
- **Trade Status**: Real-time status of all active trades
- **Duration Tracking**: Time elapsed since trade entry
- **PnL Calculation**: Current profit/loss for each trade
- **System Health**: Overall bot performance metrics

### Telegram Notifications
- **Trade Events**: Entry, exit, SL/TP hits
- **System Alerts**: Errors, warnings, status updates
- **Performance Reports**: Daily/weekly performance summaries
- **Health Checks**: System status and monitoring reports

## 🧪 **Testing**

### Comprehensive Test Suite
```bash
# Test timeout protection
python test_timeout_system.py

# Test API integration
python test_api_integration.py

# Test signal parsing
python signal_module/enhanced_mock_tester.py

# Demo complete workflow
python demo_timeout_system.py
```

### Test Coverage
- ✅ **Timeout Protection** - Trade auto-closure after 4 hours
- ✅ **Break-even Logic** - SL movement to break-even
- ✅ **Trailing Stops** - Dynamic SL adjustments
- ✅ **Signal Parsing** - Multi-format signal processing
- ✅ **API Integration** - Exchange API functionality
- ✅ **Error Handling** - Robust error management

## 🔧 **Advanced Configuration**

### Conservative Trading (Lower Risk)
```python
TIMEOUT_HOURS = 2.0               # Auto-close after 2 hours
RISK_PERCENT = 1.0                # 1% risk per trade
TRAILING_THRESHOLD = 5.0          # Activate trailing at 5% profit
```

### Aggressive Trading (Higher Risk)
```python
TIMEOUT_HOURS = 6.0               # Auto-close after 6 hours
RISK_PERCENT = 3.0                # 3% risk per trade
TRAILING_THRESHOLD = 2.0          # Activate trailing at 2% profit
```

### Balanced Trading (Recommended)
```python
TIMEOUT_HOURS = 4.0               # Auto-close after 4 hours
RISK_PERCENT = 2.0                # 2% risk per trade
TRAILING_THRESHOLD = 3.0          # Activate trailing at 3% profit
```

## 📋 **Dependencies**

### Core Dependencies
```
asyncio>=3.4.3
telethon>=1.28.5
ccxt>=4.0.0
python-dotenv>=1.0.0
aiohttp>=3.8.0
```

### Optional Dependencies
```
pandas>=1.5.0          # Data analysis
numpy>=1.24.0          # Numerical operations
matplotlib>=3.6.0      # Chart generation
```

## 🚨 **Important Notes**

### Security
- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use .env file for sensitive data
- **Test Mode**: Always test with small amounts first
- **Monitoring**: Monitor bot performance continuously

### Risk Disclaimer
- **Cryptocurrency trading involves substantial risk**
- **Past performance does not guarantee future results**
- **Only trade with funds you can afford to lose**
- **This bot is for educational purposes**

### Best Practices
- **Start Small**: Begin with small position sizes
- **Monitor Closely**: Watch bot performance regularly
- **Test Thoroughly**: Test all features before live trading
- **Backup Data**: Regularly backup configuration and logs

## 🤝 **Contributing**

### Development Setup
```bash
# Fork the repository
git clone <your-fork-url>
cd tg-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

### Code Style
- Follow PEP 8 guidelines
- Add comprehensive docstrings
- Include type hints
- Write unit tests for new features

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Telethon** - Telegram client library
- **CCXT** - Unified cryptocurrency trading API
- **Asyncio** - Asynchronous programming support
- **Python Community** - Excellent documentation and support

## 📞 **Support**

For support and questions:
- **Issues**: Create an issue on GitHub
- **Documentation**: Check the inline code documentation
- **Testing**: Run the test suite for troubleshooting

---

**🚀 Ready for production trading with advanced risk management and comprehensive monitoring!**