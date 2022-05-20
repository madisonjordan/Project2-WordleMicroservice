# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [4.0.0]

### Added

- Added BFF service
- Added Guess model to game_state

### Fixed

### Changed

- Changed GET game in game_state to use path (no body used in requests)
- Change UPDATE game in game_state to use game_id in path
- Changed response model in game state to use GameState model instead of Game input model and State output model
- Changed stats to search by user_id for passing from BFF service
- Changed answers.db to use int as date instead of string
- Changed settings in services to contain default values when not using .env files

### Removed

- Removed Game model from game state service
- Removed redundant traefik prefix path routing

## [3.0.1] 2022-05-13

### Added

- Added response models and examples for autodocumentation

### Fixed

### Changed

- Changed user stats search to search by username

## [3.0.0] (Project 4) - 2022-05-11

### Added

- Added leaderboard redis cron job
- Added game state service

### Fixed

### Changed

- Changed stats database shards to use original sqlite-populated.sql data
- Changed file structure and configuration

## [2.0.0] (Project 3) - 2022-04-30

### Added

- Added traefik load balancing
- Added user game stats to statistics service
- Added Top10 wins to stats service
- Added Top10 streaks to stats service
- Added sharded database for statistics service

### Fixed

- Fixed unique username generation in statistics database

## [1.0.0] (Project 2) - 2022-04-29

### Added

- Added change future answers function to answer service

## [0.9.1] - 2022-04-08

### Added

- Added answers database
- Added word database
- Added word validation service
- Added answer checking service
- Added foreman config
