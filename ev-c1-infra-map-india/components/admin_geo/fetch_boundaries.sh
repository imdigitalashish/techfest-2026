#!/bin/sh
# State boundaries for analysis (geoBoundaries IND ADM1, source DataMeet/ECI, CC BY 2.5 IN). Not SoI-certified.
# Usage (from ev-c1-infra-map-india/): sh components/admin_geo/fetch_boundaries.sh
mkdir -p .data/geo && curl -sL -m 300 -o .data/geo/ind_adm1.geojson \
  "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1_simplified.geojson"
# District boundaries (geoBoundaries IND ADM2, 2021, source Pathways Data Pvt. Ltd. + lgdirectory.gov.in, ODbL 1.0, 736 units;
# includes Palghar). Metadata: .../IND/ADM2/geoBoundaries-IND-ADM2-metaData.json
curl -sL -m 600 -o .data/geo/ind_adm2.geojson \
  "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/IND/ADM2/geoBoundaries-IND-ADM2_simplified.geojson"
