#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
EMAIL="${TEST_EMAIL:-e2e@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"
ANALYSIS_ID="${ANALYSIS_ID:-e2e-run-$(date +%s)}"

echo "=== End-to-End API Flow Test ==="
echo "Base URL: $BASE_URL"
echo

echo "Step 1: Signup"
SIGNUP_RESPONSE=$(curl -sS -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  -w "\nHTTP:%{http_code}")

if ! echo "$SIGNUP_RESPONSE" | grep -q '"access_token"'; then
  echo "$SIGNUP_RESPONSE"
  echo "Signup failed. Check DATABASE_URL and JWT_SECRET in backend/.env"
  exit 1
fi

TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import json,sys; print(json.loads(sys.stdin.read().split('HTTP:')[0])['access_token'])")
echo "Signup OK"
echo

echo "Step 2: Login"
LOGIN_RESPONSE=$(curl -sS -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo "$LOGIN_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print('Login OK for', data['email'])"
echo

echo "Step 3: Resource groups (requires Azure CLI)"
RG_STATUS=$(curl -sS -o /tmp/rg.json -w "%{http_code}" \
  "$BASE_URL/api/resource-groups" -H "Authorization: Bearer $TOKEN")
echo "HTTP $RG_STATUS"
cat /tmp/rg.json
echo
echo

echo "Step 4: History"
curl -sS "$BASE_URL/api/history" -H "Authorization: Bearer $TOKEN"
echo
echo

echo "Step 5: Analyze with WebSocket progress id=$ANALYSIS_ID"
ANALYZE_STATUS=$(curl -sS -o /tmp/analyze.json -w "%{http_code}" \
  -X POST "$BASE_URL/api/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"resource_group\":\"test-rg\",\"analysis_id\":\"$ANALYSIS_ID\"}")
echo "HTTP $ANALYZE_STATUS"
cat /tmp/analyze.json
echo

if [ "$RG_STATUS" = "200" ] && [ "$ANALYZE_STATUS" = "200" ]; then
  echo
  echo "Full end-to-end flow succeeded."
else
  echo
  echo "Auth/history flow succeeded. Azure CLI and OpenAI are required for steps 3 and 5."
fi
