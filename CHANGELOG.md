# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.0.3]

✨ Features

- New Endpoint: LeagueDashTeamClutch — Team clutch performance statistics with configurable clutch time parameters
- Response Caching — TTL-based caching via cache_ttl parameter, with clear_cache() and cache_info support
- Live API Testing — New CI workflow for integration tests against NBA Stats API
- Examples — Added examples/ directory with practical usage patterns (box scores, player trends, gravity metrics, shot analysis)

🔧 Improvements

- AnyIO Migration — Replaced asyncio primitives with AnyIO for backend-agnostic structured concurrency
- Structured Logging — Consistent structlog usage throughout
- Dashboard Endpoint Hierarchy — New DashboardEndpoint base class for cleaner inheritance
- Enhanced Type Safety — Expanded Annotated[Literal, Field] type aliases
- Error Visibility — Logging distinguishes parse failures from empty responses

🗑️  Breaking Changes

- Removed PlayerCareerByCollege endpoint (non-functional upstream)
- Removed TeamAndPlayersVsPlayers endpoint (non-functional upstream)

🧪 Testing

- Major test coverage expansion
- Client test reorganization

📝 Documentation

- Updated endpoint count (80+ → 100+)
- Added Stargazers chart to README
