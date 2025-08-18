import os, google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a content safety classifier.
Label input as one of: toxic, spam, harassment, safe.
Return JSON with keys: classification, confidence (0-1), reasoning (1-2 lines).
"""

def classify_text(text: str) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"{SYSTEM_PROMPT}\nInput:\n{text}"
    resp = model.generate_content(prompt)
    # Best-effort parse; keep raw too
    import json
    try:
        data = json.loads(resp.text)
    except Exception:
        # fallback heuristic: map keywords (super simple)
        lower = text.lower()
        label = "safe"
        if any(w in lower for w in ["kill","hate","idiot","stupid"]): label = "toxic"
        if any(w in lower for w in ["buy now","click here","free $$$"]): label = "spam"
        if any(w in lower for w in ["harass","bully","threat"]): label = "harassment"
        data = {"classification": label, "confidence": 0.55, "reasoning": "Heuristic fallback."}
    data["_raw"] = {"model": "gemini-1.5-flash", "text": resp.text}
    return data

def classify_image_bytes(image_bytes: bytes, mime_type: str) -> dict:
    """
    Classify image bytes using Gemini.
    Mime type is read from the uploaded file (no need for user to provide).
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    parts = [{"mime_type": mime_type, "data": image_bytes}]
    prompt = SYSTEM_PROMPT + "\nInput: (image attached)"
    resp = model.generate_content([prompt, parts])

    import json
    try:
        data = json.loads(resp.text)
    except Exception:
        data = {
            "classification": "safe",
            "confidence": 0.5,
            "reasoning": "Default fallback.",
        }

    data["_raw"] = {"model": "gemini-1.5-flash", "text": resp.text}
    return data

