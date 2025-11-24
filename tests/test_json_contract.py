"""
Minimal contract tests for the judge JSON.
No external test runner required—just run:
    python tests/test_json_contract.py
"""

import json
from pathlib import Path

# Import the parser from the project
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import try_parse_json  # noqa: E402


def ok(msg):
    print(f"✅ {msg}")


def fail(msg):
    print(f"❌ {msg}")
    raise SystemExit(1)


def test_valid_json():
    sample = {
        "scores": {
            "audience_fit": 5,
            "plot_structure": 4,
            "moral_clarity": 5,
            "vocabulary": 4,
            "safety": 5,
            "length": 4
        },
        "overall": 4.5,
        "actionable_feedback": ["Tighten the middle section.", "Use simpler synonyms in two sentences."]
    }
    parsed = try_parse_json(json.dumps(sample))
    if not parsed:
        fail("Valid JSON should parse and pass contract check.")
    ok("Valid JSON contract parses correctly.")


def test_invalid_json_missing_fields():
    bad = {"overall": 4.2}  # missing 'scores' and 'actionable_feedback'
    parsed = try_parse_json(json.dumps(bad))
    if parsed is not None:
        fail("Invalid JSON should NOT pass contract check.")
    ok("Invalid JSON (missing fields) is rejected.")


if __name__ == "__main__":
    test_valid_json()
    test_invalid_json_missing_fields()
    ok("All contract checks passed.")
