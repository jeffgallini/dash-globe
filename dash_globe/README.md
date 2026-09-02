# Dash Globe

Dash Globe is a Dash component library that wraps [`react-globe.gl`](https://github.com/vasturiano/react-globe.gl) with a figure-like Python API.

**Docs:** https://jeffgallini.github.io/dash-globe/  
**PyPI:** https://pypi.org/project/dash-globe/

## Highlights

- Chainable Python helpers on `dash_globe.DashGlobe`
- Snake_case aliases for raw layer props such as `arc_dash_animate_time` and `points_merge`
- First-class day/night globe shader via `update_day_night_cycle(...)`
- First-class rotating cloud shell via `update_clouds(...)`
- Serializable ripple-ring fades via `ring_color_interpolator(...)`
- Data-driven globe layers for points, arcs, polygons, paths, heatmaps, hex bins, tiles, particles, rings, and labels
- Client-side `data_url(...)` loading and `enable_large_data_mode()` for large GeoJSON / JSON datasets
- Dash callback props for `clickData`, `rightClickData`, `hoverData`, and `currentView`
- Interactive gallery in [`usage.py`](usage.py) and hosted docs with example media

## Quick Start

```bash
pip install dash-globe
```

```python
from dash import Dash, html
import dash_globe

app = Dash(__name__)
app.layout = html.Div(
    dash_globe.DashGlobe(id="globe")
    .update_layout(height=500)
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT)
)
```

## Local gallery

```bash
python usage.py
```

Open `http://127.0.0.1:8050`.

## Development

```bash
npm install
npm run build:js
npm run build:backends
python usage.py
```
