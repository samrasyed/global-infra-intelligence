"""
AI extraction pipeline. Runs once per article:

  1. clean            -> strip boilerplate/whitespace
  2. summarize        -> extractive summary (no paid LLM required)
  3. extract entities  -> spaCy NER: countries, orgs, people, money, dates
  4. infra category    -> keyword classifier over 19 categories
  5. geopolitical topics -> keyword tagging
  6. threat score      -> app.services.threat_scoring

A HuggingFace/Gemini/OpenAI/Ollama summarizer can be swapped in behind
`summarize()` without touching the rest of the pipeline - see
services/llm_provider.py for the pluggable interface.
"""
import re
from functools import lru_cache

from app.services.threat_scoring import score_text, level_for_score
from app.services.llm_provider import get_provider

INFRA_KEYWORDS = {
    "undersea_cable": ["undersea cable", "subsea cable", "submarine cable"],
    "port": ["port", "seaport", "container terminal", "harbor", "harbour"],
    "railway": ["railway", "rail line", "railroad", "high-speed rail"],
    "airport": ["airport", "runway", "air traffic"],
    "shipping": ["shipping", "container ship", "tanker", "freight", "maritime"],
    "semiconductor": ["semiconductor", "chip fab", "foundry", "wafer plant", "chipmaker"],
    "data_center": ["data center", "data centre", "hyperscale", "server farm"],
    "ai_infrastructure": ["ai infrastructure", "gpu cluster", "compute cluster", "ai data center"],
    "nuclear": ["nuclear plant", "nuclear reactor", "nuclear facility"],
    "rare_earth": ["rare earth", "rare-earth"],
    "critical_minerals": ["critical minerals", "lithium mine", "cobalt mine", "graphite mine"],
    "oil": ["oil field", "oil refinery", "crude oil", "oil pipeline"],
    "lng": ["lng terminal", "liquefied natural gas", "lng export"],
    "pipeline": ["pipeline"],
    "power_grid": ["power grid", "electric grid", "transmission line", "blackout"],
    "renewable_energy": ["solar farm", "wind farm", "renewable energy", "offshore wind"],
    "water": ["water treatment", "water infrastructure", "desalination", "reservoir"],
    "satellite": ["satellite", "orbital"],
    "space": ["space launch", "spaceport", "rocket launch"],
}

GEOPOLITICAL_TOPICS = [
    "China", "United States", "Russia", "Taiwan", "South China Sea", "Cybersecurity",
    "Military", "Semiconductors", "Rare Earth", "BRI", "Ports", "Energy", "AI",
    "Telecom", "Shipping", "Critical Minerals", "Sanctions", "European Union", "India",
]

MONEY_RE = re.compile(
    r"(?:US\$|USD|\$|€|£)\s?(\d+(?:\.\d+)?)\s?(billion|bn|million|mn|trillion)?", re.IGNORECASE
)
MULTIPLIER = {"billion": 1e9, "bn": 1e9, "million": 1e6, "mn": 1e6, "trillion": 1e12, None: 1}


class _FallbackDoc:
    """Minimal drop-in for a spaCy Doc when spaCy itself can't load (missing
    model, or a broken torch/thinc install in the environment). Supports just
    enough of the API (`.sents`, `.ents`) for this pipeline to keep working,
    with zero entity extraction and regex sentence splitting."""

    def __init__(self, text: str):
        self.text = text
        self.ents = []
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        self.sents = [_FallbackSpan(s) for s in sentences if s]


class _FallbackSpan:
    def __init__(self, text: str):
        self.text = text


class _FallbackNLP:
    """Callable matching spaCy's `nlp(text)` interface."""

    def __call__(self, text: str) -> _FallbackDoc:
        return _FallbackDoc(text)


@lru_cache(maxsize=1)
def _spacy_nlp():
    try:
        import spacy
    except Exception:
        # spaCy (or a transitive dep like torch/thinc) failed to import in
        # this environment. Degrade to the regex-based fallback rather than
        # taking down the whole ingestion pipeline.
        return _FallbackNLP()

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not downloaded yet (`python -m spacy download en_core_web_sm`).
        # Fall back to a blank English pipeline with just a sentencizer so the
        # rest of the app still runs without the model installed.
        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        return nlp
    except Exception:
        return _FallbackNLP()


def clean_text(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw or "").strip()
    return text


def extractive_summary(text: str, max_sentences: int = 3) -> str:
    """Cheap, dependency-light extractive summary: first N substantive
    sentences. Swap for an LLM call via services.llm_provider for higher
    quality when an API key is configured."""
    nlp = _spacy_nlp()
    doc = nlp(text[:5000])
    sentences = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 40]
    return " ".join(sentences[:max_sentences]) or text[:280]


def extract_entities(text: str) -> dict:
    nlp = _spacy_nlp()
    doc = nlp(text[:20000])
    out = {"countries": set(), "companies": set(), "organizations": set(),
           "people": set(), "locations": set(), "dates": set(), "money": []}
    for ent in doc.ents:
        if ent.label_ == "GPE":
            out["countries"].add(ent.text)
        elif ent.label_ == "ORG":
            out["organizations"].add(ent.text)
        elif ent.label_ == "PERSON":
            out["people"].add(ent.text)
        elif ent.label_ == "LOC":
            out["locations"].add(ent.text)
        elif ent.label_ == "DATE":
            out["dates"].add(ent.text)
        elif ent.label_ == "MONEY":
            out["money"].append(ent.text)

    for m in MONEY_RE.finditer(text):
        amount, unit = m.group(1), (m.group(2) or "").lower() or None
        try:
            usd = float(amount) * MULTIPLIER.get(unit, 1)
            out["money"].append({"raw": m.group(0), "usd": usd})
        except ValueError:
            continue

    return {k: (list(v) if isinstance(v, set) else v) for k, v in out.items()}


def classify_infra_category(text: str) -> str:
    text_l = text.lower()
    best_cat, best_hits = "other", 0
    for cat, keywords in INFRA_KEYWORDS.items():
        hits = sum(text_l.count(k) for k in keywords)
        if hits > best_hits:
            best_cat, best_hits = cat, hits
    return best_cat


def tag_topics(text: str) -> list[str]:
    text_l = text.lower()
    return [t for t in GEOPOLITICAL_TOPICS if t.lower() in text_l]


def process_article(raw_text: str, title: str = "") -> dict:
    """Run the full pipeline and return every derived field for an article."""
    full_text = f"{title}. {raw_text}"
    clean = clean_text(raw_text)
    provider = get_provider()

    summary = provider.summarize(clean) if provider else extractive_summary(clean)
    entities = extract_entities(full_text)
    infra_category = classify_infra_category(full_text)
    topics = tag_topics(full_text)
    score, factors = score_text(full_text)
    level = level_for_score(score)

    money_usd = [m["usd"] for m in entities["money"] if isinstance(m, dict)]
    top_investment = max(money_usd) if money_usd else None

    return {
        "clean_text": clean,
        "summary": summary,
        "entities": entities,
        "infra_category": infra_category,
        "geopolitical_topics": topics,
        "threat_score": score,
        "threat_level": level,
        "threat_factors": factors,
        "investment_amount_usd": top_investment,
    }
