import os
try:
    from pybit.unified_trading import HTTP
except ImportError:
    HTTP = None  # Fallback for missing pybit dependency

# ================================================================================================
# 🎯 CENTRALIZED TRADING BOT CONFIGURATION
# ================================================================================================
# All configuration values are defined here. No hardcoded values should exist in other files.

class TradingConfig:
    """
    Centralized configuration class for all trading bot settings.
    All modules should import values from this class only.
    """
    
    # === 📐 CORE TRADING PARAMETERS ===
    DEFAULT_IM = 20.0                    # Initial Margin (USDT)
    RISK_PERCENT = 2.0                   # Risk percentage per trade
    LEVERAGE_CAP = 50                    # Maximum leverage allowed
    SL_PCT = 1.5                         # Stop Loss percentage
    TP_LEVELS = [1.5, 3.0, 6.0, 10.0]   # Take Profit levels (%)
    BREAK_EVEN_TRIGGER = 0.5             # Break-even trigger threshold (%)
    TRAILING_TRIGGER = 6.0               # Trailing stop trigger threshold (%)
    TRAILING_OFFSET = 0.5                # Trailing stop offset (%)
    AUTO_CLOSE_TIMEOUT = 14400           # Auto-close timeout (4 hours in seconds)
    ENABLE_REVERSE = True                # Enable reverse trading logic
    
    # === 🔧 ADVANCED TRADING SETTINGS ===
    DEFAULT_LEVERAGE = 10
    DEFAULT_BALANCE = 401.2
    DEFAULT_SL_OFFSET_PCT = 1.5          # Fallback SL if signal missing SL
    MIN_SL_DISTANCE = 0.003              # Minimum SL distance (0.3%)
    FALLBACK_SL_DISTANCE = 0.003         # Fallback SL distance
    BREAKEVEN_BUFFER = 0.0015            # Break-even buffer (0.15%)
    DEFAULT_SL_BUFFER = 0.001            # Default stop loss buffer (0.1%)
    
    # === 🏗️ PYRAMIDING CONFIGURATION ===
    MAX_PYRAMID_STEPS = 2                 # Maximum number of pyramiding steps allowed
    PYRAMID_POL_THRESHOLDS = [1.5, 3.0]   # Profit thresholds for pyramiding steps (%)
    PYRAMID_STEP_SIZE = 0.25              # Size of each pyramid step (25% of original position)
    PYRAMID_MIN_POL = 1.0                 # Minimum PoL required before pyramiding (%)
    PYRAMID_MAX_PRICE_DEVIATION = 2.0     # Maximum price deviation from entry for pyramiding (%)
    
    PYRAMID_STEPS = {
        "level_1": {
            "trigger_pol": 2.5,           # Profit trigger for level 1 (%)
            "topup_im": 20,               # Additional IM for level 1
            "adjust_leverage_to_max": True,
            "min_sl_to_raise_leverage": 0.0015
        },
        "level_2": {
            "trigger_pol": 4.0,           # Profit trigger for level 2 (%)
            "topup_im": 40                # Additional IM for level 2
        },
        "level_3": {
            "trigger_pol": 6.0,           # Profit trigger for level 3 (%)
            "topup_im": 100               # Additional IM for level 3
        }
    }
    
    # === 🛡️ RISK MANAGEMENT ===
    RISK_PER_TRADE = 0.01                # 1% risk per trade
    FALLBACK_SL_PERCENTAGE = 0.015       # 1.5% fallback SL
    LEVERAGE_BOOST_THRESHOLD = 0.025     # 2.5% threshold for leverage boost
    ENTRY_SL_OFFSET = 0.0015             # 0.15% entry SL offset
    FALLBACK_SL_OFFSET = 0.003           # 0.3% fallback SL offset
    HEDGE_TRIGGER_DRAWDOWN = 0.02        # 2% drawdown to trigger hedge
    HEDGE_SL_DISTANCE = 0.0015           # Hedge SL distance
    
    # === 🔄 REENTRY & TRAILING ===
    REENTRY_ENABLED = True               # Enable automatic re-entry functionality
    REENTRY_MAX_ATTEMPTS = 2             # Maximum re-entry attempts per trade
    REENTRY_DELAY = 1200                 # Re-entry delay in seconds (20 minutes)
    REENTRY_PRICE_DEVIATION = 1.0        # Maximum price deviation for re-entry (%)
    REENTRY_DELAY_SEC = [90, 180]        # Reentry delay range (seconds) - legacy
    MAX_REENTRIES = 3                    # Maximum reentry attempts - legacy
    REENTRY_MAX_PRICE_DEVIATION = 1.0    # Max price deviation for reentry (%) - legacy
    
    # === 🎯 BREAK-EVEN CONFIGURATION ===
    BREAKEVEN_THRESHOLD = 2.0            # Profit % to trigger break-even (default 2%)
    BREAKEVEN_BUFFER = 0.001             # Break-even buffer (0.1% above entry)
    
    # === 📈 TRAILING STOP CONFIGURATION ===
    TRAILING_THRESHOLD = 3.0             # Profit % to activate trailing (default 3%)
    TRAILING_DISTANCE = 0.01             # Trailing distance (1% from current price)
    TRAILING_STEP = 0.005                # Minimum step size for trailing updates (0.5%)
    
    TRAILING_ACTIVATION = {
        "activate_at_pol": 6.0,           # Activate trailing at 6% profit
        "fallback_activation": {
            "enabled": True,
            "trigger_pol": 4.0,           # Fallback activation at 4% profit
            "sl_to_entry_offset": 0.003   # SL to entry offset
        }
    }
    
    # === ⏰ TIMEOUT PROTECTION CONFIGURATION ===
    TIMEOUT_HOURS = 4.0                   # Auto-close trades after 4 hours
    TIMEOUT_CHECK_INTERVAL = 60           # Check timeout every 60 seconds
    SL_TRAILING_BY_TP = {
        "tp2": "tp1",                     # Move SL to TP1 when TP2 hit
        "tp3": "tp2",                     # Move SL to TP2 when TP3 hit
        "tp4": "tp3"                      # Move SL to TP3 when TP4 hit
    }
    
    # === ⏱️ TIMING & DELAYS ===
    SLEEP_INTERVAL = 2
    SL_TIMEOUT = 60
    TP_TIMEOUT = 300
    REENTRY_TRIGGER_DELAY = 120
    REENTRY_DELAY_SECONDS = 10
    BE_OFFSET_PCT = 0.1
    CACHE_TTL_SECONDS = 30
    TIMEOUT_SECONDS = 20
    
    # === 🧠 STRATEGY FILTERS ===
    RSI_LIMIT = 60.0
    VOLUME_FILTER_MIN = 0.75
    VOLUME_FILTER_MAX = 1.50
    ENABLE_TRAILING_AFTER = "tp4"
    
    # === ⚙️ SYSTEM FEATURES ===
    USE_REENTRY = True
    USE_TRAILING_SL = True
    DEBUG_MODE = True
    USE_POST_ONLY = True
    ADMIN_COMMANDS_ENABLED = True  # Enable admin commands via Telegram

