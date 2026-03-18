"""Tests for fastbreak.matchups — matchup analysis helpers."""

from __future__ import annotations

import pytest

from fastbreak.models.box_score_matchups_v3 import BoxScoreMatchupsV3Response
from fastbreak.models.league_season_matchups import SeasonMatchup
from fastbreak.models.player_vs_player import PlayerVsPlayerResponse


def _make_season_matchup(
    *,
    off_player_id: int = 1,
    off_player_name: str = "Offense",
    def_player_id: int = 2,
    def_player_name: str = "Defense",
    gp: int = 10,
    matchup_min: float = 5.0,
    partial_poss: float = 15.0,
    player_pts: float = 12.0,
    team_pts: float = 20.0,
    matchup_fgm: float = 5.0,
    matchup_fga: float = 12.0,
    matchup_fg_pct: float | None = 0.417,
    matchup_fg3m: float = 1.0,
    matchup_fg3a: float = 3.0,
    matchup_fg3_pct: float | None = 0.333,
    matchup_ftm: float = 2.0,
    matchup_fta: float = 3.0,
    matchup_ast: float = 1.0,
    matchup_tov: float = 0.5,
    matchup_blk: float = 0.2,
    help_blk: float = 0.1,
    help_fgm: float = 1.0,
    help_fga: float = 3.0,
    help_fg_pct: float | None = 0.333,
    sfl: float = 0.5,
    season_id: str = "22025",
) -> SeasonMatchup:
    return SeasonMatchup.model_validate(
        {
            "SEASON_ID": season_id,
            "OFF_PLAYER_ID": off_player_id,
            "OFF_PLAYER_NAME": off_player_name,
            "DEF_PLAYER_ID": def_player_id,
            "DEF_PLAYER_NAME": def_player_name,
            "GP": gp,
            "MATCHUP_MIN": matchup_min,
            "PARTIAL_POSS": partial_poss,
            "PLAYER_PTS": player_pts,
            "TEAM_PTS": team_pts,
            "MATCHUP_AST": matchup_ast,
            "MATCHUP_TOV": matchup_tov,
            "MATCHUP_BLK": matchup_blk,
            "MATCHUP_FGM": matchup_fgm,
            "MATCHUP_FGA": matchup_fga,
            "MATCHUP_FG_PCT": matchup_fg_pct,
            "MATCHUP_FG3M": matchup_fg3m,
            "MATCHUP_FG3A": matchup_fg3a,
            "MATCHUP_FG3_PCT": matchup_fg3_pct,
            "MATCHUP_FTM": matchup_ftm,
            "MATCHUP_FTA": matchup_fta,
            "HELP_BLK": help_blk,
            "HELP_FGM": help_fgm,
            "HELP_FGA": help_fga,
            "HELP_FG_PERC": help_fg_pct,
            "SFL": sfl,
        }
    )


class TestMatchupPpp:
    def test_normal_case(self) -> None:
        from fastbreak.matchups import matchup_ppp

        result = matchup_ppp(player_pts=12.0, partial_poss=8.5)
        assert result == pytest.approx(12.0 / 8.5)

    def test_zero_possessions_returns_none(self) -> None:
        from fastbreak.matchups import matchup_ppp

        assert matchup_ppp(player_pts=5.0, partial_poss=0.0) is None

    def test_negative_possessions_returns_none(self) -> None:
        from fastbreak.matchups import matchup_ppp

        assert matchup_ppp(player_pts=5.0, partial_poss=-1.0) is None

    def test_zero_points_returns_zero(self) -> None:
        from fastbreak.matchups import matchup_ppp

        assert matchup_ppp(player_pts=0.0, partial_poss=5.0) == pytest.approx(0.0)


