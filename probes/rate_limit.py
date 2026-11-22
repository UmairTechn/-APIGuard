def check_rate_limit(session, endpoint, token_user_a, count=20):
    """Send a small, fixed training burst and look for HTTP 429."""
    if not endpoint.get("rate_limit_test", False):
        return {"verdict": "N/A", "status": None, "evidence": "Rate-limit test not enabled for this endpoint."}
    statuses = []
    try:
        for _ in range(count):
            response = session.request(
                endpoint.get("method", "GET"),
                endpoint["url"],
                headers={"Authorization": f"Bearer {token_user_a}"},
                timeout=5,
            )
            statuses.append(response.status_code)
        throttled = 429 in statuses
        verdict = "PASS" if throttled else "FAIL"
        detail = f"{count} local lab requests sent; HTTP 429 observed: {throttled}; successful responses: {sum(200 <= s < 300 for s in statuses)}."
        return {"verdict": verdict, "status": 429 if throttled else (statuses[-1] if statuses else None), "evidence": detail}
    except Exception as exc:
        return {"verdict": "INCONCLUSIVE", "status": None, "evidence": f"Request error: {exc}"}
