"""Tests for DataFrame conversion mixins."""

import sys

import pytest
from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin, _unnest_all


class SimpleModel(PandasMixin, PolarsMixin):
    """Simple test model with both mixins."""

    name: str
    value: int


class NestedStats(BaseModel):
    """Nested statistics model."""

    points: int
    assists: int


class NestedModel(PandasMixin, PolarsMixin):
    """Test model with nested structure."""

    player_id: int
    stats: NestedStats


class DeeplyNestedInner(BaseModel):
    """Innermost nested model."""

    score: int


class DeeplyNestedMiddle(BaseModel):
    """Middle nested model."""

    inner: DeeplyNestedInner


class DeeplyNestedModel(PandasMixin, PolarsMixin):
    """Test model with deeply nested structure."""

    id: int
    outer: DeeplyNestedMiddle


@pytest.fixture
def pandas_available():
    """Skip test if pandas is not available."""
    return pytest.importorskip("pandas")


@pytest.fixture
def polars_available():
    """Skip test if polars is not available."""
    return pytest.importorskip("polars")


class TestPandasMixin:
    """Tests for PandasMixin.to_pandas()."""

    def test_to_pandas_basic(self, pandas_available):
        """Convert list of models to pandas DataFrame."""
        models = [
            SimpleModel(name="alice", value=10),
            SimpleModel(name="bob", value=20),
        ]
        df = SimpleModel.to_pandas(models)

        assert len(df) == 2
        assert list(df.columns) == ["name", "value"]
        assert df["name"].tolist() == ["alice", "bob"]
        assert df["value"].tolist() == [10, 20]

    def test_to_pandas_empty_list(self, pandas_available):
        """Empty list returns empty DataFrame."""
        df = SimpleModel.to_pandas([])

        assert len(df) == 0

    def test_to_pandas_single_item(self, pandas_available):
        """Single item list works correctly."""
        models = [SimpleModel(name="single", value=42)]
        df = SimpleModel.to_pandas(models)

        assert len(df) == 1
        assert df["name"].iloc[0] == "single"
        assert df["value"].iloc[0] == 42

    def test_to_pandas_flatten_nested(self, pandas_available):
        """Nested models are flattened with dot separator by default."""
        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
            NestedModel(player_id=2, stats=NestedStats(points=25, assists=15)),
        ]
        df = NestedModel.to_pandas(models)

        assert "stats.points" in df.columns
        assert "stats.assists" in df.columns
        assert df["stats.points"].tolist() == [30, 25]
        assert df["stats.assists"].tolist() == [10, 15]

    def test_to_pandas_no_flatten(self, pandas_available):
        """With flatten=False, nested models become dict columns."""
        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
        ]
        df = NestedModel.to_pandas(models, flatten=False)

        assert "stats" in df.columns
        assert isinstance(df["stats"].iloc[0], dict)
        assert df["stats"].iloc[0]["points"] == 30

    def test_to_pandas_custom_separator(self, pandas_available):
        """Custom separator for flattened column names."""
        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
        ]
        df = NestedModel.to_pandas(models, flatten=True, sep="_")

        assert "stats_points" in df.columns
        assert "stats_assists" in df.columns

    def test_to_pandas_deeply_nested(self, pandas_available):
        """Deeply nested structures are fully flattened."""
        models = [
            DeeplyNestedModel(
                id=1, outer=DeeplyNestedMiddle(inner=DeeplyNestedInner(score=100))
            ),
        ]
        df = DeeplyNestedModel.to_pandas(models)

        assert "outer.inner.score" in df.columns
        assert df["outer.inner.score"].iloc[0] == 100


