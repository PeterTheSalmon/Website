"""Render the homepage's static map.

Run with Python, Pillow and mapbox-vector-tile installed:
    python scripts/render-victoria-map.py

OpenFreeMap supplies OpenMapTiles vector tiles with OpenStreetMap data (ODbL).
The website displays the corresponding attribution alongside the rendered map.
See https://openfreemap.org/quick_start/ and https://www.openstreetmap.org/copyright.
"""

import gzip
import json
from math import ceil, floor
from pathlib import Path
from urllib.request import Request, urlopen

from mapbox_vector_tile import decode
from PIL import Image, ImageDraw
from shapely.geometry import box, shape
from shapely.affinity import affine_transform
from shapely.ops import unary_union


ZOOM = 14
LEFT, TOP, RIGHT = 2575.88, 5665.60, 2577.78
WIDTH, HEIGHT = 1440, 1024
SCALE = WIDTH / (RIGHT - LEFT)
BOTTOM = TOP + HEIGHT / SCALE
OUTPUT = Path(__file__).resolve().parents[1] / "src/assets/atlas/victoria-harbour.webp"


def fetch(url):
    request = Request(
        url, headers={"User-Agent": "petersalmon.dev static Victoria atlas"}
    )
    with urlopen(request, timeout=25) as response:
        data = response.read()
    return gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data


def tile_features():
    template = json.loads(fetch("https://tiles.openfreemap.org/planet"))["tiles"][0]
    for y in range(floor(TOP), ceil(BOTTOM)):
        for x in range(floor(LEFT), ceil(RIGHT)):
            tile = fetch(template.format(z=ZOOM, x=x, y=y))
            for layer, content in decode(
                tile, default_options={"y_coord_down": True}
            ).items():
                if layer not in {
                    "water",
                    "park",
                    "landcover",
                    "landuse",
                    "building",
                    "transportation",
                }:
                    continue
                factor = SCALE / content["extent"]
                tx = (x - LEFT) * SCALE
                ty = (y - TOP) * SCALE
                clip = box(
                    max(0, tx),
                    max(0, ty),
                    min(WIDTH, tx + SCALE),
                    min(HEIGHT, ty + SCALE),
                )
                for feature in content["features"]:
                    geom = affine_transform(
                        shape(feature["geometry"]), [factor, 0, 0, factor, tx, ty]
                    )
                    if not geom.is_valid:
                        geom = geom.buffer(0)
                    geom = geom.intersection(clip)
                    if not geom.is_empty:
                        yield layer, feature["properties"], geom


def polygon(draw, geometry, fill, hole_fill):
    if geometry.geom_type == "Polygon":
        draw.polygon(list(geometry.exterior.coords), fill=fill)
        for ring in geometry.interiors:
            draw.polygon(list(ring.coords), fill=hole_fill)
    elif hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            polygon(draw, part, fill, hole_fill)


def line(draw, geometry, fill, width):
    if geometry.geom_type == "LineString":
        draw.line(list(geometry.coords), fill=fill, width=width, joint="curve")
    elif hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            line(draw, part, fill, width)


def main():
    land, water = "#e9e9df", "#749485"
    image = Image.new("RGB", (WIDTH, HEIGHT), land)
    draw = ImageDraw.Draw(image)
    layers = {
        name: [] for name in ("green", "water", "building", "minor", "major", "pier")
    }
    for layer, properties, geometry in tile_features():
        kind = properties.get("class")
        if layer == "water":
            layers["water"].append(geometry)
        if layer == "building":
            layers["building"].append(geometry)
        if (
            layer == "park"
            or layer == "landcover"
            and kind in {"wood", "grass"}
            or layer == "landuse"
            and kind in {"recreation_ground", "cemetery"}
        ):
            layers["green"].append(geometry)
        if layer == "transportation":
            if kind in {"motorway", "trunk", "primary", "secondary", "tertiary"}:
                layers["major"].append(geometry)
            elif kind == "minor" and properties.get("subclass") != "service":
                layers["minor"].append(geometry)
            elif kind == "pier":
                layers["pier"].append(geometry)

    for green in layers["green"]:
        if green.area > 150:
            polygon(draw, green.simplify(2), "#bacbb1", land)
    for building in layers["building"]:
        point = building.representative_point()
        accent = (
            building.area > 180
            and point.x > WIDTH * 0.59
            and int(point.x + point.y) % 31 == 0
        )
        if accent:
            polygon(draw, building.simplify(1.5), "#da9a67", land)

    shoreline = unary_union(layers["water"]).simplify(2)
    polygon(draw, shoreline, water, land)

    for name, color, width in [
        ("minor", "#f8f8f3", 4),
        ("pier", "#e9e9df", 5),
        ("major", "#fdfdfb", 8),
    ]:
        for geometry in layers[name]:
            geometry = geometry.simplify(1.5)
            if name == "pier":
                polygon(draw, geometry, color, water)
            line(draw, geometry, color, width)

    # Frame the harbour as an editorial illustration using a rotated, inset crop.
    image = image.rotate(16, resample=Image.Resampling.BICUBIC, fillcolor=land)
    image = image.crop((130, 110, WIDTH - 130, HEIGHT - 110))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, quality=90, method=6)


if __name__ == "__main__":
    main()
