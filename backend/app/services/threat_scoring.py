"""
Rule-based threat scoring.

Real deployments would blend this with a classifier; a transparent rule-based
score is the right MVP because analysts need to see *why* a score is what it
is, not just trust a black box.
"""
import re

FACTOR_KEYWORDS = {
    "cyber_attack": (30, [r"\bcyber\s?attack", r"\bhack(ed|ers?)?\b", r"\bransomware\b", r"\bdata breach\b"]),
    "military_activity": (25, [r"\bmilitary\b", r"\bnaval\b", r"\btroops?\b", r"\bmissile\b", r"\bwarship\b"]),
    "strategic_acquisition": (15, [r"\bacqui(re|sition|res|red)\b", r"\btakeover\b", r"\bstake\b"]),
    "sanctions": (20, [r"\bsanctions?\b", r"\bembargo\b", r"\bblacklist(ed)?\b"]),
    "export_restrictions": (18, [r"\bexport (control|restriction|ban)s?\b", r"\bexport-controlled\b"]),
    "investment": (8, [r"\binvest(ment|s|ed)?\b", r"\bfunding\b", r"\bcapital\b"]),
    "infrastructure_disruption": (28, [r"\boutage\b", r"\bdisrupt(ion|ed)?\b", r"\bsabotage\b", r"\bcut (undersea )?cable\b", r"\bblackout\b"]),
    "political_instability": (20, [r"\bcoup\b", r"\bunrest\b", r"\bprotests?\b", r"\bpolitical crisis\b"]),
    "natural_disaster": (15, [r"\bearthquake\b", r"\btyphoon\b", r"\bhurricane\b", r"\bflood(ing)?\b"]),
}


def score_text(text: str) -> tuple[float, dict[str, bool]]:
    """Return (score 0-100, factor flags) for a piece of article text."""
    text_l = (text or "").lower()
    score = 0
    factors: dict[str, bool] = {}
    for factor, (weight, patterns) in FACTOR_KEYWORDS.items():
        hit = any(re.search(p, text_l) for p in patterns)
        factors[factor] = hit
        if hit:
            score += weight
    return min(score, 100), factors


def level_for_score(score: float) -> str:
    if score >= 70:
        return "critical"
    if score >= 45:
        return "high"
    if score >= 20:
        return "medium"
    return "low"
