from fastbreak.endpoints.base import Endpoint
from fastbreak.models import GravityLeadersResponse


class GravityLeaders(Endpoint[GravityLeadersResponse]):
    """Fetch gravity leaders for a given season.

    Gravity measures how much defensive attention a player draws,
    based on how close defenders stay to them.
    """

    path = "gravityleaders"
    response_model = GravityLeadersResponse

    def __init__(
        self,
        season: str = "2024-25",
        season_type: str = "Regular Season",
        league_id: str = "00",
    ) -> None:
        self.season = season
        self.season_type = season_type
        self.league_id = league_id

    def params(self) -> dict[str, str]:
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