# === 🔐 EXCHANGE API CONFIGURATION ===
class ExchangeConfig:
    """Exchange-specific configuration settings."""
    
    # Bybit Configuration
    BYBIT_API_KEY = "MgOknaxKRsEHdzTEv1"
    BYBIT_API_SECRET = "gv62DEyoyQ7qAJERVhKtRq5K1BDebrM2RaKO"
    BYBIT_TESTNET = False  # LIVE MODE
    BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"
    
    # Bitget Configuration  
    BITGET_API_KEY = os.getenv("BITGET_API_KEY", "bg_ddb256661c2eb7d933572f3053339971")
    BITGET_API_SECRET = os.getenv("BITGET_API_SECRET", "4a16c89972883532318025d23e5086757f1cdc40633034565725977949a3f279")
    BITGET_API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE", "BotDemo2025")
    
    # API Endpoints
    BASE_URL = "https://api.bybit.com/v5"
    ORDER_URL = f"{BASE_URL}/order/create"
    LEVERAGE_URL = f"{BASE_URL}/position/set-leverage"
    STOP_LOSS_URL = f"{BASE_URL}/position/trading-stop"
    POSITION_URL = f"{BASE_URL}/position/list"
    
    # Supported Symbols & Leverage
    SUPPORTED_SYMBOLS = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
        "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT"
    ]
    
    MAX_LEVERAGE = {
        "BTCUSDT": 50, "ETHUSDT": 50, "SOLUSDT": 50, "XRPUSDT": 50,
        "ADAUSDT": 50, "DOGEUSDT": 50, "AVAXUSDT": 50, "DOTUSDT": 50,
        "LINKUSDT": 50, "MATICUSDT": 50
    }

