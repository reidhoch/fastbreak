"""Tests for fastbreak.lineups — league-wide lineup analysis helpers."""

from __future__ import annotations

import pytest

from fastbreak.models.league_dash_lineups import LeagueLineup
from fastbreak.models.league_lineup_viz import LineupViz


def _make_league_lineup(
    *,
    group_set: str = "Overall",
    group_id: str = "1-2-3-4-5",
    group_name: str = "A - B - C - D - E",
    team_id: int = 1610612747,
    team_abbreviation: str = "LAL",
    gp: int = 20,
    w: int = 12,
    losses: int = 8,
    w_pct: float = 0.600,
    min: float = 15.0,
    sum_time_played: int | None = 300,
    fgm: float = 8.0,
    fga: float = 18.0,
    fg_pct: float | None = 0.444,
    fg3m: float = 2.0,
    fg3a: float = 6.0,
    fg3_pct: float | None = 0.333,
    ftm: float = 3.0,
    fta: float = 4.0,
    ft_pct: float | None = 0.750,
    oreb: float = 1.5,
    dreb: float = 5.0,
    reb: float = 6.5,
    ast: float = 4.0,
    tov: float = 2.0,
    stl: float = 1.0,
    blk: float = 0.5,
    blka: float = 0.3,
    pf: float = 2.5,
    pfd: float = 3.0,
    pts: float = 21.0,
    plus_minus: float = 5.0,
    gp_rank: int = 1,
    w_rank: int = 1,
    l_rank: int = 1,
    w_pct_rank: int = 1,
    min_rank: int = 1,
    fgm_rank: int = 1,
    fga_rank: int = 1,
    fg_pct_rank: int = 1,
    fg3m_rank: int = 1,
    fg3a_rank: int = 1,
    fg3_pct_rank: int = 1,
    ftm_rank: int = 1,
    fta_rank: int = 1,
    ft_pct_rank: int = 1,
    oreb_rank: int = 1,
    dreb_rank: int = 1,
    reb_rank: int = 1,
    ast_rank: int = 1,
    tov_rank: int = 1,
    stl_rank: int = 1,
    blk_rank: int = 1,
    blka_rank: int = 1,
    pf_rank: int = 1,
    pfd_rank: int = 1,
    pts_rank: int = 1,
    plus_minus_rank: int = 1,
) -> LeagueLineup:
    return LeagueLineup.model_validate(
        {
            "GROUP_SET": group_set,
            "GROUP_ID": group_id,
            "GROUP_NAME": group_name,
            "TEAM_ID": team_id,
            "TEAM_ABBREVIATION": team_abbreviation,
            "GP": gp,
            "W": w,
            "L": losses,
            "W_PCT": w_pct,
            "MIN": min,
            "SUM_TIME_PLAYED": sum_time_played,
            "FGM": fgm,
            "FGA": fga,
            "FG_PCT": fg_pct,
            "FG3M": fg3m,
            "FG3A": fg3a,
            "FG3_PCT": fg3_pct,
            "FTM": ftm,
            "FTA": fta,
            "FT_PCT": ft_pct,
            "OREB": oreb,
            "DREB": dreb,
            "REB": reb,
            "AST": ast,
            "TOV": tov,
            "STL": stl,
            "BLK": blk,
            "BLKA": blka,
            "PF": pf,
            "PFD": pfd,
            "PTS": pts,
            "PLUS_MINUS": plus_minus,
            "GP_RANK": gp_rank,
            "W_RANK": w_rank,
            "L_RANK": l_rank,
            "W_PCT_RANK": w_pct_rank,
            "MIN_RANK": min_rank,
            "FGM_RANK": fgm_rank,
            "FGA_RANK": fga_rank,
            "FG_PCT_RANK": fg_pct_rank,
            "FG3M_RANK": fg3m_rank,
            "FG3A_RANK": fg3a_rank,
            "FG3_PCT_RANK": fg3_pct_rank,
            "FTM_RANK": ftm_rank,
            "FTA_RANK": fta_rank,
            "FT_PCT_RANK": ft_pct_rank,
            "OREB_RANK": oreb_rank,
            "DREB_RANK": dreb_rank,
            "REB_RANK": reb_rank,
            "AST_RANK": ast_rank,
            "TOV_RANK": tov_rank,
            "STL_RANK": stl_rank,
            "BLK_RANK": blk_rank,
            "BLKA_RANK": blka_rank,
            "PF_RANK": pf_rank,
            "PFD_RANK": pfd_rank,
            "PTS_RANK": pts_rank,
            "PLUS_MINUS_RANK": plus_minus_rank,
        }
    )


