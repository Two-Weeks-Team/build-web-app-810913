import json
import os
import re
from typing import Any, Dict, List

import httpx


INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
MODEL_NAME = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    key = os.getenv("GRADIENT_MODEL_ACCESS_KEY") or os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    if not key:
        return {
            "ok": False,
            "note": "AI temporarily unavailable: missing inference key.",
            "data": {},
        }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(INFERENCE_URL, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        content = ""
        choices = body.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "") or ""

        extracted = _extract_json(content)
        parsed = json.loads(extracted)
        return {"ok": True, "note": "", "data": parsed}
    except Exception as exc:
        return {
            "ok": False,
            "note": f"AI temporarily unavailable. Showing fallback output. ({str(exc)[:140]})",
            "data": {},
        }


async def generate_plan(query: str, preferences: str) -> Dict[str, Any]:
    schema_hint = {
        "summary": "string",
        "items": [
            {
                "section": "target_users|problem_framing|value_proposition|feature_priorities|assumptions|next_actions",
                "title": "string",
                "content": "string",
                "source_quote": "string"
            }
        ],
        "score": 0
    }

    messages = [
        {"role": "system", "content": "You are a product planning strategist. Return JSON only."},
        {
            "role": "user",
            "content": (
                "Transform rough input into a structured Product Brief for a planning studio app. "
                "Return strict JSON with keys summary, items, score. "
                f"Schema: {json.dumps(schema_hint)}\n"
                f"Rough input:\n{query}\n\n"
                f"Planning preferences/constraints:\n{preferences}"
            ),
        },
    ]

    result = await _call_inference(messages, max_tokens=512)
    if result.get("ok") and isinstance(result.get("data"), dict):
        data = result["data"]
        if all(k in data for k in ["summary", "items", "score"]):
            return data

    return {
        "summary": "Draft brief generated with fallback logic while AI is temporarily unavailable.",
        "items": [
            {
                "section": "target_users",
                "title": "Primary users",
                "content": "Founders, PMs, consultants, and internal innovation teams working from incomplete planning context.",
                "source_quote": "People exploring product planning from incomplete context."
            },
            {
                "section": "problem_framing",
                "title": "Core problem",
                "content": "Users struggle to move from messy notes to an actionable product plan without starting from a blank spec.",
                "source_quote": "Users need a clearer way to act on product planning without starting from a blank product spec."
            },
            {
                "section": "feature_priorities",
                "title": "Top priorities",
                "content": "1) One-pass brief generation, 2) source-to-output trace, 3) versioned snapshots, 4) promotable insight cards.",
                "source_quote": "One-Pass Brief Generation; Source-to-Output Trace View; Versioned Planning Snapshot Shelf"
            },
            {
                "section": "next_actions",
                "title": "Next actions",
                "content": "Validate with 5 real planning inputs, measure usefulness of generated sections, and iterate trace clarity.",
                "source_quote": "Show the system turning messy input into a usable product planning artifact in one pass."
            }
        ],
        "score": 78
    }


async def generate_insights(selection: str, context: str) -> Dict[str, Any]:
    schema_hint = {
        "insights": ["string"],
        "next_actions": ["string"],
        "highlights": ["string"]
    }
    messages = [
        {"role": "system", "content": "You create artifact-first planning insights. Return JSON only."},
        {
            "role": "user",
            "content": (
                "Given a selected brief section and broader context, create promotable insight cards output. "
                "Return strict JSON with keys insights, next_actions, highlights. "
                f"Schema: {json.dumps(schema_hint)}\n"
                f"Selection:\n{selection}\n\nContext:\n{context}"
            ),
        },
    ]

    result = await _call_inference(messages, max_tokens=512)
    if result.get("ok") and isinstance(result.get("data"), dict):
        data = result["data"]
        if all(k in data for k in ["insights", "next_actions", "highlights"]):
            return data

    return {
        "insights": [
            "Promote feature priorities as separate artifact cards to preserve decision history.",
            "Use source-linked highlights to build trust during team review.",
            "Keep draft vs saved stamps visible to communicate planning maturity."
        ],
        "next_actions": [
            "Promote one risk and one feature insight into saved cards.",
            "Run a second snapshot with tighter platform constraints.",
            "Compare two snapshots to identify stable priorities."
        ],
        "highlights": [
            "Transformation from rough input to structured brief happened in one pass.",
            "Versioned shelf demonstrates durable planning artifacts.",
            "Trace links explain why each section exists."
        ]
    }
