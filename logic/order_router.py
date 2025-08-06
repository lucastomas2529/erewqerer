from typing import Optional
from utils.telegram_logger import send_telegram_log


def get_order_type_based_on_ema(current_price: float, ema_value: float) -> str:
    """
    Returnerar 'Market' om priset rör sig snabbt över EMA, annars 'Limit'.
    Enkel EMA-baserad logik (1% diff).
    """
    if abs(current_price - ema_value) / ema_value > 0.01:
        return "Market"
    return "Limit"

from typing import Optional
from utils.telegram_logger import send_telegram_log


async def place_conditional_order(
    client,
    symbol: str,
    side: str,
    trigger_price: float,
    price: float,
    qty: float,
    leverage: float,
    sl: float,
    tp: Optional[float] = None,
    time_in_force: str = "GoodTillCancel"
):
    """
    Skickar en villkorad order med dynamisk ordertyp baserat på EMA.
    """
    try:
        # 🔍 EMA-baserad ordertyp (kan ersättas med riktig EMA-logik)
        ema_value = price * 0.995
        order_type = get_order_type_based_on_ema(price, ema_value)

        response = await client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            price=round(price, 2),
            triggerDirection=1,
            triggerPrice=round(trigger_price, 2),
            takeProfit=tp,
            stopLoss=sl,
            base_price_type="LastPrice",
            timeInForce=time_in_force,
            isLeverage=True,
            leverage=leverage,
            reduceOnly=False,
            closeOnTrigger=False
        )

        order_id = response["data"]["orderId"]
        await send_telegram_log(
            f"📦 Villkorad Bitget-order skickad:\nSymbol: {symbol}, Side: {side}, Qty: {qty}, Price: {price}, Trigger: {trigger_price}, SL: {sl}, TP: {tp}, Lev: {leverage}, ID: {order_id}",
            tag="order"
        )
        return order_id

    except Exception as e:
        await send_telegram_log(f"❌ Fel i place_conditional_order: {e}", tag="error")
        return None


def fallback_to_limit_order(
    client,
    symbol: str,
    side: str,
    qty: float,
    price: float
):
    """
    Om market order misslyckas, skicka limit-order som fallback.
    """
    try:
        result = client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type="Limit",
            price=round(price, 2),
            qty=qty,
            time_in_force="PostOnly",
            reduce_only=False,
            position_idx=0
        )
        send_telegram_log(
            f"🟡 Market misslyckades – Fallback limit order skickad på {symbol}@{price}",
            tag="entry"
        )
        return result
    except Exception as e:
        send_telegram_log(f"❌ Fallback-limit-order misslyckades: {e}", tag="error")
        return None


def cancel_order(
    client,
    symbol: str,
    order_id: str
):
    """
    Avbryter en enskild order.
    """
    try:
        result = client.cancel_order(
            category="linear",
            symbol=symbol,
            order_id=order_id
        )
        send_telegram_log(f"🚫 Order avbruten – {symbol} (ID: {order_id})", tag="error")
        return result
    except Exception as e:
        send_telegram_log(f"❌ Misslyckades avbryta order: {e}", tag="error")
        return None


def modify_order(
    client,
    symbol: str,
    order_id: str,
    new_price: float,
    new_qty: float
):
    """
    Ändrar en existerande order (pris och mängd).
    """
    try:
        result = client.amend_order(
            category="linear",
            symbol=symbol,
            order_id=order_id,
            price=new_price,
            qty=new_qty
        )
        send_telegram_log(
            f"✏️ Order ändrad – {symbol}\n📍 Pris: {new_price}, Qty: {new_qty}",
            tag="entry"
        )
        return result
    except Exception as e:
        send_telegram_log(f"❌ Kunde inte ändra order: {e}", tag="error")
        return None
