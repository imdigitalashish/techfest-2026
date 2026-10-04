#!/usr/bin/env bash
# Serve the NullahNet dashboard offline for the pitch (backup slide 11). Usage: bash innovatex-t3-coastal-plastic/deliverables/serve_dashboard.sh
# Then open http://localhost:8765 . Everything (Leaflet, data bundle) is local; only the OpenStreetMap tiles need a network.
set -euo pipefail
cd "$(dirname "$0")/../components/dashboard/site"
echo "NullahNet dashboard: http://localhost:8765  (Ctrl-C to stop)"
python3 -m http.server 8765 --bind 127.0.0.1
