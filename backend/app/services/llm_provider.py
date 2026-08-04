"""
Optional LLM provider for higher-quality summarization + the RAG chatbot.

The platform runs fully without any of these - extractive summarization and
the rule-based threat scorer are the defaults. Set one of the env vars below
to upgrade summarization quality; nothing else in the codebase needs to
change.

  GEMINI_API_KEY   -> Google Gemini (has a free tier)
  OPENAI_API_KEY   -> OpenAI
  OLLAMA_HOST      -> local Ollama server, e.g. http://localhost:11434
"""
import os
from functools import lru_cache
from typing import Optional


class LLMProvider:
    def summarize(self, text: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    def chat(self, prompt: str, context: str) -> str:  # pragma: no cover
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def summarize(self, text: str) -> str:
        resp = self.model.generate_content(f"Summarize in 3 sentences for an intelligence analyst:\n\n{text[:6000]}")
        return resp.text.strip()

    def chat(self, prompt: str, context: str) -> str:
        resp = self.model.generate_content(
            f"You are an infrastructure-intelligence analyst assistant. "
            f"Answer using only the context below; cite article titles.\n\n"
            f"Context:\n{context[:8000]}\n\nQuestion: {prompt}"
        )
        return resp.text.strip()


class OllamaProvider(LLMProvider):
    def __init__(self, host: str, model: str = "llama3"):
        self.host = host.rstrip("/")
        self.model = model

    def _call(self, prompt: str) -> str:
        import httpx
        r = httpx.post(f"{self.host}/api/generate",
                        json={"model": self.model, "prompt": prompt, "stream": False}, timeout=60)
        r.raise_for_status()
        return r.json().get("response", "").strip()

    def summarize(self, text: str) -> str:
        return self._call(f"Summarize in 3 sentences for an intelligence analyst:\n\n{text[:6000]}")

    def chat(self, prompt: str, context: str) -> str:
        return self._call(
            f"Context:\n{context[:8000]}\n\nAnswer this question using only the context above, "
            f"citing article titles: {prompt}"
        )


@lru_cache(maxsize=1)
def get_provider() -> Optional[LLMProvider]:
    if os.getenv("GEMINI_API_KEY"):
        try:
            return GeminiProvider(os.environ["GEMINI_API_KEY"])
        except Exception:
            return None
    if os.getenv("OLLAMA_HOST"):
        return OllamaProvider(os.environ["OLLAMA_HOST"], os.getenv("OLLAMA_MODEL", "llama3"))
    return None
