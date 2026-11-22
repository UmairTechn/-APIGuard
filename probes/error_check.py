import re

PATTERNS = [
    re.compile(r"traceback", re.I),
    re.compile(r"database(error|exception)", re.I),
    re.compile(r"sql(error| syntax)", re.I),
    re.compile(r"(/[A-Za-z0-9_.-]+){2,}"),
    re.compile(r"\b(stack trace|internal server path)\b", re.I),
]

def check_error_leak(session, endpoint):
    """Inspect response text for common internal-error indicators."""
    try:
        response = session.request(endpoint.get("method", "GET"), endpoint["url"], timeout=5)
        matches = [pattern.pattern for pattern in PATTERNS if pattern.search(response.text)]
        if matches:
            verdict = "FAIL"
            detail = "Potential internal error details detected: " + ", ".join(matches)
        else:
            verdict = "PASS"
            detail = "No configured error-leak patterns detected in the response."
        return {"verdict": verdict, "status": response.status_code, "evidence": detail}
    except Exception as exc:
        return {"verdict": "INCONCLUSIVE", "status": None, "evidence": f"Request error: {exc}"}
