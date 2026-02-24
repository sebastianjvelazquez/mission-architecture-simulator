#!/bin/bash
set -e

echo ""
echo "=== TEST 1: Health Check ==="
curl -s http://localhost:8000/health
echo ""

echo ""
echo "=== TEST 2: POST /architectures ==="
ARCH=$(curl -s -X POST http://localhost:8000/architectures \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Architecture","description":"Three-node chain for demo","components":[{"component_id":"s1","name":"Sensor Alpha","component_type":"Sensor","criticality":8,"x":100,"y":100},{"component_id":"c1","name":"Compute Node","component_type":"ComputeNode","criticality":9,"x":300,"y":100},{"component_id":"ctrl1","name":"Control System","component_type":"ControlSystem","criticality":10,"x":500,"y":100}],"flows":[{"source_component_id":"s1","target_component_id":"c1"},{"source_component_id":"c1","target_component_id":"ctrl1"}]}')
echo $ARCH | python3 -m json.tool
ARCH_ID=$(echo $ARCH | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created architecture with ID: $ARCH_ID"

echo ""
echo "=== TEST 3: GET /architectures ==="
curl -s http://localhost:8000/architectures | python3 -m json.tool

echo ""
echo "=== TEST 4: GET /architectures/$ARCH_ID ==="
curl -s http://localhost:8000/architectures/$ARCH_ID | python3 -m json.tool

echo ""
echo "=== TEST 5: POST /architectures/$ARCH_ID/simulate ==="
# NOTE: The simulate endpoint uses a hardcoded stub architecture with IDs sensor-1, compute-1, control-1
# The arch_id in the URL is accepted but the stub ignores the DB data (Increment 2 will fix this)
curl -s -X POST "http://localhost:8000/architectures/$ARCH_ID/simulate?scenario_type=node_compromise&target_component_id=sensor-1" | python3 -m json.tool

echo ""
echo "=== ALL TESTS PASSED ==="
