from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.core.logging import get_logger
from app.schemas.article import FeedItem

logger = get_logger(__name__)

HTTP_TIMEOUT = 15.0


def _parse_published(entry: dict) -> datetime | None:
    """Extract a timezone-aware datetime from an RSS entry."""
    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _extract_description(entry: dict) -> str | None:
    """Return the plain-text description from an RSS entry."""
    summary = entry.get("summary") or entry.get("description")
    if not summary:
        return None
    return summary.strip()


def _extract_source(feed: dict, url: str) -> str:
    """Derive a human-readable source name from the feed metadata."""
    title = feed.get("feed", {}).get("title")
    if title:
        return title.strip()
    return url


async def fetch_feed(feed_url: str, category: str | None = None) -> list[FeedItem]:
    """Fetch an RSS feed and return normalized FeedItem objects.

    Args:
        feed_url: URL of the RSS/Atom feed.
        category: Category label to tag every item from this feed.

    Returns:
        List of normalized FeedItem instances. Items that cannot be
        parsed (missing title or link) are silently skipped.
    """
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Failed to fetch feed %s: %s", feed_url, exc)
        return []

    feed = feedparser.parse(response.text)
    source = _extract_source(feed, feed_url)
    items: list[FeedItem] = []

    for entry in feed.entries:
        title = entry.get("title")
        link = entry.get("link")

        if not title or not link:
            logger.debug("Skipping entry with missing title/link in %s", feed_url)
            continue

        item = FeedItem(
            title=title.strip(),
            source=source,
            url=link.strip(),
            description=_extract_description(entry),
            category=category,
            published_at=_parse_published(entry),
        )
        items.append(item)

    logger.info("Fetched %d items from %s", len(items), feed_url)
    return items
