from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, AuthenticationError, RateLimitError, APIStatusError

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.services.db_service import init_db, log_chat, log_feedback
from app.services.openai_service import generate_rag_answer
from app.services.retrieval_service import search_vector_store
from app.services.session_service import (
    add_assistant_message,
    add_user_message,
    get_session_history,
)
from app.utils.security import verify_bearer_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as exc:
        print(f"SQLite init skipped: {exc}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "name": "FINKO AI Backend",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def detect_language(text: str, language_hint: str | None = None) -> str:
    if language_hint in {"ru", "uz_latn", "uz_cyrl", "en"}:
        return language_hint

    text_lower = text.lower()

    uz_cyrl_chars = {"ў", "қ", "ғ", "ҳ"}
    if any(ch in text_lower for ch in uz_cyrl_chars):
        return "uz_cyrl"

    cyrillic_chars = [ch for ch in text_lower if "а" <= ch <= "я" or ch == "ё"]
    if cyrillic_chars:
        return "ru"

    uz_latn_markers = ["o‘", "g‘", "sh", "ch", "ng", "yo", "ya", "yu", "q", "x"]
    if any(marker in text_lower for marker in uz_latn_markers):
        return "uz_latn"

    return "en"


def fallback_by_language(language: str) -> str:
    messages = {
        "ru": "Извините, сейчас сервис временно недоступен. Попробуйте позже.",
        "uz_latn": "Kechirasiz, xizmat vaqtincha ishlamayapti.",
        "uz_cyrl": "Кечирасиз, хизмат вақтинча ишламаяпти.",
        "en": "Service temporarily unavailable. Try again later.",
    }
    return messages.get(language, messages["en"])


def no_answer_found_message(language: str) -> str:
    messages = {
        "ru": "У меня пока нет информации по этому вопросу.",
        "uz_latn": "Bu savol bo‘yicha ma’lumot topilmadi.",
        "uz_cyrl": "Бу савол бўйича маълумот топилмади.",
        "en": "No information found for this request.",
    }
    return messages.get(language, messages["en"])


def build_history_text(session_id: str) -> str:
    history = get_session_history(session_id)

    if not history:
        return "No previous messages."

    lines = []
    for item in history:
        role = item["role"].upper()
        lines.append(f"{role}: {item['content']}")

    return "\n".join(lines)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(verify_bearer_token)])
async def chat(payload: ChatRequest):
    message = payload.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    language = detect_language(message, payload.language_hint)
    history_text = build_history_text(payload.session_id)

    try:
        retrieved_chunks = search_vector_store(
            query=message,
            language=language,
            max_results=6,
        )

        if not retrieved_chunks:
            answer = no_answer_found_message(language)
            sources_used = False
        else:
            answer = generate_rag_answer(
                user_message=message,
                language=language,
                history_text=history_text,
                retrieved_chunks=retrieved_chunks,
            )
            sources_used = True

    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")

    except RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded")

    except APIConnectionError:
        raise HTTPException(status_code=503, detail="OpenAI connection error")

    except APIStatusError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {exc.status_code}")

    except Exception:
        answer = fallback_by_language(language)
        sources_used = False

    add_user_message(payload.session_id, message)
    add_assistant_message(payload.session_id, answer)

    log_chat(
        session_id=payload.session_id,
        page=payload.page,
        language=language,
        user_message=message,
        assistant_answer=answer,
        sources_used=sources_used,
    )

    return ChatResponse(
        answer=answer,
        language=language,
        sources_used=sources_used,
        session_id=payload.session_id,
        suggestions=[],
    )


@app.post("/api/feedback", dependencies=[Depends(verify_bearer_token)])
async def feedback(payload: FeedbackRequest):
    log_feedback(
        session_id=payload.session_id,
        rating=payload.rating,
        comment=payload.comment,
    )

    return {
        "status": "received",
        "session_id": payload.session_id,
        "rating": payload.rating,
    }