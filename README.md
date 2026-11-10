# Shotlore maps

Offline base maps for [Shotlore Field](https://shotlore.app/field): one file per country (states or provinces for the
largest), cut every month from the [Protomaps](https://protomaps.com) basemap build of OpenStreetMap at zoom 0–14
(13 for a region that would otherwise go over GitHub's 2 GiB file limit).

- `index.json` lists every region with its download URL, size and bounding box. Shotlore Field reads it.
- The files are in the [Releases](../../releases), tagged `maps-YYYYMMDD`.
- Built by `.github/workflows/maps.yml` (monthly, or Actions › Build maps › Run workflow).
- Country and state outlines: [Natural Earth](https://www.naturalearthdata.com) (public domain).

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the
[Open Database License](https://opendatacommons.org/licenses/odbl/). The tiles are a Produced Work under the ODbL.
