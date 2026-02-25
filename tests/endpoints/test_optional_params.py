"""Tests for endpoint optional parameter branches to reach 100% coverage."""

from fastbreak.endpoints.draft_history import DraftHistory
from fastbreak.endpoints.shot_chart_detail import ShotChartDetail
from fastbreak.endpoints.team_dash_pt_reb import TeamDashPtReb
from fastbreak.endpoints.team_dash_pt_shots import TeamDashPtShots
from fastbreak.endpoints.video_status import VideoStatus


class TestDraftHistoryOptionalParams:
    """Tests for DraftHistory optional parameters."""

    def test_params_with_all_optional(self):
        """DraftHistory params includes all optional parameters when set."""
        endpoint = DraftHistory(
            round_num="1",
            round_pick="1",
            overall_pick="1",
            college="Duke",
        )
        params = endpoint.params()
        assert params["RoundNum"] == "1"
        assert params["RoundPick"] == "1"
        assert params["OverallPick"] == "1"
        assert params["College"] == "Duke"

    def test_params_without_optional(self):
        """DraftHistory params excludes None optional parameters."""
        endpoint = DraftHistory()
        params = endpoint.params()
        assert "RoundNum" not in params
        assert "RoundPick" not in params
        assert "OverallPick" not in params
        assert "College" not in params


class TestShotChartDetailOptionalParams:
    """Tests for ShotChartDetail optional parameters."""

    def test_params_with_date_from(self):
        """ShotChartDetail params includes date_from when set."""
        endpoint = ShotChartDetail(
            team_id=1610612737,
            player_id=201566,
            season="2024-25",
            date_from="10/01/2024",
        )
        params = endpoint.params()
        assert params["DateFrom"] == "10/01/2024"

    def test_params_without_optional(self):
        """ShotChartDetail params handles default empty date_from."""
        endpoint = ShotChartDetail(
            team_id=1610612737,
            player_id=201566,
            season="2024-25",
        )
        params = endpoint.params()
        # date_from is not in params or empty when not set
        assert "DateFrom" not in params or params.get("DateFrom") == ""


class TestTeamDashPtRebOptionalParams:
    """Tests for TeamDashPtReb optional parameters."""

    def test_params_with_optional(self):
        """TeamDashPtReb params includes date parameters when set."""
        endpoint = TeamDashPtReb(
            team_id="1610612737",
            season="2024-25",
            date_from="10/01/2024",
            date_to="12/31/2024",
        )
        params = endpoint.params()
        assert params["DateFrom"] == "10/01/2024"
        assert params["DateTo"] == "12/31/2024"

    def test_params_defaults_to_empty(self):
        """TeamDashPtReb params has empty date defaults."""
        endpoint = TeamDashPtReb(
            team_id="1610612737",
            season="2024-25",
        )
        params = endpoint.params()
        # These default to empty string, not excluded
        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_params_with_season_segment(self):
        """TeamDashPtReb params includes optional season_segment when set."""
        endpoint = TeamDashPtReb(
            team_id="1610612737",
            season="2024-25",
            season_segment="Pre All-Star",
        )
        params = endpoint.params()
        assert params["SeasonSegment"] == "Pre All-Star"


class TestTeamDashPtShotsOptionalParams:
    """Tests for TeamDashPtShots optional parameters."""

    def test_params_with_optional(self):
        """TeamDashPtShots params includes date parameters when set."""
        endpoint = TeamDashPtShots(
            team_id="1610612737",
            season="2024-25",
            date_from="10/01/2024",
            date_to="12/31/2024",
        )
        params = endpoint.params()
        assert params["DateFrom"] == "10/01/2024"
        assert params["DateTo"] == "12/31/2024"

    def test_params_defaults_to_empty(self):
        """TeamDashPtShots params has empty date defaults."""
        endpoint = TeamDashPtShots(
            team_id="1610612737",
            season="2024-25",
        )
        params = endpoint.params()
        # These default to empty string, not excluded
        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_params_with_season_segment(self):
        """TeamDashPtShots params includes optional season_segment when set."""
        endpoint = TeamDashPtShots(
            team_id="1610612737",
            season="2024-25",
            season_segment="Pre All-Star",
        )
        params = endpoint.params()
        assert params["SeasonSegment"] == "Pre All-Star"


