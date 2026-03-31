#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS=(messaging-api line-login line-liff line-mini-app line-notification-message)
PASS=0
FAIL=0

for skill in "${SKILLS[@]}"; do
  echo "=== Testing: $skill ==="
  if "$SCRIPT_DIR/test_skill.sh" "$skill" --max-iterations 1 "$@"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
  fi
  echo ""
done

echo "========================================="
echo "Results: $PASS passed, $FAIL failed (${#SKILLS[@]} total)"
echo "========================================="
