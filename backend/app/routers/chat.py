from fastapi import APIRouter
from pydantic import BaseModel

from app.services import embeddings as vec
from app.services.llm_provider import get_provider

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatSource(BaseModel):
    article_id: str
    title: str | None = None
    source: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    AI analyst assistant. Retrieves the most relevant articles by vector
    similarity, then either hands them to a configured LLM provider for a
    grounded answer, or - if no provider is configured - returns the
    retrieved evidence directly so the assistant is still useful with zero
    paid API keys.
    """
    try:
        hits = vec.search(req.message, n_results=6)
    except Exception:
        hits = []

    if not hits:
        return ChatResponse(
            answer="No indexed articles match that yet. Try again once the ingestion pipeline has "
                   "processed some articles, or rephrase the question.",
            sources=[],
        )

    context = "\n\n".join(f"[{h['metadata'].get('title')}] {h['document']}" for h in hits)
    provider = get_provider()

    if provider:
        answer = provider.chat(req.message, context)
    else:
        # No LLM configured: return a grounded extractive answer instead of
        # a hallucination-prone one.
        bullets = "\n".join(f"- {h['metadata'].get('title')} ({h['metadata'].get('source')})" for h in hits)
        answer = (
            "No LLM provider is configured (set GEMINI_API_KEY or OLLAMA_HOST for a synthesized answer). "
            f"Here are the most relevant indexed articles for '{req.message}':\n{bullets}"
        )

    return ChatResponse(
        answer=answer,
        sources=[ChatSource(article_id=h["id"], title=h["metadata"].get("title"), source=h["metadata"].get("source"))
                  for h in hits],
    )
