from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a concise news editor for a Telegram channel. "
    "Summarize the following article in under 100 words. "
    "Write in a neutral, informative tone. Do not use markdown formatting."
)


async def summarize(title: str, description: str | None) -> str | None:
    """Generate a short Telegram-friendly summary via OpenAI.

    This function is strictly optional. It returns None (triggering fallback
    to the original description) when:
      - The OpenAI API key is not configured
      - The API call fails for any reason (network, quota, server error)

    Args:
        title: Article headline.
        description: Original RSS description text (used as input context).

    Returns:
        A sub-100-word summary string, or None if AI is unavailable.
    """
    api_key = settings.openai_key
    if not api_key:
        logger.debug("OpenAI key not configured — skipping summarization")
        return None

    content = f"Title: {title}\n\nDescription: {description or 'No description available.'}"

    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            max_tokens=150,
            temperature=0.4,
        )
        summary = response.choices[0].message.content
        if summary:
            return summary.strip()
        return None

    except RateLimitError:
        logger.warning("OpenAI rate limit exceeded — falling back to description")
        return None
    except APIConnectionError as exc:
        logger.warning("OpenAI connection error: %s — falling back to description", exc)
        return None
    except APIError as exc:
        logger.warning("OpenAI API error (status %s): %s — falling back", exc.status_code, exc.message)
        return None
    except Exception as exc:
        logger.error("Unexpected error during summarization: %s — falling back", exc)
        return None
