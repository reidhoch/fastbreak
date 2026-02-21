"""Models for the video events endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse


class VideoUrl(BaseModel):
    """Video URL metadata for a play event.

    Note: Many fields may be null depending on video availability.
    When populated, these fields contain URLs for different video sizes.
    """

    uuid: str
    dur: int | None = None  # Duration
    # Small thumbnail
    stt: str | None = None  # Small thumbnail type
    stp: str | None = None  # Small thumbnail path
    sth: int | None = None  # Small thumbnail height
    stw: int | None = None  # Small thumbnail width
    # Medium thumbnail
    mtt: str | None = None  # Medium thumbnail type
    mtp: str | None = None  # Medium thumbnail path
    mth: int | None = None  # Medium thumbnail height
    mtw: int | None = None  # Medium thumbnail width
    # Large thumbnail
    ltt: str | None = None  # Large thumbnail type
    ltp: str | None = None  # Large thumbnail path
    lth: int | None = None  # Large thumbnail height
    ltw: int | None = None  # Large thumbnail width


class VideoMeta(BaseModel):
    """Metadata containing video URLs for the event."""

    video_urls: list[VideoUrl] = Field(alias="videoUrls", default_factory=list)


class PlaylistItem(PandasMixin, PolarsMixin, BaseModel):
    """A single play event in the video playlist."""

    game_id: str = Field(alias="gi")
    event_id: int = Field(alias="ei")
    year: int = Field(alias="y")
    month: str = Field(alias="m")
    day: str = Field(alias="d")
    game_code: str = Field(alias="gc")
    period: int = Field(alias="p")
    description: str = Field(alias="dsc")
    home_abbreviation: str = Field(alias="ha")
    visitor_abbreviation: str = Field(alias="va")
    home_points_before: int = Field(alias="hpb")
    home_points_after: int = Field(alias="hpa")
    visitor_points_before: int = Field(alias="vpb")
    visitor_points_after: int = Field(alias="vpa")
    points_attempted: int = Field(alias="pta")


class VideoResultSets(BaseModel):
    """Result sets from the video events endpoint."""

    meta: VideoMeta = Field(alias="Meta")
    playlist: list[PlaylistItem]


class VideoEventsResponse(FrozenResponse):
    """Response from the video events endpoint.

    Contains video metadata and playlist information for a specific
    play event in a game. Use this to access video clips of individual
    plays like shots, turnovers, and other game events.

    The video URLs may not always be populated depending on the
    NBA's video availability for the specific event.
    """

    resource: str
    parameters: dict[str, str | int]
    result_sets: VideoResultSets = Field(alias="resultSets")
