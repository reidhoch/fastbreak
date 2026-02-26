import pytest
from pydantic import ValidationError

from fastbreak.endpoints import AssistLeaders
from fastbreak.models import AssistLeadersResponse
from fastbreak.seasons import get_season_from_date


class TestAssistLeaders:
    """Tests for AssistLeaders endpoint."""

    def test_init_with_defaults(self):
        """AssistLeaders uses sensible defaults."""
        endpoint = AssistLeaders()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.player_or_team == "Team"

    def test_init_with_custom_league_id(self):
        """AssistLeaders accepts custom league_id."""
        endpoint = AssistLeaders(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """AssistLeaders accepts custom season."""
        endpoint = AssistLeaders(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """AssistLeaders accepts custom season_type."""
        endpoint = AssistLeaders(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """AssistLeaders accepts custom per_mode."""
        endpoint = AssistLeaders(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_player_mode(self):
        """AssistLeaders accepts Player mode."""
        endpoint = AssistLeaders(player_or_team="Player")

        assert endpoint.player_or_team == "Player"

    def test_init_with_all_custom_params(self):
        """AssistLeaders accepts all custom parameters."""
        endpoint = AssistLeaders(
            league_id="10",
            season="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            player_or_team="Player",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.player_or_team == "Player"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = AssistLeaders(
            league_id="00",
            season="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
            player_or_team="Team",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "PlayerOrTeam": "Team",
        }

    def test_params_with_player_mode(self):
        """params() correctly includes PlayerOrTeam=Player."""
        endpoint = AssistLeaders(player_or_team="Player")

        params = endpoint.params()

        assert params["PlayerOrTeam"] == "Player"

    def test_path_is_correct(self):
        """AssistLeaders has correct API path."""
        endpoint = AssistLeaders()

        assert endpoint.path == "assistleaders"

    def test_response_model_is_correct(self):
        """AssistLeaders uses AssistLeadersResponse model."""
        endpoint = AssistLeaders()

        assert endpoint.response_model is AssistLeadersResponse

    def test_endpoint_is_frozen(self):
        """AssistLeaders is immutable (frozen dataclass)."""
        endpoint = AssistLeaders()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
