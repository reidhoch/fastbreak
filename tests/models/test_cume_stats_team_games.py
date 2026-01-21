"""Tests for cumestatsteamgames models."""

from fastbreak.models.cume_stats_team_games import (
    CumeStatsTeamGamesResponse,
    TeamGame,
)


class TestTeamGame:
    """Tests for TeamGame model."""

    def test_parse_valid_entry(self):
        """TeamGame parses a valid game entry."""
        data = {
            "MATCHUP": "01/20/2026 Spurs at Rockets",
            "GAME_ID": "0022500615",
        }

        game = TeamGame.model_validate(data)

        assert game.matchup == "01/20/2026 Spurs at Rockets"
        assert game.game_id == "0022500615"

    def test_parse_road_game(self):
        """TeamGame parses a road game entry."""
        data = {
            "MATCHUP": "01/11/2026 Rockets at Kings",
            "GAME_ID": "0022500557",
        }

        game = TeamGame.model_validate(data)

        assert game.matchup == "01/11/2026 Rockets at Kings"
        assert game.game_id == "0022500557"


class TestCumeStatsTeamGamesResponse:
    """Tests for CumeStatsTeamGamesResponse model."""

    def test_parse_full_response(self):
        """CumeStatsTeamGamesResponse parses API result sets."""
        data = {
            "resource": "cumestatsteamgames",
            "parameters": {
                "LeagueID": "00",
                "SeasonID": "2025-26",
                "SeasonType": "Regular Season",
                "TeamID": 1610612745,
            },
            "resultSets": [
                {
                    "name": "CumeStatsTeamGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": [
                        ["01/20/2026 Spurs at Rockets", "0022500615"],
                        ["01/18/2026 Pelicans at Rockets", "0022500604"],
                        ["01/16/2026 Timberwolves at Rockets", "0022500591"],
                    ],
                },
            ],
        }

        response = CumeStatsTeamGamesResponse.model_validate(data)

        assert len(response.games) == 3
        assert response.games[0].matchup == "01/20/2026 Spurs at Rockets"
        assert response.games[0].game_id == "0022500615"
        assert response.games[2].game_id == "0022500591"

    def test_handles_empty_result_set(self):
        """CumeStatsTeamGamesResponse handles empty games list."""
        data = {
            "resultSets": [
                {
                    "name": "CumeStatsTeamGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": [],
                },
            ],
        }

        response = CumeStatsTeamGamesResponse.model_validate(data)

        assert len(response.games) == 0

    def test_parse_direct_dict(self):
        """CumeStatsTeamGamesResponse handles already-parsed dict format."""
        data = {
            "games": [
                {"MATCHUP": "01/20/2026 Spurs at Rockets", "GAME_ID": "0022500615"},
            ],
        }

        response = CumeStatsTeamGamesResponse.model_validate(data)

        assert len(response.games) == 1
        assert response.games[0].game_id == "0022500615"

    def test_preserves_game_order(self):
        """CumeStatsTeamGamesResponse maintains game order from API."""
        data = {
            "resultSets": [
                {
                    "name": "CumeStatsTeamGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": [
                        ["Game 1", "001"],
                        ["Game 2", "002"],
                        ["Game 3", "003"],
                        ["Game 4", "004"],
                    ],
                },
            ],
        }

        response = CumeStatsTeamGamesResponse.model_validate(data)

        assert response.games[0].game_id == "001"
        assert response.games[1].game_id == "002"
        assert response.games[2].game_id == "003"
        assert response.games[3].game_id == "004"

    def test_handles_full_season(self):
        """CumeStatsTeamGamesResponse handles full season of games."""
        # Simulating a full season worth of games (41 home games)
        games = [[f"Game {i}", f"00225006{i:02d}"] for i in range(41)]
        data = {
            "resultSets": [
                {
                    "name": "CumeStatsTeamGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": games,
                },
            ],
        }

        response = CumeStatsTeamGamesResponse.model_validate(data)

        assert len(response.games) == 41
