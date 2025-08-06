# startup.py - Clean startup script for reports and trading loop

import asyncio
from generate.daily_report import analyze_trades as analyze_daily
from generate.weekly_report import analyze_trades as analyze_weekly
from monitor.loop_manager import trading_loop

async def run_startup():
    """Run startup tasks including reports and trading loop."""
    print("🚀 Starting trading bot components...")
    
    # Run report analysis
    try:
        print("📊 Running daily report analysis...")
        await analyze_daily()  # Make async if needed
        
        print("📈 Running weekly report analysis...")
        await analyze_weekly()  # Make async if needed
        
        print("✅ Reports completed successfully")
    except Exception as e:
        print(f"⚠️ Error running reports: {e}")
    
    # Start trading loop
    try:
        print("🔄 Starting trading loop...")
        await trading_loop()
    except Exception as e:
        print(f"❌ Error in trading loop: {e}")

if __name__ == "__main__":
    asyncio.run(run_startup())
