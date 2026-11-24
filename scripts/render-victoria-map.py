# /// script
# requires-python = ">=3.11"
# dependencies = ["mapbox-vector-tile", "shapely"]
# ///
"""Render the homepage hero map of Victoria as a small, static SVG.

    uv run scripts/render-victoria-map.py

OpenFreeMap supplies OpenMapTiles vector tiles with OpenStreetMap data (ODbL).
The site displays the matching attribution in its footer.
See https://openfreemap.org/quick_start/ and https://www.openstreetmap.org/copyright.

Set TILE_CACHE=/some/dir to keep downloaded tiles between runs while iterating.
"""

import gzip
import json
import os
import random
from math import ceil, cos, floor, log, pi, radians, sin, tan
from pathlib import Path
from urllib.request import Request, urlopen

from mapbox_vector_tile import decode
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, Polygon, box, shape
from shapely.ops import linemerge, unary_union

ZOOM = 14
# Output frame in SVG units.
WIDTH, HEIGHT = 1800, 1040
# Inner Harbour (Laurel Point) sits left of centre so the harbour, Vic West,
# downtown and James Bay all stay in view once the left edge fades out.
ANCHOR_LON, ANCHOR_LAT = -123.3745, 48.4232
ANCHOR_X, ANCHOR_Y = 0.47, 0.5
METRES_ACROSS = 5000
ROTATION = -9  # degrees; tilts the downtown grid onto a gentle diagonal
SEED = 11

OUTPUT = Path(__file__).resolve().parents[1] / "src/assets/atlas/victoria-harbour.svg"

PALETTE = {
    "land": "#efede4",
    "street": "#fbfaf6",
    "green": "#c3d3b8",
    "water": "#86a593",
    "shore": "#76978a",
    "parcel": "#f0a868",
}

# Street widths in SVG units.
ROADS = {
    "major": ({"motorway", "trunk", "primary"}, 9.0),
    "arterial": ({"secondary", "tertiary"}, 6.2),
    "minor": ({"minor"}, 3.6),
    "service": ({"service"}, 1.8),
}


def world(lon, lat):
    """Longitude/latitude to tile units at ZOOM."""
    n = 2**ZOOM
    x = (lon + 180) / 360 * n
    lat_r = radians(lat)
    y = (1 - log(tan(lat_r) + 1 / cos(lat_r)) / pi) / 2 * n
    return x, y


