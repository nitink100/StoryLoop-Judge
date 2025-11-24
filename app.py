"""
This tool generates a children's bedtime story (ages 5-10) with a simple
judge-and-revise loop. It keeps the OpenAI model per the brief and uses your
OPENAI_API_KEY from the environment. Keys are not committed.

Usage:
  export OPENAI_API_KEY="sk-..."  
  python app.py --topic "A kid helps a lost cloud find home" --age 8 --style "bedtime, gentle" --moral "kindness"

Flags:
  --max-loops: Max judge-revise iterations (default: 1, keep tight)
  --threshold: Required overall score (1-5 scale, default: 4.2)
  --verbose:   Print scores and decisions
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Tuple, Optional, List

from prompts import build_storyteller_messages, build_judge_messages, build_revise_messages
from utils import call_openai_chat, word_count, try_parse_json

MODEL_NAME = "gpt-3.5-turbo"  # NOTE: do not change per instructions


def storyteller(topic: str, age: int, style: str, moral: str, temperature: float = 0.5) -> str:
    messages: List[Dict[str, str]] = build_storyteller_messages(topic=topic, age=age, style=style, moral=moral)
    return call_openai_chat(model=MODEL_NAME, messages=messages, temperature=temperature)


def judge(story_text: str, temperature: float = 0.0) -> Tuple[Dict[str, Any], str]:
    """Return (parsed_json, raw_text). Retries JSON once if invalid."""
    messages = build_judge_messages(story_text)
    raw = call_openai_chat(model=MODEL_NAME, messages=messages, temperature=temperature)
    parsed = try_parse_json(raw)

    if parsed is None:
        # One strict retry requesting valid JSON only
        messages[-1]["content"] += "\n\nIMPORTANT: Return VALID JSON only. No commentary."
        raw = call_openai_chat(model=MODEL_NAME, messages=messages, temperature=temperature)
        parsed = try_parse_json(raw)

    if parsed is None:
        raise ValueError("Judge did not return valid JSON after one retry.")
    return parsed, raw


def revise(story_text: str, judge_report: Dict[str, Any], temperature: float = 0.4) -> str:
    feedback = judge_report.get("actionable_feedback", [])
    overall = judge_report.get("overall", 0)
    messages = build_revise_messages(story_text, feedback, target_overall=max(overall, 4.2))
    return call_openai_chat(model=MODEL_NAME, messages=messages, temperature=temperature)


def enforce_length(story: str, low: int = 350, high: int = 550) -> bool:
    """True if story word count is within [low, high]."""
    wc = word_count(story)
    return low <= wc <= high


def length_hint_for(story: str, low: int = 350, high: int = 550) -> Optional[str]:
    wc = word_count(story)
    if wc < low:
        return "Expand to 350-550 words with full paragraphs."
    if wc > high:
        return "Tighten to 350-550 words without removing key plot beats."
    return None


def run(topic: str, age: int, style: str, moral: str, max_loops: int, threshold: float, verbose: bool) -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in environment.", file=sys.stderr)
        return 2

    print("🚀 Starting story generation...")
    print(f"   Topic: {topic}")
    print(f"   Age: {age}")
    print(f"   Style: {style}")
    print(f"   Moral: {moral}")
    print(f"   Score Threshold: {threshold}/5")
    print(f"   Max Revisions: {max_loops}\n")

    # 1) Initial draft
    draft = storyteller(topic=topic, age=age, style=style, moral=moral, temperature=0.5)
    if verbose:
        print(f"Draft word count: {word_count(draft)}\n")

    revisions_used = 0

    # Single optional pre-revise ONLY for length (counts toward max_loops)
    lh = length_hint_for(draft)
    if lh is not None and revisions_used < max_loops:
        if verbose:
            print(f"Length off on first draft; applying one length-aware revision: {lh}")
        pseudo_report = {"actionable_feedback": [lh], "overall": 3.5}
        draft = revise(draft, pseudo_report, temperature=0.4)
        revisions_used += 1
        if verbose:
            print(f"Post-length-fix word count: {word_count(draft)}\n")

    # 2) Judge
    report, _ = judge(draft, temperature=0.0)
    if verbose:
        print("Judge report (JSON):")
        print(json.dumps(report, indent=2))
        print()

    if report.get("overall", 0) >= threshold:
        print("✅ Threshold met on first pass.\n")
        print("=== FINAL STORY ===\n")
        print(draft)
        print("\n=== SCORES ===")
        print(json.dumps(report, indent=2))
        return 0

    # 3) Bounded revise loop — ONE revise per loop (merge judge + length)
    current = draft
    while revisions_used < max_loops and report.get("overall", 0) < threshold:
        if verbose:
            print(f"\n🔁 Revision loop {revisions_used + 1} / {max_loops}")

        feedback = list(report.get("actionable_feedback", []))
        lh = length_hint_for(current)
        if lh:
            feedback.append(lh)

        merged_report = {
            "actionable_feedback": feedback if feedback else ["Polish flow while keeping clarity for ages 5-10."],
            "overall": report.get("overall", 3.5),
        }

        current = revise(current, merged_report, temperature=0.4)
        revisions_used += 1

        report, _ = judge(current, temperature=0.0)
        if verbose:
            print("Judge report (JSON):")
            print(json.dumps(report, indent=2))

    # Finalize
    if report.get("overall", 0) >= threshold:
        print("\n✅ Threshold met.\n")
        print("=== FINAL STORY ===\n")
        print(current)
        print("\n=== SCORES ===")
        print(json.dumps(report, indent=2))
        return 0

    print("\nMax revisions reached. Returning latest draft.\n")
    print("=== FINAL STORY (BEST EFFORT) ===\n")
    print(current)
    print("\n=== SCORES ===")
    print(json.dumps(report, indent=2))
    return 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Children's Story Generator with LLM Judge (Ages 5-10)")
    p.add_argument("--topic", required=True, help="Story topic or premise")
    p.add_argument("--age", type=int, default=7, help="Target age (5-10)")
    p.add_argument("--style", default="bedtime, gentle", help="Style or vibe (e.g., 'bedtime, gentle')")
    p.add_argument("--moral", default="kindness", help="One-sentence moral to end with")
    p.add_argument("--max-loops", type=int, default=2, help="Max revision loops (keeps it lean)")
    p.add_argument("--threshold", type=float, default=4.2, help="Required overall score (1-5 scale)")
    p.add_argument("--verbose", action="store_true", help="Verbose logs (scores, decisions)")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    try:
        sys.exit(
            run(
                topic=args.topic,
                age=args.age,
                style=args.style,
                moral=args.moral,
                max_loops=args.max_loops,
                threshold=args.threshold,
                verbose=args.verbose,
            )
        )
    except Exception as e:
        print("\n" + "❌ " * 20)
        print(f"ERROR: {e}")
        print("❌ " * 20 + "\n")
        sys.exit(1)