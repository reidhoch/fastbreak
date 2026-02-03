"""Tests for league season matchups models."""

from fastbreak.models.league_season_matchups import (
    LeagueSeasonMatchupsResponse,
)


class TestLeagueSeasonMatchupsResponse:
    """Tests for LeagueSeasonMatchupsResponse model."""

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"matchups": []}

        response = LeagueSeasonMatchupsResponse.model_validate(data)

        assert response.matchups == []
