import anthropic
from loguru import logger
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

VALID_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Health",
    "Entertainment",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]


async def categorize_expense(description: str, amount: float) -> dict:
    """
    Send expense description to Claude and get back category + confidence.
    Returns: {"category": str, "confidence": float, "reasoning": str}
    """
    prompt = f"""You are a personal finance assistant. Categorize this expense.

Expense description: "{description}"
Amount: {amount}

Choose EXACTLY ONE category from this list:
{', '.join(VALID_CATEGORIES)}

Respond with ONLY a JSON object in this exact format (no markdown, no explanation):
{{"category": "Food & Dining", "confidence": 0.95, "reasoning": "brief reason"}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )

        import json
        raw = message.content[0].text.strip()
        result = json.loads(raw)

        # Validate category is in our list
        if result.get("category") not in VALID_CATEGORIES:
            result["category"] = "Other"
            result["confidence"] = 0.5

        logger.info(
            f"Categorized '{description}' → {result['category']} "
            f"(confidence: {result['confidence']})"
        )
        return result

    except Exception as e:
        logger.error(f"AI categorization failed for '{description}': {e}")
        return {"category": "Other", "confidence": 0.0, "reasoning": "Categorization failed"}
