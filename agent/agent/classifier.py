import logging
import os

import anthropic

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "ia": ["inteligência artificial", "machine learning", "deep learning", "llm", "gpt", "neural"],
    "tecnologia": ["software", "hardware", "programação", "developer", "código", "api", "cloud"],
    "negocios": ["empresa", "startup", "mercado", "investimento", "receita", "negócio"],
    "inovacao": ["inovação", "disruption", "futuro", "tendência", "nova tecnologia"],
    "ciencia": ["pesquisa", "estudo", "descoberta", "cientistas", "experimento"],
    "politica": ["governo", "lei", "regulação", "política", "eleição", "congresso"],
}

_ai_client = anthropic.Anthropic(api_key=os.getenv("AGENT_AI_API_KEY"))
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-4-5-20251001")


def classify_article(article_data: dict) -> dict:
    raw_content = f"{article_data.get('title', '')} {article_data.get('content', '')}".lower()

    for category_slug, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in raw_content for keyword in keywords):
            article_data["category_slug"] = category_slug
            logger.info(f"Category matched via keywords: {category_slug}")
            return article_data

    category_slug = _classify_via_ai(article_data)
    article_data["category_slug"] = category_slug
    return article_data


def _classify_via_ai(article_data: dict) -> str:
    available_categories = list(CATEGORY_KEYWORDS.keys())
    prompt = (
        f"Classify the article below into one of these categories: {', '.join(available_categories)}.\n"
        f"Reply with only the category slug, no explanation.\n\n"
        f"Title: {article_data.get('title', '')}\n"
        f"Content: {article_data.get('content', '')[:500]}"
    )

    try:
        message = _ai_client.messages.create(
            model=AI_MODEL,
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
        )
        category_slug = message.content[0].text.strip().lower()
        if category_slug in available_categories:
            logger.info(f"Category matched via AI: {category_slug}")
            return category_slug
    except Exception as error:
        logger.error(f"AI classification failed: {error}")

    return "tecnologia"
