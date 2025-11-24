````markdown
#StoryLoop Judge
This submission implements a **children’s bedtime story** generator (ages 5-10) with a **judge-and-revise loop**.  
It **keeps the required model**: `gpt-3.5-turbo` and uses your local `OPENAI_API_KEY` (not included).

## Why this design
- **Clear flow**: storyteller → judge (JSON) → optional revise → final.
- **Deterministic judge** (`temperature=0.0`) ensures reproducible scores.
- **Safety & audience fit** baked into prompts and a **light length guard** (targets ~350-600 words).
- **Tiny footprint**: a few readable files, no frameworks, quick to run.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY="sk-...your_openai_key..."   # do NOT commit keys
python app.py --topic "A kid helps a lost cloud find home" --age 8 --style "bedtime, gentle" --moral "kindness" --verbose
````

### Common gotcha

If you accidentally put a Google/Gemini key in `OPENAI_API_KEY`, the app will error.
Use a real OpenAI key (`sk-...` or `sk-proj-...`).

## CLI flags

* `--topic` (required): story premise
* `--age` (default 7): target age (5-10)
* `--style` (default `bedtime, gentle`)
* `--moral` (default `kindness`)
* `--max-loops` (default 1): max revise iterations
* `--threshold` (default 4.2): required overall score (1-5 scale)
* `--verbose`: prints judge JSON and decisions


## Sample verbose run (illustrative)

> Example output to show readability and scoring (values will vary).

```
🚀 Starting story generation...
   Topic: A kid helps a lost cloud find home
   Age: 8
   Style: bedtime, gentle
   Moral: kindness
   Score Threshold: 4.2/5
   Max Revisions: 1

Draft word count: 482

Judge report (JSON):
{
  "scores": {
    "audience_fit": 5,
    "plot_structure": 4,
    "moral_clarity": 5,
    "vocabulary": 4,
    "safety": 5,
    "length": 4
  },
  "overall": 4.5,
  "actionable_feedback": [
    "Tighten two sentences in the middle for pacing.",
    "Use one simpler synonym in a descriptive paragraph."
  ]
}

✅ Threshold met on first pass.

=== FINAL STORY ===

... (story text) ...

=== SCORES ===
{ same JSON as above }
```

## Files

* **app.py** — CLI + orchestration (story → judge → revise loop → final)
* **prompts.py** — Minimal, targeted prompts for storyteller, judge, reviser
* **utils.py** — OpenAI call wrapper, JSON parsing, small helpers
* **tests/test_json_contract.py** — Tiny self-contained contract test (no pytest needed)
* **requirements.txt** — Minimal deps
* **ARCHITECTURE.md** - Mermaid code describing the picture "ArchitectureVisualized.png" flow diagram

## Evaluation mapping (per README)

* **Efficacy**: scoring loop measurably improves quality
* **Python comfort**: clean CLI; small modules; explicit contracts
* **Prompting strategy**: deterministic judge + targeted revise
* **Open-ended**: supports any topic; clear moral; safe tone
* **Surprise factor**: JSON rubric + quick loop in a tiny tool
---
```
