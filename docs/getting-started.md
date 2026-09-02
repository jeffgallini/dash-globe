# Getting Started · Dash Globe

> Install from PyPI, configure with chainable helpers, and wire events like any other Dash component.

HTML version: [getting-started.html](./getting-started.html)

## Install

```bash
pip install dash-globe
```

## Minimal app

```python
from dash import Dash, html
import dash_globe

app = Dash(__name__)

globe = (
    dash_globe.DashGlobe(id="globe")
    .update_layout(height=520, background_color="#020817")
    .update_globe(globe_image_url=dash_globe.PRESETS.EARTH_NIGHT, show_atmosphere=True)
    .update_controls(auto_rotate=True, auto_rotate_speed=0.4)
    .add_points([
        {"name": "New York", "lat": 40.7128, "lng": -74.0060, "color": "#ff6b6b"},
        {"name": "London", "lat": 51.5072, "lng": -0.1276, "color": "#ffd166"},
        {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503, "color": "#4cc9f0"},
    ])
    .update_points(
        point_lat="lat",
        point_lng="lng",
        point_color="color",
        point_label="name",
        point_altitude=0.08,
        point_radius=0.28,
    )
)

app.layout = html.Div(globe)

if __name__ == "__main__":
    app.run(debug=True)
```

## Large GeoJSON without bloating the layout

```python
globe = (
    dash_globe.DashGlobe(id="countries")
    .enable_large_data_mode()
    .update_polygons(
        data=dash_globe.data_url(
            "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/ne_110m_admin_0_countries.geojson"
        ),
        polygon_geo_json_geometry="geometry",
        polygon_cap_color="rgba(56, 189, 248, 0.55)",
        polygon_side_color="rgba(14, 165, 233, 0.12)",
        polygon_stroke_color="#0f172a",
        polygon_altitude=0.06,
        polygon_label="properties.ADMIN",
    )
)
```

## Local docs gallery

```bash
cd dash_globe
python usage.py
```

Then open `http://127.0.0.1:8050`. Set `DASH_GLOBE_DEBUG=1` for Dash debug tooling.

See also: [API reference](./api.md), [llms.txt](./llms.txt).
