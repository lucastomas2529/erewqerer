from telethon import TelegramClient, events
from signal_module.multi_format_parser import parse_signal_text_multi
from signal_module.signal_queue import signal_queue
from signal_module.spam_filter import preprocess_telegram_message
from signal_module.group_monitor import record_signal_processing, record_group_error
from config.settings import TelegramConfig
from core.admin_commands import admin_handler
from core.reporting_system import reporting_system
import asyncio
import time
from typing import Dict, List

# Use centralized Telegram configuration
api_id = TelegramConfig.TELEGRAM_API_ID
api_hash = TelegramConfig.TELEGRAM_API_HASH
session_name = "tradingbot"

client = TelegramClient(session_name, api_id, api_hash)

# Get all group IDs and names from TELEGRAM_GROUPS dictionary
group_configs = TelegramConfig.TELEGRAM_GROUPS
print(f"📡 Monitoring {len(group_configs)} Telegram groups:")
for name, group_id in group_configs.items():
    print(f"  • {name}: {group_id}")

# Store active listeners for management
active_listeners: List[asyncio.Task] = []

async def handle_group_message(event, group_name: str):
    """Handle incoming message from a specific group with spam filtering and admin commands."""
    start_time = time.time()
    try:
        chat_id = event.chat_id
        text = event.message.message
        message_id = event.message.id
        user_id = event.sender_id
        username = event.sender.username if event.sender else None
        
        print(f"📨 Raw message received from {group_name} ({chat_id}) by {username} ({user_id}): {text[:100]}...")
        
        # Check for admin commands first
        if text.startswith('/'):
            try:
                # Parse command and arguments
                parts = text.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Handle admin command
                admin_response = await admin_handler.handle_command(user_id, command, args)
                if admin_response:
                    # Send admin response back to the chat
                    try:
                        from utils.telegram_logger import send_telegram_log
                        await send_telegram_log(
                            admin_response,
                            group_name=group_name,
                            tag="admin_command"
                        )
                        print(f"👑 Admin command processed from {username}: {text[:50]}...")
                        return  # Don't process as signal
                    except Exception as e:
                        print(f"⚠️ Failed to send admin response for {group_name}: {e}")
            except Exception as e:
                print(f"❌ Error processing admin command from {username}: {e}")
        
        # Apply spam filtering and preprocessing
        is_valid, sanitized_text, filter_info = await preprocess_telegram_message(
            text=text,
            source=group_name,
            message_id=message_id,
            chat_id=chat_id
        )
        
        if not is_valid:
            print(f"🛡️ Message blocked by spam filter from {group_name}: {filter_info.get('reason', 'unknown')}")
            
            # Log blocked message for debugging
            try:
                from utils.telegram_logger import send_telegram_log
                await send_telegram_log(
                    f"🛡️ Message blocked from {group_name}: {filter_info.get('reason', 'unknown')} - {text[:100]}...",
                    group_name=group_name,
                    tag="spam_filter"
                )
            except Exception as e:
                print(f"⚠️ Failed to send spam filter log for {group_name}: {e}")
            
            return
        
        print(f"✅ Message passed spam filter from {group_name}: {sanitized_text[:100]}...")
        
        # Parse the sanitized signal
        parsed = await parse_signal_text_multi(sanitized_text)
        processing_time = time.time() - start_time
        
        if parsed:
            # Enhance signal with source information and filter metadata
            parsed["group_name"] = group_name
            parsed["source_group"] = group_name  # Backward compatibility
            parsed["source_chat_id"] = chat_id
            parsed["timestamp"] = event.message.date.isoformat()
            parsed["message_id"] = message_id
            parsed["original_text"] = text
            parsed["sanitized_text"] = sanitized_text
            parsed["filter_info"] = filter_info
            parsed["processing_time"] = processing_time
            
            # Log signal with reporting system
            await reporting_system.log_signal({
                'group_name': group_name,
                'signal_text': sanitized_text,
                'parsed_data': parsed,
                'processing_time': processing_time,
                'status': 'processed'
            })
            
            await signal_queue.put(parsed)
            
            # Record successful signal processing for monitoring
            await record_signal_processing(group_name, parsed, processing_time)
            
            confidence = parsed.get("confidence", 0.0)
            print(f"✅ Signal parsed from {group_name}: {parsed.get('symbol', 'Unknown')} {parsed.get('side', 'Unknown')} (confidence: {confidence:.2f})")
            
            # Log to Telegram for debugging
            try:
                from utils.telegram_logger import send_telegram_log
                await send_telegram_log(
                    f"📨 High-quality signal from {group_name}: {parsed.get('symbol', 'Unknown')} {parsed.get('side', 'Unknown')} (confidence: {confidence:.2f})",
                    group_name=group_name
                )
            except Exception as e:
                print(f"⚠️ Failed to send Telegram log for {group_name}: {e}")
        else:
            # Record failed parsing for monitoring
            await record_signal_processing(group_name, None, processing_time)
            await record_group_error(group_name, "parse")
            
            print(f"❌ Could not parse signal from {group_name} (processed in {processing_time:.3f}s)")
            
            # Log unparseable signals for debugging
            try:
                from utils.telegram_logger import send_telegram_log
                await send_telegram_log(
                    f"❌ Unparseable signal from {group_name}: {sanitized_text[:200]}",
                    group_name=group_name
                )
            except Exception as e:
                print(f"⚠️ Failed to send error log for {group_name}: {e}")
                
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Record error for monitoring
        await record_group_error(group_name, "connection")
        
        print(f"❌ Error handling message from {group_name}: {e} (processed in {processing_time:.3f}s)")
        try:
            from utils.telegram_logger import send_telegram_log
            await send_telegram_log(
                f"🚨 Error processing signal from {group_name}: {str(e)[:100]}",
                group_name=group_name
            )
        except:
            pass

