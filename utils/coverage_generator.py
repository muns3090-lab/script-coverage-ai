"""Coverage generation via the Anthropic Claude API."""

import json
import re
from typing import Optional

import anthropic


SYSTEM_PROMPT = """You are a senior Hollywood development executive with 20+ years of experience \
at major studios including Warner Bros., Universal, and A24. You have read thousands of screenplays \
and your coverage is trusted by producers, agents, and studio heads to make acquisition and \
development decisions worth millions of dollars.

Your coverage is known for being:
- Analytically rigorous: you assess structure, character, dialogue, and marketability with precision
- Commercially savvy: you always consider budget, audience, and comparable titles
- Constructively honest: you identify genuine strengths and actionable weaknesses without being cruel
- Industry-standard: your reports follow the professional format used at major studios

When you read a screenplay, you respond ONLY with a valid JSON object — no preamble, no markdown \
code fences, no commentary outside the JSON. The JSON must be complete and correctly formatted."""


USER_PROMPT_TEMPLATE = """Please read the following screenplay and produce a full professional \
coverage report.

Return your analysis as a single JSON object with exactly this structure (no extra keys, \
no missing keys):

{{
  "title": "inferred or found title",
  "format": "Feature / Pilot / Short",
  "genre": "primary genre",
  "subgenre": "secondary genre or tone",
  "logline": "one sentence logline",
  "synopsis": "3-4 paragraph synopsis",
  "tone": "description of tone",
  "setting": "time and place",
  "protagonist": {{
    "name": "name",
    "description": "brief character description",
    "arc": "character arc summary"
  }},
  "supporting_characters": [
    {{"name": "name", "role": "role description"}}
  ],
  "themes": ["theme1", "theme2", "theme3"],
  "comparable_titles": ["title1 (year)", "title2 (year)"],
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "marketability": "assessment of commercial potential",
  "recommendation": "PASS or CONSIDER or RECOMMEND",
  "recommendation_reason": "2-3 sentence justification",
  "overall_score": 7,
  "analyst_notes": "additional notes for the development team"
}}

SCREENPLAY:
{screenplay_text}"""


def generate_coverage(screenplay_text: str, api_key: str) -> Optional[dict]:
    """
    Call the Claude API to generate structured script coverage.

    Args:
        screenplay_text: The full cleaned text of the screenplay.
        api_key: Anthropic API key.

    Returns:
        A dict matching the coverage JSON schema, or None if the call fails.

    Raises:
        Nothing — all exceptions are caught and returned as None.
    """
    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = USER_PROMPT_TEMPLATE.format(screenplay_text=screenplay_text)

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.AuthenticationError:
        return {"_error": "Invalid API key. Check your ANTHROPIC_API_KEY in .env."}
    except anthropic.RateLimitError:
        return {"_error": "Rate limit reached. Please wait a moment and try again."}
    except anthropic.APIStatusError as exc:
        if "credit balance" in str(exc).lower():
            return {"_error": (
                "CREDIT_ERROR: Your credit balance is too low and needs to be topped up. "
                "Please contact the app owner or follow the below steps:\n\n"
                "**Step 1 — Go to Anthropic Console**  \n"
                "👉 https://console.anthropic.com\n\n"
                "**Step 2 — Add Credits**  \n"
                "1. Click 'Settings' in the left sidebar  \n"
                "2. Click 'Billing'  \n"
                "3. Click 'Add Credits'  \n"
                "4. Add $5–10 to start — that's plenty for portfolio testing  \n"
                "   - Script coverage runs cost roughly $0.02–0.05 per screenplay with Claude Opus  \n"
                "   - $10 = ~200–500 test runs"
            )}
        return {"_error": f"API error {exc.status_code}: {exc.message}"}
    except Exception as exc:
        return {"_error": f"Unexpected error: {exc}"}

    raw = message.content[0].text
    return _parse_json_response(raw)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _parse_json_response(raw: str) -> Optional[dict]:
    """
    Parse a JSON object from the model's raw text response.

    Tries strict parsing first; falls back to extracting the first {...} block
    in case the model added any surrounding text despite instructions.
    """
    # 1. Strict parse — ideal path
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Extract the first balanced {...} block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 3. Give up — return the raw text under a special key so the caller
    #    can still display something meaningful
    return {"_error": "Could not parse JSON from model response.", "_raw": raw}