def _make_lineup_viz(
    *,
    group_id: str = "1-2-3-4-5",
    group_name: str = "A - B - C - D - E",
    team_id: int = 1610612747,
    team_abbreviation: str = "LAL",
    min: float = 100.0,
    off_rating: float = 115.0,
    def_rating: float = 108.0,
    net_rating: float = 7.0,
    pace: float = 100.0,
    ts_pct: float = 0.580,
    fta_rate: float = 0.250,
    tm_ast_pct: float = 0.600,
    pct_fga_2pt: float = 0.550,
    pct_fga_3pt: float = 0.450,
    pct_pts_2pt_mr: float = 0.100,
    pct_pts_fb: float = 0.120,
    pct_pts_ft: float = 0.150,
    pct_pts_paint: float = 0.400,
    pct_ast_fgm: float = 0.650,
    pct_uast_fgm: float = 0.350,
    opp_fg3_pct: float = 0.360,
    opp_efg_pct: float = 0.520,
    opp_fta_rate: float = 0.220,
    opp_tov_pct: float = 0.130,
    sum_tm_min: float = 500.0,
) -> LineupViz:
    return LineupViz.model_validate(
        {
            "GROUP_ID": group_id,
            "GROUP_NAME": group_name,
            "TEAM_ID": team_id,
            "TEAM_ABBREVIATION": team_abbreviation,
            "MIN": min,
            "OFF_RATING": off_rating,
            "DEF_RATING": def_rating,
            "NET_RATING": net_rating,
            "PACE": pace,
            "TS_PCT": ts_pct,
            "FTA_RATE": fta_rate,
            "TM_AST_PCT": tm_ast_pct,
            "PCT_FGA_2PT": pct_fga_2pt,
            "PCT_FGA_3PT": pct_fga_3pt,
            "PCT_PTS_2PT_MR": pct_pts_2pt_mr,
            "PCT_PTS_FB": pct_pts_fb,
            "PCT_PTS_FT": pct_pts_ft,
            "PCT_PTS_PAINT": pct_pts_paint,
            "PCT_AST_FGM": pct_ast_fgm,
            "PCT_UAST_FGM": pct_uast_fgm,
            "OPP_FG3_PCT": opp_fg3_pct,
            "OPP_EFG_PCT": opp_efg_pct,
            "OPP_FTA_RATE": opp_fta_rate,
            "OPP_TOV_PCT": opp_tov_pct,
            "SUM_TM_MIN": sum_tm_min,
        }
    )


# ─── LeagueDashLineups fixture helper ─────────────────────────────────────

_LEAGUE_LINEUP_HEADERS = [
    "GROUP_SET",
    "GROUP_ID",
    "GROUP_NAME",
    "TEAM_ID",
    "TEAM_ABBREVIATION",
    "GP",
    "W",
    "L",
    "W_PCT",
    "MIN",
    "SUM_TIME_PLAYED",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "TOV",
    "STL",
    "BLK",
    "BLKA",
    "PF",
    "PFD",
    "PTS",
    "PLUS_MINUS",
    "GP_RANK",
    "W_RANK",
    "L_RANK",
    "W_PCT_RANK",
    "MIN_RANK",
    "FGM_RANK",
    "FGA_RANK",
    "FG_PCT_RANK",
    "FG3M_RANK",
    "FG3A_RANK",
    "FG3_PCT_RANK",
    "FTM_RANK",
    "FTA_RANK",
    "FT_PCT_RANK",
    "OREB_RANK",
    "DREB_RANK",
    "REB_RANK",
    "AST_RANK",
    "TOV_RANK",
    "STL_RANK",
    "BLK_RANK",
    "BLKA_RANK",
    "PF_RANK",
    "PFD_RANK",
    "PTS_RANK",
    "PLUS_MINUS_RANK",
]

