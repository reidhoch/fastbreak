"""DataFrame conversion utilities for Pydantic models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from pandas import DataFrame as PandasDataFrame
    from polars import DataFrame as PolarsDataFrame

from pydantic import BaseModel


class PandasMixin(BaseModel):
    """Mixin that adds pandas DataFrame conversion to Pydantic models.

    Example:
        >>> players = response.boxScoreTraditional.homeTeam.players
        >>> df = TraditionalPlayer.to_pandas(players)

    """

    @classmethod
    def to_pandas(
        cls,
        models: list[Self],
        *,
        flatten: bool = True,
        sep: str = ".",
    ) -> PandasDataFrame:
        """Convert a list of models to a pandas DataFrame.

        Args:
            models: List of model instances to convert.
            flatten: If True, nested models are flattened into dot-separated
                columns (e.g., 'statistics.points'). If False, nested models
                become dict columns. Defaults to True.
            sep: Separator for flattened column names. Defaults to '.'.

        Returns:
            A pandas DataFrame with one row per model.

        Raises:
            ImportError: If pandas is not installed.

        """
        try:
            import pandas as pd  # noqa: PLC0415
        except ImportError as e:
            msg = (
                "pandas is required for DataFrame conversion. "
                "Install it with: pip install pandas"
            )
            raise ImportError(msg) from e

        if not models:
            return pd.DataFrame()

        data = [m.model_dump() for m in models]

        if flatten:
            return pd.json_normalize(data, sep=sep)
        return pd.DataFrame(data)


class PolarsMixin(BaseModel):
    """Mixin that adds Polars DataFrame conversion to Pydantic models.

    Example:
        >>> players = response.boxScoreTraditional.homeTeam.players
        >>> df = TraditionalPlayer.to_polars(players)

    """

    @classmethod
    def to_polars(
        cls,
        models: list[Self],
        *,
        flatten: bool = True,
        sep: str = ".",
    ) -> PolarsDataFrame:
        """Convert a list of models to a Polars DataFrame.

        Args:
            models: List of model instances to convert.
            flatten: If True, nested struct columns are flattened into
                dot-separated columns (e.g., 'statistics.points'). If False,
                nested models remain as struct columns. Defaults to True.
            sep: Separator for flattened column names. Defaults to '.'.

        Returns:
            A Polars DataFrame with one row per model.

        Raises:
            ImportError: If polars is not installed.

        """
        try:
            import polars as pl  # noqa: PLC0415
        except ImportError as e:
            msg = (
                "polars is required for Polars DataFrame conversion. "
                "Install it with: pip install polars"
            )
            raise ImportError(msg) from e

        if not models:
            return pl.DataFrame()

        data = [m.model_dump() for m in models]
        df = pl.DataFrame(data)

        if flatten:
            df = _unnest_all(df, sep=sep)

        return df


def _unnest_all(
    df: PolarsDataFrame, sep: str = ".", prefix: str = ""
) -> PolarsDataFrame:
    """Recursively unnest all struct columns in a Polars DataFrame."""
    import polars as pl  # noqa: PLC0415

    struct_cols = [col for col in df.columns if df[col].dtype == pl.Struct]

    if not struct_cols:
        return df

    for col in struct_cols:
        # Unnest the struct column
        unnested = df.select(pl.col(col).struct.unnest())

        # Rename columns with prefix
        new_prefix = f"{prefix}{col}{sep}" if prefix else f"{col}{sep}"
        unnested = unnested.rename({c: f"{new_prefix}{c}" for c in unnested.columns})

        # Drop original struct column and add unnested columns
        df = df.drop(col).hstack(unnested)

    # Recursively unnest any nested structs
    return _unnest_all(df, sep=sep)
