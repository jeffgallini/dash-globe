# Dash Globe

Dash Globe is a Dash component library that wraps `react-globe.gl` with a more Pythonic, figure-like API.

## Highlights

- Chainable Python helpers on `dash_globe.DashGlobe`
- Snake_case aliases for raw layer props such as `arc_dash_animate_time` and `points_merge`
- First-class day/night globe shader via `update_day_night_cycle(...)`
- First-class rotating cloud shell via `update_clouds(...)`
- Serializable ripple-ring fades via `ring_color_interpolator(...)`
- Data-driven globe layers for points, arcs, polygons, paths, heatmaps, hex bins, tiles, particles, rings, and labels
- Dash callback props for `clickData`, `rightClickData`, `hoverData`, and `currentView`
- Example gallery in [`usage.py`](./usage.py), including upstream ports for clouds, submarine cables, ripple rings, and airline-routes hover highlighting

## Quick Start

```bash
python usage.py
```

## Example

```python
import dash_globe

globe = (
    dash_globe.DashGlobe(id="cities")
    .update_layout(height=420, background_color="#020817")
    .update_globe(show_graticules=True, atmosphere_color="#5bc0eb")
    .add_points([
        {"name": "Tokyo", "lat": 35.6764, "lng": 139.6500, "color": "#4cc9f0"},
        {"name": "Sydney", "lat": -33.8688, "lng": 151.2093, "color": "#f72585"},
    ])
    .update_points(
        pointLat="lat",
        pointLng="lng",
        pointColor="color",
        pointLabel="name",
        pointAltitude=0.12,
        pointRadius=0.3,
    )
)
```

## Development

```bash
npm install
npm run build:js
venv\Scripts\dash-generate-components.exe .\src\lib\components dash_globe -p package-info.json -i \.test\.
python usage.py
```
