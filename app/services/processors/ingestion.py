from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.database.models.article import Article
from app.schemas.article import FeedItem

logger = get_logger(__name__)


async def ingest_articles(
    session: AsyncSession, items: list[FeedItem]
) -> list[Article]:
    """Insert normalized feed items into the database.

    Deduplication relies on the UNIQUE constraint on Article.url.
    Duplicates trigger an IntegrityError which is caught and skipped
    gracefully — the pipeline continues processing remaining items.

    Args:
        session: An active async database session.
        items: Normalized feed items to persist.

    Returns:
        List of newly inserted Article instances (duplicates excluded).
    """
    inserted: list[Article] = []

    for item in items:
        article = Article(
            title=item.title,
            source=item.source,
            url=str(item.url),
            summary=None,
            category=item.category,
            published_at=item.published_at,
        )

        session.add(article)

        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            logger.debug("Duplicate skipped: %s", item.url)
            continue

        inserted.append(article)

    await session.commit()

    logger.info(
        "Ingestion complete: %d new, %d duplicates skipped",
        len(inserted),
        len(items) - len(inserted),
    )
    return inserted
