#!/usr/bin/env python3
"""Writes regions/<CODE>.geojson for every country (Natural Earth 1:10m, public domain), plus
regions/admin1/<CC>/<CC-SUB>.geojson for the states/provinces used when a country's map is over the
2 GiB GitHub file limit. Also regions/list.json: [{code, name, bbox}]. No dependencies."""
import json, os, sys, urllib.request
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
def get(name):
    with urllib.request.urlopen(NE + name, timeout=300) as r:
        return json.load(r)
def bbox(geom):
    xs, ys = [], []
    def walk(c):
        if isinstance(c[0], (int, float)): xs.append(c[0]); ys.append(c[1])
        else:
            for x in c: walk(x)
    walk(geom["coordinates"])
    return [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)]
def code_of(p):
    for k in ("ISO_A2_EH", "ISO_A2", "WB_A2"):
        v = p.get(k)
        if v and v not in ("-99", "-1"): return v.upper()
    return None
os.makedirs("regions/admin1", exist_ok=True)
countries = get("ne_10m_admin_0_countries.geojson")
out = {}
for f in countries["features"]:
    p = f["properties"]; code = code_of(p)
    if not code: continue
    name = p.get("NAME_EN") or p.get("NAME")
    if code in out:  # same code twice (e.g. disputed parts): merge into one multipolygon
        prev = out[code]; g = prev["geometry"]
        polys = (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]) + (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]])
        prev["geometry"] = {"type": "MultiPolygon", "coordinates": polys}
        continue
    out[code] = {"type": "Feature", "properties": {"code": code, "name": name}, "geometry": f["geometry"]}
listing = []
for code, feat in sorted(out.items()):
    with open(f"regions/{code}.geojson", "w") as fh: json.dump({"type": "FeatureCollection", "features": [feat]}, fh)
    listing.append({"code": code, "name": feat["properties"]["name"], "bbox": bbox(feat["geometry"])})
states = get("ne_10m_admin_1_states_provinces.geojson")
subs = {}
for f in states["features"]:
    p = f["properties"]; cc = (p.get("iso_a2") or "").upper(); sub = p.get("iso_3166_2") or ""
    if not cc or cc == "-99" or not sub or "~" in sub: continue
    os.makedirs(f"regions/admin1/{cc}", exist_ok=True)
    feat = {"type": "Feature", "properties": {"code": sub, "name": p.get("name_en") or p.get("name")}, "geometry": f["geometry"]}
    with open(f"regions/admin1/{cc}/{sub}.geojson", "w") as fh: json.dump({"type": "FeatureCollection", "features": [feat]}, fh)
    subs.setdefault(cc, []).append({"code": sub, "name": feat["properties"]["name"], "bbox": bbox(f["geometry"])})
for c in listing: c["subregions"] = sorted(subs.get(c["code"], []), key=lambda s: s["code"])
with open("regions/list.json", "w") as fh: json.dump(listing, fh, ensure_ascii=False, indent=1)
print(f"{len(listing)} countries, {sum(len(v) for v in subs.values())} subregions")
