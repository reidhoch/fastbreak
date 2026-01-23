"""Tests for LeagueHustleStatsTeam endpoint."""

from fastbreak.endpoints import LeagueHustleStatsTeam
from fastbreak.models import LeagueHustleStatsTeamResponse


class TestLeagueHustleStatsTeam:
    """Tests for LeagueHustleStatsTeam endpoint."""

    def test_init_with_defaults(self):
        """LeagueHustleStatsTeam uses sensible defaults."""
        endpoint = LeagueHustleStatsTeam()

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.league_id is None

    def test_init_with_custom_season(self):
        """LeagueHustleStatsTeam accepts custom season."""
        endpoint = LeagueHustleStatsTeam(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_totals_mode(self):
        """LeagueHustleStatsTeam accepts Totals mode."""
        endpoint = LeagueHustleStatsTeam(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_playoffs(self):
        """LeagueHustleStatsTeam accepts Playoffs season type."""
        endpoint = LeagueHustleStatsTeam(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueHustleStatsTeam(
            season="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
        )

        params = endpoint.params()

        assert params == {
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
        }

    def test_params_includes_league_id(self):
        """params() includes league_id when set."""
        endpoint = LeagueHustleStatsTeam(league_id="00")

        params = endpoint.params()

        assert params["LeagueID"] == "00"

    def test_path_is_correct(self):
        """LeagueHustleStatsTeam has correct API path."""
        endpoint = LeagueHustleStatsTeam()

        assert endpoint.path == "leaguehustlestatsteam"

    def test_response_model_is_correct(self):
        """LeagueHustleStatsTeam uses LeagueHustleStatsTeamResponse model."""
        endpoint = LeagueHustleStatsTeam()

        assert endpoint.response_model is LeagueHustleStatsTeamResponse

    def test_endpoint_is_frozen(self):
        """LeagueHustleStatsTeam is immutable (frozen dataclass)."""
        endpoint = LeagueHustleStatsTeam()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestLeagueHustleStatsTeamResponse:
    """Tests for LeagueHustleStatsTeamResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsTeam",
                    "headers": [
                        "TEAM_ID",
                        "TEAM_NAME",
                        "MIN",
                        "CONTESTED_SHOTS",
                        "CONTESTED_SHOTS_2PT",
                        "CONTESTED_SHOTS_3PT",
                        "DEFLECTIONS",
                        "CHARGES_DRAWN",
                        "SCREEN_ASSISTS",
                        "SCREEN_AST_PTS",
                        "OFF_LOOSE_BALLS_RECOVERED",
                        "DEF_LOOSE_BALLS_RECOVERED",
                        "LOOSE_BALLS_RECOVERED",
                        "PCT_LOOSE_BALLS_RECOVERED_OFF",
                        "PCT_LOOSE_BALLS_RECOVERED_DEF",
                        "OFF_BOXOUTS",
                        "DEF_BOXOUTS",
                        "BOX_OUTS",
                        "PCT_BOX_OUTS_OFF",
                        "PCT_BOX_OUTS_DEF",
                    ],
                    "rowSet": [
                        [
                            1610612737,
                            "Atlanta Hawks",
                            47.9,
                            41.08,
                            24.44,
                            16.64,
                            19.0,
                            0.45,
                            7.19,
                            17.07,
                            2.49,
                            2.42,
                            4.91,
                            0.507,
                            0.493,
                            1.23,
                            4.27,
                            5.5,
                            0.223,
                            0.777,
                        ],
                    ],
                },
            ]
        }

        response = LeagueHustleStatsTeamResponse.model_validate(raw_response)

        assert len(response.teams) == 1

        team = response.teams[0]
        assert team.team_name == "Atlanta Hawks"
        assert team.team_id == 1610612737
        assert team.min == 47.9
        assert team.contested_shots == 41.08
        assert team.deflections == 19.0
        assert team.loose_balls_recovered == 4.91

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HustleStatsTeam",
                    "headers": ["TEAM_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = LeagueHustleStatsTeamResponse.model_validate(raw_response)

        assert response.teams == []
