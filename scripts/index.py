#!/usr/bin/env python3
"""index.py <tag> <planet-date> <repo>: builds index.json (what Shotlore Field reads) from regions/list.json and the
sizes each shard recorded. A country with its own file has "file"; a split country lists "parts" (states/provinces)."""
import json, glob, sys
tag, built, repo = sys.argv[1], sys.argv[2], sys.argv[3]
sizes = {}
for p in glob.glob("sizes/*.txt"):
    for line in open(p):
        code, n, z = line.split(); sizes[code] = (int(n), int(z[1:]))
base = f"https://github.com/{repo}/releases/download/{tag}/"
out = []
for c in json.load(open("regions/list.json")):
    e = {"code": c["code"], "name": c["name"], "bbox": c["bbox"]}
    if c["code"] in sizes:
        n, z = sizes[c["code"]]; e.update(url=base + c["code"] + ".pmtiles", bytes=n, maxzoom=z)
    else:
        parts = [{"code": s["code"], "name": s["name"], "bbox": s["bbox"], "url": base + s["code"] + ".pmtiles", "bytes": sizes[s["code"]][0], "maxzoom": sizes[s["code"]][1]}
                 for s in c.get("subregions", []) if s["code"] in sizes]
        if not parts: continue
        e["parts"] = parts
    out.append(e)
json.dump({"v": 1, "built": built, "release": tag, "source": "Protomaps basemap (OpenStreetMap)", "attribution": "© OpenStreetMap contributors", "regions": out},
          open("index.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "regions in index.json")
