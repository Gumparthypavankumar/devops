#!/usr/bin/env bash
# Interval load test for the FastAPI Metrics App using Apache Benchmark (ab).
# Traffic is sent in bursts separated by idle gaps so each burst is a visible
# spike in Grafana. Mirrors the requests in "FastAPI Metrics App" (Bruno collection).
#
# Usage: ./load_test.sh [BASE_URL] [ROUNDS] [PAUSE_SECONDS]
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
ROUNDS="${2:-5}"
PAUSE="${3:-30}"

TMP_DIR="$(mktemp -d)"
echo '{"name": "Test Item"}'    > "$TMP_DIR/create.json"
echo '{"name": "Updated Item"}' > "$TMP_DIR/update.json"

# Create one item up front and reuse its item_id for the GET/PUT stages.
ITEM_ID="$(curl -sf -X POST "$BASE_URL/items" -H 'Content-Type: application/json' \
  -d '{"name": "Test Item"}' | sed -n 's/.*"item_id":\([0-9]*\).*/\1/p')"
[[ -n "$ITEM_ID" ]] || { echo "Failed to create item / parse item_id" >&2; exit 1; }
echo "Using item_id=$ITEM_ID"
# Remove the item when the script exits.
trap 'curl -s -o /dev/null -X DELETE "$BASE_URL/items/$ITEM_ID"; rm -rf "$TMP_DIR"' EXIT

# run ab quietly and show only the key lines (grep finding nothing is not an error)
run_ab() {
  ab -q "$@" | grep -E "Requests per second|Failed requests|Non-2xx" || true
}

# burst <total_requests> <concurrency>
burst() {
  local n="$1" c="$2"
  echo "  GET  /"
  run_ab -n "$n" -c "$c" "$BASE_URL/"
  echo "  POST /items"
  run_ab -n "$n" -c "$c" -p "$TMP_DIR/create.json" -T application/json "$BASE_URL/items"
  echo "  GET  /items/$ITEM_ID"
  run_ab -n "$n" -c "$c" "$BASE_URL/items/$ITEM_ID"
  echo "  PUT  /items/$ITEM_ID"
  run_ab -n "$n" -c "$c" -u "$TMP_DIR/update.json" -T application/json "$BASE_URL/items/$ITEM_ID"
}

for ((i = 1; i <= ROUNDS; i++)); do
  # Intensity grows each round so spikes are distinguishable: 200, 400, 600...
  n=$((i * 200))
  c=$((i * 5))
  echo "[$(date +%H:%M:%S)] Round $i/$ROUNDS: $n requests per endpoint, concurrency $c"
  burst "$n" "$c"
  if ((i < ROUNDS)); then
    echo "[$(date +%H:%M:%S)] Idle for ${PAUSE}s..."
    sleep "$PAUSE"
  fi
done
echo "[$(date +%H:%M:%S)] Done."
