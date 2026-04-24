from typing import List, Optional

from openai import OpenAI

from app.config import settings


def get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _extract_texts_from_results(results) -> List[str]:
    chunks: List[str] = []

    for item in results.data:
        content_items = getattr(item, "content", None) or []
        for content in content_items:
            text_obj = getattr(content, "text", None)
            if isinstance(text_obj, str) and text_obj.strip():
                chunks.append(text_obj.strip())
            elif hasattr(text_obj, "value") and isinstance(text_obj.value, str) and text_obj.value.strip():
                chunks.append(text_obj.value.strip())

    # remove duplicates, keep order
    seen = set()
    unique_chunks = []
    for chunk in chunks:
        if chunk not in seen:
            seen.add(chunk)
            unique_chunks.append(chunk)

    return unique_chunks


def search_vector_store(
    query: str,
    language: str,
    max_results: int = 6,
) -> List[str]:
    if not settings.OPENAI_VECTOR_STORE_ID:
        raise RuntimeError("OPENAI_VECTOR_STORE_ID is missing")

    client = get_openai_client()

    # First try: strict same-language search by file attribute
    try:
        results = client.vector_stores.search(
            vector_store_id=settings.OPENAI_VECTOR_STORE_ID,
            query=query,
            max_num_results=max_results,
            filters={
                "type": "eq",
                "key": "language",
                "value": language,
            },
        )
        same_language_chunks = _extract_texts_from_results(results)
        if same_language_chunks:
            return same_language_chunks
    except Exception:
        # If file attributes are not configured, we silently fall back below.
        pass

    # Second try: no filter, global search across all knowledge base files
    results = client.vector_stores.search(
        vector_store_id=settings.OPENAI_VECTOR_STORE_ID,
        query=query,
        max_num_results=max_results,
    )
    return _extract_texts_from_results(results)