_SAMPLE_LINEUP_ROW = [
    "Overall",
    "1-2-3-4-5",
    "A - B - C - D - E",
    1610612747,
    "LAL",
    20,
    12,
    8,
    0.600,
    15.0,
    300,
    8.0,
    18.0,
    0.444,
    2.0,
    6.0,
    0.333,
    3.0,
    4.0,
    0.750,
    1.5,
    5.0,
    6.5,
    4.0,
    2.0,
    1.0,
    0.5,
    0.3,
    2.5,
    3.0,
    21.0,
    5.0,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]


def _make_league_dash_response(rows: list[list]) -> dict:
    return {
        "resource": "leaguedashlineups",
        "parameters": {},
        "resultSets": [
            {
                "name": "Lineups",
                "headers": _LEAGUE_LINEUP_HEADERS,
                "rowSet": rows,
            }
        ],
    }


# ─── LeagueLineupViz fixture helper ──────────────────────────────────────

_LINEUP_VIZ_HEADERS = [
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
]

_SAMPLE_VIZ_ROW = [
    "1-2-3-4-5",
    "A - B - C - D - E",
    1610612747,
    "LAL",
    100.0,
    115.0,
    108.0,
    7.0,
    100.0,
    0.580,
    0.250,
    0.600,
    0.550,
    0.450,
    0.100,
    0.120,
    0.150,
    0.400,
    0.650,
    0.350,
    0.360,
    0.520,
    0.220,
    0.130,
    500.0,
]


def _make_lineup_viz_response(rows: list[list]) -> dict:
    return {
        "resource": "leaguelineupviz",
        "parameters": {},
        "resultSets": [
            {
                "name": "LeagueLineupViz",
                "headers": _LINEUP_VIZ_HEADERS,
                "rowSet": rows,
            }
        ],
    }


# ─── Pure computation tests ───────────────────────────────────────────────


class TestLineupNetRating:
    def test_positive(self) -> None:
        from fastbreak.lineups import lineup_net_rating

        assert lineup_net_rating(115.0, 108.0) == pytest.approx(7.0)

    def test_negative(self) -> None:
        from fastbreak.lineups import lineup_net_rating

        assert lineup_net_rating(105.0, 112.0) == pytest.approx(-7.0)

    def test_zero(self) -> None:
        from fastbreak.lineups import lineup_net_rating

        assert lineup_net_rating(110.0, 110.0) == pytest.approx(0.0)

    def test_exact_values(self) -> None:
        from fastbreak.lineups import lineup_net_rating

        assert lineup_net_rating(115.2, 108.4) == pytest.approx(6.8)


class TestRankLineups:
    def test_sorts_by_plus_minus_descending_by_default(self) -> None:
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="a", plus_minus=2.0),
            _make_league_lineup(group_id="b", plus_minus=8.0),
            _make_league_lineup(group_id="c", plus_minus=5.0),
        ]
        result = rank_lineups(lineups, min_minutes=0.0)
        assert [lu.group_id for lu in result] == ["b", "c", "a"]

    def test_ascending(self) -> None:
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="a", plus_minus=8.0),
            _make_league_lineup(group_id="b", plus_minus=2.0),
        ]
        result = rank_lineups(lineups, min_minutes=0.0, ascending=True)
        assert [lu.group_id for lu in result] == ["b", "a"]

    def test_filters_by_min_minutes(self) -> None:
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="a", min=5.0),
            _make_league_lineup(group_id="b", min=15.0),
        ]
        result = rank_lineups(lineups, min_minutes=10.0)
        assert len(result) == 1
        assert result[0].group_id == "b"

    def test_by_fg_pct_excludes_none(self) -> None:
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="a", fg_pct=0.500),
            _make_league_lineup(group_id="b", fg_pct=None),
        ]
        result = rank_lineups(lineups, min_minutes=0.0, by="fg_pct")
        assert len(result) == 1
        assert result[0].group_id == "a"

    def test_empty_list(self) -> None:
        from fastbreak.lineups import rank_lineups

        assert rank_lineups([], min_minutes=0.0) == []

    def test_by_w_pct(self) -> None:
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="a", w_pct=0.400),
            _make_league_lineup(group_id="b", w_pct=0.700),
        ]
        result = rank_lineups(lineups, min_minutes=0.0, by="w_pct")
        assert result[0].group_id == "b"

    def test_lineup_exactly_at_min_minutes_is_included(self) -> None:
        """A lineup with min exactly equal to min_minutes passes the >= filter."""
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="at", min=10.0),
            _make_league_lineup(group_id="below", min=9.9),
        ]
        result = rank_lineups(lineups, min_minutes=10.0)
        assert len(result) == 1
        assert result[0].group_id == "at"

    def test_by_fg_pct_ascending(self) -> None:
        """by='fg_pct' with ascending=True sorts lowest fg_pct first."""
        from fastbreak.lineups import rank_lineups

        lineups = [
            _make_league_lineup(group_id="high", fg_pct=0.550),
            _make_league_lineup(group_id="low", fg_pct=0.380),
            _make_league_lineup(group_id="mid", fg_pct=0.450),
        ]
        result = rank_lineups(lineups, min_minutes=0.0, by="fg_pct", ascending=True)
        assert [lu.group_id for lu in result] == ["low", "mid", "high"]