def fetch(url):
    cache = os.environ.get("TILE_CACHE")
    path = None
    if cache:
        path = Path(cache) / url.split("://", 1)[1].replace("/", "_")
        if path.exists():
            return path.read_bytes()
    request = Request(url, headers={"User-Agent": "static-site-map-render/1.0"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
    data = gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return data


def frame():
    """Scale (SVG units per tile unit) and the anchor in tile units."""
    ax, ay = world(ANCHOR_LON, ANCHOR_LAT)
    tile_metres = 40_075_016 * cos(radians(ANCHOR_LAT)) / 2**ZOOM
    scale = WIDTH / (METRES_ACROSS / tile_metres)
    return scale, ax, ay


def to_svg_space(geometry, scale, ax, ay):
    """Tile units → SVG units, rotated about the anchor."""
    cx, cy = ANCHOR_X * WIDTH, ANCHOR_Y * HEIGHT
    g = affinity.affine_transform(
        geometry, [scale, 0, 0, scale, cx - ax * scale, cy - ay * scale]
    )
    return affinity.rotate(g, ROTATION, origin=(cx, cy))


def tile_features():
    scale, ax, ay = frame()
    # Generous padding so rotation never exposes an empty corner.
    half = (WIDTH**2 + HEIGHT**2) ** 0.5 / scale
    template = json.loads(fetch("https://tiles.openfreemap.org/planet"))["tiles"][0]
    view = box(0, 0, WIDTH, HEIGHT).buffer(30)
    for ty in range(floor(ay - half), ceil(ay + half)):
        for tx in range(floor(ax - half), ceil(ax + half)):
            tile = fetch(template.format(z=ZOOM, x=tx, y=ty))
            layers = decode(tile, default_options={"y_coord_down": True})
            for layer, content in layers.items():
                if layer not in {"water", "park", "landcover", "landuse", "transportation"}:
                    continue
                k = 1 / content["extent"]
                clip = box(tx, ty, tx + 1, ty + 1)
                for feature in content["features"]:
                    g = affinity.affine_transform(
                        shape(feature["geometry"]), [k, 0, 0, k, tx, ty]
                    )
                    if not g.is_valid:
                        g = g.buffer(0)
                    g = g.intersection(clip)
                    if g.is_empty:
                        continue
                    g = to_svg_space(g, scale, ax, ay)
                    if not g.intersects(view):
                        continue
                    yield layer, feature["properties"], g.intersection(view)


def fmt(v):
    s = f"{v:.1f}"
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return "0" if s == "-0" else s


def ring_path(coords):
    pts = list(coords)
    if len(pts) < 3:
        return ""
    out = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    px, py = pts[0]
    for x, y in pts[1:-1]:
        out.append(f"l{fmt(x - px)} {fmt(y - py)}")
        px, py = x, y
    return "".join(out) + "z"


def polys(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "Polygon":
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [p for g in geometry.geoms for p in polys(g)]
    return []


def area_path(geometry):
    parts = []
    for p in polys(geometry):
        parts.append(ring_path(p.exterior.coords))
        parts.extend(ring_path(r.coords) for r in p.interiors)
    return "".join(parts)


def lines(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, LineString):
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [l for g in geometry.geoms for l in lines(g)]
    return []


def line_path(geometry):
    out = []
    for ln in lines(geometry):
        pts = list(ln.coords)
        if len(pts) < 2:
            continue
        out.append(f"M{fmt(pts[0][0])} {fmt(pts[0][1])}")
        px, py = pts[0]
        for x, y in pts[1:]:
            out.append(f"l{fmt(x - px)} {fmt(y - py)}")
            px, py = x, y
    return "".join(out)


def main():
    buckets = {"water": [], "green": [], **{name: [] for name in ROADS}}
    for layer, props, g in tile_features():
        kind = props.get("class")
        if layer == "water" and kind != "swimming_pool":
            buckets["water"].append(g)
        elif (
            layer == "park"
            or (layer == "landcover" and kind in {"wood", "grass"})
            or (layer == "landuse" and kind in {"cemetery", "recreation_ground", "pitch"})
        ) and g.area > 250:
            buckets["green"].append(g)
        elif layer == "transportation" and props.get("brunnel") != "tunnel":
            for name, (classes, _) in ROADS.items():
                if kind in classes:
                    buckets[name].extend(lines(g))

    view = box(0, 0, WIDTH, HEIGHT)
    water = unary_union(buckets["water"]).buffer(0.6).buffer(-0.6).simplify(0.8)
    land = view.difference(water)
    green = unary_union(buckets["green"]).intersection(land).simplify(0.8)

    merged = {}
    for name in ROADS:
        merged[name] = linemerge(MultiLineString(buckets[name])) if buckets[name] else None
        if merged[name] is not None:
            merged[name] = merged[name].simplify(0.5)

    # City blocks = land with the streets carved out; a few become "parcels".
    street_area = unary_union(
        [
            merged[name].buffer(width / 2, cap_style="flat")
            for name, (_, width) in ROADS.items()
            if merged[name] is not None and name != "service"
        ]
    )
    blocks = [
        p
        for p in polys(land.difference(street_area).difference(green.buffer(2)))
        if 900 < p.area < 9000
        and p.minimum_rotated_rectangle.area < p.area * 1.35  # tidy, block-like shapes
        and p.centroid.x > WIDTH * 0.4
        and 40 < p.centroid.y < HEIGHT * 0.86
    ]
    rng = random.Random(SEED)
    rng.shuffle(blocks)
    picks = []
    for b in blocks:
        if all(b.distance(p) > 120 for p in picks):
            picks.append(b)
        if len(picks) == 14:
            break
    parcels = unary_union([p.buffer(-1.4, join_style="mitre") for p in picks]).simplify(0.4)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" preserveAspectRatio="xMidYMid slice">',
        "<!-- Map data © OpenStreetMap contributors (ODbL), © OpenMapTiles, via OpenFreeMap -->",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PALETTE["land"]}"/>',
        f'<path fill="{PALETTE["green"]}" d="{area_path(green)}"/>',
        '<g fill="none" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for name in ("service", "parcels", "minor", "arterial", "major"):
        if name == "parcels":
            svg.append(f'<path fill="{PALETTE["parcel"]}" d="{area_path(parcels)}"/>')
            continue
        if merged[name] is None:
            continue
        width = ROADS[name][1]
        svg.append(
            f'<path stroke="{PALETTE["street"]}" stroke-width="{width}" d="{line_path(merged[name])}"/>'
        )
    svg.append("</g>")
    svg.append(
        f'<path fill="{PALETTE["water"]}" stroke="{PALETTE["shore"]}" stroke-width="1.6" '
        f'stroke-linejoin="round" d="{area_path(water)}"/>'
    )
    svg.append("</svg>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg) + "\n")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB, {len(picks)} parcels)")


if __name__ == "__main__":
    main()
