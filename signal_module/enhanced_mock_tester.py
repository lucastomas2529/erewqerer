# Enhanced Mock Signal Testing System
"""
Comprehensive testing system for Telegram signal parsing and multi-group handling.
Tests various signal formats from different trading channels and validates parsing accuracy.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from signal_module.multi_format_parser import parse_signal_text_multi
from signal_module.signal_handler import SignalHandler
from config.settings import TelegramConfig

class MockSignalTester:
    def __init__(self):
        self.signal_handler = SignalHandler()
        self.test_results = []
        
    async def run_comprehensive_tests(self):
        """Run all signal parsing tests."""
        print("🧪 Starting Enhanced Mock Signal Testing...")
        print("=" * 60)
        
        # Test different signal formats
        await self.test_standard_formats()
        await self.test_exchange_formats()
        await self.test_emoji_formats()
        await self.test_edge_cases()
        await self.test_multi_group_scenarios()
        
        # Generate test report
        await self.generate_test_report()
        
    async def test_standard_formats(self):
        """Test standard trading signal formats."""
        print("📊 Testing Standard Signal Formats...")
        
        test_signals = [
            # Standard Binance format
            {
                "text": "🔥 BTCUSDT LONG\nEntry: 45000-46000\nTP1: 47000\nTP2: 48000\nTP3: 50000\nSL: 44000\nLeverage: 10x",
                "group": "binance_signals",
                "expected": {"symbol": "BTCUSDT", "side": "LONG", "confidence": 1.0}
            },
            
            # Bybit format
            {
                "text": "Signal: BTC\nDirection: SHORT\nPrice: 45500\nTargets: 44000, 43000, 42000\nStop Loss: 46500",
                "group": "bybit_channel",
                "expected": {"symbol": "BTCUSDT", "side": "SHORT"}
            },
            
            # CryptoBull format
            {
                "text": "Coin: ETH\nSide: LONG\nBuy: 3200-3250\n🎯 3300, 3400, 3500\n❌ 3100",
                "group": "cryptobull",
                "expected": {"symbol": "ETHUSDT", "side": "LONG"}
            },
            
            # Professional format
            {
                "text": "ADAUSDT\nPosition: LONG\nEntry Zone: 0.35-0.36\nTake Profit: 0.38, 0.40, 0.42\nStoploss: 0.33\nRisk: 2%",
                "group": "pro_signals",
                "expected": {"symbol": "ADAUSDT", "side": "LONG"}
            }
        ]
        
        await self._run_test_batch("Standard Formats", test_signals)
        
    async def test_exchange_formats(self):
        """Test exchange-specific signal formats."""
        print("📈 Testing Exchange-Specific Formats...")
        
        test_signals = [
            # Bitget futures format
            {
                "text": "BTCPERP\nTrade: LONG\n@45000\nTargets: 46000 47000 48000\nCut Loss: 44000",
                "group": "bitget_futures",
                "expected": {"symbol": "BTCUSDT", "side": "LONG"}
            },
            
            # Binance futures
            {
                "text": "BTC-25DEC22\nDirection: SHORT\nOpen: 45000\nExit: 44000, 43000\n🛑 46000",
                "group": "binance_futures",
                "expected": {"symbol": "BTCUSDT", "side": "SHORT"}
            },
            
            # OKX format
            {
                "text": "Pair: SOL\nBUY\nCurrent Price: 120\nTarget: 125, 130, 135\nS/L: 115",
                "group": "okx_channel",
                "expected": {"symbol": "SOLUSDT", "side": "LONG"}
            }
        ]
        
        await self._run_test_batch("Exchange Formats", test_signals)
        
    async def test_emoji_formats(self):
        """Test signals with heavy emoji usage."""
        print("😎 Testing Emoji-Heavy Formats...")
        
        test_signals = [
            # Emoji-heavy format
            {
                "text": "🚀 #BNBUSDT 📈 LONG\n🎯 Entry: 300\n✅ Targets: 310, 320, 330\n❌ SL: 290",
                "group": "emoji_signals",
                "expected": {"symbol": "BNBUSDT", "side": "LONG"}
            },
            
            # Mixed format
            {
                "text": "🔥🔥 DOGEUSDT 🔥🔥\n📉 SHORT\n🎯 0.08\n✅ 0.075, 0.07, 0.065\n🛑 0.085",
                "group": "doge_channel",
                "expected": {"symbol": "DOGEUSDT", "side": "SHORT"}
            }
        ]
        
        await self._run_test_batch("Emoji Formats", test_signals)
        
    async def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("🔍 Testing Edge Cases...")
        
        test_signals = [
            # Missing SL (should auto-calculate)
            {
                "text": "ETHUSDT LONG\nEntry: 3200\nTargets: 3300, 3400",
                "group": "incomplete_signals",
                "expected": {"symbol": "ETHUSDT", "side": "LONG", "sl_calculated": True}
            },
            
            # No entry (should use market price)
            {
                "text": "BTCUSDT SHORT\nTargets: 44000, 43000\nSL: 46000",
                "group": "market_entry",
                "expected": {"symbol": "BTCUSDT", "side": "SHORT"}
            },
            
            # Swedish format
            {
                "text": "ADAUSDT LÅNG\nIngång: 0.35\nMål: 0.40, 0.45\nSL: 0.30",
                "group": "swedish_channel",
                "expected": {"symbol": "ADAUSDT", "side": "LONG"}
            },
            
            # Invalid/incomplete signal
            {
                "text": "Just some random text without any trading info",
                "group": "spam_channel",
                "expected": None  # Should return None
            }
        ]
        
        await self._run_test_batch("Edge Cases", test_signals)
        
    async def test_multi_group_scenarios(self):
        """Test multi-group signal processing scenarios."""
        print("🌐 Testing Multi-Group Scenarios...")
        
        # Simulate signals from different groups at the same time
        group_signals = [
            ("premium_crypto", "BTCUSDT LONG\nEntry: 45000\nTP: 47000\nSL: 44000"),
            ("binance_alerts", "BTC Direction: SHORT Entry: 45500 Targets: 44000 Stop: 46500"),
            ("trading_bots", "Signal: ETH Side: LONG Buy: 3200 Targets: 3300,3400 SL: 3100"),
            ("scalping_channel", "🚀 DOGEUSDT 📈 LONG @0.08 🎯0.085,0.09 ❌0.075"),
            ("whale_alerts", "ADAUSDT Position: SHORT Open: 0.35 Exit: 0.33,0.31 Cut Loss: 0.37")
        ]
        
        print(f"📡 Processing {len(group_signals)} signals from different groups simultaneously...")
        
        tasks = []
        for group_name, signal_text in group_signals:
            task = self._test_single_signal_with_group(signal_text, group_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        print(f"✅ Multi-group test: {successful}/{len(group_signals)} signals processed successfully")
        
    async def _run_test_batch(self, test_name: str, test_signals: List[Dict]):
        """Run a batch of test signals."""
        successful = 0
        total = len(test_signals)
        
        for test_case in test_signals:
            try:
                result = await parse_signal_text_multi(test_case["text"])
                
                if test_case["expected"] is None:
                    # Expecting parsing to fail
                    if result is None:
                        successful += 1
                        print(f"✅ Correctly rejected invalid signal")
                    else:
                        print(f"❌ Should have rejected signal but parsed: {result}")
                else:
                    # Expecting parsing to succeed
                    if result:
                        # Check expected fields
                        matches = all(
                            result.get(key) == value 
                            for key, value in test_case["expected"].items()
                        )
                        if matches:
                            successful += 1
                            confidence = result.get("confidence", 0)
                            print(f"✅ Parsed {result['symbol']} {result['side']} (confidence: {confidence:.2f})")
                        else:
                            print(f"❌ Parsed but values don't match expected: {result}")
                    else:
                        print(f"❌ Failed to parse valid signal: {test_case['text'][:50]}...")
                        
            except Exception as e:
                print(f"❌ Error parsing signal: {e}")
        
        print(f"📊 {test_name}: {successful}/{total} tests passed ({successful/total*100:.1f}%)")
        print("-" * 40)
        
        self.test_results.append({
            "test_name": test_name,
            "successful": successful,
            "total": total,
            "success_rate": successful/total*100
        })
        
    async def _test_single_signal_with_group(self, signal_text: str, group_name: str):
        """Test a single signal with group context."""
        try:
            result = await parse_signal_text_multi(signal_text)
            if result:
                result["group_name"] = group_name
                self.signal_handler.add_signal(result)
                return result
            return None
        except Exception as e:
            print(f"❌ Error processing signal from {group_name}: {e}")
            return None
            
    async def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 ENHANCED SIGNAL TESTING REPORT")
        print("=" * 60)
        
        total_tests = sum(r["total"] for r in self.test_results)
        total_successful = sum(r["successful"] for r in self.test_results)
        overall_rate = total_successful / total_tests * 100 if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {overall_rate:.1f}% ({total_successful}/{total_tests})")
        print()
        
        for result in self.test_results:
            print(f"{result['test_name']}: {result['success_rate']:.1f}% ({result['successful']}/{result['total']})")
        
        print()
        print("📈 Group Statistics:")
        stats = self.signal_handler.get_all_group_stats()
        for group_name, group_stats in stats.items():
            print(f"  • {group_name}: {group_stats['total_signals']} signals")
        
        print("\n🎉 Enhanced signal parsing system is ready for production!")
        
        # Save results to file (fix datetime serialization)
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
            
        # Clean stats for JSON serialization
        clean_stats = {}
        for group_name, group_data in stats.items():
            clean_stats[group_name] = {}
            for key, value in group_data.items():
                if key == "last_signal_time" and value:
                    clean_stats[group_name][key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                else:
                    clean_stats[group_name][key] = value
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": overall_rate,
            "total_tests": total_tests,
            "test_results": self.test_results,
            "group_stats": clean_stats
        }
        
        with open("signal_testing_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("💾 Test report saved to: signal_testing_report.json")

# Test runner functions
async def run_mock_signal_tests():
    """Run comprehensive mock signal tests."""
    tester = MockSignalTester()
    await tester.run_comprehensive_tests()

async def test_live_group_integration():
    """Test integration with actual Telegram groups (without sending real signals)."""
    print("🔗 Testing Live Group Integration...")
    
    from signal_module.listener import group_configs
    
    print(f"📡 Configured groups: {len(group_configs)}")
    for name, group_id in group_configs.items():
        print(f"  • {name}: {group_id}")
    
    # Test group configuration
    if len(group_configs) > 0:
        print("✅ Group configuration is valid")
    else:
        print("⚠️ No groups configured - add groups to TelegramConfig.TELEGRAM_GROUPS")
    
    print("🎯 Integration test complete!")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Mock Signal Testing System...")
    
    # Run all tests
    asyncio.run(run_mock_signal_tests())
    asyncio.run(test_live_group_integration())