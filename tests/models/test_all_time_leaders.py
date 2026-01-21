import pytest

from fastbreak.models import AllTimeLeadersResponse, LeaderEntry


class TestLeaderEntry:
    """Tests for LeaderEntry model."""

    def test_parse_valid_entry(self):
        """LeaderEntry parses valid data."""
        data = {
            "PLAYER_ID": 2544,
            "PLAYER_NAME": "LeBron James",
            "rank": 1,
            "value": 27.1,
            "is_active": True,
        }

        entry = LeaderEntry.model_validate(data)

        assert entry.player_id == 2544
        assert entry.player_name == "LeBron James"
        assert entry.rank == 1
        assert entry.value == 27.1
        assert entry.is_active is True

    def test_parse_inactive_player(self):
        """LeaderEntry correctly handles inactive players."""
        data = {
            "PLAYER_ID": 893,
            "PLAYER_NAME": "Michael Jordan",
            "rank": 1,
            "value": 30.1,
            "is_active": False,
        }

        entry = LeaderEntry.model_validate(data)

        assert entry.is_active is False

    def test_parse_integer_value(self):
        """LeaderEntry handles integer stat values."""
        data = {
            "PLAYER_ID": 305,
            "PLAYER_NAME": "Robert Parish",
            "rank": 1,
            "value": 1611,
            "is_active": False,
        }

        entry = LeaderEntry.model_validate(data)

        assert entry.value == 1611.0

    def test_parse_float_value(self):
        """LeaderEntry handles float stat values."""
        data = {
            "PLAYER_ID": 926,
            "PLAYER_NAME": "Alvin Robertson",
            "rank": 1,
            "value": 2.71117,
            "is_active": False,
        }

        entry = LeaderEntry.model_validate(data)

        assert entry.value == pytest.approx(2.71117)


