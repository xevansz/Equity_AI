"""Ingestion Document Schema"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class IngestionDocument(BaseModel):
    id: str = Field(..., description="Stable dedup ID (hash of source+url or source+vendor_id)")
    symbol: str
    source: str = Field(..., description="newsapi | sec | alphavantage | fmp | manual")
    type: Literal["news_article", "earnings_transcript", "sec_filing"] = "news_article"
    title: str = ""
    text: str = ""
    url: str = ""
    published_at: str = ""
    raw: dict[str, Any] | None = None

    def to_mongo(self) -> dict:
        d = self.model_dump()
        d["_id"] = d.pop("id")
        return d

    @classmethod
    def from_mongo(cls, doc: dict) -> "IngestionDocument":
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        return cls(**doc)
