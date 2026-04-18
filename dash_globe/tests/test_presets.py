from dash_globe import PRESETS
from usage import CHOROPLETH_BACKGROUND_IMAGE_URL


OLD_JSDELIVR_PREFIX = "//cdn.jsdelivr.net/npm/three-globe/example/img/"


def test_presets_use_absolute_https_urls():
    preset_urls = [
        PRESETS.EARTH,
        PRESETS.EARTH_NIGHT,
        PRESETS.EARTH_DARK,
        PRESETS.EARTH_DAY,
        PRESETS.EARTH_TOPOGRAPHY,
        PRESETS.EARTH_WATER,
        PRESETS.NIGHT_SKY,
    ]

    assert all(url.startswith("https://") for url in preset_urls)
    assert all(OLD_JSDELIVR_PREFIX not in url for url in preset_urls)


def test_choropleth_background_image_uses_absolute_https_url():
    assert CHOROPLETH_BACKGROUND_IMAGE_URL.startswith("https://")
    assert OLD_JSDELIVR_PREFIX not in CHOROPLETH_BACKGROUND_IMAGE_URL
