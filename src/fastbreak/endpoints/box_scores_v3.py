"""Box score V3 endpoints.

All V3 box score endpoints share the same pattern: they accept a game_id
and return modern nested JSON format with player/team statistics.

This module consolidates all 9 box score V3 endpoints into a single file
for easier maintenance and discovery.
"""

from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.box_score_advanced_v3 import BoxScoreAdvancedV3Response
from fastbreak.models.box_score_four_factors_v3 import BoxScoreFourFactorsV3Response
from fastbreak.models.box_score_matchups_v3 import BoxScoreMatchupsV3Response
from fastbreak.models.box_score_misc_v3 import BoxScoreMiscV3Response
from fastbreak.models.box_score_player_track_v3 import BoxScorePlayerTrackV3Response
from fastbreak.models.box_score_scoring_v3 import BoxScoreScoringV3Response
from fastbreak.models.box_score_summary_v3 import BoxScoreSummaryV3Response
from fastbreak.models.box_score_traditional_v3 import BoxScoreTraditionalV3Response
from fastbreak.models.box_score_usage_v3 import BoxScoreUsageV3Response


class BoxScoreAdvancedV3(GameIdEndpoint[BoxScoreAdvancedV3Response]):
    """Fetch advanced box score analytics in V3 format.

    Returns offensive/defensive ratings, pace, PIE, usage percentage,
    true shooting percentage, and other advanced metrics in modern
    nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreAdvancedV3(game_id="0022400001"))
        ...     for player in box.box_score_advanced.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.net_rating:+.1f} NetRtg, {stats.pie:.3f} PIE")

    """

    path: ClassVar[str] = "boxscoreadvancedv3"
    response_model: ClassVar[type[BoxScoreAdvancedV3Response]] = (
        BoxScoreAdvancedV3Response
    )


class BoxScoreFourFactorsV3(GameIdEndpoint[BoxScoreFourFactorsV3Response]):
    """Fetch Dean Oliver's Four Factors in V3 format.

    Returns the four factors that determine basketball success:
    effective field goal percentage, turnover rate, offensive rebounding
    rate, and free throw attempt rate (plus opponent versions).

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreFourFactorsV3(game_id="0022400001"))
        ...     team = box.box_score_four_factors.home_team
        ...     stats = team.statistics
        ...     print(f"{team.team_name}: {stats.effective_field_goal_percentage:.1%} eFG%")

    """

    path: ClassVar[str] = "boxscorefourfactorsv3"
    response_model: ClassVar[type[BoxScoreFourFactorsV3Response]] = (
        BoxScoreFourFactorsV3Response
    )


class BoxScoreMatchupsV3(GameIdEndpoint[BoxScoreMatchupsV3Response]):
    """Fetch detailed player matchup data in V3 format.

    Returns who guarded whom during the game with comprehensive
    statistics including shooting percentages, assists, turnovers,
    help defense, and time spent in each matchup.

    This V3 format uses modern nested JSON with richer data than
    the traditional BoxScoreMatchups endpoint.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     matchups = await client.get(BoxScoreMatchupsV3(game_id="0022400001"))
        ...     for player in matchups.box_score_matchups.home_team.players:
        ...         print(f"{player.name_i} matchups:")
        ...         for m in player.matchups[:2]:
        ...             pct = m.statistics.matchup_field_goals_percentage
        ...             print(f"  vs {m.name_i}: {pct:.1%} FG%")

    """

    path: ClassVar[str] = "boxscorematchupsv3"
    response_model: ClassVar[type[BoxScoreMatchupsV3Response]] = (
        BoxScoreMatchupsV3Response
    )


class BoxScoreMiscV3(GameIdEndpoint[BoxScoreMiscV3Response]):
    """Fetch miscellaneous box score stats in V3 format.

    Returns points off turnovers, second chance points, fastbreak points,
    paint points, blocks against, and fouls drawn in modern nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreMiscV3(game_id="0022400001"))
        ...     for player in box.box_score_misc.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.points_paint} paint pts")

    """

    path: ClassVar[str] = "boxscoremiscv3"
    response_model: ClassVar[type[BoxScoreMiscV3Response]] = BoxScoreMiscV3Response


class BoxScorePlayerTrackV3(GameIdEndpoint[BoxScorePlayerTrackV3Response]):
    """Fetch player tracking stats in V3 format.

    Returns SportVU tracking data: speed, distance, touches, passes,
    contested vs uncontested shots, and rim protection stats in modern
    nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScorePlayerTrackV3(game_id="0022400001"))
        ...     for player in box.box_score_player_track.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.touches} touches, {stats.distance:.1f} mi")

    """

    path: ClassVar[str] = "boxscoreplayertrackv3"
    response_model: ClassVar[type[BoxScorePlayerTrackV3Response]] = (
        BoxScorePlayerTrackV3Response
    )


class BoxScoreScoringV3(GameIdEndpoint[BoxScoreScoringV3Response]):
    """Fetch scoring breakdown stats in V3 format.

    Returns detailed scoring analysis: 2pt vs 3pt percentages,
    assisted vs unassisted shots, paint points, fastbreak points,
    and points off turnovers in modern nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreScoringV3(game_id="0022400001"))
        ...     for player in box.box_score_scoring.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.percentage_points_3pt:.1%} from 3")

    """

    path: ClassVar[str] = "boxscorescoringv3"
    response_model: ClassVar[type[BoxScoreScoringV3Response]] = (
        BoxScoreScoringV3Response
    )


class BoxScoreSummaryV3(GameIdEndpoint[BoxScoreSummaryV3Response]):
    """Fetch game summary metadata in V3 format.

    Returns game information including status, arena details, officials,
    broadcasters, and team records in modern nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     summary = await client.get(BoxScoreSummaryV3(game_id="0022400001"))
        ...     game = summary.box_score_summary
        ...     print(f"{game.game_status_text} at {game.arena.arena_name}")
        ...     print(f"Attendance: {game.attendance:,}")

    """

    path: ClassVar[str] = "boxscoresummaryv3"
    response_model: ClassVar[type[BoxScoreSummaryV3Response]] = (
        BoxScoreSummaryV3Response
    )


class BoxScoreTraditionalV3(GameIdEndpoint[BoxScoreTraditionalV3Response]):
    """Fetch traditional box score stats in V3 format.

    Returns points, rebounds, assists, steals, blocks, turnovers,
    shooting percentages, and plus/minus in modern nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreTraditionalV3(game_id="0022400001"))
        ...     for player in box.box_score_traditional.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.points} pts, {stats.rebounds_total} reb")

    """

    path: ClassVar[str] = "boxscoretraditionalv3"
    response_model: ClassVar[type[BoxScoreTraditionalV3Response]] = (
        BoxScoreTraditionalV3Response
    )


class BoxScoreUsageV3(GameIdEndpoint[BoxScoreUsageV3Response]):
    """Fetch usage/share stats in V3 format.

    Returns what percentage of team stats each player accounted for
    while on the court (shots, assists, rebounds, etc.) in modern
    nested JSON format.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreUsageV3(game_id="0022400001"))
        ...     for player in box.box_score_usage.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.usage_percentage:.1%} USG%")

    """

    path: ClassVar[str] = "boxscoreusagev3"
    response_model: ClassVar[type[BoxScoreUsageV3Response]] = BoxScoreUsageV3Response
