#!/bin/sh
# State boundaries for analysis (geoBoundaries IND ADM1, source DataMeet/ECI, CC BY 2.5 IN). Not SoI-certified.
# Usage (from ev-c1-infra-map-india/): sh components/admin_geo/fetch_boundaries.sh
mkdir -p .data/geo && curl -sL -m 300 -o .data/geo/ind_adm1.geojson \
  "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1_simplified.geojson"
