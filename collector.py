from telethon import TelegramClient, events
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION_STRING
from database import save_message, get_channels, add_channel

_client: TelegramClient = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        _client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    return _client


async def resolve_and_fetch(identifier: str, limit: int = 200):
    """Resolve a channel by username/link and fetch its recent messages."""
    client = get_client()
    entity = await client.get_entity(identifier)
    count = 0
    async for message in client.iter_messages(entity, limit=limit):
        if message.text:
            await save_message(
                channel_id=entity.id,
                message_id=message.id,
                text=message.text,
                date=str(message.date),
            )
            count += 1
    return entity, count


async def sync_all_channels():
    """Re-sync recent messages from all tracked channels."""
    channels = await get_channels()
    total = 0
    errors = []
    for channel_id, channel_name, username in channels:
        try:
            identifier = username if username else channel_id
            _, count = await resolve_and_fetch(identifier, limit=100)
            total += count
        except Exception as e:
            errors.append(f"{channel_name}: {e}")
    return total, errors


async def start_listener():
    """Start Telethon and listen for new messages in tracked channels."""
    client = get_client()
    await client.start()
    print("Telethon listener started.")

    @client.on(events.NewMessage)
    async def handler(event):
        channels = await get_channels()
        tracked_ids = {ch[0] for ch in channels}
        if event.chat_id in tracked_ids and event.text:
            await save_message(
                channel_id=event.chat_id,
                message_id=event.id,
                text=event.text,
                date=str(event.date),
            )

    await client.run_until_disconnected()
