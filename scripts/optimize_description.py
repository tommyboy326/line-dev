#!/usr/bin/env python3
"""
Skill description optimizer for LINE dev plugin.
Uses Claude (via claude-agent-sdk or subprocess) to assess and improve
skill trigger accuracy based on an assessment set.

Usage:
  python3 optimize_description.py \
    --assessment-set scripts/test-data/messaging-api/assessment_set.json \
    --skill-path skills/messaging-api \
    --scope-config scripts/test-data/messaging-api/scope.json \
    [--max-iterations 5] \
    [--output result.json] \
    [--verbose]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def load_json(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_skill_md(skill_path: str) -> tuple[dict, str]:
    """Parse SKILL.md frontmatter and body."""
    skill_file = Path(skill_path) / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml  # type: ignore
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].strip()

    return frontmatter, body


def write_skill_description(skill_path: str, new_description: str):
    """Update the description field in SKILL.md frontmatter."""
    skill_file = Path(skill_path) / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")

    # Replace description in frontmatter
    # Handle multiline description (>  block scalar)
    pattern = r"(description:\s*>?\s*\n)((?:[ \t]+.*\n?)*)"
    replacement = f"description: >\n  {new_description.strip()}\n"
    new_content = re.sub(pattern, replacement, content, count=1)

    if new_content == content:
        # Try single-line description
        pattern2 = r"(description:\s*)(.+)"
        new_content = re.sub(pattern2, f"description: |\n  {new_description.strip()}", content, count=1)

    skill_file.write_text(new_content, encoding="utf-8")


def assess_query(query: str, skill_name: str, description: str, scope: dict) -> bool:
    """
    Ask Claude whether it would trigger the skill for this query.
    Uses claude CLI subprocess.
    """
    knowledge_domain = scope.get("knowledge_domain", "LINE API")
    assess_scope = "\n".join(scope.get("assess_scope", []))

    prompt = f"""You are evaluating whether the skill "{skill_name}" should be triggered for a user query.

Skill description:
{description}

Scope constraints:
{assess_scope}

User query: "{query}"

Answer with only "true" or "false": Would you trigger the skill "{skill_name}" for this query?
Consider: does the query clearly match the skill's domain ({knowledge_domain}) and description?
Do NOT trigger for queries about other LINE products (LIFF, LINE Login, MINI App, etc.) unless this skill covers them.
"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=30
        )
        response = result.stdout.strip().lower()
        return "true" in response
    except Exception as e:
        print(f"  Warning: assessment failed for '{query}': {e}", file=sys.stderr)
        return False


def run_assessment(assessment_set: list, skill_name: str, description: str, scope: dict, verbose: bool = False) -> dict:
    """Run full assessment and return results."""
    results = {"passed": 0, "failed": 0, "total": len(assessment_set), "failures": []}

    for item in assessment_set:
        query = item["query"]
        should_trigger = item["should_trigger"]

        triggered = assess_query(query, skill_name, description, scope)
        correct = triggered == should_trigger

        if correct:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["failures"].append({
                "query": query,
                "should_trigger": should_trigger,
                "triggered": triggered,
                "type": "missed" if should_trigger else "false_positive"
            })

        if verbose:
            status = "✅" if correct else "❌"
            print(f"  {status} [{'+' if should_trigger else '-'}] {query}")

    results["accuracy"] = results["passed"] / results["total"] if results["total"] > 0 else 0
    return results


def improve_description(current_description: str, failures: list, scope: dict, skill_name: str) -> str:
    """Ask Claude to improve the skill description based on failures."""
    improve_scope = "\n".join(scope.get("improve_scope", []))
    missed = [f["query"] for f in failures if f["type"] == "missed"]
    false_positives = [f["query"] for f in failures if f["type"] == "false_positive"]

    prompt = f"""You are improving the description of a Claude skill named "{skill_name}".

The description is used by Claude to decide when to auto-trigger this skill.
It must be specific enough to avoid false positives but broad enough to capture all relevant queries.

Scope constraints:
{improve_scope}

Current description:
{current_description}

Queries that SHOULD trigger but didn't (missed — make description broader for these):
{json.dumps(missed, ensure_ascii=False, indent=2) if missed else "None"}

Queries that should NOT trigger but did (false positives — make description more specific):
{json.dumps(false_positives, ensure_ascii=False, indent=2) if false_positives else "None"}

Write an improved description that fixes these failures.
- Include both English and Traditional Chinese (繁體中文) trigger phrases
- Be specific about what this skill covers vs related skills
- Keep it under 400 words
- Output ONLY the new description text, no explanation
"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Warning: description improvement failed: {e}", file=sys.stderr)
        return current_description


def main():
    parser = argparse.ArgumentParser(description="Optimize skill description trigger accuracy")
    parser.add_argument("--assessment-set", required=True, help="Path to assessment_set.json")
    parser.add_argument("--skill-path",     required=True, help="Path to skill directory")
    parser.add_argument("--scope-config",   required=True, help="Path to scope.json")
    parser.add_argument("--max-iterations", type=int, default=1, help="Max optimization iterations")
    parser.add_argument("--output",         help="Write results JSON to this file")
    parser.add_argument("--verbose", action="store_true", help="Print per-query results")
    args = parser.parse_args()

    assessment_set = load_json(args.assessment_set)
    scope          = load_json(args.scope_config)
    frontmatter, _ = read_skill_md(args.skill_path)
    skill_name     = frontmatter.get("name", Path(args.skill_path).name)

    # Extract description (handle YAML multiline)
    description = frontmatter.get("description", "")
    if isinstance(description, str):
        description = description.strip()

    print(f"Skill: {skill_name}")
    print(f"Assessment queries: {len(assessment_set)}")
    print(f"Max iterations: {args.max_iterations}")
    print()

    original_description = description
    best_description = description
    best_accuracy = 0.0
    history = []

    for iteration in range(1, args.max_iterations + 1):
        print(f"--- Iteration {iteration} ---")
        results = run_assessment(assessment_set, skill_name, description, scope, args.verbose)
        accuracy = results["accuracy"]
        print(f"Accuracy: {results['passed']}/{results['total']} ({accuracy:.1%})")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_description = description

        history.append({"iteration": iteration, "accuracy": accuracy, "description": description})

        if accuracy == 1.0:
            print("✅ 100% accuracy achieved!")
            break

        if iteration < args.max_iterations and results["failures"]:
            print(f"Improving description ({len(results['failures'])} failures)...")
            description = improve_description(description, results["failures"], scope, skill_name)

    print()
    print(f"Best accuracy: {best_accuracy:.1%}")
    print(f"Best description:\n{best_description}")

    if args.max_iterations > 1 and best_description != original_description:
        print("\nUpdating SKILL.md with best description...")
        write_skill_description(args.skill_path, best_description)

    output = {
        "skill": skill_name,
        "original_description": original_description,
        "best_description": best_description,
        "best_accuracy": best_accuracy,
        "history": history,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Results written to {args.output}")

    sys.exit(0 if best_accuracy == 1.0 else 1)


if __name__ == "__main__":
    main()
