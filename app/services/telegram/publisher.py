import re

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", text)


def _format_message(title: str, summary: str, url: str) -> str:
    """Build a MarkdownV2-formatted Telegram post."""
    safe_title = _escape_md(title)
    safe_summary = _escape_md(summary)
    safe_url = _escape_md(url)
    return f"*{safe_title}*\n\n{safe_summary}\n\n[Read more]({safe_url})"


async def publish_article(
    title: str,
    summary: str,
    url: str,
) -> bool:
    """Send a formatted article post to the configured Telegram channel.

    Args:
        title: Article headline.
        summary: Short summary text (AI-generated or original description).
        url: Link to the full article.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    bot = Bot(token=settings.telegram_token)

    message = _format_message(title, summary, url)

    try:
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=False,
        )
        logger.info("Published to Telegram: %s", title[:60])
        return True
    except TelegramError as exc:
        logger.error("Telegram publish failed for '%s': %s", title[:60], exc)
        return False
    except Exception as exc:
        logger.error("Unexpected error publishing '%s': %s", title[:60], exc)
        return False
