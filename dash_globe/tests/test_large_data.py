import pytest

from dash_globe import DashGlobe, data_url, is_data_url


def test_data_url_helper_builds_client_fetch_marker():
    marker = data_url("https://example.com/countries.geojson")
    assert marker == {
        "type": "dash-globe-data-url",
        "url": "https://example.com/countries.geojson",
        "unwrapFeatures": True,
    }
    assert is_data_url(marker) is True
    assert is_data_url({"type": "dash-globe-data-url", "url": ""}) is False
    assert is_data_url("https://example.com/countries.geojson") is False


def test_data_url_rejects_empty_url():
    with pytest.raises(ValueError, match="non-empty URL"):
        data_url("   ")


def test_update_polygons_accepts_data_url_without_list_coercion():
    marker = data_url("/assets/countries.geojson", unwrap_features=False)
    globe = (
        DashGlobe(id="url-polygons")
        .enable_large_data_mode()
        .update_polygons(
            data=marker,
            polygon_geo_json_geometry="geometry",
            polygon_cap_color="steelblue",
        )
    )

    assert globe.largeDataMode is True
    assert globe.eventDataMode == "summary"
    assert globe.polygonsData == marker
    assert globe.polygonGeoJsonGeometry == "geometry"
    assert globe.polygonCapColor == "steelblue"


def test_enable_large_data_mode_can_be_disabled():
    globe = DashGlobe(id="toggle-large-data").enable_large_data_mode(False, event_data_mode="full")
    assert globe.largeDataMode is False
    assert globe.eventDataMode == "full"