# === 📡 TELEGRAM CONFIGURATION ===
class TelegramConfig:
    """Telegram bot and notification configuration."""
    
    # Bot Authentication
    TELEGRAM_BOT_TOKEN = "8458565067:AAHruy27kUf1uDiZl9Nhvy8Af2mRmw-8ew8"
    TELEGRAM_API_ID = 27590479
    TELEGRAM_API_HASH = "6e60321cbb996b499b6a370af62342de"
    ADMIN_ID = 7617377640
    
    # Chat & Channel Configuration
    TELEGRAM_CHAT_ID = "-1002460891279"
    DESTINATION_CHANNEL_ID = -1002460891279
    
    TELEGRAM_GROUPS = {
        "CryptoraketTrading": -1002290339976,
        "SmartCrypto": -2339729195,
        "own_channel": -1002460891279,
        # Original channels (you can add these back when you join them)
        # "cryptoraketen": -1002290339976,
        # "smart_crypto_signals": -1002339729195,
        # "lux_leak": -1002464706951,
        # "degenpump_crypto_pump_signals": -1001591293151,
        # "Free_Crypto_Pumps_Signals_Vip": -1001902180876,
        # "Trading_Signal5": -1001806414771
        # Add more groups here (up to 20 total)
        # Example group configurations:
        # "premium_signals": -1234567890,
        # "altcoin_alerts": -1234567891,
        # "futures_trading": -1234567892,
        # "scalping_signals": -1234567893,
        # "whale_alerts": -1234567894,
        # "technical_analysis": -1234567895,
        # "defi_signals": -1234567896,
        # "nft_trading": -1234567897,
        # "arbitrage_opportunities": -1234567898,
        # "leverage_trading": -1234567899,
        # "spot_trading": -1234567900,
        # "options_signals": -1234567901,
        # "forex_signals": -1234567902,
        # "commodities_trading": -1234567903,
        # "macro_analysis": -1234567904,
        # "news_alerts": -1234567905,
        # "market_updates": -1234567906,
    }
    
    # Auto-generate channel IDs from TELEGRAM_GROUPS dictionary
    TELEGRAM_SIGNAL_CHANNEL_IDS = list(TELEGRAM_GROUPS.values())
    
    @classmethod
    def add_telegram_group(cls, name: str, group_id: int):
        """
        Helper method to add a new Telegram group for signal monitoring.
        
        Usage:
        TelegramConfig.add_telegram_group("new_group", -1234567890)
        """
        cls.TELEGRAM_GROUPS[name] = group_id
        cls.TELEGRAM_SIGNAL_CHANNEL_IDS = list(cls.TELEGRAM_GROUPS.values())
        print(f"✅ Added Telegram group: {name} ({group_id})")
        
    @classmethod
    def get_group_name(cls, group_id: int) -> str:
        """Get group name by ID."""
        for name, gid in cls.TELEGRAM_GROUPS.items():
            if gid == group_id:
                return name
        return "Unknown"
        
    @classmethod
    def list_monitored_groups(cls):
        """Print all monitored groups."""
        print(f"📡 Currently monitoring {len(cls.TELEGRAM_GROUPS)} Telegram groups:")
        for name, group_id in cls.TELEGRAM_GROUPS.items():
            print(f"  • {name}: {group_id}")
    
    # Notification Tags
    TELEGRAM_CHANNELS = {
        "entry": "📨 ENTRY",
        "tp": "🎯 TP", 
        "sl": "❌ SL",
        "done": "📤 DONE",
        "pol": "📊 PoL",
        "error": "🚨 ERROR",
        "report": "📈 RAPPORT"
    }

