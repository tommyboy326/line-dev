#!/bin/bash
set -euo pipefail

# End-to-end skill trigger test using actual claude -p invocations.
# Usage: ./test_skill_e2e.sh <skill-name> [--runs N] [--threshold N]
#   --runs N      : Times to run each query (default: 3)
#   --threshold N : Min % trigger rate for should_trigger=true (default: 50)

SKILL_NAME="${1:?Usage: $0 <skill-name>}"
shift

RUNS=3
THRESHOLD=50

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs)      RUNS="$2"; shift 2 ;;
    --threshold) THRESHOLD="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
ASSESSMENT_FILE="$SCRIPT_DIR/test-data/$SKILL_NAME/assessment_set.json"

if [ ! -f "$ASSESSMENT_FILE" ]; then
  echo "Error: $ASSESSMENT_FILE not found" >&2
  exit 1
fi

PASS=0
FAIL=0
TOTAL=0

echo "Running e2e tests for skill: $SKILL_NAME"
echo "Runs per query: $RUNS | Trigger threshold: $THRESHOLD%"
echo ""

while IFS= read -r entry; do
  query=$(echo "$entry" | jq -r '.query')
  should_trigger=$(echo "$entry" | jq -r '.should_trigger')
  triggered=0

  for i in $(seq 1 "$RUNS"); do
    result=$(claude -p "$query" \
      --output-format stream-json --verbose 2>&1 \
      | jq -s '[.[] | select(.type == "tool_use" and .name == "Skill")] | length' 2>/dev/null || echo 0)
    # Check if the specific skill was triggered
    skill_triggered=$(claude -p "$query" \
      --output-format stream-json --verbose 2>&1 \
      | jq -s --arg skill "$SKILL_NAME" \
        '[.[] | select(.type == "tool_use" and .name == "Skill" and (.input.skill | test($skill)))] | length > 0' \
        2>/dev/null || echo "false")
    if [ "$skill_triggered" = "true" ]; then
      triggered=$((triggered + 1))
    fi
  done

  trigger_rate=$(( triggered * 100 / RUNS ))
  TOTAL=$((TOTAL + 1))

  if [ "$should_trigger" = "true" ]; then
    if [ "$trigger_rate" -ge "$THRESHOLD" ]; then
      PASS=$((PASS + 1))
      status="✅ PASS"
    else
      FAIL=$((FAIL + 1))
      status="❌ FAIL (should trigger)"
    fi
  else
    if [ "$trigger_rate" -lt "$THRESHOLD" ]; then
      PASS=$((PASS + 1))
      status="✅ PASS"
    else
      FAIL=$((FAIL + 1))
      status="❌ FAIL (false positive)"
    fi
  fi

  echo "$status | $trigger_rate% | $query"
done < <(jq -c '.[]' "$ASSESSMENT_FILE")

echo ""
echo "========================================="
echo "E2E Results: $PASS/$TOTAL passed ($FAIL failed)"
echo "========================================="

[ "$FAIL" -eq 0 ]
