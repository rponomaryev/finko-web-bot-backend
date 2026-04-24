from openai import OpenAI

from app.config import settings


SYSTEM_PROMPT = """
You are the official AI assistant of FINKO (Uzbekistan).

Your role:
- Answer website visitors in a concise, reliable, support-style manner.
- Use the same language as the user's latest message.
- Base factual answers only on the provided FINKO knowledge base context.
- If the context is insufficient, explicitly say that you do not have enough confirmed information.
- Do not invent financial terms, rates, limits, fees, approval outcomes, eligibility, timelines, or partner decisions.
- Important rule: FINKO does not issue loans directly.
- Final decisions are made by partner banks, MFOs, or other financial institutions.
- Do not present assumptions as facts.
- Keep answers safe for public website use.
- If the user asks something outside the available FINKO knowledge base, politely say that you can only answer based on available FINKO information.
- Prefer concise answers. Usually 2-6 sentences.
""".strip()


def get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_rag_answer(
    user_message: str,
    language: str,
    history_text: str,
    retrieved_chunks: list[str],
) -> str:
    client = get_openai_client()

    context_block = "\n\n---\n\n".join(retrieved_chunks) if retrieved_chunks else "NO_KNOWLEDGE_FOUND"

    prompt = f"""
Reply language: {language}

Conversation history:
{history_text}

Latest user message:
{user_message}

Knowledge base context:
{context_block}

Instructions:
- Answer ONLY from the knowledge base context.
- If the context does not contain enough information, say so clearly.
- Do not add facts that are not present in the context.
- If needed, remind the user that FINKO does not issue loans directly and final decisions are made by partner financial institutions.
""".strip()

    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )

    return response.output_text.strip()