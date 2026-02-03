"""Tests for shot chart leaguewide models."""

from fastbreak.models.shot_chart_leaguewide import (
    LeagueWideShotZone,
    ShotChartLeaguewideResponse,
)


class TestLeagueWideShotZone:
    """Tests for LeagueWideShotZone model."""

    def test_parse_zone_data(self):
        """LeagueWideShotZone parses API data correctly."""
        data = {
            "GRID_TYPE": "Shot Zones",
            "SHOT_ZONE_BASIC": "Restricted Area",
            "SHOT_ZONE_AREA": "Center(C)",
            "SHOT_ZONE_RANGE": "Less Than 8 ft.",
            "FGA": 15000,
            "FGM": 9000,
            "FG_PCT": 0.600,
        }

        zone = LeagueWideShotZone.model_validate(data)

        assert zone.grid_type == "Shot Zones"
        assert zone.shot_zone_basic == "Restricted Area"
        assert zone.fga == 15000
        assert zone.fg_pct == 0.600


class TestShotChartLeaguewideResponse:
    """Tests for ShotChartLeaguewideResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueWide",
                    "headers": [
                        "GRID_TYPE",
                        "SHOT_ZONE_BASIC",
                        "SHOT_ZONE_AREA",
                        "SHOT_ZONE_RANGE",
                        "FGA",
                        "FGM",
                        "FG_PCT",
                    ],
                    "rowSet": [
                        [
                            "Shot Zones",
                            "Restricted Area",
                            "Center(C)",
                            "Less Than 8 ft.",
                            15000,
                            9000,
                            0.600,
                        ],
                        [
                            "Shot Zones",
                            "Mid-Range",
                            "Left Side(L)",
                            "16-24 ft.",
                            8000,
                            3200,
                            0.400,
                        ],
                    ],
                }
            ]
        }

        response = ShotChartLeaguewideResponse.model_validate(data)

        assert len(response.league_wide) == 2
        assert response.league_wide[0].shot_zone_basic == "Restricted Area"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "LeagueWide",
                    "headers": ["GRID_TYPE"],
                    "rowSet": [],
                }
            ]
        }

        response = ShotChartLeaguewideResponse.model_validate(data)

        assert response.league_wide == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"league_wide": []}

        response = ShotChartLeaguewideResponse.model_validate(data)

        assert response.league_wide == []
