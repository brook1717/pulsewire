from datetime import datetime

from pydantic import BaseModel, HttpUrl


class FeedItem(BaseModel):
    """Normalized schema for a single RSS feed entry."""

    title: str
    source: str
    url: HttpUrl
    description: str | None = None
    category: str | None = None
    published_at: datetime | None = None