class TestPolarsMixin:
    """Tests for PolarsMixin.to_polars()."""

    def test_to_polars_basic(self, polars_available):
        """Convert list of models to Polars DataFrame."""
        models = [
            SimpleModel(name="alice", value=10),
            SimpleModel(name="bob", value=20),
        ]
        df = SimpleModel.to_polars(models)

        assert len(df) == 2
        assert df["name"].to_list() == ["alice", "bob"]
        assert df["value"].to_list() == [10, 20]

    def test_to_polars_empty_list(self, polars_available):
        """Empty list returns empty DataFrame."""
        df = SimpleModel.to_polars([])

        assert len(df) == 0

    def test_to_polars_single_item(self, polars_available):
        """Single item list works correctly."""
        models = [SimpleModel(name="single", value=42)]
        df = SimpleModel.to_polars(models)

        assert len(df) == 1
        assert df["name"][0] == "single"
        assert df["value"][0] == 42

    def test_to_polars_flatten_structs(self, polars_available):
        """Nested structs are flattened with dot separator by default."""
        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
            NestedModel(player_id=2, stats=NestedStats(points=25, assists=15)),
        ]
        df = NestedModel.to_polars(models)

        assert "stats.points" in df.columns
        assert "stats.assists" in df.columns
        assert df["stats.points"].to_list() == [30, 25]
        assert df["stats.assists"].to_list() == [10, 15]

    def test_to_polars_no_flatten(self, polars_available):
        """With flatten=False, structs remain as Struct type."""
        import polars as pl

        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
        ]
        df = NestedModel.to_polars(models, flatten=False)

        assert "stats" in df.columns
        assert df["stats"].dtype == pl.Struct

    def test_to_polars_custom_separator(self, polars_available):
        """Custom separator for flattened column names."""
        models = [
            NestedModel(player_id=1, stats=NestedStats(points=30, assists=10)),
        ]
        df = NestedModel.to_polars(models, flatten=True, sep="_")

        assert "stats_points" in df.columns
        assert "stats_assists" in df.columns

    def test_to_polars_deeply_nested(self, polars_available):
        """Deeply nested structures are fully flattened recursively."""
        models = [
            DeeplyNestedModel(
                id=1, outer=DeeplyNestedMiddle(inner=DeeplyNestedInner(score=100))
            ),
        ]
        df = DeeplyNestedModel.to_polars(models)

        assert "outer.inner.score" in df.columns
        assert df["outer.inner.score"][0] == 100


