#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "Testing API at $BASE_URL"
echo

echo "1) Signup"
SIGNUP_RESPONSE=$(curl -sS -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  -w "\nHTTP:%{http_code}")
echo "$SIGNUP_RESPONSE"
echo

if echo "$SIGNUP_RESPONSE" | grep -q '"access_token"'; then
  TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import json,sys; print(json.loads(sys.stdin.read().split('HTTP:')[0])['access_token'])")
else
  echo "Signup failed. If HTTP 503, check DATABASE_URL and JWT_SECRET in backend/.env"
  exit 1
fi

echo "2) Login"
curl -sS -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"
echo
echo

echo "3) Resource groups (requires Azure CLI + az login)"
curl -sS "$BASE_URL/api/resource-groups" -H "Authorization: Bearer $TOKEN"
echo
echo

echo "4) History"
curl -sS "$BASE_URL/api/history" -H "Authorization: Bearer $TOKEN"
echo
