"""Article classification logic for the curator agent.

Provides keyword-based category detection as the primary classification
strategy. An AI fallback via the Anthropic API is available but kept
inactive by default; keyword scoring is fast, deterministic, and
sufficient for the eight canonical categories.

The eight canonical category slugs are:
    ``technology``, ``ai``, ``business``, ``science``,
    ``health``, ``politics``, ``sports``, ``general``
"""

import logging
import os

import anthropic

logger = logging.getLogger(__name__)

# Keyword lists used to score articles against each canonical category.
# Each key is a category slug; the value is a list of lowercase substrings
# that, when found in the combined title+content text, increment that
# category's score by 1.  The category with the highest score wins.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "technology": [
        "tech",
        "software",
        "hardware",
        "apple",
        "google",
        "microsoft",
        "chip",
        "device",
        "computer",
        "coding",
        "developer",
        "api",
        "cloud",
        "open source",
        "compiler",
        "codebase",
        "typescript",
        "rust",
        "python",
        "javascript",
        "smartphone",
        "laptop",
        "processor",
    ],
    "ai": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "neural network",
        "llm",
        "gpt",
        "gemini",
        "claude",
        "openai",
        "deepmind",
        "alphafold",
        "model",
        "algorithm",
        "transformer",
        "generative ai",
        "large language",
        "chatbot",
    ],
    "business": [
        "amazon",
        "startup",
        "revenue",
        "investment",
        "market",
        "company",
        "corporate",
        "billion",
        "economy",
        "trade",
        "venture capital",
        "valuation",
        "fund",
        "series",
        "ipo",
        "merger",
        "acquisition",
        "profit",
        "earnings",
        "bitcoin",
        "blockchain",
        "crypto",
        "ethereum",
        "defi",
        "stock",
        "shares",
        "nasdaq",
        "etf",
        "bonds",
        "interest rate",
        "federal reserve",
        "central bank",
        "inflation",
        "blackrock",
        "goldman sachs",
        "wall street",
        "dividend",
        "hedge fund",
        "workers",
        "employment",
        "salary",
        "hiring",
        "layoffs",
        "remote work",
        "workforce",
        "minimum wage",
        "gig economy",
    ],
    "science": [
        "research",
        "study",
        "discovery",
        "laboratory",
        "scientists",
        "breakthrough",
        "experiment",
        "biology",
        "chemistry",
        "physics",
        "researchers",
        "superconductor",
        "quantum",
        "genome",
        "particle",
        "space",
        "nasa",
        "rocket",
        "satellite",
        "mars",
        "orbit",
        "spacex",
        "astronaut",
        "telescope",
        "exoplanet",
        "starship",
        "lunar",
        "cosmos",
        "webb",
        "climate",
        "environment",
        "carbon",
        "renewable",
        "solar",
        "wind energy",
        "emission",
        "sustainability",
        "green",
        "fossil fuel",
        "net zero",
        "warming",
        "mit",
        "engineer",
        "invention",
        "prototype",
        "patent",
        "design",
        "develop",
        "self-healing",
        "autonomous",
        "robotics",
    ],
    "health": [
        "health",
        "medicine",
        "hospital",
        "vaccine",
        "cancer",
        "treatment",
        "disease",
        "clinical",
        "fda",
        "who",
        "medical",
        "alzheimer",
        "drug",
        "patient",
        "therapy",
        "diagnosis",
        "symptom",
        "surgery",
        "epidemic",
        "pandemic",
        "mRNA",
    ],
    "politics": [
        "government",
        "parliament",
        "election",
        "policy",
        "law",
        "regulation",
        "congress",
        "senate",
        "president",
        "eu",
        "un",
        "legislation",
        "democrat",
        "republican",
        "diplomat",
        "treaty",
        "summit",
        "minister",
        "vote",
        "bill",
    ],
    "sports": [
        "sports",
        "championship",
        "tournament",
        "athlete",
        "olympic",
        "football",
        "soccer",
        "basketball",
        "tennis",
        "copa america",
        "world cup",
        "medal",
        "league",
        "stadium",
        "coach",
        "transfer",
        "match",
        "goal",
        "playoff",
        "formula 1",
        "golf",
        "swimming",
    ],
    "general": [
        "community",
        "social",
        "urban",
        "neighborhood",
        "poverty",
        "inequality",
        "welfare",
        "education",
        "housing",
        "museum",
        "broadway",
        "festival",
        "grammy",
        "artwork",
        "cultural",
        "exhibition",
        "gallery",
        "theatre",
        "concert",
        "gaming",
        "netflix",
        "streaming",
        "box office",
        "music",
        "spotify",
        "playstation",
        "xbox",
        "game",
        "movie",
        "series",
        "award",
        "disney",
    ],
}

# Map secondary/derived category labels returned by the AI fallback to one
# of the eight canonical slugs above.
CATEGORY_MAP: dict[str, str] = {
    "culture": "general",
    "labor": "business",
    "entertainment": "general",
    "society": "general",
    "space": "science",
    "climate": "science",
    "finance": "business",
    "innovation": "technology",
}

CANONICAL = set(CATEGORY_KEYWORDS.keys())

_ai_client = anthropic.Anthropic(api_key=os.getenv("AGENT_AI_API_KEY"))
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-4-5-20251001")


def classify_article(article_data: dict) -> dict:
    """Classify a news article into one of the eight canonical categories.

    Combines the article's title and content into a single lowercase string,
    then counts how many keywords from each category appear in the text.
    The category with the highest keyword count is selected.  Secondary labels
    returned by ``CATEGORY_MAP`` are normalised to their canonical equivalent.
    Articles with no keyword matches default to ``"general"``.

    The resolved slug is written into ``article_data["category_slug"]`` and
    the mutated dict is returned so callers can chain operations.

    :param article_data: Dictionary with at least ``"title"`` and ``"content"``
                         keys.  Additional keys are preserved unchanged.
    :return: The same ``article_data`` dict with ``"category_slug"`` set to
             the winning canonical slug.
    """
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    text = f"{title} {content}".lower()

    # Score every category by counting keyword matches
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    preview = text[:100].replace("\n", " ")
    logger.info(f"Text preview: {preview!r}")
    logger.info(f"Category scores: {scores}")

    if not scores:
        raw = "general"
    else:
        raw = max(scores, key=lambda k: scores[k])

    # Map secondary categories to the 8 canonical ones
    final = CATEGORY_MAP.get(raw, raw)
    if final not in CANONICAL:
        final = "general"

    logger.info(f"Category: {raw!r} → {final!r} (score={scores.get(raw, 0)})")
    article_data["category_slug"] = final
    return article_data


def _classify_via_ai(article_data: dict) -> str:
    """Classify an article using the Anthropic AI API as a fallback.

    Sends a zero-shot prompt asking the model to return a single canonical
    slug.  Available for optional activation when keyword scoring produces
    ambiguous or zero-score results.

    :param article_data: Dictionary with at least ``"title"`` and ``"content"``
                         keys.
    :return: A canonical category slug, or ``"general"`` if the API call
             fails or returns an unrecognised value.
    """
    prompt = (
        f"Classify the article into one of: "
        f"{', '.join(sorted(CANONICAL))}.\n"
        f"Reply with only the slug, no explanation.\n\n"
        f"Title: {article_data.get('title', '')}\n"
        f"Content: {article_data.get('content', '')[:500]}"
    )
    try:
        message = _ai_client.messages.create(
            model=AI_MODEL,
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
        )
        slug = message.content[0].text.strip().lower()
        if slug in CANONICAL:
            return slug
    except Exception as error:
        logger.error(f"AI classification failed: {error}")
    return "general"