# === 🔧 MANUAL OVERRIDES & DEBUGGING ===
class OverrideConfig:
    """Manual overrides for debugging and testing."""
    
    FORCE_MARKET_ENTRY = False           # Force MARKET entry regardless of signal
    DISABLE_REENTRY = False              # Disable re-entry globally
    OVERRIDE_LEVERAGE = None             # Override automatic leverage (e.g., set to 10)
    BLOCKED_SYMBOLS = ["DOGEUSDT"]       # Symbols to skip entirely
    SHUTDOWN_ALL = False                 # Emergency mode - stop all trading
    USE_DUMMY_SIGNAL = False             # Enable dummy signal for testing
    
    # === ⚙️ SYSTEM FEATURE TOGGLES ===
    DEBUG_MODE = False                   # Enable debug mode
    ENABLE_HEDGING = True                # Enable hedging functionality
    ENABLE_REENTRY = True                # Enable re-entry logic
    ENABLE_PYRAMIDING = True             # Enable pyramiding functionality
    ENABLE_SIGNAL_INVERSION = False      # Enable signal inversion (LONG ↔ SHORT)
    ENABLE_HEDGING = False               # Enable hedging (allow opposite positions simultaneously)
    
    # === 📊 REPORTING CONFIGURATION ===
    TELEGRAM_REPORT_ENABLED = True       # Enable Telegram trade reports
    REPORT_RECIPIENTS = ["@admin", "@channel"]  # Report recipients
    REPORT_DETAILED_ANALYSIS = True      # Include detailed trade analysis
    REPORT_INCLUDE_CHARTS = False        # Include chart images (if available)
    REPORT_GROUP_BY_SYMBOL = True        # Group reports by symbol
    REPORT_INCLUDE_PYRAMIDING = True     # Include pyramiding information
    REPORT_INCLUDE_REENTRY = True        # Include re-entry information
    
    # === 📊 CHART GENERATION CONFIGURATION ===
    REPORT_INCLUDE_CHARTS = True         # Enable chart generation in reports
    CHART_TIME_PERIOD = "1h"            # Chart timeframe (1m, 5m, 15m, 1h, 4h, 1d)
    CHART_LOOKBACK_PERIODS = 100        # Number of candles to include
    CHART_SAVE_LOCALLY = True           # Save charts locally
    CHART_UPLOAD_TO_TELEGRAM = True     # Upload charts to Telegram
    CHART_IMAGE_FORMAT = "png"          # Image format (png, jpg, svg)
    CHART_IMAGE_QUALITY = 90            # Image quality (1-100)
    CHART_THEME = "dark"                # Chart theme (dark, light)
    CHART_SHOW_VOLUME = True            # Show volume bars
    CHART_SHOW_INDICATORS = True        # Show technical indicators
    
    # === 👑 ADMIN COMMAND SYSTEM CONFIGURATION ===
ADMIN_COMMANDS_ENABLED = True       # Enable admin command system
ADMIN_USER_IDS = [123456789, 987654321]  # List of authorized admin user IDs
ADMIN_USERNAMES = ["admin", "owner", "trader"]  # List of authorized admin usernames
ADMIN_COMMAND_PREFIX = "/"          # Command prefix for admin commands
ADMIN_LOG_ALL_COMMANDS = True       # Log all admin commands for audit
ADMIN_REQUIRE_CONFIRMATION = False  # Require confirmation for destructive commands

# === 📈 SIGNAL ACCURACY TRACKING CONFIGURATION ===
ENABLE_SIGNAL_ACCURACY_TRACKING = True
ACCURACY_TRACKING_TIMEFRAME = "1d"  # or "7d", "30d"
SAVE_ACCURACY_TO_FILE = True
ACCURACY_RESULTS_PATH = "data/signal_accuracy.json"

# === 🎛️ STRATEGY CONTROL CONFIGURATION ===
ENABLE_TP = True                    # Enable take profit orders
ENABLE_SL = True                    # Enable stop loss orders
ENABLE_TRAILING_STOP = True         # Enable trailing stop functionality
ENABLE_BREAK_EVEN = True            # Enable break-even functionality
ENABLE_REENTRY = True               # Enable re-entry functionality
ENABLE_PYRAMIDING = True            # Enable pyramiding functionality

