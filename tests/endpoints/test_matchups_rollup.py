import pytest
from pydantic import ValidationError

from fastbreak.endpoints import MatchupsRollup
from fastbreak.models import MatchupsRollupResponse


class TestMatchupsRollup:
    """Tests for MatchupsRollup endpoint."""

    def test_init_with_defaults(self):
        """MatchupsRollup uses sensible defaults."""
        endpoint = MatchupsRollup()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.off_team_id == 0
        assert endpoint.def_team_id == 0
        assert endpoint.off_player_id == 0
        assert endpoint.def_player_id == 0

    def test_init_with_custom_league_id(self):
        """MatchupsRollup accepts custom league_id."""
        endpoint = MatchupsRollup(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season(self):
        """MatchupsRollup accepts custom season."""
        endpoint = MatchupsRollup(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_season_type(self):
        """MatchupsRollup accepts custom season_type."""
        endpoint = MatchupsRollup(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """MatchupsRollup accepts custom per_mode."""
        endpoint = MatchupsRollup(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_team_ids(self):
        """MatchupsRollup accepts team IDs."""
        endpoint = MatchupsRollup(off_team_id=1610612754, def_team_id=1610612765)

        assert endpoint.off_team_id == 1610612754
        assert endpoint.def_team_id == 1610612765

    def test_init_with_player_ids(self):
        """MatchupsRollup accepts player IDs."""
        endpoint = MatchupsRollup(off_player_id=201566, def_player_id=203507)

        assert endpoint.off_player_id == 201566
        assert endpoint.def_player_id == 203507

    def test_init_with_all_custom_params(self):
        """MatchupsRollup accepts all custom parameters."""
        endpoint = MatchupsRollup(
            league_id="10",
            season="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            off_team_id=1610612754,
            def_team_id=1610612765,
            off_player_id=201566,
            def_player_id=203507,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.off_team_id == 1610612754
        assert endpoint.def_team_id == 1610612765
        assert endpoint.off_player_id == 201566
        assert endpoint.def_player_id == 203507

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = MatchupsRollup(
            league_id="00",
            season="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
            off_team_id=1610612754,
            def_team_id=1610612765,
            off_player_id=0,
            def_player_id=0,
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "OffTeamID": "1610612754",
            "DefTeamID": "1610612765",
            "OffPlayerID": "0",
            "DefPlayerID": "0",
        }

    def test_path_is_correct(self):
        """MatchupsRollup has correct API path."""
        endpoint = MatchupsRollup()

        assert endpoint.path == "matchupsrollup"

    def test_response_model_is_correct(self):
        """MatchupsRollup uses MatchupsRollupResponse model."""
        endpoint = MatchupsRollup()

        assert endpoint.response_model is MatchupsRollupResponse

    def test_endpoint_is_frozen(self):
        """MatchupsRollup is immutable (frozen dataclass)."""
        endpoint = MatchupsRollup()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
