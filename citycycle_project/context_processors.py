"""Template context shared by every page: map (Leaflet) configuration."""
import re
from urllib.parse import quote

from django.conf import settings

MAPTILER_ATTRIBUTION = (
    '<a href="https://www.maptiler.com/copyright/" target="_blank" rel="noopener">'
    '&copy; MapTiler</a> '
    '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">'
    '&copy; OpenStreetMap contributors</a>'
)


def map_config(request):
    """Expose tile/geocoding settings as ``CITYCYCLE_MAP``.

    The template renders it with ``json_script`` and static/common/js/citycycle_map.js
    reads it. The key is read from Django settings (.env) - never hardcoded.
    Note: any browser-side tile key is visible to the browser, so restrict it
    by HTTP origin in the MapTiler dashboard.
    """
    key = (getattr(settings, "MAPTILER_API_KEY", "") or "").strip()
    style = getattr(settings, "MAPTILER_STYLE", "streets-v2")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", style or ""):
        style = "streets-v2"

    tile_url = ""
    if key:
        # {z}/{x}/{y} placeholders are filled in by Leaflet.
        tile_url = (
            f"https://api.maptiler.com/maps/{style}/256/{{z}}/{{x}}/{{y}}.png"
            f"?key={quote(key, safe='')}"
        )

    return {
        "CITYCYCLE_MAP": {
            "tileUrl": tile_url,
            "attribution": MAPTILER_ATTRIBUTION,
            "maxZoom": 20,
            "hasKey": bool(key),
            "geocodeUrl": "https://api.maptiler.com/geocoding/",
            "apiKey": key,
        }
    }
