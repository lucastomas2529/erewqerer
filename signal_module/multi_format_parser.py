
import re
from utils.price import get_current_price
from utils.telegram_logger import send_telegram_log
from config.settings import OverrideConfig

def parse_entry_zone(entry_text):
    if "-" in entry_text:
        parts = [float(p.strip()) for p in entry_text.split("-") if p.strip()]
        return sum(parts) / len(parts)
    try:
        return float(entry_text.strip())
    except:
        return None

def parse_targets(text):
    # Enhanced to catch both decimal and integer numbers
    targets = re.findall(r"(\d+\.\d+|\d+)", text)
    return [float(t) for t in targets[:6]]

async def parse_signal_text_multi(raw_text):
    """
    Enhanced multi-format signal parser supporting various trading signal formats.
    Supports formats from: Binance, Bybit, Bitget, CryptoBull, and custom channels.
    """
    signal = {}
    original_text = raw_text
    raw_text = raw_text.replace("\xa0", " ").replace("\n", " ").strip()

    # Enhanced Symbol Detection - Support multiple formats
    symbol_patterns = [
        r"[#\$]?([A-Z]{2,10})[/\-]?USDT",  # Standard: BTCUSDT, BTC/USDT, #BTCUSDT
        r"Coin:\s*([A-Z]{2,10})",           # Coin: BTC format
        r"Symbol:\s*([A-Z]{2,10})",         # Symbol: BTC format  
        r"([A-Z]{2,10})PERP",               # BTCPERP perpetual format
        r"([A-Z]{2,10})-\d{2}[A-Z]{3}\d{2}", # BTC-25DEC22 futures format
        r"Signal:\s*([A-Z]{2,10})",         # Signal: BTC format
        r"Pair:\s*([A-Z]{2,10})",           # Pair: BTC format
        r"([A-Z]{2,10})\s+Position:",       # BNB Position: format
        r"([A-Z]{2,10})\s+Trade:",          # BNB Trade: format
        r"([A-Z]{2,10})\s+Side:",           # BNB Side: format
        r"^([A-Z]{2,10})\s",                # BNB at start followed by space
        r"🐋\s*([A-Z]{2,10})",              # 🐋 BTC format
        r"🔥\s*([A-Z]{2,10})"               # 🔥 BTC format
    ]
    
    for pattern in symbol_patterns:
        symbol_match = re.search(pattern, raw_text, re.IGNORECASE)
        if symbol_match:
            base_symbol = symbol_match.group(1).upper()
            signal["symbol"] = base_symbol + "USDT" if not base_symbol.endswith("USDT") else base_symbol
            break

    # Enhanced Side/Direction Detection - Support multiple formats
    side_patterns = [
        r"Direction:\s*(LONG|SHORT)",       # Direction: LONG
        r"Side:\s*(LONG|SHORT)",            # Side: LONG
        r"Position:\s*(LONG|SHORT)",        # Position: LONG
        r"Trade:\s*(LONG|SHORT)",           # Trade: LONG
        r"(BUY|SELL)",                      # BUY/SELL format
        r"(LÅNG|KORT)",                     # Swedish
        r"(LONG|SHORT)",                    # Standard
        r"📈\s*(LONG|BUY)",                 # 📈 LONG
        r"📉\s*(SHORT|SELL)"                # 📉 SHORT
    ]
    
    for pattern in side_patterns:
        side_match = re.search(pattern, raw_text, re.IGNORECASE)
        if side_match:
            side_text = side_match.group(1).upper()
            if side_text in ["LONG", "BUY", "LÅNG"]:
                signal["side"] = "LONG"
            elif side_text in ["SHORT", "SELL", "KORT"]:
                signal["side"] = "SHORT"
            break
    
    # Apply signal inversion if enabled
    if "side" in signal and OverrideConfig.ENABLE_SIGNAL_INVERSION:
        original_side = signal["side"]
        if original_side == "LONG":
            signal["side"] = "SHORT"
        elif original_side == "SHORT":
            signal["side"] = "LONG"
        
        signal["is_inverted"] = True
        signal["original_side"] = original_side

    # Enhanced Entry Detection - Support multiple formats
    entry_patterns = [
        r"Entry\s*[:\-]?\s*([\d\.\-\s]+)",           # Entry: 45000-46000
        r"Entry\s*Zone\s*[:\-]?\s*([\d\.\-\s]+)",    # Entry Zone: 45000
        r"Buy\s*[:\-]?\s*([\d\.\-\s]+)",             # Buy: 45000
        r"Price\s*[:\-]?\s*([\d\.\-\s]+)",           # Price: 45000
        r"Open\s*[:\-]?\s*([\d\.\-\s]+)",            # Open: 45000
        r"Enter\s*[:\-]?\s*([\d\.\-\s]+)",           # Enter: 45000
        r"Ingång\s*[:\-]?\s*([\d\.\-\s]+)",          # Swedish
        r"Current\s*Price\s*[:\-]?\s*([\d\.\-\s]+)", # Current Price: 45000
        r"@\s*([\d\.\-\s]+)",                        # @45000
        r"🎯\s*([\d\.\-\s]+)"                        # 🎯45000
    ]
    
    parsed_entry = None
    for pattern in entry_patterns:
        entry_match = re.search(pattern, raw_text, re.IGNORECASE)
        if entry_match:
            entry_text = entry_match.group(1)
            parsed_entry = parse_entry_zone(entry_text)
            if parsed_entry:
                break

    # Handle entry price with enhanced fallback
    if parsed_entry is None:
        try:
            symbol = signal.get("symbol")
            if symbol:
                fallback_price = await get_current_price(symbol)
                signal["entry_price"] = fallback_price
                await send_telegram_log(f"⚠️ No valid entry found - using market price: {fallback_price} for {symbol}")
            else:
                await send_telegram_log("❌ No symbol found for entry fallback")
                return None
        except Exception as e:
            await send_telegram_log(f"❌ Failed to get fallback price: {e}")
            return None
    else:
        signal["entry_price"] = parsed_entry



    # Enhanced SL Detection with automatic calculation fallback
    sl_patterns = [
        r"SL\s*[:\-]?\s*([\d\.]+)",              # SL: 44000
        r"Stop\s*Loss\s*[:\-]?\s*([\d\.]+)",     # Stop Loss: 44000
        r"Stop\s*[:\-]?\s*([\d\.]+)",            # Stop: 44000
        r"Stoploss\s*[:\-]?\s*([\d\.]+)",        # Stoploss: 44000
        r"❌\s*([\d\.]+)",                       # ❌44000
        r"🛑\s*([\d\.]+)",                       # 🛑44000
        r"S/L\s*[:\-]?\s*([\d\.]+)",             # S/L: 44000
        r"Cut\s*Loss\s*[:\-]?\s*([\d\.]+)",      # Cut Loss: 44000
        r"Cut\s*[:\-]?\s*([\d\.]+)"              # Cut: 610
    ]
    
    sl_price = None
    for pattern in sl_patterns:
        sl_match = re.search(pattern, raw_text, re.IGNORECASE)
        if sl_match:
            try:
                sl_price = float(sl_match.group(1))
                signal["sl_price"] = sl_price
                break
            except ValueError:
                continue
    
    # Enhanced SL Fallback Logic - Calculate based on risk and side
    if sl_price is None and "entry_price" in signal and "side" in signal:
        try:
            from config.settings import TradingConfig
            entry_price = signal["entry_price"]
            side = signal["side"]
            risk_percent = 0.02  # Default 2% risk
            
            # Calculate SL based on side and risk percentage
            if side == "LONG":
                calculated_sl = entry_price * (1 - risk_percent)
            else:  # SHORT
                calculated_sl = entry_price * (1 + risk_percent)
            
            signal["sl_price"] = calculated_sl
            signal["sl_calculated"] = True
            await send_telegram_log(f"⚠️ No SL found - calculated {risk_percent*100}% risk SL: {calculated_sl:.6f} for {signal.get('symbol', 'unknown')}")
            
        except Exception as e:
            await send_telegram_log(f"❌ Failed to calculate fallback SL: {e}")
            # Don't return None here - signal can still be valid without SL

    # Enhanced TP/Target Detection - Support multiple formats
    target_patterns = [
        r"Targets?\s*[:\-]?\s*([\d\s\.,]+)",       # Targets: 46000, 47000
        r"TP\d*\s*[:\-]?\s*([\d\s\.,]+)",          # TP1: 46000, TP2: 47000
        r"Take\s*Profit\s*[:\-]?\s*([\d\s\.,]+)",  # Take Profit: 46000
        r"Target\s*[:\-]?\s*([\d\s\.,]+)",         # Target: 46000
        r"Exit\s*[:\-]?\s*([\d\s\.,]+)",           # Exit: 46000
        r"Sell\s*[:\-]?\s*([\d\s\.,]+)",           # Sell: 46000
        r"Mål\s*[:\-]?\s*([\d\s\.,]+)",            # Swedish - Mål: 46000
        r"🎯\s*([\d\s\.,]+)",                      # 🎯46000, 47000
        r"✅\s*([\d\s\.,]+)",                      # ✅46000
        r"Exit:\s*([\d\s\.,]+)",                   # Exit: 640,660 (exact match)
    ]
    
    # Try to find targets with multiple patterns
    targets_found = []
    for pattern in target_patterns:
        targets_match = re.search(pattern, raw_text, re.IGNORECASE)
        if targets_match:
            targets_text = targets_match.group(1) if targets_match.groups() else targets_match.group(0)
            targets = parse_targets(targets_text)
            if targets:
                targets_found = targets
                break
    
    # Add targets to signal (up to 6 targets)
    for i, target in enumerate(targets_found[:6], 1):
        signal[f"tp{i}"] = target

    # Leverage (optional)
    lev_match = re.search(r"(Leverage|Hävstång).*?(\d{1,2}x)", raw_text, re.IGNORECASE)
    if lev_match:
        signal["leverage"] = lev_match.group(2).upper()

    # RRR (optional)
    rrr_match = re.search(r"RRR[:\s]+(\d+:\d+)", raw_text)
    if rrr_match:
        signal["rrr"] = rrr_match.group(1)

    # Risk (optional)
    risk_match = re.search(r"risk.*?(\d+\.?\d*)%", raw_text, re.IGNORECASE)
    if risk_match:
        signal["risk"] = float(risk_match.group(1))

    # Enhanced signal validation - More flexible requirements
    required_fields = ["symbol", "side", "entry_price"]
    has_required = all(field in signal for field in required_fields)
    
    if has_required:
        # Add parsing metadata
        signal["parser_version"] = "enhanced_v2.0"
        signal["original_text"] = original_text
        signal["confidence"] = calculate_signal_confidence(signal)
        signal["has_targets"] = any(f"tp{i}" in signal for i in range(1, 7))
        signal["has_sl"] = "sl_price" in signal
        
        return signal
    else:
        missing_fields = [field for field in required_fields if field not in signal]
        await send_telegram_log(f"❌ Signal validation failed - missing: {', '.join(missing_fields)}")
        return None

def calculate_signal_confidence(signal: dict) -> float:
    """Calculate confidence score for parsed signal (0.0 to 1.0)."""
    score = 0.0
    
    # Base score for required fields
    if "symbol" in signal: score += 0.3
    if "side" in signal: score += 0.3
    if "entry_price" in signal: score += 0.2
    
    # Bonus for optional fields
    if "sl_price" in signal: score += 0.1
    if any(f"tp{i}" in signal for i in range(1, 7)): score += 0.1
    
    # Penalty for calculated fields
    if signal.get("sl_calculated"): score -= 0.05
    
    return min(1.0, max(0.0, score))

# Alias for backward compatibility
parse_signal = parse_signal_text_multi
