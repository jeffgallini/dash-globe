# Changelog

## [1.0.0] - 2026-09-02

First major release of `dash-globe`.

### Added

- Client-side `data_url(...)` layer sources so large GeoJSON/JSON datasets stay out of the Dash layout and are fetched in the browser.
- `enable_large_data_mode()` helper plus `largeDataMode` / `eventDataMode` props for snappier large-dataset rendering and compact click/hover payloads.
- Webpack splits the physical globe bundle into cached `async-three`, `async-h3`, and `async-globe-vendor` chunks so `async-DashGlobe.js` stays small.
- Gallery example: "Large Dataset via data_url".
- Mantine-styled interactive docs gallery in `usage.py` (AppShell sidebar, Demo/Code tabs, CodeHighlight).
- GitHub Pages documentation site under `docs/` with getting-started guide and example screenshots/GIFs.
- `script/capture_docs_media.py` to regenerate docs media from the local gallery.
- Release tooling now keeps `DESCRIPTION` and `package-lock.json` in sync with the package version.

### Changed

- Default interaction payloads now use summary mode (geometry omitted) to avoid shipping full polygon/path objects back to Python on every hover.
- Distributed Python package no longer ships multi-megabyte `.js.map` files.
- CSS color constants (for example `rgba(...)`) and dotted label paths are wrapped into real accessors so upstream `accessor-fn` renders them correctly.
- `data_url` layers wait until fetch completes before mounting the globe, avoiding an empty polygons layer after async load.
- Root and package READMEs updated for the 1.0 docs/media experience.

### Fixed

- Large-dataset polygons using constant CSS colors no longer fail to paint.
- Client fetch retry after aborted `data_url` requests (Strict Mode / remount-safe).

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