# Strategy overrides per group/symbol/timeframe
STRATEGY_OVERRIDES = {
        "cryptoraketen": {
            "BTCUSDT": {
                "5m": {
                    "ENABLE_REENTRY": False,
                    "ENABLE_TP": True,
                    "ENABLE_SL": True,
                    "ENABLE_TRAILING_STOP": False,
                    "ENABLE_BREAK_EVEN": True,
                    "ENABLE_PYRAMIDING": False
                },
                "1h": {
                    "ENABLE_REENTRY": True,
                    "ENABLE_TP": True,
                    "ENABLE_SL": True,
                    "ENABLE_TRAILING_STOP": True,
                    "ENABLE_BREAK_EVEN": True,
                    "ENABLE_PYRAMIDING": True
                }
            },
            "ETHUSDT": {
                "5m": {
                    "ENABLE_REENTRY": False,
                    "ENABLE_PYRAMIDING": False
                }
            }
        },
        "smart_crypto_signals": {
            "SOLUSDT": {
                "1h": {
                    "ENABLE_TRAILING_STOP": False,
                    "ENABLE_BREAK_EVEN": False
                }
            }
        },
        "own_channel": {
            "default": {
                "default": {
                    "ENABLE_REENTRY": True,
                    "ENABLE_PYRAMIDING": True
                }
            }
        }
    }

# === 🛡️ SPAM FILTERING CONFIGURATION ===
SPAM_FILTER_ENABLED = True           # Enable spam filtering
SPAM_RATE_LIMIT_SECONDS = 5         # Minimum seconds between messages from same source
SPAM_MAX_DUPLICATES = 3             # Maximum duplicate messages allowed
SPAM_MIN_MESSAGE_LENGTH = 10        # Minimum message length to process
SPAM_BLOCKED_KEYWORDS = [           # Keywords that indicate spam
    "bot", "automated", "spam", "scam", "fake", "click here", "join now"
]
SPAM_ALLOWED_SOURCES = [            # Whitelist of allowed message sources
    "cryptoraketen", "smart_crypto_signals", "own_channel"
]
SPAM_DUPLICATE_WINDOW_MINUTES = 10  # Window to detect duplicate messages
SPAM_MAX_MESSAGES_PER_MINUTE = 20   # Rate limit per source per minute

# === 🧪 BACKTEST CONFIGURATION ===
BACKTEST_MODE = False               # Enable backtest mode
BACKTEST_DATA_PATH = "data/test_signals.json"  # Path to test signals file
BACKTEST_START_DATE = "2024-01-01"  # Start date for backtest
BACKTEST_END_DATE = "2024-12-31"    # End date for backtest
BACKTEST_INITIAL_BALANCE = 10000    # Initial account balance for backtest
BACKTEST_COMMISSION_RATE = 0.001    # Commission rate (0.1%)
BACKTEST_SLIPPAGE = 0.0005          # Slippage rate (0.05%)
BACKTEST_ENABLE_REALISTIC_DELAYS = True  # Add realistic execution delays
BACKTEST_SAVE_RESULTS = True        # Save backtest results to file
BACKTEST_RESULTS_PATH = "data/backtest_results.json"  # Results output path

DUMMY_SIGNAL = {
    "symbol": "BTCUSDT",
    "side": "long", 
    "entry": 27300.0,
    "sl": 27000.0,
    "tp": [27400.0, 27500.0, 27600.0, 27800.0]
}

