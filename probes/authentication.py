def check_unauthenticated(session, endpoint):
    """Check an endpoint with no Authorization header."""
    try:
        response = session.request(
            endpoint.get("method", "GET"),
            endpoint["url"],
            timeout=5,
        )
        success_with_data = 200 <= response.status_code < 300 and bool(response.text.strip())
        if endpoint.get("auth_required", False) and success_with_data:
            verdict = "FAIL"
            detail = "Protected endpoint returned a successful response without a token."
        elif endpoint.get("auth_required", False) and response.status_code in (401, 403):
            verdict = "PASS"
            detail = f"Protected endpoint rejected the unauthenticated request ({response.status_code})."
        elif not endpoint.get("auth_required", False) and success_with_data:
            verdict = "PASS"
            detail = "Endpoint is configured as public and returned a successful response."
        else:
            verdict = "INCONCLUSIVE"
            detail = f"Unexpected response for this endpoint configuration: HTTP {response.status_code}."
        return {"verdict": verdict, "status": response.status_code, "evidence": detail}
    except Exception as exc:
        return {"verdict": "INCONCLUSIVE", "status": None, "evidence": f"Request error: {exc}"}
