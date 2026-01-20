from fastbreak.models.advanced_statistics import (
    AdvancedStatistics,
    AdvancedTeamStatistics,
)
from fastbreak.models.arena import Arena
from fastbreak.models.box_score_advanced import (
    AdvancedPlayer,
    AdvancedTeam,
    BoxScoreAdvancedData,
    BoxScoreAdvancedResponse,
)
from fastbreak.models.box_score_four_factors import (
    BoxScoreFourFactorsData,
    BoxScoreFourFactorsResponse,
    FourFactorsPlayer,
    FourFactorsTeam,
)
from fastbreak.models.box_score_matchups import (
    BoxScoreMatchupsData,
    BoxScoreMatchupsResponse,
    MatchupOpponent,
    MatchupsPlayer,
    MatchupsTeam,
)
from fastbreak.models.box_score_misc import (
    BoxScoreMiscData,
    BoxScoreMiscResponse,
    MiscPlayer,
    MiscTeam,
)
from fastbreak.models.box_score_player_track import (
    BoxScorePlayerTrackData,
    BoxScorePlayerTrackResponse,
    PlayerTrackPlayer,
    PlayerTrackTeam,
)
from fastbreak.models.box_score_scoring import (
    BoxScoreScoringData,
    BoxScoreScoringResponse,
    ScoringPlayer,
    ScoringTeam,
)
from fastbreak.models.box_score_summary import (
    BoxScoreSummaryData,
    BoxScoreSummaryResponse,
)
from fastbreak.models.box_score_traditional import (
    BoxScoreTraditionalData,
    BoxScoreTraditionalResponse,
    TraditionalPlayer,
    TraditionalTeam,
)
from fastbreak.models.box_score_usage import (
    BoxScoreUsageData,
    BoxScoreUsageResponse,
    UsagePlayer,
    UsageTeam,
)
from fastbreak.models.broadcaster import Broadcaster, Broadcasters
from fastbreak.models.chart import Charts, ChartTeam
from fastbreak.models.four_factors_statistics import FourFactorsStatistics
from fastbreak.models.gravity_leader import GravityLeader, GravityLeadersResponse
from fastbreak.models.league_standings import LeagueStandingsResponse, TeamStanding
from fastbreak.models.matchup_statistics import MatchupStatistics
from fastbreak.models.meeting import LastFiveMeetings, Meeting, MeetingTeam
from fastbreak.models.meta import Meta
from fastbreak.models.misc_statistics import MiscStatistics
from fastbreak.models.official import Official
from fastbreak.models.period import Period
from fastbreak.models.play_by_play import (
    PlayByPlayAction,
    PlayByPlayGame,
    PlayByPlayResponse,
)
from fastbreak.models.player import Player
from fastbreak.models.player_track_statistics import (
    PlayerTrackStatistics,
    TeamPlayerTrackStatistics,
)
from fastbreak.models.result_set import (
    is_tabular_response,
    parse_result_set,
    parse_result_set_by_name,
)
from fastbreak.models.scoring_statistics import ScoringStatistics
from fastbreak.models.summary_player import InactivePlayer, SummaryPlayer
from fastbreak.models.summary_team import SummaryTeam
from fastbreak.models.team import Team
from fastbreak.models.traditional_statistics import (
    TraditionalGroupStatistics,
    TraditionalStatistics,
)
from fastbreak.models.usage_statistics import UsageStatistics

type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None

__all__ = [
    "JSON",
    "AdvancedPlayer",
    "AdvancedStatistics",
    "AdvancedTeam",
    "AdvancedTeamStatistics",
    "Arena",
    "BoxScoreAdvancedData",
    "BoxScoreAdvancedResponse",
    "BoxScoreFourFactorsData",
    "BoxScoreFourFactorsResponse",
    "BoxScoreMatchupsData",
    "BoxScoreMatchupsResponse",
    "BoxScoreMiscData",
    "BoxScoreMiscResponse",
    "BoxScorePlayerTrackData",
    "BoxScorePlayerTrackResponse",
    "BoxScoreScoringData",
    "BoxScoreScoringResponse",
    "BoxScoreSummaryData",
    "BoxScoreSummaryResponse",
    "BoxScoreTraditionalData",
    "BoxScoreTraditionalResponse",
    "BoxScoreUsageData",
    "BoxScoreUsageResponse",
    "Broadcaster",
    "Broadcasters",
    "ChartTeam",
    "Charts",
    "FourFactorsPlayer",
    "FourFactorsStatistics",
    "FourFactorsTeam",
    "GravityLeader",
    "GravityLeadersResponse",
    "InactivePlayer",
    "LastFiveMeetings",
    "LeagueStandingsResponse",
    "MatchupOpponent",
    "MatchupStatistics",
    "MatchupsPlayer",
    "MatchupsTeam",
    "Meeting",
    "MeetingTeam",
    "Meta",
    "MiscPlayer",
    "MiscStatistics",
    "MiscTeam",
    "Official",
    "Period",
    "PlayByPlayAction",
    "PlayByPlayGame",
    "PlayByPlayResponse",
    "Player",
    "PlayerTrackPlayer",
    "PlayerTrackStatistics",
    "PlayerTrackTeam",
    "ScoringPlayer",
    "ScoringStatistics",
    "ScoringTeam",
    "SummaryPlayer",
    "SummaryTeam",
    "Team",
    "TeamPlayerTrackStatistics",
    "TeamStanding",
    "TraditionalGroupStatistics",
    "TraditionalPlayer",
    "TraditionalStatistics",
    "TraditionalTeam",
    "UsagePlayer",
    "UsageStatistics",
    "UsageTeam",
    "is_tabular_response",
    "parse_result_set",
    "parse_result_set_by_name",
]
