# forward_signals_userbot.py

import asyncio
from telethon import TelegramClient, events
from telethon.types import PeerChannel
from config.settings import TelegramConfig

# 🔐 Logga in med ditt Telegram-användarkonto
api_id = TelegramConfig.TELEGRAM_API_ID
api_hash = TelegramConfig.TELEGRAM_API_HASH

SOURCE_CHANNELS = TelegramConfig.TELEGRAM_SIGNAL_CHANNEL_IDS
DESTINATION_CHANNEL = TelegramConfig.DESTINATION_CHANNEL_ID

# 📡 Skapa klientsession – första gången får du ange kod från Telegram
client = TelegramClient("forward_session", api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_handler(event):
    try:
        message = event.message.message
        if not message:
            print("⚠️ Tomt meddelande ignorerat.")
            return

        print(f"🔁 Vidarebefordrar meddelande från {event.chat_id}")
        await client.send_message(PeerChannel(DESTINATION_CHANNEL), message)

    except Exception as e:
        print(f"❌ Fel vid vidarebefordran: {e}")

async def main():
    await client.start()
    print("📡 Telegram UserBot aktiv – lyssnar på signal-kanaler...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
