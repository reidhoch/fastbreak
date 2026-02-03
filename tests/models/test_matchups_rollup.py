"""Tests for matchups rollup models."""

from fastbreak.models.matchups_rollup import (
    MatchupRollupEntry,
    MatchupsRollupResponse,
)


class TestMatchupRollupEntry:
    """Tests for MatchupRollupEntry model."""

    def test_parse_entry(self):
        """MatchupRollupEntry parses API data correctly."""
        data = {
            "SEASON_ID": "22024",
            "POSITION": "G",
            "PERCENT_OF_TIME": 0.35,
            "DEF_PLAYER_ID": 201566,
            "DEF_PLAYER_NAME": "Anthony Davis",
            "GP": 25,
            "MATCHUP_MIN": 150.5,
            "PARTIAL_POSS": 200.0,
            "PLAYER_PTS": 45.5,
            "TEAM_PTS": 120.0,
            "MATCHUP_AST": 5.5,
            "MATCHUP_TOV": 3.2,
            "MATCHUP_BLK": 2.1,
            "MATCHUP_FGM": 18.0,
            "MATCHUP_FGA": 40.0,
            "MATCHUP_FG_PCT": 0.450,
            "MATCHUP_FG3M": 4.0,
            "MATCHUP_FG3A": 12.0,
            "MATCHUP_FG3_PCT": 0.333,
            "MATCHUP_FTM": 5.5,
            "MATCHUP_FTA": 7.0,
            "SFL": 1.5,
        }

        entry = MatchupRollupEntry.model_validate(data)

        assert entry.season_id == "22024"
        assert entry.def_player_name == "Anthony Davis"
        assert entry.matchup_fg_pct == 0.450
        assert entry.gp == 25


class TestMatchupsRollupResponse:
    """Tests for MatchupsRollupResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        data = {
            "resultSets": [
                {
                    "name": "MatchupsRollup",
                    "headers": [
                        "SEASON_ID",
                        "POSITION",
                        "PERCENT_OF_TIME",
                        "DEF_PLAYER_ID",
                        "DEF_PLAYER_NAME",
                        "GP",
                        "MATCHUP_MIN",
                        "PARTIAL_POSS",
                        "PLAYER_PTS",
                        "TEAM_PTS",
                        "MATCHUP_AST",
                        "MATCHUP_TOV",
                        "MATCHUP_BLK",
                        "MATCHUP_FGM",
                        "MATCHUP_FGA",
                        "MATCHUP_FG_PCT",
                        "MATCHUP_FG3M",
                        "MATCHUP_FG3A",
                        "MATCHUP_FG3_PCT",
                        "MATCHUP_FTM",
                        "MATCHUP_FTA",
                        "SFL",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            "G",
                            0.35,
                            201566,
                            "Anthony Davis",
                            25,
                            150.5,
                            200.0,
                            45.5,
                            120.0,
                            5.5,
                            3.2,
                            2.1,
                            18.0,
                            40.0,
                            0.450,
                            4.0,
                            12.0,
                            0.333,
                            5.5,
                            7.0,
                            1.5,
                        ],
                    ],
                }
            ]
        }

        response = MatchupsRollupResponse.model_validate(data)

        assert len(response.matchups) == 1
        assert response.matchups[0].def_player_name == "Anthony Davis"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        data = {
            "resultSets": [
                {
                    "name": "MatchupsRollup",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                }
            ]
        }

        response = MatchupsRollupResponse.model_validate(data)

        assert response.matchups == []

    def test_parse_non_tabular_data(self):
        """Response handles pre-parsed dict data."""
        data = {"matchups": []}

        response = MatchupsRollupResponse.model_validate(data)

        assert response.matchups == []
