import asyncio

import polars as pl

from fastbreak.clients import NBAClient
from fastbreak.endpoints import LeagueStandings
from fastbreak.models import TeamStanding


def format_rank_with_ties(rank_col: str = "rank") -> pl.Expr:
    """Return expression that formats ranks with 'T-' prefix for ties."""
    return (
        pl.when(pl.col(rank_col).is_duplicated())
        .then(pl.format("T-{}", pl.col(rank_col).cast(pl.Int64)))
        .otherwise(pl.col(rank_col).cast(pl.Int64).cast(pl.Utf8))
        .alias(rank_col)
    )


def rank(df: pl.DataFrame) -> pl.DataFrame:
    """Apply 3-2-1 point system ranking based on regulation/overtime records."""
    # Fill null OT records with "0-0"
    df = df.with_columns(pl.col("ot").fill_null("0-0"))

    # Split OT record "W-L" into separate wins/losses columns
    return (
        df.with_columns(pl.col("ot").str.split("-").alias("ot_parts"))
        .with_columns(
            pl.col("ot_parts").list.get(0).cast(pl.Int64).alias("ot_wins"),
            pl.col("ot_parts").list.get(1).cast(pl.Int64).alias("ot_losses"),
        )
        # Calculate regulation record (total - OT)
        .with_columns(
            (pl.col("wins") - pl.col("ot_wins")).alias("reg_wins"),
            (pl.col("losses") - pl.col("ot_losses")).alias("reg_losses"),
        )
        # Apply 3-2-1 point system: 3 for reg win, 2 for OT win, 1 for OT loss
        .with_columns(
            (
                3 * pl.col("reg_wins") + 2 * pl.col("ot_wins") + pl.col("ot_losses")
            ).alias("pts")
        )
        # Rank by points (descending, ties get same rank)
        .with_columns(pl.col("pts").rank(method="min", descending=True).alias("rank"))
        .sort("rank")
        # Format ties with "T-" prefix
        .with_columns(format_rank_with_ties("rank"))
        .select(
            [
                "team_name",
                "wins",
                "losses",
                "ot",
                "reg_wins",
                "reg_losses",
                "ot_wins",
                "ot_losses",
                "pts",
                "rank",
            ]
        )
    )


async def main() -> None:
    async with NBAClient() as client:
        standings = await client.get(
            LeagueStandings(season="2025-26", season_type="Regular Season")
        )
        league = TeamStanding.to_polars(standings.standings)
        ranked = rank(league)
        with pl.Config(tbl_rows=-1, tbl_cols=-1):
            print(ranked)


if __name__ == "__main__":
    asyncio.run(main())