# === 🎯 SYMBOL & PRICE CONFIGURATION ===
class SymbolConfig:
    """Symbol-specific configuration and utilities."""
    
    TICK_SIZE_DICT = {
        "BTCUSDT": 0.1,
        "ETHUSDT": 0.01,
        "XRPUSDT": 0.0001,
        "NEARUSDT": 0.0001,
        "1000SHIBUSDT": 0.00001,
        "CATIUSDT": 0.0001,
        "JASMYUSDT": 0.000001,
    }
    
    SYMBOL_TRANSLATION = {
        "#NEAR/USDT": "NEARUSDT",
        "NEAR/USDT": "NEARUSDT",
        "NEARUSDT": "NEARUSDT",
        "OP/USDT": "OPUSDT",
        "OPUSDT": "OPUSDT",
        "RAYSOLUSDT": "RAYDIUMUSDT",
        "RAYSOL/USDT": "RAYDIUMUSDT",
        "RAYDIUMUSDT": "RAYDIUMUSDT",
        "JASMYUSDT.P": "JASMYUSDT",
        "JASMY/USDT": "JASMYUSDT",
        "JASMYUSDT": "JASMYUSDT",
    }
    
    DEFAULT_DECIMALS = 4
    FALLBACK_DECIMALS_MAP = {
        "BTCUSDT": 2,
        "ETHUSDT": 2,
        "XRPUSDT": 4,
        "SOLUSDT": 3,
        "DOGEUSDT": 5,
        "IOTAUSDT": 5,
        "ADAUSDT": 4,
    }
    
    @staticmethod
    def translate_symbol(symbol: str) -> str:
        """Translate symbol from various formats to standard format."""
        s = symbol.strip().replace(" ", "").upper()
        if s.startswith("#"):
            s = s[1:]
        if s.endswith(".P"):
            s = s[:-2]
        s = s.replace("/", "")
        return SymbolConfig.SYMBOL_TRANSLATION.get(s, s)

# ================================================================================================
# 🎯 CONVENIENCE IMPORTS - Backward Compatibility
# ================================================================================================
# These provide direct access to commonly used config values for easier imports

# Core Trading Parameters
DEFAULT_IM = TradingConfig.DEFAULT_IM
RISK_PERCENT = TradingConfig.RISK_PERCENT
LEVERAGE_CAP = TradingConfig.LEVERAGE_CAP
SL_PCT = TradingConfig.SL_PCT
TP_LEVELS = TradingConfig.TP_LEVELS
BREAK_EVEN_TRIGGER = TradingConfig.BREAK_EVEN_TRIGGER
TRAILING_TRIGGER = TradingConfig.TRAILING_TRIGGER
TRAILING_OFFSET = TradingConfig.TRAILING_OFFSET
AUTO_CLOSE_TIMEOUT = TradingConfig.AUTO_CLOSE_TIMEOUT
ENABLE_REVERSE = TradingConfig.ENABLE_REVERSE

# Advanced Trading Settings  
DEFAULT_LEVERAGE = TradingConfig.DEFAULT_LEVERAGE
DEFAULT_BALANCE = TradingConfig.DEFAULT_BALANCE
DEFAULT_SL_OFFSET_PCT = TradingConfig.DEFAULT_SL_OFFSET_PCT
MIN_SL_DISTANCE = TradingConfig.MIN_SL_DISTANCE
FALLBACK_SL_DISTANCE = TradingConfig.FALLBACK_SL_DISTANCE
BREAKEVEN_BUFFER = TradingConfig.BREAKEVEN_BUFFER
DEFAULT_SL_BUFFER = TradingConfig.DEFAULT_SL_BUFFER

# Pyramiding
MAX_PYRAMID_STEPS = TradingConfig.MAX_PYRAMID_STEPS
PYRAMID_POL_THRESHOLDS = TradingConfig.PYRAMID_POL_THRESHOLDS
PYRAMID_STEP_SIZE = TradingConfig.PYRAMID_STEP_SIZE
PYRAMID_MIN_POL = TradingConfig.PYRAMID_MIN_POL
PYRAMID_MAX_PRICE_DEVIATION = TradingConfig.PYRAMID_MAX_PRICE_DEVIATION
PYRAMID_STEPS = TradingConfig.PYRAMID_STEPS

# Re-entry
REENTRY_ENABLED = TradingConfig.REENTRY_ENABLED
REENTRY_MAX_ATTEMPTS = TradingConfig.REENTRY_MAX_ATTEMPTS
REENTRY_DELAY = TradingConfig.REENTRY_DELAY
REENTRY_PRICE_DEVIATION = TradingConfig.REENTRY_PRICE_DEVIATION

# Risk Management
RISK_PER_TRADE = TradingConfig.RISK_PER_TRADE
FALLBACK_SL_PERCENTAGE = TradingConfig.FALLBACK_SL_PERCENTAGE
LEVERAGE_BOOST_THRESHOLD = TradingConfig.LEVERAGE_BOOST_THRESHOLD
ENTRY_SL_OFFSET = TradingConfig.ENTRY_SL_OFFSET
FALLBACK_SL_OFFSET = TradingConfig.FALLBACK_SL_OFFSET
HEDGE_TRIGGER_DRAWDOWN = TradingConfig.HEDGE_TRIGGER_DRAWDOWN
HEDGE_SL_DISTANCE = TradingConfig.HEDGE_SL_DISTANCE