class TestIntegrationWithRealModels:
    """Integration tests using actual fastbreak models."""

    def test_team_standing_to_pandas(self, pandas_available):
        """TeamStanding model converts to pandas DataFrame."""
        from fastbreak.models import TeamStanding

        # Minimal valid TeamStanding data
        data = {
            "LeagueID": "00",
            "SeasonID": "22025",
            "TeamID": 1610612760,
            "TeamCity": "Oklahoma City",
            "TeamName": "Thunder",
            "TeamSlug": "thunder",
            "Conference": "West",
            "ConferenceRecord": "28-6",
            "PlayoffRank": 1,
            "ClinchIndicator": "",
            "Division": "Northwest",
            "DivisionRecord": "7-2",
            "DivisionRank": 1,
            "WINS": 36,
            "LOSSES": 8,
            "WinPCT": 0.818,
            "Record": "36-8",
            "HOME": "20-2",
            "ROAD": "16-5",
            "L10": "7-3",
            "Last10Home": "8-2",
            "Last10Road": "6-4",
            "OT": "3-0",
            "ThreePTSOrLess": "2-4",
            "TenPTSOrMore": "27-3",
            "LongHomeStreak": 14,
            "strLongHomeStreak": "W 14",
            "LongRoadStreak": 8,
            "strLongRoadStreak": "W 8",
            "LongWinStreak": 16,
            "LongLossStreak": 2,
            "CurrentHomeStreak": 3,
            "strCurrentHomeStreak": "W 3",
            "CurrentRoadStreak": 1,
            "strCurrentRoadStreak": "W 1",
            "CurrentStreak": 1,
            "strCurrentStreak": "W 1",
            "ConferenceGamesBack": 0.0,
            "DivisionGamesBack": 0.0,
            "ClinchedPlayIn": 0,
            "AheadAtHalf": "30-3",
            "BehindAtHalf": "5-5",
            "TiedAtHalf": "1-0",
            "AheadAtThird": "32-2",
            "BehindAtThird": "3-6",
            "TiedAtThird": "1-0",
            "Score100PTS": "33-7",
            "OppScore100PTS": "23-8",
            "OppOver500": "17-5",
            "LeadInFGPCT": "28-2",
            "LeadInReb": "26-3",
            "FewerTurnovers": "21-4",
            "PointsPG": 120.5,
            "OppPointsPG": 106.3,
            "DiffPointsPG": 14.2,
            "vsEast": "8-2",
            "vsAtlantic": "3-1",
            "vsCentral": "2-1",
            "vsSoutheast": "3-0",
            "vsWest": "28-6",
            "vsNorthwest": "7-2",
            "vsPacific": "10-2",
            "vsSouthwest": "11-2",
            "Jan": "10-2",
            "Feb": "0-0",
            "Mar": "0-0",
            "Apr": "0-0",
            "May": "0-0",
            "Jun": "0-0",
            "Jul": "0-0",
            "Aug": "0-0",
            "Sep": "0-0",
            "Oct": "3-0",
            "Nov": "13-3",
            "Dec": "10-3",
            "Score_80_Plus": "36-8",
            "Opp_Score_80_Plus": "35-8",
            "Score_Below_80": "0-0",
            "Opp_Score_Below_80": "1-0",
            "TotalPoints": 5302,
            "OppTotalPoints": 4677,
            "DiffTotalPoints": 625,
            "LeagueGamesBack": 0.0,
            "ClinchedPostSeason": 0,
            "NEUTRAL": "0-1",
        }

        standing = TeamStanding.model_validate(data)
        df = TeamStanding.to_pandas([standing])

        assert len(df) == 1
        assert df["team_name"].iloc[0] == "Thunder"
        assert df["wins"].iloc[0] == 36

    def test_team_standing_to_polars(self, polars_available):
        """TeamStanding model converts to Polars DataFrame."""
        from fastbreak.models import TeamStanding

        data = {
            "LeagueID": "00",
            "SeasonID": "22025",
            "TeamID": 1610612760,
            "TeamCity": "Oklahoma City",
            "TeamName": "Thunder",
            "TeamSlug": "thunder",
            "Conference": "West",
            "ConferenceRecord": "28-6",
            "PlayoffRank": 1,
            "ClinchIndicator": "",
            "Division": "Northwest",
            "DivisionRecord": "7-2",
            "DivisionRank": 1,
            "WINS": 36,
            "LOSSES": 8,
            "WinPCT": 0.818,
            "Record": "36-8",
            "HOME": "20-2",
            "ROAD": "16-5",
            "L10": "7-3",
            "Last10Home": "8-2",
            "Last10Road": "6-4",
            "OT": "3-0",
            "ThreePTSOrLess": "2-4",
            "TenPTSOrMore": "27-3",
            "LongHomeStreak": 14,
            "strLongHomeStreak": "W 14",
            "LongRoadStreak": 8,
            "strLongRoadStreak": "W 8",
            "LongWinStreak": 16,
            "LongLossStreak": 2,
            "CurrentHomeStreak": 3,
            "strCurrentHomeStreak": "W 3",
            "CurrentRoadStreak": 1,
            "strCurrentRoadStreak": "W 1",
            "CurrentStreak": 1,
            "strCurrentStreak": "W 1",
            "ConferenceGamesBack": 0.0,
            "DivisionGamesBack": 0.0,
            "ClinchedPlayIn": 0,
            "AheadAtHalf": "30-3",
            "BehindAtHalf": "5-5",
            "TiedAtHalf": "1-0",
            "AheadAtThird": "32-2",
            "BehindAtThird": "3-6",
            "TiedAtThird": "1-0",
            "Score100PTS": "33-7",
            "OppScore100PTS": "23-8",
            "OppOver500": "17-5",
            "LeadInFGPCT": "28-2",
            "LeadInReb": "26-3",
            "FewerTurnovers": "21-4",
            "PointsPG": 120.5,
            "OppPointsPG": 106.3,
            "DiffPointsPG": 14.2,
            "vsEast": "8-2",
            "vsAtlantic": "3-1",
            "vsCentral": "2-1",
            "vsSoutheast": "3-0",
            "vsWest": "28-6",
            "vsNorthwest": "7-2",
            "vsPacific": "10-2",
            "vsSouthwest": "11-2",
            "Jan": "10-2",
            "Feb": "0-0",
            "Mar": "0-0",
            "Apr": "0-0",
            "May": "0-0",
            "Jun": "0-0",
            "Jul": "0-0",
            "Aug": "0-0",
            "Sep": "0-0",
            "Oct": "3-0",
            "Nov": "13-3",
            "Dec": "10-3",
            "Score_80_Plus": "36-8",
            "Opp_Score_80_Plus": "35-8",
            "Score_Below_80": "0-0",
            "Opp_Score_Below_80": "1-0",
            "TotalPoints": 5302,
            "OppTotalPoints": 4677,
            "DiffTotalPoints": 625,
            "LeagueGamesBack": 0.0,
            "ClinchedPostSeason": 0,
            "NEUTRAL": "0-1",
        }

        standing = TeamStanding.model_validate(data)
        df = TeamStanding.to_polars([standing])

        assert len(df) == 1
        assert df["team_name"][0] == "Thunder"
        assert df["wins"][0] == 36


