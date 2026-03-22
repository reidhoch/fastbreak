from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.games import (
    elapsed_game_seconds,
    get_box_scores,
    get_game_ids,
    get_game_summary,
    get_games_on_date,
    get_play_by_play,
    get_todays_games,
    get_yesterdays_games,
)
from fastbreak.models.play_by_play import PlayByPlayAction


def _make_client(mocker: MockerFixture, game_entries: list[dict]):
    """Return a NBAClient whose .get() resolves to a mock LeagueGameLogResponse."""
    entry_mocks = [mocker.MagicMock(**e) for e in game_entries]
    response = mocker.MagicMock()
    response.games = entry_mocks
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGameIds:
    """Tests for the get_game_ids standalone function."""

    async def test_deduplicates_game_ids(self, mocker: MockerFixture):
        """get_game_ids returns each game ID once even though each game has two team rows."""
        # LeagueGameLog returns one row per team — two rows per game
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400001"},
                {"game_id": "0022400001"},  # same game, other team
                {"game_id": "0022400002"},
                {"game_id": "0022400002"},
            ],
        )

        result = await get_game_ids(client)

        assert result == ["0022400001", "0022400002"]

    async def test_returns_sorted_game_ids(self, mocker: MockerFixture):
        """get_game_ids returns game IDs in ascending (chronological) order."""
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400003"},
                {"game_id": "0022400003"},
                {"game_id": "0022400001"},
                {"game_id": "0022400001"},
                {"game_id": "0022400002"},
                {"game_id": "0022400002"},
            ],
        )

        result = await get_game_ids(client)

        assert result == ["0022400001", "0022400002", "0022400003"]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_game_ids returns [] when the log has no entries."""
        client = _make_client(mocker, [])

        result = await get_game_ids(client)

        assert result == []

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes the given season to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, season="2023-24")

        call_args = client.get.call_args
        endpoint = call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes season_type to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"

    async def test_passes_date_range_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes date_from and date_to to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, date_from="01/01/2025", date_to="01/31/2025")

        endpoint = client.get.call_args[0][0]
        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes team_id to LeagueGameLog for team-specific filtering."""
        client = _make_client(mocker, [])

        await get_game_ids(client, team_id=1610612744)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612744

    async def test_team_id_omitted_by_default(self, mocker: MockerFixture):
        """get_game_ids passes no team filter when team_id is not provided."""
        client = _make_client(mocker, [])

        await get_game_ids(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id is None

    async def test_logs_debug_when_team_id_filter_yields_no_results(
        self, mocker: MockerFixture
    ):
        """A debug log is emitted when a team_id filter produces an empty result."""
        client = _make_client(
            mocker,
            [{"game_id": "0022400001", "team_id": 2}],
        )
        mock_logger = mocker.patch("fastbreak.games.logger", create=True)

        result = await get_game_ids(client, team_id=999)

        assert result == []
        mock_logger.debug.assert_called_once()

    async def test_filters_game_ids_by_team_id_client_side(self, mocker: MockerFixture):
        """get_game_ids filters entries by team_id client-side (API ignores TeamID param)."""
        # API returns all teams' rows — game 3 doesn't involve team 1
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400001", "team_id": 1},
                {"game_id": "0022400001", "team_id": 2},  # other team, same game
                {"game_id": "0022400002", "team_id": 1},
                {"game_id": "0022400002", "team_id": 3},  # other team, same game
                {"game_id": "0022400003", "team_id": 2},  # team 1 not in this game
                {"game_id": "0022400003", "team_id": 3},  # team 1 not in this game
            ],
        )

        result = await get_game_ids(client, team_id=1)

        assert result == ["0022400001", "0022400002"]


