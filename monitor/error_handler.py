# error_handler.py – Felhantering och notifiering
import logging
import traceback
from utils.telegram_logger import send_telegram_log


def handle_exception(e: Exception, context: str = "okänd") -> None:
    """
    Loggar och rapporterar ett fel till Telegram.
    """
    error_msg = f"❌ Fel i {context}: {str(e)}"
    stack_trace = traceback.format_exc()

    # Logga till konsol / fil
    logging.error(error_msg)
    logging.debug(stack_trace)

    # Skicka till Telegram
    try:
        send_telegram_log(f"{error_msg}\n```{stack_trace}```", tag="error")
    except Exception as te:
        logging.error(f"⚠️ Kunde inte skicka felmeddelande till Telegram: {te}")

