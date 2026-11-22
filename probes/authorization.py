def check_cross_account(session, endpoint, token_user_b):
    """Try User B's token against the configured User A object URL."""
    target = endpoint.get("cross_account_url")
    if not target:
        return {"verdict": "N/A", "status": None, "evidence": "No cross-account test URL configured."}
    try:
        response = session.get(
            target,
            headers={"Authorization": f"Bearer {token_user_b}"},
            timeout=5,
        )
        if response.status_code in (401, 403, 404):
            verdict = "PASS"
            detail = f"Cross-account access was denied (HTTP {response.status_code})."
        elif 200 <= response.status_code < 300:
            verdict = "FAIL"
            detail = "User B received a successful response for User A's object; possible BOLA."
        else:
            verdict = "INCONCLUSIVE"
            detail = f"Unexpected cross-account response: HTTP {response.status_code}."
        return {"verdict": verdict, "status": response.status_code, "evidence": detail}
    except Exception as exc:
        return {"verdict": "INCONCLUSIVE", "status": None, "evidence": f"Request error: {exc}"}
