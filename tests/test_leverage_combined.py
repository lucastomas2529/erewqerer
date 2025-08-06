import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.leverage import calculate_leverage
from config.settings import LEVERAGE_CAP, DEFAULT_LEVERAGE

# Testfall 1: SL finns – korrekt dynamisk hävstång


# Testfall 1: SL finns – korrekt dynamisk hävstång
def test_leverage_with_valid_sl():
    entry = 0.2215
    sl = 0.2149
    lev = calculate_leverage(entry, sl)
    print(f"✅ Test 1: Dynamisk hävstång → {lev}x")
    assert DEFAULT_LEVERAGE < lev < LEVERAGE_CAP, f"❌ Förväntade dynamisk hävstång, fick {lev}x"

# Testfall 2: SL saknas → fallback till x10
def test_leverage_with_missing_sl():
    entry = 0.2215
    sl = None
    lev = calculate_leverage(entry, sl)
    print(f"✅ Test 2: SL saknas → {lev}x")
    assert lev == DEFAULT_LEVERAGE, f"❌ SL saknas → borde vara x{DEFAULT_LEVERAGE}, fick {lev}x"

# Testfall 3: SL = entry → ogiltigt → fallback
def test_leverage_sl_equal_entry():
    entry = 0.2215
    sl = 0.2215
    lev = calculate_leverage(entry, sl)
    print(f"✅ Test 3: SL = Entry → {lev}x")
    assert lev == DEFAULT_LEVERAGE, f"❌ SL=entry → borde fallbacka till x{DEFAULT_LEVERAGE}, fick {lev}x"

if __name__ == "__main__":
    test_leverage_with_valid_sl()
    test_leverage_with_missing_sl()
    test_leverage_sl_equal_entry()