class TestAllTimeLeadersResponse:
    """Tests for AllTimeLeadersResponse model."""

    def test_parse_result_sets_format(self):
        """AllTimeLeadersResponse transforms tabular resultSets format."""
        data = {
            "resource": "alltimeleadersgrids",
            "parameters": {
                "LeagueID": "00",
                "SeasonType": "Regular Season",
                "PerMode": "PerGame",
                "TopX": "3",
            },
            "resultSets": [
                {
                    "name": "GPLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "GP",
                        "GP_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [
                        [305, "Robert Parish", 1611, 1, "N"],
                        [2544, "LeBron James", 1587, 2, "Y"],
                        [76003, "Kareem Abdul-Jabbar", 1560, 3, "N"],
                    ],
                },
                {
                    "name": "PTSLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "PTS",
                        "PTS_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [
                        [893, "Michael Jordan", 30.1, 1, "N"],
                        [76375, "Wilt Chamberlain", 30.1, 2, "N"],
                        [1629029, "Luka Dončić", 29.0, 3, "Y"],
                    ],
                },
                {
                    "name": "ASTLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "AST",
                        "AST_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [
                        [77142, "Magic Johnson", 11.2, 1, "N"],
                        [304, "John Stockton", 10.5, 2, "N"],
                        [1629027, "Trae Young", 9.8, 3, "Y"],
                    ],
                },
                {
                    "name": "STLLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "STL",
                        "STL_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[926, "Alvin Robertson", 2.71117, 1, "N"]],
                },
                {
                    "name": "OREBLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "OREB",
                        "OREB_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[77449, "Moses Malone", 5.06471, 1, "N"]],
                },
                {
                    "name": "DREBLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "DREB",
                        "DREB_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76462, "Dave Cowens", 9.77481, 1, "N"]],
                },
                {
                    "name": "REBLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "REB",
                        "REB_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76375, "Wilt Chamberlain", 22.89378, 1, "N"]],
                },
                {
                    "name": "BLKLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "BLK",
                        "BLK_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76631, "Mark Eaton", 3.50171, 1, "N"]],
                },
                {
                    "name": "FGMLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FGM",
                        "FGM_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76375, "Wilt Chamberlain", 12.13493, 1, "N"]],
                },
                {
                    "name": "FGALeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FGA",
                        "FGA_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76127, "Elgin Baylor", 23.84279, 1, "N"]],
                },
                {
                    "name": "FG_PCTLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FG_PCT",
                        "FG_PCT_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[1629655, "Daniel Gafford", 0.704, 1, "Y"]],
                },
                {
                    "name": "TOVLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TOV",
                        "TOV_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[1629027, "Trae Young", 4.21298, 1, "Y"]],
                },
                {
                    "name": "FG3MLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FG3M",
                        "FG3M_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[201939, "Stephen Curry", 3.97172, 1, "Y"]],
                },
                {
                    "name": "FG3ALeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FG3A",
                        "FG3A_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[201939, "Stephen Curry", 9.41753, 1, "Y"]],
                },
                {
                    "name": "FG3_PCTLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FG3_PCT",
                        "FG3_PCT_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[70, "Steve Kerr", 0.454, 1, "N"]],
                },
                {
                    "name": "PFLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "PF",
                        "PF_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[600012, "George Mikan", 4.24146, 1, "N"]],
                },
                {
                    "name": "FTMLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FTM",
                        "FTM_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[203954, "Joel Embiid", 8.24, 1, "Y"]],
                },
                {
                    "name": "FTALeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FTA",
                        "FTA_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[76375, "Wilt Chamberlain", 11.3512, 1, "N"]],
                },
                {
                    "name": "FT_PCTLeaders",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "FT_PCT",
                        "FT_PCT_RANK",
                        "IS_ACTIVE_FLAG",
                    ],
                    "rowSet": [[201939, "Stephen Curry", 0.912, 1, "Y"]],
                },
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        # Check GP leaders parsed correctly
        assert len(response.gp_leaders) == 3
        assert response.gp_leaders[0].player_name == "Robert Parish"
        assert response.gp_leaders[0].value == 1611
        assert response.gp_leaders[0].rank == 1
        assert response.gp_leaders[0].is_active is False
        assert response.gp_leaders[1].player_name == "LeBron James"
        assert response.gp_leaders[1].is_active is True

        # Check PTS leaders parsed correctly
        assert len(response.pts_leaders) == 3
        assert response.pts_leaders[0].player_name == "Michael Jordan"
        assert response.pts_leaders[0].value == pytest.approx(30.1)
        assert response.pts_leaders[2].player_name == "Luka Dončić"

        # Check AST leaders
        assert len(response.ast_leaders) == 3
        assert response.ast_leaders[0].player_name == "Magic Johnson"

    def test_parses_all_19_categories(self):
        """AllTimeLeadersResponse parses all 19 leader categories."""
        data = _make_minimal_result_sets()

        response = AllTimeLeadersResponse.model_validate(data)

        # Verify all 19 categories have data
        assert len(response.gp_leaders) == 1
        assert len(response.pts_leaders) == 1
        assert len(response.ast_leaders) == 1
        assert len(response.stl_leaders) == 1
        assert len(response.oreb_leaders) == 1
        assert len(response.dreb_leaders) == 1
        assert len(response.reb_leaders) == 1
        assert len(response.blk_leaders) == 1
        assert len(response.fgm_leaders) == 1
        assert len(response.fga_leaders) == 1
        assert len(response.fg_pct_leaders) == 1
        assert len(response.tov_leaders) == 1
        assert len(response.fg3m_leaders) == 1
        assert len(response.fg3a_leaders) == 1
        assert len(response.fg3_pct_leaders) == 1
        assert len(response.pf_leaders) == 1
        assert len(response.ftm_leaders) == 1
        assert len(response.fta_leaders) == 1
        assert len(response.ft_pct_leaders) == 1

    def test_is_active_flag_conversion(self):
        """AllTimeLeadersResponse converts IS_ACTIVE_FLAG to boolean."""
        data = {
            "resultSets": [
                _make_result_set(
                    "GPLeaders",
                    "GP",
                    [
                        [1, "Active Player", 100, 1, "Y"],
                        [2, "Retired Player", 90, 2, "N"],
                    ],
                ),
                *_make_empty_result_sets_except("GPLeaders"),
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert response.gp_leaders[0].is_active is True
        assert response.gp_leaders[1].is_active is False

    def test_preserves_order_from_api(self):
        """AllTimeLeadersResponse maintains ranking order from API."""
        data = {
            "resultSets": [
                _make_result_set(
                    "PTSLeaders",
                    "PTS",
                    [
                        [1, "First", 30.0, 1, "N"],
                        [2, "Second", 28.0, 2, "N"],
                        [3, "Third", 26.0, 3, "N"],
                    ],
                ),
                *_make_empty_result_sets_except("PTSLeaders"),
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert response.pts_leaders[0].player_name == "First"
        assert response.pts_leaders[0].rank == 1
        assert response.pts_leaders[1].player_name == "Second"
        assert response.pts_leaders[1].rank == 2
        assert response.pts_leaders[2].player_name == "Third"
        assert response.pts_leaders[2].rank == 3

    def test_handles_empty_result_set(self):
        """AllTimeLeadersResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                _make_result_set("GPLeaders", "GP", []),
                *_make_empty_result_sets_except("GPLeaders"),
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert len(response.gp_leaders) == 0

    def test_handles_percentage_values(self):
        """AllTimeLeadersResponse correctly parses percentage stat values."""
        data = {
            "resultSets": [
                _make_result_set(
                    "FG_PCTLeaders",
                    "FG_PCT",
                    [
                        [1, "High FG", 0.704, 1, "Y"],
                    ],
                ),
                _make_result_set(
                    "FG3_PCTLeaders",
                    "FG3_PCT",
                    [
                        [2, "High 3PT", 0.454, 1, "N"],
                    ],
                ),
                _make_result_set(
                    "FT_PCTLeaders",
                    "FT_PCT",
                    [
                        [3, "High FT", 0.912, 1, "Y"],
                    ],
                ),
                *_make_empty_result_sets_except(
                    "FG_PCTLeaders", "FG3_PCTLeaders", "FT_PCTLeaders"
                ),
            ],
        }

        response = AllTimeLeadersResponse.model_validate(data)

        assert response.fg_pct_leaders[0].value == pytest.approx(0.704)
        assert response.fg3_pct_leaders[0].value == pytest.approx(0.454)
        assert response.ft_pct_leaders[0].value == pytest.approx(0.912)


# Helper functions for creating test data


def _make_result_set(name: str, stat_col: str, rows: list[list]) -> dict:
    """Create a single result set with the given name and rows."""
    rank_col = f"{stat_col}_RANK"
    return {
        "name": name,
        "headers": ["PLAYER_ID", "PLAYER_NAME", stat_col, rank_col, "IS_ACTIVE_FLAG"],
        "rowSet": rows,
    }


def _make_empty_result_sets_except(*exclude: str) -> list[dict]:
    """Create empty result sets for all categories except the specified ones."""
    all_categories = [
        ("GPLeaders", "GP"),
        ("PTSLeaders", "PTS"),
        ("ASTLeaders", "AST"),
        ("STLLeaders", "STL"),
        ("OREBLeaders", "OREB"),
        ("DREBLeaders", "DREB"),
        ("REBLeaders", "REB"),
        ("BLKLeaders", "BLK"),
        ("FGMLeaders", "FGM"),
        ("FGALeaders", "FGA"),
        ("FG_PCTLeaders", "FG_PCT"),
        ("TOVLeaders", "TOV"),
        ("FG3MLeaders", "FG3M"),
        ("FG3ALeaders", "FG3A"),
        ("FG3_PCTLeaders", "FG3_PCT"),
        ("PFLeaders", "PF"),
        ("FTMLeaders", "FTM"),
        ("FTALeaders", "FTA"),
        ("FT_PCTLeaders", "FT_PCT"),
    ]
    return [
        _make_result_set(name, stat, [])
        for name, stat in all_categories
        if name not in exclude
    ]


def _make_minimal_result_sets() -> dict:
    """Create minimal valid response with one entry per category."""
    return {
        "resultSets": [
            _make_result_set("GPLeaders", "GP", [[1, "Player", 100, 1, "Y"]]),
            _make_result_set("PTSLeaders", "PTS", [[1, "Player", 25.0, 1, "Y"]]),
            _make_result_set("ASTLeaders", "AST", [[1, "Player", 8.0, 1, "Y"]]),
            _make_result_set("STLLeaders", "STL", [[1, "Player", 2.0, 1, "Y"]]),
            _make_result_set("OREBLeaders", "OREB", [[1, "Player", 3.0, 1, "Y"]]),
            _make_result_set("DREBLeaders", "DREB", [[1, "Player", 7.0, 1, "Y"]]),
            _make_result_set("REBLeaders", "REB", [[1, "Player", 10.0, 1, "Y"]]),
            _make_result_set("BLKLeaders", "BLK", [[1, "Player", 2.5, 1, "Y"]]),
            _make_result_set("FGMLeaders", "FGM", [[1, "Player", 9.0, 1, "Y"]]),
            _make_result_set("FGALeaders", "FGA", [[1, "Player", 18.0, 1, "Y"]]),
            _make_result_set("FG_PCTLeaders", "FG_PCT", [[1, "Player", 0.5, 1, "Y"]]),
            _make_result_set("TOVLeaders", "TOV", [[1, "Player", 3.0, 1, "Y"]]),
            _make_result_set("FG3MLeaders", "FG3M", [[1, "Player", 3.0, 1, "Y"]]),
            _make_result_set("FG3ALeaders", "FG3A", [[1, "Player", 8.0, 1, "Y"]]),
            _make_result_set("FG3_PCTLeaders", "FG3_PCT", [[1, "Player", 0.4, 1, "Y"]]),
            _make_result_set("PFLeaders", "PF", [[1, "Player", 3.0, 1, "Y"]]),
            _make_result_set("FTMLeaders", "FTM", [[1, "Player", 5.0, 1, "Y"]]),
            _make_result_set("FTALeaders", "FTA", [[1, "Player", 6.0, 1, "Y"]]),
            _make_result_set("FT_PCTLeaders", "FT_PCT", [[1, "Player", 0.85, 1, "Y"]]),
        ],
    }
