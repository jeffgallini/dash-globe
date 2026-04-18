# Dash Globe

Dash Globe is a Pythonic Dash wrapper for [`react-globe.gl`](https://github.com/vasturiano/react-globe.gl), aimed at giving Dash developers a figure-like API for building interactive 3D globes.

The current implementation includes:

- A real `react-globe.gl` integration instead of the Dash boilerplate placeholder component.
- A chainable Python API with helpers such as `update_layout`, `update_globe`, `update_controls`, `update_view`, `update_clouds`, `add_points`, `add_arcs`, `add_polygons`, `add_labels`, `add_hex_bins`, and `add_rings`.
- Raw layer props can be configured with either Dash-style camelCase names or Python-friendly snake_case aliases.
- Dash-friendly event props like `clickData`, `rightClickData`, `hoverData`, and `currentView`.
- A richer [`usage.py`](dash_globe/usage.py) gallery showing multiple globe configurations, including upstream airline-routes and choropleth-countries examples.

## Quick Start

From the generated package folder:

```bash
cd dash_globe
python usage.py
```

Then open `http://127.0.0.1:8050`.

To opt back into Dash debug mode for local development:

```bash
DASH_GLOBE_DEBUG=1 python usage.py
```

In PowerShell:

```powershell
$env:DASH_GLOBE_DEBUG="1"
python usage.py
```

## Python API Example

```python
import dash_globe

globe = (
    dash_globe.DashGlobe(id="routes")
    .update_layout(height=500, background_color="#03111f")
    .update_globe(show_atmosphere=True, atmosphere_color="#8ecae6")
    .update_controls(auto_rotate=True, auto_rotate_speed=0.35)
    .update_view(lat=25, lng=20, altitude=1.9)
    .update_clouds(image_url=dash_globe.PRESETS.CLOUDS)
    .add_points([
        {"name": "New York", "lat": 40.7128, "lng": -74.0060, "color": "#ff6b6b"},
        {"name": "London", "lat": 51.5072, "lng": -0.1276, "color": "#ffd166"},
    ])
    .update_points(
        pointLat="lat",
        pointLng="lng",
        pointColor="color",
        pointLabel="name",
        pointAltitude=0.08,
        pointRadius=0.28,
    )
)
```

## Development

Inside [`dash_globe`](dash_globe):

```bash
npm install
npm run build:js
venv\Scripts\dash-generate-components.exe .\src\lib\components dash_globe -p package-info.json -i \.test\.
python usage.py
```

`usage.py` now runs with Dash debug mode off by default to avoid upstream Dash/React dev-bundle warnings in the browser console. Set `DASH_GLOBE_DEBUG=1` when you want Dash debug tooling back.

## Notes

- The wrapper currently focuses on JSON-serialisable `react-globe.gl` features, which maps well to Dash callbacks.
- Features that require raw JavaScript functions, DOM nodes, or arbitrary ThreeJS objects are not yet exposed through high-level Python helpers, although common scene-level effects like day/night shaders and the rotating clouds shell now have first-class APIs.
- Any remaining `defaultProps` warnings seen only while `DASH_GLOBE_DEBUG=1` is enabled come from upstream Dash core component dev bundles, not from `dash-globe` rendering logic.
