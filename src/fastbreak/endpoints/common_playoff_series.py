"""Common playoff series endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.common_playoff_series import CommonPlayoffSeriesResponse
from fastbreak.types import LeagueID, Season
from fastbreak.utils import get_season_from_date


class CommonPlayoffSeries(Endpoint[CommonPlayoffSeriesResponse]):
    """Fetch playoff series games for a season.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        series_id: Optional specific series ID to filter by

    """

    path: ClassVar[str] = "commonplayoffseries"
    response_model: ClassVar[type[CommonPlayoffSeriesResponse]] = (
        CommonPlayoffSeriesResponse
    )

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    series_id: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        params = {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
        if self.series_id is not None:
            params["SeriesID"] = self.series_id
        return params