def create_group_handler(group_name: str, group_id: int):
    """Create a message handler for a specific group."""
    @client.on(events.NewMessage(chats=[group_id]))
    async def group_specific_handler(event):
        await handle_group_message(event, group_name)
    
    return group_specific_handler

async def start_group_listeners():
    """Start listeners for all configured groups."""
    global active_listeners
    
    # Create handlers for each group
    for group_name, group_id in group_configs.items():
        try:
            handler = create_group_handler(group_name, group_id)
            print(f"✅ Listener started for {group_name} ({group_id})")
        except Exception as e:
            print(f"❌ Failed to start listener for {group_name}: {e}")
            try:
                from utils.telegram_logger import send_telegram_log
                await send_telegram_log(f"❌ Failed to start listener for {group_name}: {e}")
            except:
                pass

async def stop_group_listeners():
    """Stop all active group listeners."""
    global active_listeners
    
    for listener in active_listeners:
        if not listener.done():
            listener.cancel()
            try:
                await listener
            except asyncio.CancelledError:
                pass
    
    active_listeners.clear()
    print("🛑 All group listeners stopped")

async def start_telegram_listener(signal_handler=None):
    """Start the Telegram listener with support for multiple groups."""
    try:
        await client.start()
        print("✅ Telegram client started")
        
        # Start listeners for all groups
        await start_group_listeners()
        
        print(f"🎯 Monitoring {len(group_configs)} Telegram groups concurrently")
        print("📡 Groups:", ", ".join(group_configs.keys()))
        
        # Keep the client running
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Error in Telegram listener: {e}")
        try:
            from utils.telegram_logger import send_telegram_log
            await send_telegram_log(f"🚨 Telegram listener error: {e}")
        except:
            pass
    finally:
        await stop_group_listeners()
        await client.disconnect()

# Backward compatibility function
async def handler(event):
    """Legacy handler for backward compatibility."""
    chat_id = event.chat_id
    group_name = TelegramConfig.get_group_name(chat_id)
    await handle_group_message(event, group_name)

# Register legacy handler for all groups
@client.on(events.NewMessage(chats=list(group_configs.values())))
async def legacy_handler(event):
    await handler(event)
