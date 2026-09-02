# Dash Globe · Interactive 3D globes for Dash

> A figure-like Python API around [react-globe.gl](https://github.com/vasturiano/react-globe.gl). Chain helpers, map your data with accessors, and wire globe events into normal Dash callbacks.

HTML version: [index.html](./index.html)

## Why Dash Globe

Built for Dash developers who want globe visualizations without dropping into raw Three.js. The 1.0 release locks in the chainable API, large-data helpers, and a docs-ready example gallery.

- **Figure-like API** — `update_layout`, `update_globe`, `add_points`, `add_arcs`, and more — all chainable.
- **Full layer coverage** — Points, arcs, polygons, paths, heatmaps, hex bins, tiles, particles, rings, and labels.
- **Dash-native events** — `clickData`, `hoverData`, `rightClickData`, and `currentView` participate in normal callbacks.
- **Large data ready** — `data_url(...)` and `enable_large_data_mode()` keep GeoJSON out of the Dash layout.

## Install

```bash
pip install dash-globe
```

## Featured examples

Screenshots and short loops from the interactive gallery. Run the full gallery locally with `python usage.py`.

- Large Dataset — Client-fetched GeoJSON with compact summary hover payloads
- Choropleth — GDP-per-capita country coloring with hover highlighting
- Day / Night — First-class day-night shader without raw Three.js materials

## Docs for agents

- [llms.txt](./llms.txt) — curated entry point for LLMs ([spec](https://llmstxt.org/))
- [API (markdown)](./api.md)
- [Getting started (markdown)](./getting-started.md)
- [Examples (markdown)](./examples.md)
