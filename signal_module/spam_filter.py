# Spam filtering and message preprocessing module

import re
from typing import Tuple, Dict, Any

async def preprocess_telegram_message(text: str, source: str, message_id: int, chat_id: int) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Preprocess and filter Telegram messages for spam and invalid content.
    
    Args:
        text: Raw message text
        source: Source group name
        message_id: Telegram message ID
        chat_id: Telegram chat ID
    
    Returns:
        Tuple of (is_valid, sanitized_text, filter_info)
    """
    
    # Basic spam filtering rules
    filter_info = {"reason": None, "applied_filters": []}
    
    # Skip empty messages
    if not text or not text.strip():
        return False, "", {"reason": "empty_message", "applied_filters": ["empty_check"]}
    
    # Skip very short messages (likely not trading signals)
    if len(text.strip()) < 10:
        return False, "", {"reason": "too_short", "applied_filters": ["length_check"]}
    
    # Skip messages that are likely spam (excessive repetition)
    if len(set(text.lower())) < len(text) * 0.3:  # Less than 30% unique characters
        return False, "", {"reason": "excessive_repetition", "applied_filters": ["repetition_check"]}
    
    # Basic sanitization
    sanitized_text = text.strip()
    
    # Remove excessive whitespace
    sanitized_text = re.sub(r'\s+', ' ', sanitized_text)
    
    # Remove common spam patterns (adjust as needed)
    spam_patterns = [
        r'@everyone',
        r'@here',
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, sanitized_text, re.IGNORECASE):
            filter_info["applied_filters"].append(f"removed_{pattern[:10]}...")
            sanitized_text = re.sub(pattern, '', sanitized_text, flags=re.IGNORECASE)
    
    # Check if message looks like a trading signal (basic heuristics)
    signal_indicators = [
        r'\b(long|short|buy|sell)\b',
        r'\b(entry|tp|sl|stop)\b',
        r'\b[A-Z]{3,6}USDT?\b',  # Crypto symbols
        r'\$[A-Z]{3,6}\b',       # $ symbols
    ]
    
    has_signal_indicators = any(re.search(pattern, sanitized_text, re.IGNORECASE) for pattern in signal_indicators)
    
    if not has_signal_indicators:
        return False, "", {"reason": "no_signal_indicators", "applied_filters": ["signal_check"]}
    
    filter_info["applied_filters"].append("passed_all_checks")
    return True, sanitized_text, filter_info