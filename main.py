import asyncio
from database import init_db
from collector import start_listener
from bot import start_bot


async def main():
    await init_db()
    print("Database initialized.")
    await asyncio.gather(
        start_listener(),
        start_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
