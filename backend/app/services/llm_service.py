import json
import re
import unicodedata
from openai import OpenAI
import google.generativeai as genai
import anthropic
from app.models import EngineConfig, ListingResult

# Global constants
SMART_MAP = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u00A0": " ",
}

def to_utf8_clean(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", str(s))
    for k, v in SMART_MAP.items():
        s = s.replace(k, v)
    return s.encode("utf-8", "ignore").decode("utf-8")

def coerce_json(s: str):
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        m = re.search(r"\{.*\}", s, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass
    return None

def ensure_listing_shape(obj: dict) -> ListingResult:
    return ListingResult(
        new_title=(obj.get("new_title") or "").strip(),
        new_description=(obj.get("new_description") or "").strip(),
        keywords_short=obj.get("keywords_short") or obj.get("short_tail_keywords") or [],
        keywords_mid=obj.get("keywords_mid") or obj.get("mid_tail_keywords") or [],
        keywords_long=obj.get("keywords_long") or obj.get("long_tail_keywords") or [],
    )

def openai_chat_completion(api_key, model, messages, temperature: float = None) -> str:
    client = OpenAI(api_key=api_key, timeout=120.0)  # 2 minute timeout per request
    
    # GPT-5 models only support temperature=1
    if temperature is None:
        if model.startswith('gpt-5'):
            temperature = 1.0
        else:
            temperature = 0.2
    
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    return resp.choices[0].message.content or ""


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_REFERER = "https://atelier-seo.local"
OPENROUTER_TITLE = "Atelier SEO Optimizer"


def openrouter_chat_completion(api_key: str, model: str, messages, temperature: float = None) -> str:
    """Route a chat completion through OpenRouter.

    OpenRouter exposes an OpenAI-compatible API, so we reuse the OpenAI SDK
    with a custom base_url. Model id is of form "<provider>/<model>" e.g.
    "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-2.5-pro".
    """
    if not api_key:
        raise RuntimeError("OpenRouter API key is required.")
    if not model:
        raise RuntimeError("OpenRouter model id is required (e.g. 'openai/gpt-4o').")

    if temperature is None:
        temperature = 0.2

    client = OpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": OPENROUTER_REFERER,
            "X-Title": OPENROUTER_TITLE,
        },
        timeout=120.0,
    )
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    return resp.choices[0].message.content or ""

def single_contract():
    return """
Return ONLY a JSON object with keys:
- new_title (string, <=200 chars)
- new_description (string, HTML, <=2000 chars)
- keywords_short (array of strings)
- keywords_mid (array of strings)
- keywords_long (array of strings)
No extra text or markdown.
"""