class TestVideoStatusOptionalParams:
    """Tests for VideoStatus optional parameters."""

    def test_params_with_game_date(self):
        """VideoStatus params includes game_date when set."""
        endpoint = VideoStatus(
            league_id="00",
            game_date="2024-10-22",
        )
        params = endpoint.params()
        assert params["GameDate"] == "2024-10-22"

    def test_params_without_game_date(self):
        """VideoStatus params handles None game_date."""
        endpoint = VideoStatus(
            league_id="00",
        )
        params = endpoint.params()
        # game_date is optional and should not be in params if None
        assert "GameDate" not in params or params.get("GameDate") == ""


class TestLeagueDashTeamPtShotParams:
    """Tests for LeagueDashTeamPtShot params() coverage."""

    def test_params_default_keys(self):
        """params() includes required keys with correct default values."""
        from fastbreak.endpoints import LeagueDashTeamPtShot

        params = LeagueDashTeamPtShot().params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"

    def test_params_excludes_season_by_default(self):
        """params() omits Season when season is None."""
        from fastbreak.endpoints import LeagueDashTeamPtShot

        assert "Season" not in LeagueDashTeamPtShot().params()

    def test_params_includes_season_when_set(self):
        """params() includes Season when explicitly provided."""
        from fastbreak.endpoints import LeagueDashTeamPtShot

        assert LeagueDashTeamPtShot(season="2024-25").params()["Season"] == "2024-25"


class TestLeagueDashOppPtShotParams:
    """Tests for LeagueDashOppPtShot params() coverage."""

    def test_params_default_keys(self):
        """params() includes required keys with correct default values."""
        from fastbreak.endpoints import LeagueDashOppPtShot

        params = LeagueDashOppPtShot().params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"

    def test_params_excludes_season_by_default(self):
        """params() omits Season when season is None."""
        from fastbreak.endpoints import LeagueDashOppPtShot

        assert "Season" not in LeagueDashOppPtShot().params()

    def test_params_includes_season_when_set(self):
        """params() includes Season when explicitly provided."""
        from fastbreak.endpoints import LeagueDashOppPtShot

        assert LeagueDashOppPtShot(season="2024-25").params()["Season"] == "2024-25"


class TestLeagueDashPlayerBioStatsParams:
    """Tests for LeagueDashPlayerBioStats params() coverage."""

    def test_params_default_keys(self):
        """params() includes required keys with correct default values."""
        from fastbreak.endpoints import LeagueDashPlayerBioStats

        params = LeagueDashPlayerBioStats().params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"

    def test_params_excludes_all_optional_by_default(self):
        """params() omits all optional keys when not set."""
        from fastbreak.endpoints import LeagueDashPlayerBioStats

        params = LeagueDashPlayerBioStats().params()

        for key in (
            "Season",
            "College",
            "Country",
            "DraftYear",
            "DraftPick",
            "Height",
            "Weight",
        ):
            assert key not in params

    def test_params_includes_all_optional_filters_when_set(self):
        """params() includes every optional key when all filters are provided."""
        from fastbreak.endpoints import LeagueDashPlayerBioStats

        params = LeagueDashPlayerBioStats(
            season="2024-25",
            college="Duke",
            country="USA",
            draft_year="2024",
            draft_pick="1st Round",
            height="6-0",
            weight="200",
        ).params()

        assert params["Season"] == "2024-25"
        assert params["College"] == "Duke"
        assert params["Country"] == "USA"
        assert params["DraftYear"] == "2024"
        assert params["DraftPick"] == "1st Round"
        assert params["Height"] == "6-0"
        assert params["Weight"] == "200"


class TestLeagueDashPtTeamDefendParams:
    """Tests for LeagueDashPtTeamDefend params() coverage."""

    def test_params_default_keys(self):
        """params() includes required keys including DefenseCategory."""
        from fastbreak.endpoints import LeagueDashPtTeamDefend

        params = LeagueDashPtTeamDefend().params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"
        assert params["DefenseCategory"] == "Overall"

    def test_params_excludes_season_by_default(self):
        """params() omits Season when season is None."""
        from fastbreak.endpoints import LeagueDashPtTeamDefend

        assert "Season" not in LeagueDashPtTeamDefend().params()

    def test_params_includes_season_when_set(self):
        """params() includes Season when explicitly provided."""
        from fastbreak.endpoints import LeagueDashPtTeamDefend

        assert LeagueDashPtTeamDefend(season="2024-25").params()["Season"] == "2024-25"

    def test_params_uses_custom_defense_category(self):
        """params() uses the provided defense_category value."""
        from fastbreak.endpoints import LeagueDashPtTeamDefend

        params = LeagueDashPtTeamDefend(defense_category="3 Pointers").params()

        assert params["DefenseCategory"] == "3 Pointers"