# ─── Async wrapper tests ─────────────────────────────────────────────────


class TestGetLeagueLineups:
    async def test_returns_list_of_league_lineups(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineups

        client, _ = make_mock_client(
            json_data=_make_league_dash_response([_SAMPLE_LINEUP_ROW])
        )
        result = await get_league_lineups(client, team_id=1610612747)
        assert len(result) == 1
        assert result[0].team_abbreviation == "LAL"
        assert result[0].plus_minus == pytest.approx(5.0)

    async def test_empty_result_set(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineups

        client, _ = make_mock_client(json_data=_make_league_dash_response([]))
        result = await get_league_lineups(client, 1610612747)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineups

        client, mock_session = make_mock_client(
            json_data=_make_league_dash_response([])
        )
        await get_league_lineups(client, 1610612747)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineups

        client, _ = make_mock_client(json_data=_make_league_dash_response([]))
        result = await get_league_lineups(client, 1610612747, season="2025-26")
        assert result == []

    async def test_custom_group_quantity(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineups

        client, _ = make_mock_client(json_data=_make_league_dash_response([]))
        result = await get_league_lineups(client, 1610612747, group_quantity=2)
        assert result == []


class TestGetLeagueLineupRatings:
    async def test_returns_list_of_lineup_viz(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineup_ratings

        client, _ = make_mock_client(
            json_data=_make_lineup_viz_response([_SAMPLE_VIZ_ROW])
        )
        result = await get_league_lineup_ratings(client, team_id=1610612747)
        assert len(result) == 1
        assert result[0].off_rating == pytest.approx(115.0)
        assert result[0].net_rating == pytest.approx(7.0)

    async def test_empty_result_set(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineup_ratings

        client, _ = make_mock_client(json_data=_make_lineup_viz_response([]))
        result = await get_league_lineup_ratings(client)
        assert result == []

    async def test_calls_client_once(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineup_ratings

        client, mock_session = make_mock_client(json_data=_make_lineup_viz_response([]))
        await get_league_lineup_ratings(client)
        mock_session.get.assert_called_once()

    async def test_season_kwarg_accepted(self, make_mock_client) -> None:
        from fastbreak.lineups import get_league_lineup_ratings

        client, _ = make_mock_client(json_data=_make_lineup_viz_response([]))
        result = await get_league_lineup_ratings(client, season="2025-26")
        assert result == []


# ─── Convenience function tests ──────────────────────────────────────────


class TestGetTopLineups:
    async def test_returns_top_n_sorted(self, make_mock_client) -> None:
        from fastbreak.lineups import get_top_lineups

        rows = []
        for pm, gid in [(2.0, "low"), (8.0, "high"), (5.0, "mid")]:
            row = list(_SAMPLE_LINEUP_ROW)
            row[1] = gid  # GROUP_ID
            row[31] = pm  # PLUS_MINUS
            rows.append(row)

        client, _ = make_mock_client(json_data=_make_league_dash_response(rows))
        result = await get_top_lineups(client, 1610612747, top_n=2, min_minutes=0.0)
        assert len(result) == 2
        assert result[0].group_id == "high"
        assert result[1].group_id == "mid"

    async def test_top_n_exceeds_results(self, make_mock_client) -> None:
        from fastbreak.lineups import get_top_lineups

        client, _ = make_mock_client(
            json_data=_make_league_dash_response([_SAMPLE_LINEUP_ROW])
        )
        result = await get_top_lineups(client, 1610612747, top_n=10, min_minutes=0.0)
        assert len(result) == 1

    async def test_by_pts(self, make_mock_client) -> None:
        from fastbreak.lineups import get_top_lineups

        rows = []
        for pts, gid in [(18.0, "low"), (25.0, "high")]:
            row = list(_SAMPLE_LINEUP_ROW)
            row[1] = gid
            row[30] = pts  # PTS
            rows.append(row)

        client, _ = make_mock_client(json_data=_make_league_dash_response(rows))
        result = await get_top_lineups(
            client, 1610612747, top_n=1, by="pts", min_minutes=0.0
        )
        assert result[0].group_id == "high"


class TestGetTwoManCombos:
    async def test_returns_lineups(self, make_mock_client) -> None:
        from fastbreak.lineups import get_two_man_combos

        client, _ = make_mock_client(
            json_data=_make_league_dash_response([_SAMPLE_LINEUP_ROW])
        )
        result = await get_two_man_combos(client, team_id=1610612747)
        assert len(result) == 1

    async def test_empty_result(self, make_mock_client) -> None:
        from fastbreak.lineups import get_two_man_combos

        client, _ = make_mock_client(json_data=_make_league_dash_response([]))
        result = await get_two_man_combos(client, team_id=1610612747)
        assert result == []


class TestGetLineupEfficiency:
    async def test_returns_sorted_by_net_rating(self, make_mock_client) -> None:
        from fastbreak.lineups import get_lineup_efficiency

        rows = []
        for net, gid in [(3.0, "low"), (12.0, "high"), (7.0, "mid")]:
            row = list(_SAMPLE_VIZ_ROW)
            row[0] = gid  # GROUP_ID
            row[7] = net  # NET_RATING
            rows.append(row)

        client, _ = make_mock_client(json_data=_make_lineup_viz_response(rows))
        result = await get_lineup_efficiency(client)
        assert result[0].group_id == "high"
        assert result[1].group_id == "mid"
        assert result[2].group_id == "low"

    async def test_top_n_caps_results(self, make_mock_client) -> None:
        from fastbreak.lineups import get_lineup_efficiency

        rows = []
        for net, gid in [(3.0, "a"), (12.0, "b"), (7.0, "c")]:
            row = list(_SAMPLE_VIZ_ROW)
            row[0] = gid
            row[7] = net
            rows.append(row)

        client, _ = make_mock_client(json_data=_make_lineup_viz_response(rows))
        result = await get_lineup_efficiency(client, top_n=2)
        assert len(result) == 2

    async def test_no_top_n_returns_all(self, make_mock_client) -> None:
        from fastbreak.lineups import get_lineup_efficiency

        rows = [_SAMPLE_VIZ_ROW, _SAMPLE_VIZ_ROW]
        client, _ = make_mock_client(json_data=_make_lineup_viz_response(rows))
        result = await get_lineup_efficiency(client)
        assert len(result) == 2


# ─── Module export tests ─────────────────────────────────────────────────


class TestLineupsModuleExports:
    def test_all_public_symbols_importable_from_lineups(self) -> None:
        from fastbreak.lineups import (
            get_league_lineup_ratings,
            get_league_lineups,
            get_lineup_efficiency,
            get_top_lineups,
            get_two_man_combos,
            lineup_net_rating,
            rank_lineups,
        )

        assert callable(get_league_lineup_ratings)
        assert callable(get_league_lineups)
        assert callable(get_lineup_efficiency)
        assert callable(get_top_lineups)
        assert callable(get_two_man_combos)
        assert callable(lineup_net_rating)
        assert callable(rank_lineups)

    def test_all_public_symbols_importable_from_fastbreak(self) -> None:
        import fastbreak

        assert callable(fastbreak.get_league_lineup_ratings)
        assert callable(fastbreak.get_league_lineups)
        assert callable(fastbreak.get_lineup_efficiency)
        assert callable(fastbreak.get_top_lineups)
        assert callable(fastbreak.get_two_man_combos)
        assert callable(fastbreak.lineup_net_rating)
        assert callable(fastbreak.rank_lineups)
