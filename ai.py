from groq import AsyncGroq
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant with access to a knowledge base built from Telegram channel messages.
Answer the user's question based on the provided context messages.
Be concise and direct. If the context doesn't contain relevant information, say so clearly.
Always mention which channel a piece of information came from when relevant."""


async def ask(question: str, context_messages: list) -> str:
    if not context_messages:
        context = "The knowledge base is empty. No messages have been synced yet."
    else:
        parts = []
        for text, date, channel_name in context_messages:
            parts.append(f"[{channel_name} | {date[:10]}]\n{text}")
        context = "\n\n---\n\n".join(parts)

    user_message = f"""CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION:
{question}"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1000,
        temperature=0.3,
    )

    return response.choices[0].message.content
