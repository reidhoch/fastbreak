import pytest
from pydantic import ValidationError

from fastbreak.endpoints import AssistTracker
from fastbreak.models import AssistTrackerResponse
from fastbreak.utils import get_season_from_date


class TestAssistTracker:
    """Tests for AssistTracker endpoint."""

    def test_init_with_defaults(self):
        """AssistTracker uses sensible defaults."""
        endpoint = AssistTracker()

        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "Totals"

    def test_init_optional_params_default_to_none(self):
        """AssistTracker optional params default to None."""
        endpoint = AssistTracker()

        assert endpoint.po_round is None
        assert endpoint.outcome is None
        assert endpoint.location is None
        assert endpoint.month is None
        assert endpoint.season_segment is None
        assert endpoint.date_from is None
        assert endpoint.date_to is None
        assert endpoint.opponent_team_id is None
        assert endpoint.vs_conference is None
        assert endpoint.vs_division is None
        assert endpoint.team_id is None
        assert endpoint.conference is None
        assert endpoint.division is None
        assert endpoint.last_n_games is None
        assert endpoint.game_scope is None
        assert endpoint.player_experience is None
        assert endpoint.player_position is None
        assert endpoint.starter_bench is None
        assert endpoint.draft_year is None
        assert endpoint.draft_pick is None
        assert endpoint.college is None
        assert endpoint.country is None
        assert endpoint.height is None
        assert endpoint.weight is None

    def test_init_with_custom_required_params(self):
        """AssistTracker accepts custom required parameters."""
        endpoint = AssistTracker(
            league_id="10",
            season="2023-24",
            season_type="Playoffs",
            per_mode="Per36",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Per36"

    def test_init_with_optional_filters(self):
        """AssistTracker accepts optional filter parameters."""
        endpoint = AssistTracker(
            team_id="1610612744",
            player_position="G",
            conference="West",
            outcome="W",
            location="Home",
        )

        assert endpoint.team_id == "1610612744"
        assert endpoint.player_position == "G"
        assert endpoint.conference == "West"
        assert endpoint.outcome == "W"
        assert endpoint.location == "Home"

    def test_init_with_date_filters(self):
        """AssistTracker accepts date filter parameters."""
        endpoint = AssistTracker(
            date_from="01/01/2025",
            date_to="01/31/2025",
            month="1",
            season_segment="Post All-Star",
        )

        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"
        assert endpoint.month == "1"
        assert endpoint.season_segment == "Post All-Star"

    def test_init_with_player_filters(self):
        """AssistTracker accepts player filter parameters."""
        endpoint = AssistTracker(
            player_experience="Rookie",
            starter_bench="Starter",
            draft_year="2024",
            draft_pick="1",
            college="Duke",
            country="USA",
            height="6-6",
            weight="220",
        )

        assert endpoint.player_experience == "Rookie"
        assert endpoint.starter_bench == "Starter"
        assert endpoint.draft_year == "2024"
        assert endpoint.draft_pick == "1"
        assert endpoint.college == "Duke"
        assert endpoint.country == "USA"
        assert endpoint.height == "6-6"
        assert endpoint.weight == "220"

    def test_params_returns_required_only_when_no_optionals(self):
        """params() returns only required params when no optionals set."""
        endpoint = AssistTracker()

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "Totals",
        }
        assert "TeamID" not in params
        assert "PlayerPosition" not in params

    def test_params_includes_optional_when_set(self):
        """params() includes optional params when they are set."""
        endpoint = AssistTracker(
            team_id="1610612744",
            player_position="G",
            conference="West",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612744"
        assert params["PlayerPosition"] == "G"
        assert params["Conference"] == "West"

    def test_params_includes_all_optional_params_when_set(self):
        """params() includes all optional params when set."""
        endpoint = AssistTracker(
            po_round="1",
            outcome="W",
            location="Home",
            month="1",
            season_segment="Post All-Star",
            date_from="01/01/2025",
            date_to="01/31/2025",
            opponent_team_id="1610612745",
            vs_conference="East",
            vs_division="Atlantic",
            team_id="1610612744",
            conference="West",
            division="Pacific",
            last_n_games="10",
            game_scope="Season",
            player_experience="Veteran",
            player_position="G",
            starter_bench="Starter",
            draft_year="2020",
            draft_pick="2",
            college="Kentucky",
            country="USA",
            height="6-6",
            weight="200",
        )

        params = endpoint.params()

        assert params["PORound"] == "1"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["Month"] == "1"
        assert params["SeasonSegment"] == "Post All-Star"
        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"
        assert params["OpponentTeamID"] == "1610612745"
        assert params["VsConference"] == "East"
        assert params["VsDivision"] == "Atlantic"
        assert params["TeamID"] == "1610612744"
        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"
        assert params["LastNGames"] == "10"
        assert params["GameScope"] == "Season"
        assert params["PlayerExperience"] == "Veteran"
        assert params["PlayerPosition"] == "G"
        assert params["StarterBench"] == "Starter"
        assert params["DraftYear"] == "2020"
        assert params["DraftPick"] == "2"
        assert params["College"] == "Kentucky"
        assert params["Country"] == "USA"
        assert params["Height"] == "6-6"
        assert params["Weight"] == "200"

    def test_path_is_correct(self):
        """AssistTracker has correct API path."""
        endpoint = AssistTracker()

        assert endpoint.path == "assisttracker"

    def test_response_model_is_correct(self):
        """AssistTracker uses AssistTrackerResponse model."""
        endpoint = AssistTracker()

        assert endpoint.response_model is AssistTrackerResponse

    def test_endpoint_is_frozen(self):
        """AssistTracker is immutable (frozen dataclass)."""
        endpoint = AssistTracker()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
