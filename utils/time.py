import asyncio
import random
from datetime import datetime

def get_timestamp() -> str:
    """
    Returnerar aktuell UTC-tid som ISO-formaterad sträng.
    """
    return datetime.utcnow().isoformat()

from config.settings import REENTRY_DELAY_SEC

async def wait_after_sl(min_seconds=None, max_seconds=None) -> int:
    """
    Väntar slumpmässigt mellan konfigurerade sekunder efter SL innan re-entry.
    Returnerar faktisk väntetid i sekunder.
    """
    if min_seconds is None:
        min_seconds = REENTRY_DELAY_SEC[0]
    if max_seconds is None:
        max_seconds = REENTRY_DELAY_SEC[1]
    delay = random.randint(min_seconds, max_seconds)
    await asyncio.sleep(delay)
    return delay
