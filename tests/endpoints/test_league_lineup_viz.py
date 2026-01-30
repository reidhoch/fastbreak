"""Tests for LeagueLineupViz endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import LeagueLineupViz
from fastbreak.models import LeagueLineupVizResponse


class TestLeagueLineupViz:
    """Tests for LeagueLineupViz endpoint."""

    def test_init_with_defaults(self):
        """LeagueLineupViz uses sensible defaults."""
        endpoint = LeagueLineupViz(team_id=1610612747)

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "Totals"
        assert endpoint.measure_type == "Base"
        assert endpoint.group_quantity == 5
        assert endpoint.minutes_min == 10
        assert endpoint.league_id == "00"
        assert endpoint.team_id == 1610612747

    def test_init_with_custom_season(self):
        """LeagueLineupViz accepts custom season."""
        endpoint = LeagueLineupViz(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_per_game_mode(self):
        """LeagueLineupViz accepts PerGame mode."""
        endpoint = LeagueLineupViz(team_id=1610612747, per_mode="PerGame")

        assert endpoint.per_mode == "PerGame"

    def test_init_with_playoffs(self):
        """LeagueLineupViz accepts Playoffs season type."""
        endpoint = LeagueLineupViz(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_team_filter(self):
        """LeagueLineupViz accepts team filter."""
        endpoint = LeagueLineupViz(team_id=1610612737)

        assert endpoint.team_id == 1610612737

    def test_init_with_group_quantity(self):
        """LeagueLineupViz accepts different group quantities."""
        endpoint = LeagueLineupViz(team_id=1610612747, group_quantity=3)

        assert endpoint.group_quantity == 3

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueLineupViz(
            team_id=1610612747,
            season="2024-25",
            season_type="Regular Season",
            per_mode="Totals",
            measure_type="Base",
            group_quantity=5,
            minutes_min=10,
        )

        params = endpoint.params()

        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"
        assert params["MeasureType"] == "Base"
        assert params["GroupQuantity"] == "5"
        assert params["MinutesMin"] == "10"

    def test_params_includes_all_filters(self):
        """params() includes all filter parameters."""
        endpoint = LeagueLineupViz(team_id=1610612747)

        params = endpoint.params()

        # All required filter params should be present
        assert "Conference" in params
        assert "Division" in params
        assert "GameSegment" in params
        assert "LastNGames" in params
        assert "VsConference" in params
        assert "VsDivision" in params

    def test_path_is_correct(self):
        """LeagueLineupViz has correct API path."""
        endpoint = LeagueLineupViz(team_id=1610612747)

        assert endpoint.path == "leaguelineupviz"

    def test_response_model_is_correct(self):
        """LeagueLineupViz uses LeagueLineupVizResponse model."""
        endpoint = LeagueLineupViz(team_id=1610612747)

        assert endpoint.response_model is LeagueLineupVizResponse

    def test_endpoint_is_frozen(self):
        """LeagueLineupViz is immutable (frozen dataclass)."""
        endpoint = LeagueLineupViz(team_id=1610612747)

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestLeagueLineupVizResponse:
    """Tests for LeagueLineupVizResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueLineupViz",
                    "headers": [
                        "GROUP_ID",
                        "GROUP_NAME",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "MIN",
                        "OFF_RATING",
                        "DEF_RATING",
                        "NET_RATING",
                        "PACE",
                        "TS_PCT",
                        "FTA_RATE",
                        "TM_AST_PCT",
                        "PCT_FGA_2PT",
                        "PCT_FGA_3PT",
                        "PCT_PTS_2PT_MR",
                        "PCT_PTS_FB",
                        "PCT_PTS_FT",
                        "PCT_PTS_PAINT",
                        "PCT_AST_FGM",
                        "PCT_UAST_FGM",
                        "OPP_FG3_PCT",
                        "OPP_EFG_PCT",
                        "OPP_FTA_RATE",
                        "OPP_TOV_PCT",
                        "SUM_TM_MIN",
                    ],
                    "rowSet": [
                        [
                            "-1626157-1628384-1628404-1628969-1628973-",
                            "K. Towns - O. Anunoby - J. Hart - M. Bridges - J. Brunson",
                            1610612752,
                            "NYK",
                            939.9,
                            117.7,
                            114.4,
                            3.3,
                            98.76,
                            0.601,
                            0.239,
                            0.661,
                            0.648,
                            0.352,
                            0.06,
                            0.138,
                            0.143,
                            0.508,
                            0.661,
                            0.339,
                            0.372,
                            0.561,
                            0.188,
                            0.133,
                            939.936667,
                        ],
                    ],
                },
            ]
        }

        response = LeagueLineupVizResponse.model_validate(raw_response)

        assert len(response.lineups) == 1

        lineup = response.lineups[0]
        assert lineup.team_abbreviation == "NYK"
        assert (
            lineup.group_name
            == "K. Towns - O. Anunoby - J. Hart - M. Bridges - J. Brunson"
        )
        assert lineup.off_rating == 117.7
        assert lineup.def_rating == 114.4
        assert lineup.net_rating == 3.3

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueLineupViz",
                    "headers": ["GROUP_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = LeagueLineupVizResponse.model_validate(raw_response)

        assert response.lineups == []