class TestUnnestAll:
    """Tests for _unnest_all helper function."""

    def test_returns_unchanged_when_no_struct_columns(self, polars_available):
        """DataFrame without struct columns is returned unchanged."""
        import polars as pl

        df = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        result = _unnest_all(df)

        assert result.columns == ["a", "b"]
        assert result["a"].to_list() == [1, 2]
        assert result["b"].to_list() == ["x", "y"]

    def test_unnests_single_struct_column(self, polars_available):
        """Single struct column is unnested with proper prefix."""
        import polars as pl

        df = pl.DataFrame(
            {
                "id": [1, 2],
                "data": [{"x": 10, "y": 20}, {"x": 30, "y": 40}],
            }
        )
        result = _unnest_all(df)

        assert "id" in result.columns
        assert "data.x" in result.columns
        assert "data.y" in result.columns
        assert result["data.x"].to_list() == [10, 30]
        assert result["data.y"].to_list() == [20, 40]

    def test_unnests_multiple_struct_columns(self, polars_available):
        """Multiple struct columns are all unnested."""
        import polars as pl

        df = pl.DataFrame(
            {
                "id": [1],
                "stats1": [{"a": 10}],
                "stats2": [{"b": 20}],
            }
        )
        result = _unnest_all(df)

        assert "stats1.a" in result.columns
        assert "stats2.b" in result.columns
        assert result["stats1.a"][0] == 10
        assert result["stats2.b"][0] == 20

    def test_uses_custom_separator(self, polars_available):
        """Custom separator is used for column names."""
        import polars as pl

        df = pl.DataFrame(
            {
                "id": [1],
                "data": [{"x": 10}],
            }
        )
        result = _unnest_all(df, sep="_")

        assert "data_x" in result.columns
        assert result["data_x"][0] == 10

    def test_unnests_nested_structs_recursively(self, polars_available):
        """Nested structs are recursively unnested."""
        import polars as pl

        df = pl.DataFrame(
            {
                "id": [1],
                "outer": [{"inner": {"value": 100}}],
            }
        )
        result = _unnest_all(df)

        assert "outer.inner.value" in result.columns
        assert result["outer.inner.value"][0] == 100

    def test_preserves_prefix_through_recursion(self, polars_available):
        """Prefix is properly accumulated through recursive calls."""
        import polars as pl

        # Create deeply nested structure
        df = pl.DataFrame(
            {
                "id": [1],
                "a": [{"b": {"c": 42}}],
            }
        )
        result = _unnest_all(df)

        # The column should have full path
        assert "a.b.c" in result.columns
        assert result["a.b.c"][0] == 42

    def test_handles_empty_dataframe(self, polars_available):
        """Empty DataFrame is handled correctly."""
        import polars as pl

        df = pl.DataFrame()
        result = _unnest_all(df)

        assert len(result) == 0

    def test_drops_original_struct_column(self, polars_available):
        """Original struct column is dropped after unnesting."""
        import polars as pl

        df = pl.DataFrame(
            {
                "id": [1],
                "nested": [{"x": 10}],
            }
        )
        result = _unnest_all(df)

        assert "nested" not in result.columns
        assert "nested.x" in result.columns

    def test_combines_unnested_columns_with_hstack(self, polars_available):
        """Unnested columns are added alongside original columns."""
        import polars as pl

        df = pl.DataFrame(
            {
                "first": [1],
                "middle": [{"val": 50}],
                "last": [3],
            }
        )
        result = _unnest_all(df)

        assert "first" in result.columns
        assert "middle.val" in result.columns
        assert "last" in result.columns
        assert result["first"][0] == 1
        assert result["middle.val"][0] == 50
        assert result["last"][0] == 3


class TestImportErrorHandling:
    """Tests for ImportError handling when pandas/polars are not installed."""

    def test_to_pandas_raises_import_error_when_pandas_missing(self, mocker):
        """to_pandas raises ImportError with helpful message when pandas not installed."""
        import builtins

        models = [SimpleModel(name="test", value=1)]

        mocker.patch.dict(sys.modules, {"pandas": None})
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "pandas":
                raise ImportError("No module named 'pandas'")
            return original_import(name, *args, **kwargs)

        mocker.patch.object(builtins, "__import__", side_effect=mock_import)
        with pytest.raises(ImportError, match="pandas is required"):
            SimpleModel.to_pandas(models)

    def test_to_polars_raises_import_error_when_polars_missing(self, mocker):
        """to_polars raises ImportError with helpful message when polars not installed."""
        import builtins

        models = [SimpleModel(name="test", value=1)]

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "polars":
                raise ImportError("No module named 'polars'")
            return original_import(name, *args, **kwargs)

        mocker.patch.object(builtins, "__import__", side_effect=mock_import)
        with pytest.raises(ImportError, match="polars is required"):
            SimpleModel.to_polars(models)
