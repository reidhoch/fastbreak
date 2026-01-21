"""Tests for cumestatsplayergames models."""

from fastbreak.models.cume_stats_player_games import (
    CumeStatsPlayerGamesResponse,
    PlayerGame,
)


class TestPlayerGame:
    """Tests for PlayerGame model."""

    def test_parse_valid_entry(self):
        """PlayerGame parses a valid game entry."""
        data = {
            "MATCHUP": "01/20/2026 Lakers at Nuggets",
            "GAME_ID": "0022500617",
        }

        game = PlayerGame.model_validate(data)

        assert game.matchup == "01/20/2026 Lakers at Nuggets"
        assert game.game_id == "0022500617"

    def test_parse_home_game(self):
        """PlayerGame parses a home game entry."""
        data = {
            "MATCHUP": "01/18/2026 Raptors at Lakers",
            "GAME_ID": "0022500607",
        }

        game = PlayerGame.model_validate(data)

        assert game.matchup == "01/18/2026 Raptors at Lakers"
        assert game.game_id == "0022500607"


class TestCumeStatsPlayerGamesResponse:
    """Tests for CumeStatsPlayerGamesResponse model."""

    def test_parse_full_response(self):
        """CumeStatsPlayerGamesResponse parses API result sets."""
        data = {
            "resource": "cumestatsplayergames",
            "parameters": {
                "LeagueID": "00",
                "Season": "2025-26",
                "SeasonType": "Regular Season",
                "PlayerID": 2544,
            },
            "resultSets": [
                {
                    "name": "CumeStatsPlayerGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": [
                        ["01/20/2026 Lakers at Nuggets", "0022500617"],
                        ["01/18/2026 Raptors at Lakers", "0022500607"],
                        ["01/17/2026 Lakers at Trail Blazers", "0022500601"],
                    ],
                },
            ],
        }

        response = CumeStatsPlayerGamesResponse.model_validate(data)

        assert len(response.games) == 3
        assert response.games[0].matchup == "01/20/2026 Lakers at Nuggets"
        assert response.games[0].game_id == "0022500617"
        assert response.games[2].game_id == "0022500601"

    def test_handles_empty_result_set(self):
        """CumeStatsPlayerGamesResponse handles empty games list."""
        data = {
            "resultSets": [
                {
                    "name": "CumeStatsPlayerGames",
                    "headers": ["MATCHUP", "GAME_ID"],
                    "rowSet": [],
                },
            ],
        }

        response = CumeStatsPlayerGamesResponse.model_validate(data)

        assert len(response.games) == 0

    def test_parse_direct_dict(self):
        """CumeStatsPlayerGamesResponse handles already-parsed dict format."""
        data = {
            "games": [
                {"MATCHUP": "01/20/2026 Lakers at Nuggets", "GAME_ID": "0022500617"},
            ],
        }

        response = CumeStatsPlayerGamesResponse.model_validate(data)

        assert len(response.games) == 1
        assert response.games[0].game_id == "0022500617"

    def test_preserves_game_order(self):
        """CumeStatsPlayerGamesResponse maintains game order from API."""
        data = {
            "resultSets": [
                {
                    "name": "CumeStatsPlayerGames",
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

        response = CumeStatsPlayerGamesResponse.model_validate(data)

        assert response.games[0].game_id == "001"
        assert response.games[1].game_id == "002"
        assert response.games[2].game_id == "003"
        assert response.games[3].game_id == "004"