class TestHelpDefenseRate:
    def test_normal_case(self) -> None:
        from fastbreak.matchups import help_defense_rate

        result = help_defense_rate(matchup_fga=80.0, help_fga=20.0)
        assert result == pytest.approx(0.2)

    def test_zero_total_fga_returns_none(self) -> None:
        from fastbreak.matchups import help_defense_rate

        assert help_defense_rate(matchup_fga=0.0, help_fga=0.0) is None

    def test_no_help_returns_zero(self) -> None:
        from fastbreak.matchups import help_defense_rate

        assert help_defense_rate(matchup_fga=50.0, help_fga=0.0) == pytest.approx(0.0)

    def test_all_help_returns_one(self) -> None:
        from fastbreak.matchups import help_defense_rate

        assert help_defense_rate(matchup_fga=0.0, help_fga=30.0) == pytest.approx(1.0)


class TestRankMatchups:
    def test_sorts_by_fg_pct_ascending_by_default(self) -> None:
        from fastbreak.matchups import rank_matchups

        matchups = [
            _make_season_matchup(def_player_id=1, matchup_fg_pct=0.500),
            _make_season_matchup(def_player_id=2, matchup_fg_pct=0.300),
            _make_season_matchup(def_player_id=3, matchup_fg_pct=0.400),
        ]
        result = rank_matchups(matchups, min_poss=0.0)
        assert [m.def_player_id for m in result] == [2, 3, 1]

    def test_sorts_descending(self) -> None:
        from fastbreak.matchups import rank_matchups

        matchups = [
            _make_season_matchup(def_player_id=1, matchup_fg_pct=0.300),
            _make_season_matchup(def_player_id=2, matchup_fg_pct=0.500),
        ]
        result = rank_matchups(matchups, min_poss=0.0, ascending=False)
        assert [m.def_player_id for m in result] == [2, 1]

    def test_filters_by_min_poss(self) -> None:
        from fastbreak.matchups import rank_matchups

        matchups = [
            _make_season_matchup(def_player_id=1, partial_poss=5.0),
            _make_season_matchup(def_player_id=2, partial_poss=15.0),
        ]
        result = rank_matchups(matchups, min_poss=10.0)
        assert len(result) == 1
        assert result[0].def_player_id == 2

    def test_excludes_none_fg_pct(self) -> None:
        from fastbreak.matchups import rank_matchups

        matchups = [
            _make_season_matchup(def_player_id=1, matchup_fg_pct=0.400),
            _make_season_matchup(def_player_id=2, matchup_fg_pct=None),
        ]
        result = rank_matchups(matchups, min_poss=0.0)
        assert len(result) == 1
        assert result[0].def_player_id == 1

    def test_by_ppp(self) -> None:
        from fastbreak.matchups import rank_matchups

        matchups = [
            _make_season_matchup(def_player_id=1, player_pts=10.0, partial_poss=10.0),
            _make_season_matchup(def_player_id=2, player_pts=15.0, partial_poss=10.0),
        ]
        result = rank_matchups(matchups, min_poss=0.0, by="ppp")
        assert result[0].def_player_id == 1  # lowest PPP first

    def test_empty_list(self) -> None:
        from fastbreak.matchups import rank_matchups

        assert rank_matchups([], min_poss=0.0) == []


# ─── LeagueSeasonMatchups fixture helper ─────────────────────────────────────

_SEASON_MATCHUP_HEADERS = [
    "SEASON_ID",
    "OFF_PLAYER_ID",
    "OFF_PLAYER_NAME",
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
    "HELP_BLK",
    "HELP_FGM",
    "HELP_FGA",
    "HELP_FG_PERC",
    "SFL",
]


def _make_season_matchups_response(rows: list[list]) -> dict:
    return {
        "resource": "leagueseasonmatchups",
        "parameters": {},
        "resultSets": [
            {
                "name": "SeasonMatchups",
                "headers": _SEASON_MATCHUP_HEADERS,
                "rowSet": rows,
            }
        ],
    }


_SAMPLE_ROW = [
    "22025",
    2544,
    "LeBron James",
    1628389,
    "Bam Adebayo",
    3,
    8.5,
    15.0,
    12.0,
    20.0,
    1.0,
    0.5,
    0.2,
    5.0,
    12.0,
    0.417,
    1.0,
    3.0,
    0.333,
    2.0,
    3.0,
    0.1,
    1.0,
    3.0,
    0.333,
    0.5,
]


