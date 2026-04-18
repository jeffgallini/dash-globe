# Changelog

## [0.0.1] - 2026-04-18

Initial public release of `dash_globe`.

### Added

- A real Dash wrapper around `react-globe.gl` with a figure-like, chainable Python API.
- High-level helpers for globe layout, controls, view state, clouds, materials, events, and serializable ring color interpolation.
- Data-driven globe layers for points, arcs, polygons, paths, heatmaps, hex bins, tiles, particles, rings, and labels.
- Snake_case aliases for raw component props alongside Dash-style camelCase support.
- A richer `usage.py` gallery with multiple live examples, including airline routes, choropleth countries, submarine cables, ripple rings, day/night cycle, and situation-room style overlays.
- Packaged frontend assets, improved Python package metadata, and PyPI-ready build configuration.

### Changed

- Updated package documentation for installation and usage from PyPI.
- Added automated release infrastructure for versioning, tagging, validation, and publishing from GitHub Actions.