def run_l1_l2_logic(
    prev_title: str,
    prev_desc: str,
    product_link: str,
    sp_l1: str,
    sp_l2: str,
    config: EngineConfig
):
    # Build user prompts once
    u1 = f"""
You are given an existing Amazon listing fragment.

Inputs:
- Previous Title: {prev_title or '(empty)'}
- Previous Description: {prev_desc or '(empty)'}
- Product Link: {product_link or '(none)'}

TASK: Using the Level-1 system prompt’s framework, produce an improved listing.
{single_contract()}
""".strip()

    u2_base = f"""
Refine a JSON listing produced by another model using the Level-2 system prompt rules.
- Keep the exact JSON structure (new_title, new_description, keywords_short, keywords_mid, keywords_long).
- Title <= 200 chars; Description is HTML <= 2000 chars; avoid keyword stuffing; ensure clarity & compliance.
Return ONLY the JSON.

Context:
Previous Title: {prev_title or '(empty)'}
Previous Description: {prev_desc or '(empty)'}
Product Link: {product_link or '(none)'}
""".strip()

    # ============================================================
    # OPENROUTER MODE — single key, any L1/L2 model
    # ============================================================
    if (config.mode or "").lower() == "openrouter":
        if not config.openrouter_key:
            raise RuntimeError("OpenRouter API key is required.")
        if not config.l1_model:
            raise RuntimeError("OpenRouter L1 model is required.")

        raw1 = to_utf8_clean(
            openrouter_chat_completion(
                api_key=config.openrouter_key,
                model=config.l1_model,
                messages=[
                    {"role": "system", "content": to_utf8_clean(sp_l1)},
                    {"role": "user", "content": to_utf8_clean(u1)},
                ],
                temperature=config.l1_temperature,
            ).strip()
        )
        p1 = coerce_json(raw1)
        if not p1:
            raise RuntimeError("L1 (OpenRouter) returned non-JSON.")
        draft = ensure_listing_shape(p1)

        l2 = (config.l2_model or "").strip().lower()
        if not config.l2_model or l2 in ("", "none"):
            return draft, draft

        draft_dict = draft.dict()
        raw2 = to_utf8_clean(
            openrouter_chat_completion(
                api_key=config.openrouter_key,
                model=config.l2_model,
                messages=[
                    {"role": "system", "content": to_utf8_clean(sp_l2)},
                    {
                        "role": "user",
                        "content": to_utf8_clean(u2_base)
                        + "\n\nDraft JSON:\n"
                        + json.dumps(draft_dict, ensure_ascii=False),
                    },
                ],
                temperature=config.l2_temperature,
            ).strip()
        )
        p2 = coerce_json(raw2)
        return draft, (ensure_listing_shape(p2) if p2 else draft)

    # ============================================================
    # CLASSIC MODE — legacy per-provider flow
    # ============================================================
    if not config.openai_key:
        raise RuntimeError("OpenAI API key is required for classic mode.")
    if not config.openai_model:
        raise RuntimeError("OpenAI model is required for classic mode.")

    raw1 = to_utf8_clean(
        openai_chat_completion(
            api_key=config.openai_key,
            model=config.openai_model,
            messages=[
                {"role": "system", "content": to_utf8_clean(sp_l1)},
                {"role": "user", "content": to_utf8_clean(u1)},
            ],
        ).strip()
    )
    p1 = coerce_json(raw1)
    if not p1:
        raise RuntimeError("L1 returned non-JSON.")
    draft = ensure_listing_shape(p1)

    if config.second_engine == "None":
        return draft, draft

    u2 = u2_base
    draft_dict = draft.dict()

    if config.second_engine == "OpenAI (second pass)":
        raw2 = to_utf8_clean(
            openai_chat_completion(
                api_key=config.openai2_key or config.openai_key,
                model=config.openai2_model or config.openai_model,
                messages=[
                    {"role": "system", "content": to_utf8_clean(sp_l2)},
                    {
                        "role": "user",
                        "content": to_utf8_clean(u2)
                        + "\n\nDraft JSON:\n"
                        + json.dumps(draft_dict, ensure_ascii=False),
                    },
                ],
            ).strip()
        )
        p2 = coerce_json(raw2)
        return draft, ensure_listing_shape(p2) if p2 else draft

    if config.second_engine == "Gemini (Google)":
        if not config.gemini_key:
             raise RuntimeError("Gemini API key required.")
        genai.configure(api_key=config.gemini_key)
        model = genai.GenerativeModel(config.gemini_model)
        prompt = (
            to_utf8_clean(sp_l2)
            + "\n\n"
            + to_utf8_clean(u2)
            + "\n\nDraft JSON:\n"
            + json.dumps(draft_dict, ensure_ascii=False)
        )
        resp = model.generate_content(prompt)
        text = to_utf8_clean((resp.text or "").strip())
        p2 = coerce_json(text)
        return draft, ensure_listing_shape(p2) if p2 else draft

    if config.second_engine == "Claude (Anthropic)":
        if not config.anthropic_key:
            raise RuntimeError("Anthropic API key required.")
        aclient = anthropic.Anthropic(api_key=config.anthropic_key)
        msg = aclient.messages.create(
            model=config.claude_model,
            max_tokens=2000,
            temperature=0.2,
            system=to_utf8_clean(sp_l2),
            messages=[
                {
                    "role": "user",
                    "content": to_utf8_clean(u2)
                    + "\n\nDraft JSON:\n"
                    + json.dumps(draft_dict, ensure_ascii=False),
                }
            ],
        )
        blocks = getattr(msg, "content", []) or []
        parts = []
        for b in blocks:
            if getattr(b, "type", None) == "text":
                parts.append(getattr(b, "text", "") or "")
        text = to_utf8_clean("".join(parts))
        p2 = coerce_json(text)
        return draft, ensure_listing_shape(p2) if p2 else draft

    if config.second_engine == "OpenRouter":
        # Allow OpenRouter as second-pass while keeping L1 on classic OpenAI
        if not config.openrouter_key:
            raise RuntimeError("OpenRouter API key required for second pass.")
        if not config.l2_model:
            raise RuntimeError("OpenRouter L2 model required.")
        raw2 = to_utf8_clean(
            openrouter_chat_completion(
                api_key=config.openrouter_key,
                model=config.l2_model,
                messages=[
                    {"role": "system", "content": to_utf8_clean(sp_l2)},
                    {
                        "role": "user",
                        "content": to_utf8_clean(u2)
                        + "\n\nDraft JSON:\n"
                        + json.dumps(draft_dict, ensure_ascii=False),
                    },
                ],
                temperature=config.l2_temperature,
            ).strip()
        )
        p2 = coerce_json(raw2)
        return draft, ensure_listing_shape(p2) if p2 else draft

    return draft, draft