class TestGetSeasonMatchups:
    async def test_returns_list_of_season_matchups(self, make_mock_client) -> None:
        from fastbreak.matchups import get_season_matchups

        client, _ = make_mock_client(
            json_data=_make_season_matchups_response([_SAMPLE_ROW])
        )
        result = await get_season_matchups(client, off_player_id=2544)
        assert len(result) == 1
        assert result[0].off_player_id == 2544
        assert result[0].off_player_name == "LeBron James"
        assert result[0].def_player_name == "Bam Adebayo"
        assert result[0].matchup_fg_pct == pytest.approx(0.417)

    async def test_empty_result_set(self, make_mock_client) -> None:
        from fastbreak.matchups import get_season_matchups

        client, _ = make_mock_client(json_data=_make_season_matchups_response([]))
        result = await get_season_matchups(client, off_player_id=2544)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.matchups import get_season_matchups

        client, mock_session = make_mock_client(
            json_data=_make_season_matchups_response([])
        )
        await get_season_matchups(client)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        from fastbreak.matchups import get_season_matchups

        client, _ = make_mock_client(json_data=_make_season_matchups_response([]))
        result = await get_season_matchups(client, season="2025-26")
        assert result == []


# ─── MatchupsRollup fixture helper ───────────────────────────────────────────

_ROLLUP_HEADERS = [
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
]


def _make_rollup_response(rows: list[list]) -> dict:
    return {
        "resource": "matchupsrollup",
        "parameters": {},
        "resultSets": [
            {
                "name": "MatchupsRollup",
                "headers": _ROLLUP_HEADERS,
                "rowSet": rows,
            }
        ],
    }


_SAMPLE_ROLLUP_ROW = [
    "22025",
    "F",
    0.35,
    1628389,
    "Bam Adebayo",
    3,
    8.5,
    15.0,
    12.0,
    20.0,
    1.0,
    0.5,
    0.2,
    5.0,
    12.0,
    0.417,
    1.0,
    3.0,
    0.333,
    2.0,
    3.0,
    0.5,
]


class TestGetMatchupRollup:
    async def test_returns_list_of_rollup_entries(self, make_mock_client) -> None:
        from fastbreak.matchups import get_matchup_rollup

        client, _ = make_mock_client(
            json_data=_make_rollup_response([_SAMPLE_ROLLUP_ROW])
        )
        result = await get_matchup_rollup(client, off_player_id=2544)
        assert len(result) == 1
        assert result[0].def_player_id == 1628389
        assert result[0].position == "F"
        assert result[0].percent_of_time == pytest.approx(0.35)

    async def test_empty_result_set(self, make_mock_client) -> None:
        from fastbreak.matchups import get_matchup_rollup

        client, _ = make_mock_client(json_data=_make_rollup_response([]))
        result = await get_matchup_rollup(client)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.matchups import get_matchup_rollup

        client, mock_session = make_mock_client(json_data=_make_rollup_response([]))
        await get_matchup_rollup(client)
        mock_session.get.assert_called_once()


def _make_game_matchups_json(game_id: str = "0022500571") -> dict:
    return {
        "meta": {
            "version": 1,
            "request": f"http://nba.cloud/games/{game_id}/boxscorematchups",
            "time": "2026-01-15T12:00:00.000Z",
        },
        "boxScoreMatchups": {
            "gameId": game_id,
            "awayTeamId": 1610612748,
            "homeTeamId": 1610612738,
            "homeTeam": {
                "teamId": 1610612738,
                "teamCity": "Boston",
                "teamName": "Celtics",
                "teamTricode": "BOS",
                "teamSlug": "celtics",
                "players": [],
            },
            "awayTeam": {
                "teamId": 1610612748,
                "teamCity": "Miami",
                "teamName": "Heat",
                "teamTricode": "MIA",
                "teamSlug": "heat",
                "players": [],
            },
        },
    }


