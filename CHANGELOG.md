# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed

### Changed

- Changed stats database shards to use original sqlite-populated.sql data

## [2.0.0] - 2022-04-30

### Added

- Added traefik load balancing
- Added user game stats to statistics service
- Added Top10 wins to stats service
- Added Top10 streaks to stats service
- Added sharded database for statistics service

### Fixed

- Fixed unique username generation in statistics database

## [1.0.0] - 2022-04-29

### Added

- Added change future answers function to answer service

## [0.9.1] - 2022-04-08

### Added

- Added answers database
- Added word database
- Added word validation service
- Added answer checking service
- Added foreman config
