"""streets.json для миттєвого пошуку вулиць на карті: лінія вулиці + відомі номери будинків."""
import json, sys
from collections import defaultdict

streets_osm, houses_osm, out_path = sys.argv[1:4]
ways = json.load(open(streets_osm))["elements"]
houses = json.load(open(houses_osm))["elements"]

data = defaultdict(lambda: {"p": [], "h": {}})
for w in ways:
    name = w["tags"]["name"].strip()
    pts = [[round(g["lat"], 5), round(g["lon"], 5)] for g in w.get("geometry", [])]
    if pts:
        data[name]["p"].append(pts)
for e in houses:
    t = e.get("tags", {})
    street, number = (t.get("addr:street") or "").strip(), (t.get("addr:housenumber") or "").strip()
    if not street or not number:
        continue
    lat = e.get("lat") or e.get("center", {}).get("lat")
    lon = e.get("lon") or e.get("center", {}).get("lon")
    if lat is None:
        continue
    data[street]["h"][number] = [round(lat, 5), round(lon, 5)]

out = []
for name, d in sorted(data.items()):
    if not d["p"] and not d["h"]:
        continue
    out.append({"n": name, "p": d["p"], "h": d["h"]})
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("streets:", len(out), "| with numbers:", sum(1 for s in out if s["h"]))
