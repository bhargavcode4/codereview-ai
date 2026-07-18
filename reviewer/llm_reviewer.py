import json
import re

from anthropic import Anthropic

from . import config

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = """You are a senior software engineer performing a pull request code review.

You will be given the unified diff for one file, and optionally relevant excerpts from the
project's style guide / past reviews for grounding.

Review ONLY the added/changed lines (lines starting with "+" in the diff, ignoring the "+++"
file header). Flag real issues: bugs, security problems, and clear style-guide violations.
Do not invent nitpicks. If the diff has no issues, return an empty array.

Respond with ONLY a JSON array (no prose, no markdown fences). Each element:
{
  "line": <int, the new-file line number nearest the issue, based on the diff hunk headers>,
  "severity": "high" | "medium" | "low",
  "comment": "<concise, actionable comment, 1-3 sentences>"
}
"""


def _extract_json_array(text: str):
    text = text.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def review_file_diff(filename: str, patch: str, style_context: str = "") -> list:
    user_prompt = f"File: {filename}\n\n"
    if style_context:
        user_prompt += f"Relevant style guide context:\n{style_context}\n\n"
    user_prompt += f"Diff:\n{patch[:config.MAX_DIFF_CHARS_PER_FILE]}"

    response = _get_client().messages.create(
        model=config.REVIEW_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    issues = _extract_json_array(text)
    for issue in issues:
        issue["file"] = filename
    return issues
