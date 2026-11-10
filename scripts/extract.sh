#!/usr/bin/env bash
# extract.sh <planet-url> <shard> <shards> <release-tag>
# For each country in this shard: cut it from the remote planet at max zoom 14; if the file is over the 2 GiB
# GitHub limit, cut each state/province instead (dropping to zoom 13 for any still too big); upload to the release.
set -euo pipefail
PLANET="$1"; SHARD="$2"; SHARDS="$3"; TAG="$4"
LIMIT=$((2000 * 1024 * 1024))
mkdir -p out
codes=$(python3 -c "import json;l=json.load(open('regions/list.json'));print(' '.join(c['code'] for i,c in enumerate(l) if i % $SHARDS == $SHARD))")
cut() { # cut <geojson> <outfile> <maxzoom>
  ./pmtiles extract "$PLANET" "$2" --region="$1" --maxzoom="$3" --download-threads=4 >/dev/null
}
size() { stat -c %s "$1"; }
for c in $codes; do
  f="out/$c.pmtiles"
  if ! cut "regions/$c.geojson" "$f" 14; then echo "FAILED $c"; continue; fi
  if [ "$(size "$f")" -le "$LIMIT" ]; then
    gh release upload "$TAG" "$f" --clobber; echo "$c $(size "$f") z14" >> "out/sizes-$SHARD.txt"; rm -f "$f"; continue
  fi
  rm -f "$f"
  for g in regions/admin1/$c/*.geojson; do
    s=$(basename "$g" .geojson); sf="out/$s.pmtiles"
    cut "$g" "$sf" 14 || { echo "FAILED $s"; continue; }
    z=14
    if [ "$(size "$sf")" -gt "$LIMIT" ]; then rm -f "$sf"; cut "$g" "$sf" 13; z=13; fi
    gh release upload "$TAG" "$sf" --clobber; echo "$s $(size "$sf") z$z" >> "out/sizes-$SHARD.txt"; rm -f "$sf"
  done
done
