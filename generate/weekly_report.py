# generate_weekly_report.py

from datetime import datetime
from utils.telegram_logger import send_telegram_log
from core.api import get_trade_history
from core.api import get_trade_history_log



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


async def generate_weekly_report():
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    # MOCKAD FELDATA – ersätt detta med verklig validering senare
    error_data = {
        "Crypto Raketen": [
            "BTC – Ogiltig symbol",
            "XRP – Låg balans",
            "DOGE – Duplicerad trade",
        ],
        "Smart Crypto": [
            "SOL – Saknar SL",
        ],
        "Lux Leak": [
            "ADA – API rate limit",
            "DOGE – TP utanför tillåtet intervall",
        ],
    }

    # Beräkna totalsumma per leverantör
    totals = {k: len(v) for k, v in error_data.items()}
    total_errors = sum(totals.values())

    # Veckonummer
    from datetime import date, timedelta
    today_date = date.today()
    start_of_week = today_date - timedelta(days=today_date.weekday() + 7)  # föregående måndag
    end_of_week = start_of_week + timedelta(days=6)
    week_number = start_of_week.isocalendar()[1]

    header = f"📊 VECKOVIS FELRAPPORT – v.{week_number} ({start_of_week} till {end_of_week})\n"

    sections = ""
    for source, errors in error_data.items():
        sections += f"\n📡 {source}\n"
        if errors:
            for err in errors:
                sections += f"❌ {err}\n"
        else:
            sections += "-\n"
        sections += f"\nTotalt: {len(errors)} fel\n"

    message = f"{header}{sections}\n📌 Totalt alla leverantörer: {total_errors} fel"

    await send_telegram_log(message, tag="rapport")



# TEST
if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_weekly_report())
