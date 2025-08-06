from utils.price import round_price

# Import values from centralized configuration
from config.settings import DEFAULT_IM, DEFAULT_BALANCE, RISK_PERCENT, MAX_LEVERAGE

# Kvantitetsformel
def calculate_quantity(im, leverage, entry_price):
    raw_qty = (im * leverage) / entry_price
    return round(raw_qty, 4)

# ✅ Testfall
def test_quantity_calculation():
    entry_price = 0.2215
    tick_size = 0.0001  # exempel tick size

    # Entry 1 – IM 20, lev 10
    qty1 = calculate_quantity(20, 10, entry_price)
    rounded1 = round_price("IOTAUSDT", qty1)
    assert abs(rounded1 - 903.6) < 1, f"❌ Felaktig kvantitet vid 10x: {rounded1}"
    print(f"✅ Test 1: {rounded1} (10x)")

    # +2.5% PoL – IM 40, lev 50
    qty2 = calculate_quantity(40, 50, entry_price)
    rounded2 = round_price("IOTAUSDT", qty2)
    assert abs(rounded2 - 9036.3) < 5, f"❌ Felaktig kvantitet vid 50x: {rounded2}"
    print(f"✅ Test 2: {rounded2} (50x)")

    # +4% PoL – IM 100, lev 50
    qty3 = calculate_quantity(100, 50, entry_price)
    rounded3 = round_price("IOTAUSDT", qty3)
    print(f"✅ Test 3: {rounded3} (IM=100, lev=50)")

    # +6% PoL – IM 200, lev 50
    qty4 = calculate_quantity(200, 50, entry_price)
    rounded4 = round_price("IOTAUSDT", qty4)
    print(f"✅ Test 4: {rounded4} (IM=200, lev=50)")

if __name__ == "__main__":
    test_quantity_calculation()

