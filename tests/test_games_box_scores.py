"""Tests for additional box score variant helpers in fastbreak.games."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient


def _make_box_score_client(mocker: MockerFixture, attr: str, data):
    """Return NBAClient whose get_many() resolves with mock responses."""
    response = mocker.MagicMock()
    setattr(response, attr, data)
    client = NBAClient(session=mocker.MagicMock())
    client.get_many = mocker.AsyncMock(return_value=[response])
    return client


class TestGetBoxScoresAdvanced:
    """Tests for get_box_scores_advanced()."""

    async def test_returns_dict_keyed_by_game_id(self, mocker: MockerFixture):
        """get_box_scores_advanced returns dict mapping game_id to box score data."""
        from fastbreak.games import get_box_scores_advanced

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "boxScoreAdvanced", data)

        result = await get_box_scores_advanced(client, ["0022500001"])

        assert "0022500001" in result
        assert result["0022500001"] is data

    async def test_empty_input_returns_empty_dict(self, mocker: MockerFixture):
        """get_box_scores_advanced returns {} for empty game_ids."""
        from fastbreak.games import get_box_scores_advanced

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        result = await get_box_scores_advanced(client, [])

        assert result == {}

    async def test_does_not_call_api_for_empty_input(self, mocker: MockerFixture):
        """get_box_scores_advanced skips API call for empty game_ids."""
        from fastbreak.games import get_box_scores_advanced

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        await get_box_scores_advanced(client, [])

        client.get_many.assert_not_called()

    async def test_passes_box_score_advanced_endpoint(self, mocker: MockerFixture):
        """get_box_scores_advanced constructs BoxScoreAdvanced endpoints."""
        from fastbreak.endpoints import BoxScoreAdvanced
        from fastbreak.games import get_box_scores_advanced

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "boxScoreAdvanced", data)

        await get_box_scores_advanced(client, ["0022500001"])

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 1
        assert isinstance(endpoints[0], BoxScoreAdvanced)
        assert endpoints[0].game_id == "0022500001"


class TestGetBoxScoresHustle:
    """Tests for get_box_scores_hustle()."""

    async def test_returns_dict_keyed_by_game_id(self, mocker: MockerFixture):
        """get_box_scores_hustle returns dict mapping game_id to box score data."""
        from fastbreak.games import get_box_scores_hustle

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "box_score_hustle", data)

        result = await get_box_scores_hustle(client, ["0022500001"])

        assert "0022500001" in result
        assert result["0022500001"] is data

    async def test_empty_input_returns_empty_dict(self, mocker: MockerFixture):
        """get_box_scores_hustle returns {} for empty game_ids."""
        from fastbreak.games import get_box_scores_hustle

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        result = await get_box_scores_hustle(client, [])

        assert result == {}

    async def test_does_not_call_api_for_empty_input(self, mocker: MockerFixture):
        """get_box_scores_hustle skips API call for empty game_ids."""
        from fastbreak.games import get_box_scores_hustle

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        await get_box_scores_hustle(client, [])

        client.get_many.assert_not_called()

    async def test_passes_box_score_hustle_endpoint(self, mocker: MockerFixture):
        """get_box_scores_hustle constructs BoxScoreHustle endpoints."""
        from fastbreak.endpoints import BoxScoreHustle
        from fastbreak.games import get_box_scores_hustle

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "box_score_hustle", data)

        await get_box_scores_hustle(client, ["0022500001"])

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 1
        assert isinstance(endpoints[0], BoxScoreHustle)
        assert endpoints[0].game_id == "0022500001"


class TestGetBoxScoresScoring:
    """Tests for get_box_scores_scoring()."""

    async def test_returns_dict_keyed_by_game_id(self, mocker: MockerFixture):
        """get_box_scores_scoring returns dict mapping game_id to box score data."""
        from fastbreak.games import get_box_scores_scoring

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "boxScoreScoring", data)

        result = await get_box_scores_scoring(client, ["0022500001"])

        assert "0022500001" in result
        assert result["0022500001"] is data

    async def test_empty_input_returns_empty_dict(self, mocker: MockerFixture):
        """get_box_scores_scoring returns {} for empty game_ids."""
        from fastbreak.games import get_box_scores_scoring

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        result = await get_box_scores_scoring(client, [])

        assert result == {}

    async def test_does_not_call_api_for_empty_input(self, mocker: MockerFixture):
        """get_box_scores_scoring skips API call for empty game_ids."""
        from fastbreak.games import get_box_scores_scoring

        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        await get_box_scores_scoring(client, [])

        client.get_many.assert_not_called()

    async def test_passes_box_score_scoring_endpoint(self, mocker: MockerFixture):
        """get_box_scores_scoring constructs BoxScoreScoring endpoints."""
        from fastbreak.endpoints import BoxScoreScoring
        from fastbreak.games import get_box_scores_scoring

        data = mocker.MagicMock()
        client = _make_box_score_client(mocker, "boxScoreScoring", data)

        await get_box_scores_scoring(client, ["0022500001"])

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 1
        assert isinstance(endpoints[0], BoxScoreScoring)
        assert endpoints[0].game_id == "0022500001"
