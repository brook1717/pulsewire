from app.core.logging import get_logger
from app.database.models.article import Article
from app.database.models.bot_log import BotLog
from app.database.session import async_session_factory
from app.services.aggregators.rss_fetcher import fetch_feed
from app.services.processors.ingestion import ingest_articles
from app.services.summarizers.openai_client import summarize
from app.services.telegram.publisher import publish_article

logger = get_logger(__name__)

# Predefined RSS feeds: (url, category)
RSS_FEEDS: list[tuple[str, str]] = [
    ("https://pitchfork.com/feed/feed-news/rss", "music"),
    ("https://www.vogue.com/feed/rss", "fashion"),
]


async def _log_event(action: str, status: str, message: str | None = None) -> None:
    """Write an audit entry to the bot_logs table."""
    async with async_session_factory() as session:
        session.add(BotLog(action=action, status=status, message=message))
        await session.commit()


async def run_pipeline() -> None:
    """Execute the full content pipeline sequentially.

    Steps:
        1. Fetch items from every predefined RSS feed.
        2. Normalize and insert new articles (database deduplication).
        3. Optionally summarize each new article via OpenAI.
        4. Publish each article to Telegram.
        5. Record success/failure in BotLog.
    """
    logger.info("Pipeline started")

    # ── 1. Fetch ─────────────────────────────────────────────
    all_items = []
    for feed_url, category in RSS_FEEDS:
        items = await fetch_feed(feed_url, category=category)
        all_items.extend(items)

    if not all_items:
        logger.info("No items fetched — pipeline finished early")
        await _log_event("fetch", "success", "No items fetched from any feed")
        return

    await _log_event("fetch", "success", f"Fetched {len(all_items)} items")

    # ── 2. Ingest (deduplicate) ──────────────────────────────
    async with async_session_factory() as session:
        new_articles = await ingest_articles(session, all_items)

    if not new_articles:
        logger.info("No new articles to process — pipeline finished")
        await _log_event("process", "success", "All articles were duplicates")
        return

    await _log_event("process", "success", f"Ingested {len(new_articles)} new articles")

    # ── 3. Summarize & 4. Publish ────────────────────────────
    published_count = 0

    for article in new_articles:
        # 3. Optional AI summary — falls back to description
        summary = await summarize(article.title, article.summary)
        final_text = summary or article.summary or article.title

        # Update the article record with the summary if AI produced one
        if summary and summary != article.summary:
            async with async_session_factory() as session:
                article.summary = summary
                merged = await session.merge(article)
                await session.commit()
                logger.debug("Saved AI summary for article %d", merged.id)

        # 4. Publish to Telegram
        success = await publish_article(
            title=article.title,
            summary=final_text,
            url=article.url,
        )

        if success:
            published_count += 1

    # ── 5. Record outcome ────────────────────────────────────
    await _log_event(
        "publish",
        "success",
        f"Published {published_count}/{len(new_articles)} articles to Telegram",
    )

    logger.info(
        "Pipeline complete: %d fetched, %d new, %d published",
        len(all_items),
        len(new_articles),
        published_count,
    )
