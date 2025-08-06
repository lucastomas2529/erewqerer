import asyncio
from signal_module.multi_format_parser import parse_signal_text_multi
from signal_module.signal_queue import signal_queue

# ========== TESTSIGNALER ==========

signals = {
    "long_signal": """
✅ Ny trade från signal:
🕒 Tid: 2025-05-25 23:41:36
📊 Symbol: IOTAUSDT
📈 Riktning: LÅNG
💥 Ingång: 0.2215
🎯 Mål 1: 0.2226
🎯 Mål 2: 0.2281
🎯 Mål 3: 0.2348
🎯 Mål 4: 0.2437
❌ StopLoss: 0.2149
⚙️ Hävstång: 20x
""",

    "short_signal": """
✅ Ny trade från signal:
📊 Symbol: ETHUSDT
📉 Riktning: KORT
💥 Ingång: 1800.5
🎯 Mål 1: 1790.0
🎯 Mål 2: 1780.0
❌ StopLoss: 1810.0
⚙️ Hävstång: 10X
""",

    "entry_range": """
📊 Symbol: BTCUSDT
📈 Riktning: LÅNG
💥 Ingång: 27500 - 27700
🎯 Mål 1: 27800
🎯 Mål 2: 28000
❌ StopLoss: 27000
⚙️ Hävstång: 15x
""",

    "english_signal": """
✅ New trade signal:
📊 Symbol: DOGEUSDT
📈 Direction: LONG
💥 Entry: 0.0815
🎯 Target 1: 0.0850
🎯 Target 2: 0.0885
❌ StopLoss: 0.0790
⚙️ Leverage: 10X
""",

    "short_format": """
📊 Symbol: XRPUSDT
📉 Riktning: KORT
💥 Ingång: 0.515
🎯 Mål 1: 0.505
🎯 Mål 2: 0.495
❌ StopLoss: 0.525
⚙️ Hävstång: 5x
"""
}

# ========== TESTFUNKTIONER ==========

def test_parser():
    for name, signal in signals.items():
        print(f"\n🔍 Testar: {name}")
        parsed = parse_signal_text_multi(signal)

        assert "symbol" in parsed
        assert "side" in parsed
        assert "entry_price" in parsed
        assert "sl_price" in parsed
        assert "leverage" in parsed

        print(f"✅ {name} parser OK → {parsed['symbol']} {parsed['side']}")

async def test_signal_queue():
    signal = signals["long_signal"]
    parsed = parse_signal_text_multi(signal)
    await signal_queue.put(parsed)
    item = await signal_queue.get()
    assert item["symbol"] == "IOTAUSDT"
    print("✅ SignalQueue fungerar korrekt!")

# ========== KÖR TESTER ==========

if __name__ == "__main__":
    test_parser()
    asyncio.run(test_signal_queue())

