"""Tests for BoxScoreMatchups model parsing."""

from fastbreak.models.box_score_matchups import MatchupsTeam


class TestMatchupsTeamNullFields:
    """The NBA API returns null for team identity fields on some games."""

    def test_accepts_null_team_identity_fields(self):
        """MatchupsTeam parses cleanly when teamCity/Name/Tricode/Slug are null."""
        data = {
            "teamId": 1610612747,
            "teamCity": None,
            "teamName": None,
            "teamTricode": None,
            "teamSlug": None,
            "players": [],
        }
        team = MatchupsTeam.model_validate(data)
        assert team.teamId == 1610612747
        assert team.teamCity is None
        assert team.teamName is None
        assert team.teamTricode is None
        assert team.teamSlug is None
        assert team.players == []

    def test_accepts_populated_team_identity_fields(self):
        """MatchupsTeam still parses correctly when all fields are present."""
        data = {
            "teamId": 1610612747,
            "teamCity": "Los Angeles",
            "teamName": "Lakers",
            "teamTricode": "LAL",
            "teamSlug": "lakers",
            "players": [],
        }
        team = MatchupsTeam.model_validate(data)
        assert team.teamTricode == "LAL"
        assert team.teamCity == "Los Angeles"