# Compatibility aliases for existing imports
HEDGE_TRIGGER = HEDGE_TRIGGER_DRAWDOWN
HEDGE_SL = HEDGE_SL_DISTANCE

# Stop Loss management configuration
SL_MOVE_THRESHOLDS = {
    "tp1": 1.5,  # Move SL after TP1 (1.5% profit)
    "tp2": 3.0,  # Move SL after TP2 (3.0% profit) 
    "tp3": 6.0,  # Move SL after TP3 (6.0% profit)
    "tp4": 10.0  # Move SL after TP4 (10.0% profit)
}

SL_MOVE_OFFSETS = {
    "entry": 0.15,     # Move SL to entry + 0.15%
    "tp1": 0.5,        # Move SL to TP1 after TP2 hit
    "tp2": 1.0,        # Move SL to TP2 after TP3 hit
    "trailing": 0.5    # Trailing SL offset
}

# Reentry & Trailing
REENTRY_DELAY_SEC = TradingConfig.REENTRY_DELAY_SEC
MAX_REENTRIES = TradingConfig.MAX_REENTRIES
TRAILING_ACTIVATION = TradingConfig.TRAILING_ACTIVATION
SL_TRAILING_BY_TP = TradingConfig.SL_TRAILING_BY_TP
TRAILING_SL_PERCENT = TradingConfig.TRAILING_OFFSET  # Use trailing offset as SL percentage

# Timing
SLEEP_INTERVAL = TradingConfig.SLEEP_INTERVAL
SL_TIMEOUT = TradingConfig.SL_TIMEOUT
TP_TIMEOUT = TradingConfig.TP_TIMEOUT
REENTRY_TRIGGER_DELAY = TradingConfig.REENTRY_TRIGGER_DELAY
REENTRY_DELAY_SECONDS = TradingConfig.REENTRY_DELAY_SECONDS
TIMEOUT_SECONDS = TradingConfig.TIMEOUT_SECONDS

# System Features
USE_REENTRY = TradingConfig.USE_REENTRY
USE_TRAILING_SL = TradingConfig.USE_TRAILING_SL
DEBUG_MODE = TradingConfig.DEBUG_MODE
USE_POST_ONLY = TradingConfig.USE_POST_ONLY

# Exchange Settings
BYBIT_API_KEY = ExchangeConfig.BYBIT_API_KEY
BYBIT_API_SECRET = ExchangeConfig.BYBIT_API_SECRET
BYBIT_TESTNET = ExchangeConfig.BYBIT_TESTNET
BYBIT_WS_URL = ExchangeConfig.BYBIT_WS_URL
BASE_URL = ExchangeConfig.BASE_URL
ORDER_URL = ExchangeConfig.ORDER_URL
LEVERAGE_URL = ExchangeConfig.LEVERAGE_URL
STOP_LOSS_URL = ExchangeConfig.STOP_LOSS_URL
POSITION_URL = ExchangeConfig.POSITION_URL
SUPPORTED_SYMBOLS = ExchangeConfig.SUPPORTED_SYMBOLS
MAX_LEVERAGE = ExchangeConfig.MAX_LEVERAGE

# Telegram Settings
TELEGRAM_BOT_TOKEN = TelegramConfig.TELEGRAM_BOT_TOKEN
TELEGRAM_API_ID = TelegramConfig.TELEGRAM_API_ID
TELEGRAM_API_HASH = TelegramConfig.TELEGRAM_API_HASH
ADMIN_ID = TelegramConfig.ADMIN_ID
TELEGRAM_CHAT_ID = TelegramConfig.TELEGRAM_CHAT_ID
DESTINATION_CHANNEL_ID = TelegramConfig.DESTINATION_CHANNEL_ID
TELEGRAM_GROUPS = TelegramConfig.TELEGRAM_GROUPS
TELEGRAM_SIGNAL_CHANNEL_IDS = TelegramConfig.TELEGRAM_SIGNAL_CHANNEL_IDS
TELEGRAM_CHANNELS = TelegramConfig.TELEGRAM_CHANNELS

