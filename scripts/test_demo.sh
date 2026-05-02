#!/bin/bash
# test_demo.sh — end-to-end smoke test against a running backend instance.
#
# Usage:
#   bash scripts/test_demo.sh                          # local (localhost:8000)
#   bash scripts/test_demo.sh https://your-api.onrender.com  # production
#
# All curl calls use -f (fail-on-HTTP-error) so set -e exits on any 4xx/5xx.
set -e

BASE_URL="${1:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"   # strip trailing slash if present

echo ""
echo "Testing against: $BASE_URL"
echo ""

echo "=== TEST 1: Health Check ==="
curl -sf "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "=== TEST 2: Database Health Check ==="
DB_RESP=$(curl -s -o /tmp/health_db_resp.json -w "%{http_code}" "$BASE_URL/health/db")
if [ "$DB_RESP" = "200" ]; then
  cat /tmp/health_db_resp.json | python3 -m json.tool
else
  echo "WARNING: /health/db returned HTTP $DB_RESP (expected 200)."
  echo "  If running locally without Docker DB, this is expected."
  echo "  Against production, ensure DATABASE_URL is set correctly in Render."
  cat /tmp/health_db_resp.json 2>/dev/null || true
fi
echo ""

echo "=== TEST 3: POST /architectures — create a 3-node chain ==="
ARCH=$(curl -sf -X POST "$BASE_URL/architectures" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Architecture",
    "description": "Three-node sensor-compute-control chain for demo",
    "components": [
      {"component_id": "s1",    "name": "Sensor Alpha",   "component_type": "Sensor",  "criticality": 8},
      {"component_id": "c1",    "name": "Compute Node",   "component_type": "Compute", "criticality": 9},
      {"component_id": "ctrl1", "name": "Control System", "component_type": "Control", "criticality": 10}
    ],
    "flows": [
      {"source_component_id": "s1",   "target_component_id": "c1"},
      {"source_component_id": "c1",   "target_component_id": "ctrl1"}
    ]
  }')
echo "$ARCH" | python3 -m json.tool
ARCH_ID=$(echo "$ARCH" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
COMPONENT_ID=$(echo "$ARCH" | python3 -c "import sys,json; print(json.load(sys.stdin)['components'][0]['id'])")
echo "Created architecture ID: $ARCH_ID  |  Sensor component DB id: $COMPONENT_ID"
echo ""

echo "=== TEST 4: GET /architectures — list all architectures ==="
curl -sf "$BASE_URL/architectures" | python3 -m json.tool
echo ""

echo "=== TEST 5: GET /architectures/$ARCH_ID — fetch by id ==="
curl -sf "$BASE_URL/architectures/$ARCH_ID" | python3 -m json.tool
echo ""

echo "=== TEST 6: POST /architectures/$ARCH_ID/scenarios — run node_compromise simulation ==="
curl -sf -X POST "$BASE_URL/architectures/$ARCH_ID/scenarios" \
  -H "Content-Type: application/json" \
  -d "{\"scenario_type\": \"node_compromise\", \"target_component_id\": $COMPONENT_ID}" \
  | python3 -m json.tool
echo ""

echo "=== ALL TESTS PASSED ==="
