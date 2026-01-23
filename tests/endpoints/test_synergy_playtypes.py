from fastbreak.endpoints import SynergyPlaytypes
from fastbreak.models import SynergyPlaytypesResponse


class TestSynergyPlaytypes:
    """Tests for SynergyPlaytypes endpoint."""

    def test_init_with_defaults(self):
        """SynergyPlaytypes uses sensible defaults."""
        endpoint = SynergyPlaytypes()

        assert endpoint.league_id == "00"
        assert endpoint.season_year == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.player_or_team == "P"

    def test_init_with_custom_league_id(self):
        """SynergyPlaytypes accepts custom league_id."""
        endpoint = SynergyPlaytypes(league_id="10")

        assert endpoint.league_id == "10"

    def test_init_with_custom_season_year(self):
        """SynergyPlaytypes accepts custom season_year."""
        endpoint = SynergyPlaytypes(season_year="2023-24")

        assert endpoint.season_year == "2023-24"

    def test_init_with_custom_season_type(self):
        """SynergyPlaytypes accepts custom season_type."""
        endpoint = SynergyPlaytypes(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_custom_per_mode(self):
        """SynergyPlaytypes accepts custom per_mode."""
        endpoint = SynergyPlaytypes(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_team_mode(self):
        """SynergyPlaytypes accepts Team mode."""
        endpoint = SynergyPlaytypes(player_or_team="T")

        assert endpoint.player_or_team == "T"

    def test_init_with_play_type(self):
        """SynergyPlaytypes accepts play_type filter."""
        endpoint = SynergyPlaytypes(play_type="Isolation")

        assert endpoint.play_type == "Isolation"

    def test_init_with_type_grouping(self):
        """SynergyPlaytypes accepts type_grouping filter."""
        endpoint = SynergyPlaytypes(type_grouping="offensive")

        assert endpoint.type_grouping == "offensive"

    def test_init_with_all_custom_params(self):
        """SynergyPlaytypes accepts all custom parameters."""
        endpoint = SynergyPlaytypes(
            league_id="10",
            season_year="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            player_or_team="T",
            play_type="Transition",
            type_grouping="defensive",
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_year == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.player_or_team == "T"
        assert endpoint.play_type == "Transition"
        assert endpoint.type_grouping == "defensive"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = SynergyPlaytypes(
            league_id="00",
            season_year="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
            player_or_team="P",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonYear": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "PlayerOrTeam": "P",
        }

    def test_params_includes_optional_params(self):
        """params() includes optional parameters when set."""
        endpoint = SynergyPlaytypes(
            play_type="Isolation",
            type_grouping="offensive",
        )

        params = endpoint.params()

        assert params["PlayType"] == "Isolation"
        assert params["TypeGrouping"] == "offensive"

    def test_params_excludes_none_values(self):
        """params() excludes None optional parameters."""
        endpoint = SynergyPlaytypes()

        params = endpoint.params()

        assert "PlayType" not in params
        assert "TypeGrouping" not in params

    def test_path_is_correct(self):
        """SynergyPlaytypes has correct API path."""
        endpoint = SynergyPlaytypes()

        assert endpoint.path == "synergyplaytypes"

    def test_response_model_is_correct(self):
        """SynergyPlaytypes uses SynergyPlaytypesResponse model."""
        endpoint = SynergyPlaytypes()

        assert endpoint.response_model is SynergyPlaytypesResponse

    def test_endpoint_is_frozen(self):
        """SynergyPlaytypes is immutable (frozen dataclass)."""
        endpoint = SynergyPlaytypes()

        try:
            endpoint.season_year = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
