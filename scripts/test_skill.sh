#!/bin/bash
set -euo pipefail

# Usage: ./test_skill.sh <skill-name> [--max-iterations N] [--verbose] [--output FILE]
SKILL_NAME="${1:?Usage: $0 <skill-name> [--max-iterations N]}"
shift

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_DIR="$PLUGIN_DIR/skills/$SKILL_NAME"
TEST_DATA_DIR="$SCRIPT_DIR/test-data/$SKILL_NAME"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Error: skill directory not found: $SKILL_DIR" >&2
  exit 1
fi

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: SKILL.md not found in $SKILL_DIR" >&2
  exit 1
fi

if [ ! -f "$TEST_DATA_DIR/assessment_set.json" ]; then
  echo "Error: assessment_set.json not found in $TEST_DATA_DIR" >&2
  exit 1
fi

if [ ! -f "$TEST_DATA_DIR/scope.json" ]; then
  echo "Error: scope.json not found in $TEST_DATA_DIR" >&2
  exit 1
fi

python3 "$SCRIPT_DIR/optimize_description.py" \
  --assessment-set "$TEST_DATA_DIR/assessment_set.json" \
  --skill-path "$SKILL_DIR" \
  --scope-config "$TEST_DATA_DIR/scope.json" \
  "$@"
