"""NBA API endpoint definitions.

This module auto-exports all public symbols from submodules.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

# Explicit imports for type checkers (mypy, pyright, etc.)
# These are redundant at runtime but needed for static analysis
if TYPE_CHECKING:
    from fastbreak.endpoints.all_time_leaders import (
        AllTimeLeadersGrids as AllTimeLeadersGrids,
    )
    from fastbreak.endpoints.assist_leaders import AssistLeaders as AssistLeaders
    from fastbreak.endpoints.assist_tracker import AssistTracker as AssistTracker
    from fastbreak.endpoints.base import (
        Endpoint as Endpoint,
        GameIdEndpoint as GameIdEndpoint,
    )
    from fastbreak.endpoints.box_score_advanced import (
        BoxScoreAdvanced as BoxScoreAdvanced,
    )
    from fastbreak.endpoints.box_score_four_factors import (
        BoxScoreFourFactors as BoxScoreFourFactors,
    )
    from fastbreak.endpoints.box_score_matchups import (
        BoxScoreMatchups as BoxScoreMatchups,
    )
    from fastbreak.endpoints.box_score_misc import BoxScoreMisc as BoxScoreMisc
    from fastbreak.endpoints.box_score_player_track import (
        BoxScorePlayerTrack as BoxScorePlayerTrack,
    )
    from fastbreak.endpoints.box_score_scoring import (
        BoxScoreScoring as BoxScoreScoring,
    )
    from fastbreak.endpoints.box_score_summary import (
        BoxScoreSummary as BoxScoreSummary,
    )
    from fastbreak.endpoints.box_score_traditional import (
        BoxScoreTraditional as BoxScoreTraditional,
    )
    from fastbreak.endpoints.box_score_usage import BoxScoreUsage as BoxScoreUsage
    from fastbreak.endpoints.common_all_players import (
        CommonAllPlayers as CommonAllPlayers,
    )
    from fastbreak.endpoints.common_player_info import (
        CommonPlayerInfo as CommonPlayerInfo,
    )
    from fastbreak.endpoints.common_playoff_series import (
        CommonPlayoffSeries as CommonPlayoffSeries,
    )
    from fastbreak.endpoints.common_team_roster import (
        CommonTeamRoster as CommonTeamRoster,
    )
    from fastbreak.endpoints.common_team_years import (
        CommonTeamYears as CommonTeamYears,
    )
    from fastbreak.endpoints.cume_stats_player import (
        CumeStatsPlayer as CumeStatsPlayer,
    )
    from fastbreak.endpoints.cume_stats_player_games import (
        CumeStatsPlayerGames as CumeStatsPlayerGames,
    )
    from fastbreak.endpoints.cume_stats_team import CumeStatsTeam as CumeStatsTeam
    from fastbreak.endpoints.cume_stats_team_games import (
        CumeStatsTeamGames as CumeStatsTeamGames,
    )
    from fastbreak.endpoints.draft_combine_drill_results import (
        DraftCombineDrillResults as DraftCombineDrillResults,
    )
    from fastbreak.endpoints.draft_combine_nonstationary_shooting import (
        DraftCombineNonstationaryShooting as DraftCombineNonstationaryShooting,
    )
    from fastbreak.endpoints.draft_combine_player_anthro import (
        DraftCombinePlayerAnthro as DraftCombinePlayerAnthro,
    )
    from fastbreak.endpoints.draft_combine_spot_shooting import (
        DraftCombineSpotShooting as DraftCombineSpotShooting,
    )
    from fastbreak.endpoints.draft_combine_stats import (
        DraftCombineStats as DraftCombineStats,
    )
    from fastbreak.endpoints.draft_history import DraftHistory as DraftHistory
    from fastbreak.endpoints.dunk_score_leaders import (
        DunkScoreLeaders as DunkScoreLeaders,
    )
    from fastbreak.endpoints.franchise_history import (
        FranchiseHistory as FranchiseHistory,
    )
    from fastbreak.endpoints.franchise_leaders import (
        FranchiseLeaders as FranchiseLeaders,
    )
    from fastbreak.endpoints.franchise_players import (
        FranchisePlayers as FranchisePlayers,
    )
    from fastbreak.endpoints.gravity_leaders import GravityLeaders as GravityLeaders
    from fastbreak.endpoints.league_standings import (
        LeagueStandings as LeagueStandings,
    )
    from fastbreak.endpoints.play_by_play import PlayByPlay as PlayByPlay

# Auto-discover and import all submodules at runtime
_package_dir = Path(__file__).parent
_public_names: list[str] = []

for _module_info in pkgutil.iter_modules([str(_package_dir)]):
    if _module_info.name.startswith("_"):
        continue

    _module = importlib.import_module(f".{_module_info.name}", __package__)

    # Get exportable names from module
    if hasattr(_module, "__all__"):
        _names = _module.__all__
    else:
        _names = [n for n in dir(_module) if not n.startswith("_")]

    # Import names into this namespace and track them
    for _name in _names:
        if hasattr(_module, _name):
            globals()[_name] = getattr(_module, _name)
            _public_names.append(_name)

__all__ = sorted(set(_public_names))  # noqa: PLE0605

# Clean up module-level temporaries
del importlib, pkgutil, Path
del _package_dir, _module_info, _module, _names, _name, _public_names
