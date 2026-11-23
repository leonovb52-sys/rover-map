"""Стилі карти Rover (день і ніч) на основі даних OpenFreeMap / OpenStreetMap.
python3 make_rover_styles.py liberty.json <тека_виводу>  →  rover-day.json, rover-night.json"""
import copy, json, sys

PALETTES = {
    "day": {
        "fill": {"background": "#f2f3f5", "landuse_residential": "#eceef1", "park": "#d5ecd1", "landcover_wood": "#d7ecd2",
                 "landcover_grass": "#dcefd7", "landuse_pitch": "#d5ebd0", "landuse_track": "#dde8d9",
                 "landuse_cemetery": "#e0e8da", "landuse_hospital": "#f8e6e6", "landuse_school": "#f1efe4",
                 "water": "#a8d4f6", "landcover_sand": "#f4efdc", "aeroway_fill": "#e8e9ec", "building": "#dfe2e7"},
        "building_outline": "#cdd1d8",
        "line": {"waterway": "#a8d4f6", "park_outline": "rgba(0,0,0,0)",
                 "motorway_link_casing": "#e8b24a", "motorway_casing": "#e8b24a", "trunk_primary_casing": "#efc65e",
                 "link_casing": "#efc65e", "secondary_tertiary_casing": "#ecc96a", "minor_casing": "#d9dde3",
                 "street_casing": "#d9dde3", "service_track_casing": "#e1e4e9", "path_pedestrian_casing": "#e1e4e9",
                 "motorway_link": "#ffd36e", "motorway": "#ffd36e", "trunk_primary": "#ffe7a3", "link": "#ffe7a3",
                 "secondary_tertiary": "#fff1bd", "minor": "#ffffff", "street": "#ffffff", "service_track": "#ffffff",
                 "path_pedestrian": "#ffffff", "rail": "#c4c8d0", "aeroway": "#e8e9ec", "boundary": "#c4c8d0"},
        "text": {"label_": ("#22262d", "#ffffff"), "highway-name": ("#5b6270", "#ffffff"),
                 "poi_": ("#59606c", "#ffffff"), "water": ("#4a7db0", "rgba(255,255,255,0.85)"),
                 "airport": ("#59606c", "#ffffff")},
        "icon_opacity": 1,
    },
    "night": {
        "fill": {"background": "#171b24", "landuse_residential": "#1b202a", "park": "#1b2b24", "landcover_wood": "#1c2c25",
                 "landcover_grass": "#1c2b24", "landuse_pitch": "#1c2b24", "landuse_track": "#1d2621",
                 "landuse_cemetery": "#1c2622", "landuse_hospital": "#2a1f24", "landuse_school": "#22231f",
                 "water": "#1d3a5a", "landcover_sand": "#2a2820", "aeroway_fill": "#22262f", "building": "#252b36"},
        "building_outline": "#2f3643",
        "line": {"waterway": "#1d3a5a", "park_outline": "rgba(0,0,0,0)",
                 "motorway_link_casing": "#5a4520", "motorway_casing": "#5a4520", "trunk_primary_casing": "#4d3d1e",
                 "link_casing": "#4d3d1e", "secondary_tertiary_casing": "#463a1f", "minor_casing": "#1f242e",
                 "street_casing": "#1f242e", "service_track_casing": "#1d222b", "path_pedestrian_casing": "#1d222b",
                 "motorway_link": "#b8892f", "motorway": "#b8892f", "trunk_primary": "#9c7a33", "link": "#9c7a33",
                 "secondary_tertiary": "#7d6a3c", "minor": "#353c4a", "street": "#353c4a", "service_track": "#2d3340",
                 "path_pedestrian": "#2d3340", "rail": "#3a404c", "aeroway": "#2a2f39", "boundary": "#3a404c"},
        "text": {"label_": ("#e6e9ef", "#171b24"), "highway-name": ("#aeb4c0", "#171b24"),
                 "poi_": ("#aeb4c0", "#171b24"), "water": ("#7fa9d6", "#171b24"), "airport": ("#aeb4c0", "#171b24")},
        "icon_opacity": 0.75,
    },
}
HIDE = {"natural_earth", "building-3d", "road_area_pattern"}
UK = ["coalesce", ["get", "name:uk"], ["get", "name"]]


def build(base, pal):
    s = copy.deepcopy(base)
    for layer in s["layers"]:
        lid, paint = layer["id"], layer.setdefault("paint", {})
        if lid in HIDE:
            layer.setdefault("layout", {})["visibility"] = "none"
            continue
        if lid in pal["fill"]:
            paint["background-color" if layer["type"] == "background" else "fill-color"] = pal["fill"][lid]
            if lid == "building":
                paint["fill-outline-color"] = pal["building_outline"]
            if lid == "park":
                paint["fill-outline-color"] = "rgba(0,0,0,0)"
        if layer["type"] == "line":
            # найдовший збіг назви — щоб «trunk_primary_casing» не сплутати з «trunk_primary»
            match = max((k for k in pal["line"] if k in lid), key=len, default=None)
            if match:
                paint["line-color"] = pal["line"][match]
        if layer["type"] == "symbol":
            for prefix, (color, halo) in pal["text"].items():
                if lid.startswith(prefix) or prefix in lid:
                    paint.update({"text-color": color, "text-halo-color": halo, "text-halo-width": 1.4})
                    break
            if lid.startswith("poi"):
                paint["icon-opacity"] = pal["icon_opacity"]
            lay = layer.get("layout", {})
            if "text-field" in lay and "shield" not in lid:
                lay["text-field"] = UK  # підписи українською
    return s


base = json.load(open(sys.argv[1]))
for name, pal in PALETTES.items():
    out = build(base, pal)
    out["name"] = f"Rover {name}"
    json.dump(out, open(f"{sys.argv[2]}/rover-{name}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("ok", name)