class TestGetGameMatchups:
    async def test_returns_v3_response(self, make_mock_client) -> None:
        from fastbreak.matchups import get_game_matchups

        client, _ = make_mock_client(json_data=_make_game_matchups_json("0022500571"))
        result = await get_game_matchups(client, game_id="0022500571")
        assert isinstance(result, BoxScoreMatchupsV3Response)
        assert result.box_score_matchups.game_id == "0022500571"
        assert result.box_score_matchups.home_team.team_tricode == "BOS"

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.matchups import get_game_matchups

        client, mock_session = make_mock_client(json_data=_make_game_matchups_json())
        await get_game_matchups(client, game_id="0022500571")
        mock_session.get.assert_called_once()


def _make_player_vs_player_response() -> dict:
    return {
        "resource": "playervsplayer",
        "parameters": {},
        "resultSets": [
            {"name": "Overall", "headers": ["GROUP_SET", "PLAYER_ID"], "rowSet": []},
            {"name": "OnOffCourt", "headers": ["GROUP_SET", "PLAYER_ID"], "rowSet": []},
            {
                "name": "ShotDistanceOverall",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {
                "name": "ShotDistanceOnCourt",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {
                "name": "ShotDistanceOffCourt",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {
                "name": "ShotAreaOverall",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {
                "name": "ShotAreaOnCourt",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {
                "name": "ShotAreaOffCourt",
                "headers": ["GROUP_SET", "PLAYER_ID"],
                "rowSet": [],
            },
            {"name": "PlayerInfo", "headers": ["PERSON_ID"], "rowSet": []},
            {"name": "VsPlayerInfo", "headers": ["PERSON_ID"], "rowSet": []},
        ],
    }


class TestGetPlayerMatchupStats:
    async def test_returns_player_vs_player_response(self, make_mock_client) -> None:
        from fastbreak.matchups import get_player_matchup_stats

        client, _ = make_mock_client(json_data=_make_player_vs_player_response())
        result = await get_player_matchup_stats(
            client, player_id=2544, vs_player_id=1628389
        )
        assert isinstance(result, PlayerVsPlayerResponse)
        assert result.overall == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.matchups import get_player_matchup_stats

        client, mock_session = make_mock_client(
            json_data=_make_player_vs_player_response()
        )
        await get_player_matchup_stats(client, player_id=2544, vs_player_id=1628389)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        from fastbreak.matchups import get_player_matchup_stats

        client, _ = make_mock_client(json_data=_make_player_vs_player_response())
        result = await get_player_matchup_stats(
            client, player_id=2544, vs_player_id=1628389, season="2025-26"
        )
        assert isinstance(result, PlayerVsPlayerResponse)


class TestGetPrimaryDefenders:
    async def test_returns_top_n_sorted_by_matchup_min(self, make_mock_client) -> None:
        from fastbreak.matchups import get_primary_defenders

        rows = [
            [
                "22025",
                2544,
                "LeBron James",
                100,
                "Defender A",
                3,
                2.0,
                8.0,
                6.0,
                10.0,
                0.5,
                0.2,
                0.1,
                3.0,
                7.0,
                0.429,
                0.5,
                1.5,
                0.333,
                1.0,
                1.5,
                0.0,
                0.5,
                1.0,
                0.500,
                0.2,
            ],
            [
                "22025",
                2544,
                "LeBron James",
                200,
                "Defender B",
                3,
                8.0,
                20.0,
                15.0,
                22.0,
                1.0,
                0.5,
                0.2,
                6.0,
                14.0,
                0.429,
                1.0,
                3.0,
                0.333,
                2.0,
                3.0,
                0.1,
                1.0,
                3.0,
                0.333,
                0.5,
            ],
            [
                "22025",
                2544,
                "LeBron James",
                300,
                "Defender C",
                3,
                5.0,
                12.0,
                10.0,
                18.0,
                0.8,
                0.3,
                0.1,
                4.0,
                10.0,
                0.400,
                0.8,
                2.0,
                0.400,
                1.5,
                2.0,
                0.0,
                0.8,
                2.0,
                0.400,
                0.3,
            ],
        ]
        client, _ = make_mock_client(json_data=_make_season_matchups_response(rows))

        result = await get_primary_defenders(client, player_id=2544, top_n=2)

        assert len(result) == 2
        assert result[0].def_player_id == 200  # 8.0 min (highest)
        assert result[1].def_player_id == 300  # 5.0 min

    async def test_top_n_exceeds_results(self, make_mock_client) -> None:
        from fastbreak.matchups import get_primary_defenders

        client, _ = make_mock_client(
            json_data=_make_season_matchups_response([_SAMPLE_ROW])
        )

        result = await get_primary_defenders(client, player_id=2544, top_n=10)

        assert len(result) == 1


class TestGetDefensiveAssignments:
    async def test_returns_top_n_sorted_by_matchup_min(self, make_mock_client) -> None:
        from fastbreak.matchups import get_defensive_assignments

        rows = [
            [
                "22025",
                100,
                "Attacker A",
                1630700,
                "Dyson Daniels",
                3,
                3.0,
                10.0,
                8.0,
                12.0,
                0.5,
                0.3,
                0.2,
                4.0,
                9.0,
                0.444,
                0.5,
                1.5,
                0.333,
                1.0,
                1.5,
                0.1,
                0.5,
                1.0,
                0.500,
                0.2,
            ],
            [
                "22025",
                200,
                "Attacker B",
                1630700,
                "Dyson Daniels",
                3,
                7.0,
                18.0,
                13.0,
                20.0,
                1.0,
                0.4,
                0.3,
                5.0,
                12.0,
                0.417,
                1.0,
                3.0,
                0.333,
                2.0,
                3.0,
                0.1,
                1.0,
                3.0,
                0.333,
                0.5,
            ],
        ]
        client, _ = make_mock_client(json_data=_make_season_matchups_response(rows))

        result = await get_defensive_assignments(client, defender_id=1630700, top_n=5)

        assert len(result) == 2
        assert result[0].off_player_id == 200  # 7.0 min (highest)
        assert result[1].off_player_id == 100  # 3.0 min


class TestGetTeamMatchupSummary:
    async def test_returns_all_matchups_between_teams(self, make_mock_client) -> None:
        from fastbreak.matchups import get_team_matchup_summary

        rows = [_SAMPLE_ROW]
        client, _ = make_mock_client(json_data=_make_season_matchups_response(rows))

        result = await get_team_matchup_summary(
            client, off_team_id=1610612747, def_team_id=1610612748
        )

        assert len(result) == 1
        assert result[0].off_player_name == "LeBron James"

    async def test_empty_result(self, make_mock_client) -> None:
        from fastbreak.matchups import get_team_matchup_summary

        client, _ = make_mock_client(json_data=_make_season_matchups_response([]))

        result = await get_team_matchup_summary(
            client, off_team_id=1610612747, def_team_id=1610612748
        )

        assert result == []


class TestMatchupsModuleExports:
    def test_all_public_symbols_importable_from_matchups(self) -> None:
        from fastbreak.matchups import (
            get_defensive_assignments,
            get_game_matchups,
            get_matchup_rollup,
            get_player_matchup_stats,
            get_primary_defenders,
            get_season_matchups,
            get_team_matchup_summary,
            help_defense_rate,
            matchup_ppp,
            rank_matchups,
        )

        assert callable(get_defensive_assignments)
        assert callable(get_game_matchups)
        assert callable(get_matchup_rollup)
        assert callable(get_player_matchup_stats)
        assert callable(get_primary_defenders)
        assert callable(get_season_matchups)
        assert callable(get_team_matchup_summary)
        assert callable(help_defense_rate)
        assert callable(matchup_ppp)
        assert callable(rank_matchups)

    def test_all_public_symbols_importable_from_fastbreak(self) -> None:
        import fastbreak

        assert callable(fastbreak.get_defensive_assignments)
        assert callable(fastbreak.get_game_matchups)
        assert callable(fastbreak.get_matchup_rollup)
        assert callable(fastbreak.get_player_matchup_stats)
        assert callable(fastbreak.get_primary_defenders)
        assert callable(fastbreak.get_season_matchups)
        assert callable(fastbreak.get_team_matchup_summary)
        assert callable(fastbreak.help_defense_rate)
        assert callable(fastbreak.matchup_ppp)
        assert callable(fastbreak.rank_matchups)
