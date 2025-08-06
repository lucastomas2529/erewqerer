import json
import threading
import time
import websocket
from utils.telegram_logger import send_telegram_log
from config.settings import ExchangeConfig

class BitgetWebSocketManager:
    def __init__(self, symbol):
        self.symbol = symbol
        self.ws = None
        self.reconnect_interval = 10
        self.subscribed = False
        self.stop_event = threading.Event()

    def connect(self):
        ws_url = "wss://ws.bitget.com/mix/v1/stream"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_open(self, ws):
        send_telegram_log("✅ WebSocket-anslutning till Bitget etablerad.")
        self.subscribe_to_positions()

    def subscribe_to_positions(self):
        channel = f"positions"
        args = [{
            "instType": "UMCBL",
            "channel": channel,
            "instId": self.symbol
        }]
        subscribe_msg = {
            "op": "subscribe",
            "args": args
        }
        try:
            self.ws.send(json.dumps(subscribe_msg))
            self.subscribed = True
        except Exception as e:
            send_telegram_log(f"❌ Fel vid prenumeration: {e}")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "event" in data and data["event"] == "subscribe":
                send_telegram_log("📡 Prenumeration bekräftad.")
            elif "data" in data:
                self.handle_data(data["data"])
        except Exception as e:
            send_telegram_log(f"⚠️ Fel vid meddelandehantering: {e}")

    def handle_data(self, data):
        # Anpassa efter behov
        send_telegram_log(f"📈 Position uppdaterad: {data}")

    def on_error(self, ws, error):
        send_telegram_log(f"⚠️ WebSocket-fel: {error}")
        self.reconnect()

    def on_close(self, ws, close_status_code, close_msg):
        send_telegram_log("🔌 WebSocket-anslutning stängdes.")
        self.reconnect()

    def reconnect(self):
        if self.stop_event.is_set():
            return
        send_telegram_log(f"🔁 Försöker återansluta om {self.reconnect_interval} sekunder...")
        time.sleep(self.reconnect_interval)
        self.connect()

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.close()