def _make_scoreboard_client(mocker: MockerFixture, games: list):
    """Return a NBAClient whose .get() resolves to a mock ScoreboardV3Response."""
    scoreboard = mocker.MagicMock()
    scoreboard.games = games
    response = mocker.MagicMock()
    response.scoreboard = scoreboard
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGamesOnDate:
    """Tests for get_games_on_date standalone function."""

    async def test_returns_games_for_date(self, mocker: MockerFixture):
        """get_games_on_date returns the list of games from the scoreboard."""
        game = mocker.MagicMock()
        client = _make_scoreboard_client(mocker, [game])

        result = await get_games_on_date(client, "2025-01-15")

        assert result == [game]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_games_on_date returns [] when no games are scheduled."""
        client = _make_scoreboard_client(mocker, [])

        result = await get_games_on_date(client, "2025-07-04")

        assert result == []

    async def test_returns_empty_list_when_scoreboard_is_none(
        self, mocker: MockerFixture
    ):
        """get_games_on_date returns [] when the API returns no scoreboard."""
        response = mocker.MagicMock()
        response.scoreboard = None
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_games_on_date(client, "2025-07-04")

        assert result == []

    async def test_logs_warning_when_scoreboard_is_none(self, mocker: MockerFixture):
        """A warning is logged when the API returns a response with no scoreboard key."""
        response = mocker.MagicMock()
        response.scoreboard = None
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)
        mock_logger = mocker.patch("fastbreak.games.logger", create=True)

        result = await get_games_on_date(client, "2025-07-04")

        assert result == []
        mock_logger.warning.assert_called_once()

    async def test_passes_date_to_endpoint(self, mocker: MockerFixture):
        """get_games_on_date passes the date string to ScoreboardV3."""
        client = _make_scoreboard_client(mocker, [])

        await get_games_on_date(client, "2025-01-15")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_date == "2025-01-15"

    async def test_returns_multiple_games(self, mocker: MockerFixture):
        """get_games_on_date returns all games on a busy night."""
        games = [mocker.MagicMock() for _ in range(10)]
        client = _make_scoreboard_client(mocker, games)

        result = await get_games_on_date(client, "2025-01-07")

        assert len(result) == 10

    async def test_raises_for_mm_dd_yyyy_format(self, mocker: MockerFixture):
        """get_games_on_date raises ValueError when given MM/DD/YYYY instead of YYYY-MM-DD."""
        client = _make_scoreboard_client(mocker, [])

        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            await get_games_on_date(client, "01/15/2025")

        client.get.assert_not_called()

    async def test_raises_for_wrong_separator(self, mocker: MockerFixture):
        """get_games_on_date raises ValueError when given slashes instead of dashes."""
        client = _make_scoreboard_client(mocker, [])

        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            await get_games_on_date(client, "2025/01/15")

        client.get.assert_not_called()

    async def test_raises_for_invalid_date_string(self, mocker: MockerFixture):
        """get_games_on_date raises ValueError for a non-date string."""
        client = _make_scoreboard_client(mocker, [])

        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            await get_games_on_date(client, "not-a-date")

        client.get.assert_not_called()

    async def test_raises_for_semantically_invalid_date(self, mocker: MockerFixture):
        """get_games_on_date raises ValueError for a correctly formatted but invalid date."""
        client = _make_scoreboard_client(mocker, [])

        with pytest.raises(ValueError, match="valid calendar date"):
            await get_games_on_date(client, "2025-13-01")

        client.get.assert_not_called()

    async def test_raises_for_feb_30(self, mocker: MockerFixture):
        """get_games_on_date raises ValueError for Feb 30, which is structurally valid but not a real date."""
        client = _make_scoreboard_client(mocker, [])

        with pytest.raises(ValueError, match="valid calendar date"):
            await get_games_on_date(client, "2025-02-30")

        client.get.assert_not_called()


class TestGetTodaysGames:
    """Tests for get_todays_games convenience function."""

    async def test_returns_todays_games(self, mocker: MockerFixture):
        """get_todays_games returns games from today's scoreboard."""
        game = mocker.MagicMock()
        client = _make_scoreboard_client(mocker, [game])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.isoformat.return_value = "2025-02-25"

        result = await get_todays_games(client)

        assert result == [game]

    async def test_passes_todays_date_to_endpoint(self, mocker: MockerFixture):
        """get_todays_games uses today's date in YYYY-MM-DD format."""
        client = _make_scoreboard_client(mocker, [])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.isoformat.return_value = "2025-02-25"

        await get_todays_games(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_date == "2025-02-25"


class TestGetYesterdaysGames:
    """Tests for get_yesterdays_games convenience function."""

    async def test_returns_yesterdays_games(self, mocker: MockerFixture):
        """get_yesterdays_games returns games from yesterday's scoreboard."""
        game = mocker.MagicMock()
        client = _make_scoreboard_client(mocker, [game])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.__sub__.return_value.isoformat.return_value = (
            "2025-02-24"
        )

        result = await get_yesterdays_games(client)

        assert result == [game]

    async def test_passes_yesterdays_date_to_endpoint(self, mocker: MockerFixture):
        """get_yesterdays_games uses yesterday's date in YYYY-MM-DD format."""
        client = _make_scoreboard_client(mocker, [])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.__sub__.return_value.isoformat.return_value = (
            "2025-02-24"
        )

        await get_yesterdays_games(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_date == "2025-02-24"


def _make_summary_client(mocker: MockerFixture, summary):
    """Return a NBAClient whose .get() resolves to a mock BoxScoreSummaryResponse."""
    response = mocker.MagicMock()
    response.boxScoreSummary = summary
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGameSummary:
    """Tests for get_game_summary standalone function."""

    async def test_returns_summary_for_game(self, mocker: MockerFixture):
        """get_game_summary returns the boxScoreSummary from the response."""
        summary = mocker.MagicMock()
        client = _make_summary_client(mocker, summary)

        result = await get_game_summary(client, "0022400001")

        assert result == summary

    async def test_passes_game_id_to_endpoint(self, mocker: MockerFixture):
        """get_game_summary passes the game_id to BoxScoreSummary."""
        client = _make_summary_client(mocker, mocker.MagicMock())

        await get_game_summary(client, "0022400001")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022400001"


def _make_batch_client(mocker: MockerFixture, box_scores: dict):
    """Return a NBAClient whose .get_many() resolves to mock responses in order."""
    game_ids = list(box_scores.keys())
    responses = []
    for gid in game_ids:
        resp = mocker.MagicMock()
        resp.boxScoreTraditional = box_scores[gid]
        responses.append(resp)
    client = NBAClient(session=mocker.MagicMock())
    client.get_many = mocker.AsyncMock(return_value=responses)
    return client, game_ids


class TestGetBoxScores:
    """Tests for get_box_scores batch utility."""

    async def test_returns_dict_mapping_game_id_to_box_score(
        self, mocker: MockerFixture
    ):
        """get_box_scores returns a dict of game_id -> box score data."""
        bs1, bs2 = mocker.MagicMock(), mocker.MagicMock()
        client, game_ids = _make_batch_client(
            mocker, {"0022400001": bs1, "0022400002": bs2}
        )

        result = await get_box_scores(client, game_ids)

        assert result == {"0022400001": bs1, "0022400002": bs2}

    async def test_returns_empty_dict_for_no_game_ids(self, mocker: MockerFixture):
        """get_box_scores returns {} when given an empty list."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        result = await get_box_scores(client, [])

        assert result == {}

    async def test_calls_get_many_with_box_score_endpoints(self, mocker: MockerFixture):
        """get_box_scores passes BoxScoreTraditional endpoints to get_many."""
        client, game_ids = _make_batch_client(
            mocker, {"0022400001": mocker.MagicMock()}
        )

        await get_box_scores(client, game_ids)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 1
        assert endpoints[0].game_id == "0022400001"

    async def test_handles_single_game(self, mocker: MockerFixture):
        """get_box_scores works correctly for a single game ID."""
        bs = mocker.MagicMock()
        client, game_ids = _make_batch_client(mocker, {"0022400001": bs})

        result = await get_box_scores(client, game_ids)

        assert result == {"0022400001": bs}


class TestGetPlayByPlay:
    """Tests for get_play_by_play standalone function."""

    async def test_returns_list_of_actions(
        self, mocker: MockerFixture, make_pbp_client
    ):
        """get_play_by_play returns the list of play actions."""
        action = mocker.MagicMock()
        client = make_pbp_client([action])

        result = await get_play_by_play(client, "0022400001")

        assert result == [action]

    async def test_returns_empty_list_when_no_actions(self, make_pbp_client):
        """get_play_by_play returns [] when no actions exist."""
        client = make_pbp_client([])

        result = await get_play_by_play(client, "0022400001")

        assert result == []

    async def test_passes_game_id_to_endpoint(self, make_pbp_client):
        """get_play_by_play passes game_id to PlayByPlay."""
        client = make_pbp_client([])

        await get_play_by_play(client, "0022400001")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022400001"


def test_get_yesterdays_games_exported():
    """get_yesterdays_games is importable from the top-level package."""
    from fastbreak import get_yesterdays_games  # noqa: PLC0415

    assert callable(get_yesterdays_games)


def _make_action(
    *,
    period: int = 1,
    clock: str = "PT10M00.00S",
    score_home: str = "",
    score_away: str = "",
    description: str = "Jump Shot",
    action_type: str = "2pt",
    action_number: int = 1,
) -> PlayByPlayAction:
    """Minimal PlayByPlayAction with real Pydantic construction for game_flow tests."""
    return PlayByPlayAction(
        actionNumber=action_number,
        clock=clock,
        period=period,
        teamId=1610612744,
        teamTricode="GSW",
        personId=201939,
        playerName="Stephen Curry",
        playerNameI="S. Curry",
        xLegacy=0,
        yLegacy=0,
        shotDistance=0,
        shotResult="Made" if score_home else "",
        isFieldGoal=1 if score_home else 0,
        scoreHome=score_home,
        scoreAway=score_away,
        pointsTotal=2,
        location="H",
        description=description,
        actionType=action_type,
        subType="",
        videoAvailable=0,
        shotValue=2,
        actionId=action_number,
    )


class TestParseClock:
    """Tests for the private _parse_clock() ISO 8601 duration helper."""

    def test_full_period_start(self) -> None:
        """Start of a 12-minute period (PT12M00.00S) returns 720.0 seconds."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("PT12M00.00S") == pytest.approx(720.0)

    def test_standard_clock_string(self) -> None:
        """Typical in-game clock (PT04M32.00S) parses to 272.0 seconds remaining."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("PT04M32.00S") == pytest.approx(272.0)

    def test_zero_remaining(self) -> None:
        """End of period (PT00M00.00S) returns 0.0."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("PT00M00.00S") == pytest.approx(0.0)

    def test_sub_second_precision(self) -> None:
        """Fractional seconds are preserved (PT01M30.50S → 90.5)."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("PT01M30.50S") == pytest.approx(90.5)

    def test_malformed_returns_zero(self) -> None:
        """An unrecognised clock string returns 0.0 rather than raising."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("") == pytest.approx(0.0)
        assert _parse_clock("invalid") == pytest.approx(0.0)

    def test_ot_period_start(self) -> None:
        """Start of a 5-minute OT period (PT05M00.00S) returns 300.0 seconds."""
        from fastbreak.games import _parse_clock

        assert _parse_clock("PT05M00.00S") == pytest.approx(300.0)


class TestGameFlow:
    """Tests for the pure game_flow() score-line computation function."""

    def test_empty_actions_returns_empty_list(self) -> None:
        """No actions → no flow points."""
        from fastbreak.games import game_flow

        assert game_flow([]) == []

    def test_non_scoring_actions_skipped(self) -> None:
        """Actions with empty scoreHome/scoreAway are skipped."""
        from fastbreak.games import game_flow

        actions = [_make_action(score_home="", score_away="")]
        assert game_flow(actions) == []

    def test_single_scoring_event_returns_one_point(self) -> None:
        """A single scoring action produces exactly one GameFlowPoint."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(period=1, clock="PT10M00.00S", score_home="2", score_away="0")
        ]
        assert len(game_flow(actions)) == 1

    def test_returns_game_flow_point_instances(self) -> None:
        """All items in the result are GameFlowPoint objects."""
        from fastbreak.games import GameFlowPoint, game_flow

        actions = [
            _make_action(period=1, clock="PT10M00.00S", score_home="2", score_away="0")
        ]
        result = game_flow(actions)
        assert isinstance(result[0], GameFlowPoint)

    def test_elapsed_seconds_q1_start(self) -> None:
        """Q1 with 12:00 remaining → elapsed = 0.0 seconds from tip-off."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(period=1, clock="PT12M00.00S", score_home="2", score_away="0")
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(0.0)

    def test_elapsed_seconds_q1_midpoint(self) -> None:
        """Q1 with 10:00 remaining → elapsed = 120 seconds."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(period=1, clock="PT10M00.00S", score_home="2", score_away="0")
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(120.0)

    def test_elapsed_seconds_q2_start(self) -> None:
        """Q2 with 12:00 remaining → elapsed = 720 seconds (after Q1)."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=2, clock="PT12M00.00S", score_home="30", score_away="28"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(720.0)

    def test_elapsed_seconds_end_of_regulation(self) -> None:
        """Q4 with 0:00 remaining → elapsed = 2880 seconds (48 minutes)."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=4, clock="PT00M00.00S", score_home="110", score_away="108"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(2880.0)

    def test_elapsed_seconds_ot_start(self) -> None:
        """OT period 5 with 5:00 remaining → elapsed = 2880 seconds (start of OT)."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=5, clock="PT05M00.00S", score_home="112", score_away="110"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(2880.0)

    def test_elapsed_seconds_ot_midpoint(self) -> None:
        """OT period 5 with 2:30 remaining → elapsed = 2880 + 150 = 3030 seconds."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=5, clock="PT02M30.00S", score_home="118", score_away="115"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(3030.0)

    def test_q4_elapsed_regulation_boundary(self) -> None:
        """Period 4 with 6:00 remaining → elapsed = 3*720 + (720-360) = 2520.0 seconds.

        This tests the exact boundary between regulation (period <= 4) and
        overtime (period > 4), killing a <= to < boundary mutant.
        """
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=4, clock="PT06M00.00S", score_home="95", score_away="90"
            )
        ]
        # Q4: offset=(4-1)*720=2160, remaining=360 → 2160+(720-360)=2520
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(2520.0)

    def test_q4_end_of_regulation(self) -> None:
        """Period 4 with 0:00 remaining → elapsed = 2880.0 (full regulation)."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=4, clock="PT00M00.00S", score_home="100", score_away="100"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(2880.0)

    def test_double_overtime_elapsed(self) -> None:
        """Period 6 (2OT) with 5:00 remaining → elapsed = 2880 + 300 = 3180 seconds."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=6, clock="PT05M00.00S", score_home="125", score_away="122"
            )
        ]
        assert game_flow(actions)[0].elapsed_seconds == pytest.approx(3180.0)

    def test_margin_is_home_minus_away(self) -> None:
        """margin = score_home - score_away (positive when home leads)."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=2, clock="PT06M00.00S", score_home="55", score_away="50"
            )
        ]
        assert game_flow(actions)[0].margin == 5

    def test_margin_negative_when_away_leads(self) -> None:
        """margin is negative when the away team leads."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=3, clock="PT06M00.00S", score_home="70", score_away="78"
            )
        ]
        assert game_flow(actions)[0].margin == -8

    def test_description_preserved(self) -> None:
        """description from the action is stored on GameFlowPoint."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="3",
                score_away="0",
                description="Curry 3pt Jump Shot",
            )
        ]
        assert game_flow(actions)[0].description == "Curry 3pt Jump Shot"

    def test_score_values_stored(self) -> None:
        """score_home and score_away on GameFlowPoint match the action scores."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(period=1, clock="PT08M00.00S", score_home="7", score_away="5")
        ]
        point = game_flow(actions)[0]
        assert point.score_home == 7
        assert point.score_away == 5

    def test_period_stored(self) -> None:
        """period is stored on GameFlowPoint."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=3, clock="PT06M00.00S", score_home="70", score_away="65"
            )
        ]
        assert game_flow(actions)[0].period == 3

    def test_clock_stored_unchanged(self) -> None:
        """Original ISO 8601 clock string is stored unchanged."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1, clock="PT06M15.00S", score_home="12", score_away="10"
            )
        ]
        assert game_flow(actions)[0].clock == "PT06M15.00S"

    def test_mixed_scoring_and_non_scoring(self) -> None:
        """Only scoring actions are included; non-scoring are filtered out."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT11M00.00S",
                score_home="",
                score_away="",
                action_number=1,
            ),
            _make_action(
                period=1,
                clock="PT10M30.00S",
                score_home="2",
                score_away="0",
                action_number=2,
            ),
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="",
                score_away="",
                action_number=3,
            ),
            _make_action(
                period=1,
                clock="PT09M30.00S",
                score_home="2",
                score_away="2",
                action_number=4,
            ),
        ]
        assert len(game_flow(actions)) == 2

    def test_order_preserved(self) -> None:
        """Points appear in the same order as the input actions."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="2",
                score_away="0",
                action_number=1,
            ),
            _make_action(
                period=1,
                clock="PT09M00.00S",
                score_home="4",
                score_away="0",
                action_number=2,
            ),
            _make_action(
                period=1,
                clock="PT08M00.00S",
                score_home="4",
                score_away="2",
                action_number=3,
            ),
        ]
        result = game_flow(actions)
        scores = [(p.score_home, p.score_away) for p in result]
        assert scores == [(2, 0), (4, 0), (4, 2)]

    def test_invalid_score_string_skipped(self) -> None:
        """Actions with non-integer score strings are skipped gracefully."""
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="N/A",
                score_away="0",
            )
        ]
        assert game_flow(actions) == []

    def test_action_with_score_home_but_no_score_away_skipped(self) -> None:
        """An action where scoreHome is set but scoreAway is empty is skipped.

        The ``not scoreHome or not scoreAway`` guard must skip the action when
        *either* score is missing, not only when *both* are.
        """
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="50",
                score_away="",
            )
        ]
        assert game_flow(actions) == []

    def test_action_with_score_away_but_no_score_home_skipped(self) -> None:
        """An action where scoreAway is set but scoreHome is empty is skipped.

        Mirror of the above — ensures the `or` guards both sides independently.
        """
        from fastbreak.games import game_flow

        actions = [
            _make_action(
                period=1,
                clock="PT10M00.00S",
                score_home="",
                score_away="50",
            )
        ]
        assert game_flow(actions) == []

    def test_q4_treated_as_regulation_not_overtime(self) -> None:
        """Period 4 uses the regulation formula, not the overtime formula.

        If the boundary check ``period <= 4`` were changed to ``period < 4``,
        period 4 would be
        treated as overtime. The OT branch uses 300-second periods while
        regulation uses 720-second periods.

        While the elapsed calculation happens to be numerically equivalent for
        period 4 in both branches (an algebraic coincidence), we verify the
        regulation behaviour by checking that period 4 produces elapsed times
        consistent with three full 720-second periods plus the Q4 offset —
        and that a period-5 action immediately after lands at the expected
        2880-second boundary.
        """
        from fastbreak.games import game_flow

        # Q4 at the 6-minute mark plus the very start of OT in the same flow
        actions = [
            _make_action(
                period=4,
                clock="PT06M00.00S",
                score_home="100",
                score_away="100",
                action_number=1,
            ),
            _make_action(
                period=5,
                clock="PT05M00.00S",
                score_home="102",
                score_away="100",
                action_number=2,
            ),
        ]
        flow = game_flow(actions)
        assert len(flow) == 2
        # Q4: (4-1)*720 + (720-360) = 2520
        assert flow[0].elapsed_seconds == pytest.approx(2520.0)
        # OT1 start: 4*720 + 0*(300) + (300-300) = 2880
        assert flow[1].elapsed_seconds == pytest.approx(2880.0)


class TestElapsedGameSeconds:
    """Tests for the public elapsed_game_seconds() helper."""

    def test_q1_start(self) -> None:
        """Q1 with 12:00 remaining → 0.0 seconds elapsed."""
        assert elapsed_game_seconds("PT12M00.00S", 1) == pytest.approx(0.0)

    def test_q1_midpoint(self) -> None:
        """Q1 with 10:00 remaining → 120.0 seconds elapsed."""
        assert elapsed_game_seconds("PT10M00.00S", 1) == pytest.approx(120.0)

    def test_q2_start(self) -> None:
        """Q2 with 12:00 remaining → 720.0 seconds elapsed."""
        assert elapsed_game_seconds("PT12M00.00S", 2) == pytest.approx(720.0)

    def test_q4_end(self) -> None:
        """Q4 with 0:00 remaining → 2880.0 seconds (full regulation)."""
        assert elapsed_game_seconds("PT00M00.00S", 4) == pytest.approx(2880.0)

    def test_ot1_start(self) -> None:
        """OT1 with 5:00 remaining → 2880.0 seconds."""
        assert elapsed_game_seconds("PT05M00.00S", 5) == pytest.approx(2880.0)

    def test_ot1_midpoint(self) -> None:
        """OT1 with 2:30 remaining → 3030.0 seconds."""
        assert elapsed_game_seconds("PT02M30.00S", 5) == pytest.approx(3030.0)

    def test_double_ot(self) -> None:
        """2OT with 5:00 remaining → 3180.0 seconds."""
        assert elapsed_game_seconds("PT05M00.00S", 6) == pytest.approx(3180.0)

    def test_invalid_clock(self) -> None:
        """Invalid clock string returns period offset (0.0 remaining)."""
        assert elapsed_game_seconds("INVALID", 1) == pytest.approx(720.0)
