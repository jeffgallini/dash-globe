# Dash Globe Python API

> Chainable Python API for building interactive 3D globes in Dash on top of [react-globe.gl](https://github.com/vasturiano/react-globe.gl).

Install: `pip install dash-globe`

HTML version: [api.html](./api.html)

## Imports

```python
import dash_globe

globe = dash_globe.DashGlobe(id="globe")
dash_globe.PRESETS
dash_globe.data_url(...)
dash_globe.event_coords(...)
dash_globe.material_spec(...)
dash_globe.lambert_material(...)
dash_globe.ring_color_interpolator(...)
```

Public exports: `DashGlobe`, `PRESETS`, `data_url`, `is_data_url`, `event_coords`, `ring_color_interpolator`, `material_spec`, `lambert_material`.

## DashGlobe

`DashGlobe(*args, **kwargs)` subclasses the generated Dash component and defaults `responsive=True`. Every helper returns `self` for chaining.

`update(**kwargs)` sets props in place. Snake-case aliases map to camelCase component props (`background_color` → `backgroundColor`).

### Scene helpers

- `update_layout(width=, height=, responsive=, background_color=, background_image_url=, globe_offset=, wait_for_globe_ready=, animate_in=, renderer_config=, style=, class_name=)`
- `update_globe(globe_image_url=, bump_image_url=, show_globe=, show_graticules=, show_atmosphere=, atmosphere_color=, atmosphere_altitude=, curvature_resolution=)`
- `update_view(lat=, lng=, altitude=, transition_duration=)`
- `update_controls(auto_rotate=, auto_rotate_speed=)`
- `update_interaction(enable_pointer_interaction=, show_pointer_cursor=, line_hover_precision=, animation_paused=, current_view_report_interval=)`
- `update_day_night_cycle(enabled=, day_image_url=, night_image_url=, time=, animate=, minutes_per_second=)`
- `update_clouds(enabled=, image_url=, altitude=, rotation_speed=, opacity=)`
- `clear_tile_cache()`

### Layers

Each layer supports `add_*` (append) and `update_*` (replace data / set accessors):

| Layer | Methods |
| --- | --- |
| Points | `add_points`, `update_points` |
| Arcs | `add_arcs`, `update_arcs` |
| Polygons | `add_polygons`, `update_polygons` |
| Paths | `add_paths`, `update_paths` |
| Heatmaps | `add_heatmap`, `add_heatmaps`, `update_heatmap`, `update_heatmaps` |
| Hex bins | `add_hex_bins`, `update_hex_bins` |
| Hex polygons | `add_hex_polygons`, `update_hex_polygons` |
| Tiles | `add_tiles`, `update_tiles` |
| Particles | `add_particle_sets`, `update_particles` |
| Rings | `add_rings`, `update_rings` |
| Labels | `add_labels`, `update_labels` |
| HTML overlays | `add_html_elements`, `update_html_elements` |

Accessors accept constants or string field paths (`"lat"`, `"properties.ADMIN"`).

### Large data

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
        polygon_label="properties.ADMIN",
    )
)
```

`data_url(url, unwrap_features=True)` builds a client-fetch marker so large GeoJSON never enters the Dash layout. `enable_large_data_mode()` turns on summary event payloads and other large-data defaults.

## Helpers

### PRESETS

Texture URLs: `EARTH`, `EARTH_DAY`, `EARTH_NIGHT`, `EARTH_DARK`, `EARTH_TOPOGRAPHY`, `EARTH_WATER`, `NIGHT_SKY`, `CLOUDS`.

### event_coords(event)

Returns `{"lat", "lng", "altitude?"}` from `clickData` / `hoverData`, or `None`.

### material_spec / lambert_material

JSON material specs for tiles. Types: `basic`, `lambert`, `phong`, `standard`. Side: `front`, `back`, `double`.

### ring_color_interpolator

Serialisable ring fade spec. Easing: `linear`, `sqrt`, `square`, `cubic`.

## Events

Dash callback props: `clickData`, `rightClickData`, `hoverData`, `currentView`. Payload size controlled by `eventDataMode` (`"summary"` | `"full"`).

```python
from dash import Input, Output, callback
import dash_globe

@callback(Output("out", "children"), Input("globe", "clickData"))
def on_click(click_data):
    return str(dash_globe.event_coords(click_data))
```

## Notes

- Focus is JSON-serialisable `react-globe.gl` features that map cleanly to Dash.
- Raw JS functions, DOM nodes, and arbitrary Three.js objects are not exposed through high-level helpers.
- Source: [dash_globe/globe.py](https://github.com/jeffgallini/dash-globe/blob/master/dash_globe/dash_globe/globe.py)