# Manual Overrides
FORCE_MARKET_ENTRY = OverrideConfig.FORCE_MARKET_ENTRY
DISABLE_REENTRY = OverrideConfig.DISABLE_REENTRY
OVERRIDE_LEVERAGE = OverrideConfig.OVERRIDE_LEVERAGE
BLOCKED_SYMBOLS = OverrideConfig.BLOCKED_SYMBOLS
SHUTDOWN_ALL = OverrideConfig.SHUTDOWN_ALL
USE_DUMMY_SIGNAL = OverrideConfig.USE_DUMMY_SIGNAL
# DUMMY_SIGNAL is defined globally, not in OverrideConfig

# System Feature Toggles
DEBUG_MODE = OverrideConfig.DEBUG_MODE
ENABLE_HEDGING = OverrideConfig.ENABLE_HEDGING
ENABLE_REENTRY = OverrideConfig.ENABLE_REENTRY
ENABLE_PYRAMIDING = OverrideConfig.ENABLE_PYRAMIDING
ENABLE_SIGNAL_INVERSION = OverrideConfig.ENABLE_SIGNAL_INVERSION
ENABLE_HEDGING = OverrideConfig.ENABLE_HEDGING

# Reporting Configuration
TELEGRAM_REPORT_ENABLED = OverrideConfig.TELEGRAM_REPORT_ENABLED
REPORT_RECIPIENTS = OverrideConfig.REPORT_RECIPIENTS
REPORT_DETAILED_ANALYSIS = OverrideConfig.REPORT_DETAILED_ANALYSIS
REPORT_INCLUDE_CHARTS = OverrideConfig.REPORT_INCLUDE_CHARTS
REPORT_GROUP_BY_SYMBOL = OverrideConfig.REPORT_GROUP_BY_SYMBOL
REPORT_INCLUDE_PYRAMIDING = OverrideConfig.REPORT_INCLUDE_PYRAMIDING
REPORT_INCLUDE_REENTRY = OverrideConfig.REPORT_INCLUDE_REENTRY

# Spam Filtering Configuration - These are defined globally
# SPAM_FILTER_ENABLED, SPAM_RATE_LIMIT_SECONDS, etc. are already available globally

# Chart Generation Configuration - These are defined globally  
# REPORT_INCLUDE_CHARTS, CHART_TIME_PERIOD, etc. are already available globally

# Strategy Control Configuration - These are defined globally
# ENABLE_TP, ENABLE_SL, etc. are already available globally

# Admin Command System Configuration - These are defined globally
# ADMIN_COMMANDS_ENABLED, ADMIN_USER_IDS, etc. are already available globally

# Signal Accuracy Tracking Configuration - These are defined globally
# ENABLE_SIGNAL_ACCURACY_TRACKING, ACCURACY_TRACKING_TIMEFRAME, etc. are already available globally

# Backtest Configuration - These are defined globally
# BACKTEST_MODE, BACKTEST_DATA_PATH, etc. are already available globally

# Symbol Configuration
TICK_SIZE_DICT = SymbolConfig.TICK_SIZE_DICT
SYMBOL_TRANSLATION = SymbolConfig.SYMBOL_TRANSLATION
translate_symbol = SymbolConfig.translate_symbol

# ================================================================================================
# 🌐 GLOBAL INSTANCES
# ================================================================================================

# WebSocket Session
SESSION = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET) if HTTP else None

# Global trade state storage
global_trade_states = {}  # symbol → TradeState

# ================================================================================================
# 🧪 TESTING & DEBUGGING
# ================================================================================================

if __name__ == '__main__':
    print("🎯 Centralized Configuration Test")
    print(f"DEFAULT_IM: {DEFAULT_IM}")
    print(f"RISK_PERCENT: {RISK_PERCENT}%")
    print(f"TP_LEVELS: {TP_LEVELS}")
    print(f"SYMBOL_TRANSLATION Test - BTCUSDT → {translate_symbol('BTCUSDT')}")
    print("✅ Configuration loaded successfully!")