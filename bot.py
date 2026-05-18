from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, AUTHORIZED_USER_ID
from database import add_channel, get_channels, remove_channel, search_messages, get_recent_messages, get_stats
from ai import ask
from collector import resolve_and_fetch, sync_all_channels

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def authorized(user_id: int) -> bool:
    return AUTHORIZED_USER_ID == 0 or user_id == AUTHORIZED_USER_ID


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if not authorized(message.from_user.id):
        return
    await message.answer(
        "🧠 *Knowledge Base Bot*\n\n"
        "I collect messages from Telegram channels and let you ask questions about them using AI.\n\n"
        "*Commands:*\n"
        "`/add @channel` — Add a channel to monitor\n"
        "`/remove @channel` — Remove a channel\n"
        "`/list` — Show tracked channels\n"
        "`/sync` — Sync latest messages\n"
        "`/stats` — Database stats\n\n"
        "Just type any question to search the knowledge base 💬",
        parse_mode="Markdown",
    )


@dp.message(Command("add"))
async def cmd_add(message: Message):
    if not authorized(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: `/add @channelname`", parse_mode="Markdown")
        return

    identifier = parts[1].strip()
    status = await message.answer(f"⏳ Fetching `{identifier}`...", parse_mode="Markdown")

    try:
        entity, count = await resolve_and_fetch(identifier, limit=200)
        username = getattr(entity, "username", None) or ""
        channel_name = getattr(entity, "title", str(entity.id))
        await add_channel(channel_id=entity.id, channel_name=channel_name, username=username)
        await status.edit_text(
            f"✅ *{channel_name}* added!\n📥 Fetched {count} messages.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`", parse_mode="Markdown")


@dp.message(Command("remove"))
async def cmd_remove(message: Message):
    if not authorized(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: `/remove @channelname`", parse_mode="Markdown")
        return

    identifier = parts[1].strip()
    try:
        from collector import get_client
        client = get_client()
        entity = await client.get_entity(identifier)
        await remove_channel(entity.id)
        await message.answer(f"🗑️ Channel removed and its messages deleted.")
    except Exception as e:
        await message.answer(f"❌ Error: `{e}`", parse_mode="Markdown")


@dp.message(Command("list"))
async def cmd_list(message: Message):
    if not authorized(message.from_user.id):
        return
    channels = await get_channels()
    if not channels:
        await message.answer("No channels tracked yet. Use `/add @channel`.", parse_mode="Markdown")
        return
    lines = ["*Tracked Channels:*\n"]
    for _, name, username in channels:
        lines.append(f"• {name}" + (f" (@{username})" if username else ""))
    await message.answer("\n".join(lines), parse_mode="Markdown")


@dp.message(Command("sync"))
async def cmd_sync(message: Message):
    if not authorized(message.from_user.id):
        return
    status = await message.answer("⏳ Syncing all channels...")
    total, errors = await sync_all_channels()
    text = f"✅ Synced *{total}* new messages."
    if errors:
        text += "\n\n⚠️ *Errors:*\n" + "\n".join(errors)
    await status.edit_text(text, parse_mode="Markdown")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if not authorized(message.from_user.id):
        return
    ch_count, msg_count = await get_stats()
    await message.answer(
        f"📊 *Stats*\n\nChannels: {ch_count}\nMessages stored: {msg_count:,}",
        parse_mode="Markdown",
    )


@dp.message()
async def handle_question(message: Message):
    if not authorized(message.from_user.id):
        return
    if not message.text or message.text.startswith("/"):
        return

    # status = await message.answer("🤔 Searching knowledge base...")
    results = await search_messages(message.text, limit=15)
    if not results:
        results = await get_recent_messages(limit=20)

    answer = await ask(message.text, results)
    await status.edit_text(answer)


async def start_bot():
    print("Bot polling started.")
    await dp.start_polling(bot)
