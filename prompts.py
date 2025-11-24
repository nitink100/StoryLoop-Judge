from typing import List, Dict, Any

def build_storyteller_messages(topic: str, age: int, style: str, moral: str) -> List[Dict[str, str]]:
    system = (
        "You are an expert children's storyteller for ages 5-10. "
        "Write a safe, positive story with a clear beginning, middle, and end. "
        "Use simple, vivid vocabulary. "
        "Write a FULL narrative (no outlines or bullet points). "
        "Target 350-550 words; do NOT write fewer than 350 words. "
        "End with ONE sentence stating the moral."
    )
    user = (
        f"Write a story based on this request.\n"
        f"- Topic: {topic}\n"
        f"- Target age: {age}\n"
        f"- Style: {style}\n"
        f"- Moral to end with: {moral}\n\n"
        f"Constraints:\n"
        f"1) Avoid violence or scary imagery.\n"
        f"2) Keep vocabulary age-appropriate.\n"
        f"3) Close with a single-sentence moral.\n"
        f"4) Produce 350-550 words in full paragraphs.\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_judge_messages(story_text: str) -> List[Dict[str, str]]:
    system = (
        "You are a strict children's literature reviewer for ages 5-10. "
        "Return ONLY a JSON object with fields: scores, overall, actionable_feedback. "
        "scores is an object with keys: audience_fit, plot_structure, moral_clarity, vocabulary, safety, length. "
        "Each score is an integer 1-5. overall is 1-5. actionable_feedback is an array of 2-5 short strings. "
        "No commentary, no markdown, JSON only."
    )
    user = (
        "Evaluate the following story for ages 5-10 using the rubric.\n\n"
        "STORY:\n"
        f"{story_text}\n\n"
        "Return valid JSON only."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_revise_messages(story_text: str, feedback: Any, target_overall: float) -> List[Dict[str, str]]:
    system = (
        "You are a careful editor. Revise the story conservatively to address the listed issues. "
        "Preserve the plot and voice. "
        "Keep the story length between 350-550 words (do NOT shorten below 350 words). "
        "Maintain age-appropriate vocabulary, clear beginning-middle-end, and end with one-sentence moral. "
        "Write a FULL narrative in paragraphs; no outlines."
    )
    user = (
        f"Revise the story below. Address ONLY these issues to improve the score to at least {target_overall:.1f}/5:\n"
        f"{feedback}\n\n"
        f"STORY TO REVISE:\n{story_text}\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
