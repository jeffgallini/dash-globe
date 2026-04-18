"""Bundled texture presets for common globe scenes."""

class _Presets:
    """Namespace of built-in globe texture URLs.

    Attributes
    ----------
    EARTH : str
        Daytime Earth texture.
    EARTH_NIGHT : str
        Nighttime Earth texture.
    EARTH_DARK : str
        Dark-toned Earth texture.
    EARTH_DAY : str
        Blue-marble daytime Earth texture.
    EARTH_TOPOGRAPHY : str
        Topographic Earth texture.
    EARTH_WATER : str
        Water mask texture.
    NIGHT_SKY : str
        Starfield background image.
    CLOUDS : str
        Transparent cloud texture for the optional cloud shell.
    """

    EARTH = "https://unpkg.com/three-globe@2.45.2/example/img/earth-day.jpg"
    EARTH_NIGHT = "https://unpkg.com/three-globe@2.45.2/example/img/earth-night.jpg"
    EARTH_DARK = "https://unpkg.com/three-globe@2.45.2/example/img/earth-dark.jpg"
    EARTH_DAY = "https://unpkg.com/three-globe@2.45.2/example/img/earth-blue-marble.jpg"
    EARTH_TOPOGRAPHY = "https://unpkg.com/three-globe@2.45.2/example/img/earth-topology.png"
    EARTH_WATER = "https://unpkg.com/three-globe@2.45.2/example/img/earth-water.png"
    NIGHT_SKY = "https://unpkg.com/three-globe@2.45.2/example/img/night-sky.png"
    CLOUDS = "https://unpkg.com/globe.gl/example/clouds/clouds.png"


PRESETS = _Presets()
