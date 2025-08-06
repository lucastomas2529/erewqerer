# generate_daily_report.py

from datetime import datetime
from utils.telegram_logger import send_telegram_log, send_group_specific_log
from core.api import get_trade_history
from core.api import get_trade_history_log
from signal_module.signal_handler import signal_handler

# ✅ Hämtar verklig tradedata via API
trade_log = get_trade_history_log()

def analyze_trades(trades):
    wins = [t for t in trades if t["result"] == "win"]
    losses = [t for t in trades if t["result"] == "loss"]
    total_pnl = sum(t["pnl_pct"] for t in trades)
    avg_pnl = total_pnl / len(trades) if trades else 0
    winrate = len(wins) / len(trades) * 100 if trades else 0

    return {
        "total": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl": round(avg_pnl, 2),
        "winrate": round(winrate, 2),
    }

def analyze_signals_by_group():
    """Analyze signals by group using the signal handler."""
    group_stats = signal_handler.get_all_group_stats()
    
    analysis = {}
    for group_name, stats in group_stats.items():
        signals = signal_handler.get_signals_by_group(group_name)
        
        # Analyze signal quality
        valid_signals = [s for s in signals if s.get("symbol") and s.get("side")]
        invalid_signals = len(signals) - len(valid_signals)
        
        analysis[group_name] = {
            "total_signals": len(signals),
            "valid_signals": len(valid_signals),
            "invalid_signals": invalid_signals,
            "success_rate": round((len(valid_signals) / len(signals) * 100) if signals else 0, 1),
            "last_signal": stats.get("last_signal_time"),
            "symbols": list(set(s.get("symbol") for s in valid_signals if s.get("symbol"))),
            "sides": list(set(s.get("side") for s in valid_signals if s.get("side")))
        }
    
    return analysis

async def generate_daily_report():
    """Generate daily report with group-specific analysis."""
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get signal analysis by group
    signal_analysis = analyze_signals_by_group()
    
    # Get trade analysis (if available)
    try:
        trades = get_trade_history()
        trade_analysis = analyze_trades(trades)
    except:
        trade_analysis = None

    # Generate report header
    header = f"📅 DAGLIG RAPPORT – {today}\n"
    header += f"📡 Aktiva grupper: {len(signal_analysis)}\n\n"

    # Group-specific sections
    sections = ""
    total_signals = 0
    total_valid = 0
    
    for group_name, analysis in signal_analysis.items():
        sections += f"📡 **{group_name}**\n"
        sections += f"   • Totalt: {analysis['total_signals']} signaler\n"
        sections += f"   • Giltiga: {analysis['valid_signals']} signaler\n"
        sections += f"   • Ogiltiga: {analysis['invalid_signals']} signaler\n"
        sections += f"   • Framgångsgrad: {analysis['success_rate']}%\n"
        
        if analysis['symbols']:
            sections += f"   • Symboler: {', '.join(analysis['symbols'][:5])}\n"
        
        if analysis['last_signal']:
            last_time = analysis['last_signal'].strftime("%H:%M")
            sections += f"   • Senaste signal: {last_time}\n"
        
        sections += "\n"
        
        total_signals += analysis['total_signals']
        total_valid += analysis['valid_signals']

    # Summary section
    summary = f"📊 **SAMMANFATTNING**\n"
    summary += f"   • Totalt signaler: {total_signals}\n"
    summary += f"   • Totalt giltiga: {total_valid}\n"
    summary += f"   • Genomsnittlig framgångsgrad: {round((total_valid / total_signals * 100) if total_signals else 0, 1)}%\n\n"

    # Trade analysis section (if available)
    if trade_analysis:
        summary += f"💰 **TRADING RESULTAT**\n"
        summary += f"   • Totalt trades: {trade_analysis['total']}\n"
        summary += f"   • Vinster: {trade_analysis['wins']}\n"
        summary += f"   • Förluster: {trade_analysis['losses']}\n"
        summary += f"   • Vinstprocent: {trade_analysis['winrate']}%\n"
        summary += f"   • Total P&L: {trade_analysis['total_pnl']}%\n"
        summary += f"   • Genomsnittlig P&L: {trade_analysis['avg_pnl']}%\n\n"

    # Final message
    message = f"{header}{sections}{summary}"
    
    # Send the report
    await send_telegram_log(message, tag="rapport")
    
    # Send individual group reports if there are issues
    for group_name, analysis in signal_analysis.items():
        if analysis['invalid_signals'] > 0:
            await send_group_specific_log(
                group_name,
                f"⚠️ {analysis['invalid_signals']} ogiltiga signaler idag. Kontrollera signalformat.",
                tag="warning"
            )

async def generate_group_specific_report(group_name: str):
    """Generate a report for a specific group."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    signals = signal_handler.get_signals_by_group(group_name)
    stats = signal_handler.get_group_stats(group_name)
    
    if not signals:
        await send_group_specific_log(
            group_name,
            f"📊 Inga signaler från {group_name} idag ({today})",
            tag="report"
        )
        return
    
    # Analyze signals
    valid_signals = [s for s in signals if s.get("symbol") and s.get("side")]
    invalid_signals = len(signals) - len(valid_signals)
    
    # Generate report
    header = f"📊 {group_name.upper()} RAPPORT – {today}\n\n"
    
    stats_section = f"📈 **STATISTIK**\n"
    stats_section += f"   • Totalt signaler: {len(signals)}\n"
    stats_section += f"   • Giltiga signaler: {len(valid_signals)}\n"
    stats_section += f"   • Ogiltiga signaler: {invalid_signals}\n"
    stats_section += f"   • Framgångsgrad: {round((len(valid_signals) / len(signals) * 100) if signals else 0, 1)}%\n\n"
    
    # Recent signals
    recent_section = f"📨 **SENASTE SIGNALER**\n"
    for signal in signals[-5:]:  # Last 5 signals
        symbol = signal.get("symbol", "Unknown")
        side = signal.get("side", "Unknown")
        timestamp = signal.get("timestamp", "Unknown")
        recent_section += f"   • {symbol} {side} ({timestamp})\n"
    
    message = f"{header}{stats_section}{recent_section}"
    
    await send_group_specific_log(group_name, message, tag="report")

# TEST
if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_daily_report())
