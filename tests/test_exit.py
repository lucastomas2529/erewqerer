
import asyncio
from logic.tp_manager import handle_tp_hit
from logic.sl_manager import check_and_adjust_sl
from logic.trailing import should_activate_trailing
from logic.reentry import check_reentry_conditions
from logic.hedge import check_and_open_hedge

# Dummy testdata
symbol = "BTCUSDT"
side = "LONG"
entry_price = 100.0
tp_prices = [101.0, 102.0, 103.0, 104.0]  # TP1–TP4
current_sl = 98.0
quantity = 0.01
reentry_count = 0

# SL move to TP2 and TP3
async def test_sl_move_on_tp_levels():
    print("🔁 Testar SL-flytt vid TP2...")
    sl_tp2 = await handle_tp_hit(symbol, tp_level_hit=2, tp_prices=tp_prices, current_sl=current_sl)
    assert sl_tp2 == tp_prices[0], f"❌ SL inte flyttad till TP1: {sl_tp2}"
    print(f"✅ SL korrekt till TP1: {sl_tp2}")

    print("🔁 Testar SL-flytt vid TP3...")
    sl_tp3 = await handle_tp_hit(symbol, tp_level_hit=3, tp_prices=tp_prices, current_sl=sl_tp2)
    assert sl_tp3 == tp_prices[1], f"❌ SL inte flyttad till TP2: {sl_tp3}"
    print(f"✅ SL korrekt till TP2: {sl_tp3}")

    print("🔁 Testar SL-flytt vid TP4...")
    sl_tp4 = await handle_tp_hit(symbol, tp_level_hit=4, tp_prices=tp_prices, current_sl=sl_tp3)
    assert sl_tp4 == tp_prices[2], f"❌ SL inte flyttad till TP3: {sl_tp4}"
    print(f"✅ SL korrekt till TP3: {sl_tp4}")

# Trailing stop logic
async def test_trailing_stop_activation():
    print("✅ Testar aktivering av trailing stop...")
    pol = 6.1  # Profit > 6%
    tp4_hit = True
    assert should_activate_trailing(pol, tp4_hit) is True
    print("✅ Trailing Stop aktiveras korrekt vid TP4 eller 6% PoL")

# Realistic wait + trend check
async def test_reentry_trigger():
    print("⛔ Simulerar återinträde efter SL...")
    current_price = entry_price * 0.985
    ok = await check_reentry_conditions(symbol, reentry_count, sl_price=entry_price * 0.97, current_price=current_price)
    assert ok is True
    print("✅ Re-entry tillåten efter analys och prisåterhämtning")

# Real hedge simulation at price drop
async def test_hedge_trigger():
    print("🔄 Simulerar hedge vid -2%...")
    current_price = entry_price * 0.978  # ~-2.2%
    ok = await check_and_open_hedge(symbol, "long", entry_price, current_price)
    assert ok is True
    print("✅ Hedge korrekt aktiverad vid -2%")

# Run all tests
async def main():
    await test_sl_move_on_tp_levels()
    await test_trailing_stop_activation()
    await test_reentry_trigger()
    await test_hedge_trigger()

if __name__ == "__main__":
    asyncio.run(main())
