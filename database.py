import aiosqlite

DB_PATH = "knowledge.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER UNIQUE,
                channel_name TEXT,
                username TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                message_id INTEGER,
                text TEXT,
                date TEXT,
                UNIQUE(channel_id, message_id)
            )
        """)
        await db.commit()


async def add_channel(channel_id: int, channel_name: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO channels (channel_id, channel_name, username) VALUES (?, ?, ?)",
            (channel_id, channel_name, username)
        )
        await db.commit()


async def remove_channel(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.execute("DELETE FROM messages WHERE channel_id = ?", (channel_id,))
        await db.commit()


async def get_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT channel_id, channel_name, username FROM channels"
        ) as cursor:
            return await cursor.fetchall()


async def save_message(channel_id: int, message_id: int, text: str, date: str):
    if not text or not text.strip():
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO messages (channel_id, message_id, text, date) VALUES (?, ?, ?, ?)",
            (channel_id, message_id, text, date)
        )
        await db.commit()


async def search_messages(query: str, limit: int = 20):
    """Keyword search across stored messages."""
    words = [w for w in query.split() if len(w) > 2]
    if not words:
        return []
    async with aiosqlite.connect(DB_PATH) as db:
        conditions = " OR ".join(["m.text LIKE ?" for _ in words])
        params = [f"%{w}%" for w in words]
        async with db.execute(
            f"""SELECT m.text, m.date, c.channel_name
                FROM messages m
                JOIN channels c ON m.channel_id = c.channel_id
                WHERE {conditions}
                ORDER BY m.date DESC LIMIT ?""",
            params + [limit]
        ) as cursor:
            return await cursor.fetchall()


async def get_recent_messages(limit: int = 30):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT m.text, m.date, c.channel_name
               FROM messages m
               JOIN channels c ON m.channel_id = c.channel_id
               ORDER BY m.date DESC LIMIT ?""",
            (limit,)
        ) as cursor:
            return await cursor.fetchall()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM messages") as cursor:
            msg_count = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM channels") as cursor:
            ch_count = (await cursor.fetchone())[0]
    return ch_count, msg_count
