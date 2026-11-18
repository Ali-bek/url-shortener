from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

from app.config import BASE_URL


class LinkCreate(BaseModel):
    original_url: HttpUrl  # rejects anything that isn't a valid http(s) URL
    custom_code: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]{3,20}$")


class LinkUpdate(BaseModel):
    original_url: HttpUrl


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    original_url: str
    created_at: datetime

    @computed_field
    @property
    def short_url(self) -> str:
        return f"{BASE_URL}/{self.code}"


class DailyClicks(BaseModel):
    day: date
    clicks: int


class ReferrerCount(BaseModel):
    referrer: str
    clicks: int


class LinkStats(BaseModel):
    code: str
    original_url: str
    total_clicks: int
    clicks_per_day: list[DailyClicks]
    top_referrers: list[ReferrerCount]