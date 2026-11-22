"""Local-only training API for APIGuard. Do not expose this intentionally vulnerable lab."""
from collections import defaultdict, deque
from time import time
from flask import Flask, jsonify, render_template
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

TOKENS = {
    "token-user-a": {"id": 1, "name": "User A"},
    "token-user-b": {"id": 2, "name": "User B"},
}
PRIVATE_RECORDS = {
    1: {"id": 1, "owner": "User A", "note": "Private sample record belonging to User A"},
    2: {"id": 2, "owner": "User B", "note": "Private sample record belonging to User B"},
}
REQUEST_TIMES = defaultdict(deque)

def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return TOKENS.get(auth.removeprefix("Bearer ").strip())

def require_user():
    user = current_user()
    if user is None:
        abort(401)
    return user

def limited(key, max_requests=5, window_seconds=10):
    now = time()
    q = REQUEST_TIMES[key]
    while q and now - q[0] > window_seconds:
        q.popleft()
    if len(q) >= max_requests:
        return True
    q.append(now)
    return False

@app.get("/api/public")
def public_endpoint():
    return jsonify(message="This endpoint is public", visibility="public")

@app.get("/api/secure/profile/<int:user_id>")
def secure_profile(user_id):
    user = require_user()
    if user["id"] != user_id:
        return jsonify(error="Forbidden"), 403
    return jsonify(PRIVATE_RECORDS[user_id])

# Deliberately vulnerable training endpoint: no authentication check.
@app.get("/api/lab/no-auth/profile/<int:user_id>")
def lab_no_auth_profile(user_id):
    record = PRIVATE_RECORDS.get(user_id)
    if not record:
        return jsonify(error="Not found"), 404
    return jsonify(record)

# Deliberately vulnerable training endpoint: authenticates, but does not check ownership.
@app.get("/api/lab/bola/profile/<int:user_id>")
def lab_bola_profile(user_id):
    require_user()
    record = PRIVATE_RECORDS.get(user_id)
    if not record:
        return jsonify(error="Not found"), 404
    return jsonify(record)

@app.get("/api/lab/limited/ping")
def lab_limited_ping():
    user = require_user()
    key = f'{user["id"]}:{request.path}'
    if limited(key):
        return jsonify(error="Too many requests"), 429
    return jsonify(message="pong")
@app.route("/")
def dashboard():
    return render_template("index.html")

@app.get("/api/lab/unlimited/ping")
def lab_unlimited_ping():
    require_user()
    return jsonify(message="pong")

# Simulated error-leak endpoint. It returns fake training text, not a real stack trace.
@app.get("/api/lab/error-leak")
def lab_error_leak():
    return jsonify(error="DatabaseError: simulated training failure at /srv/demo/db.py\nTraceback (simulated)"), 500

@app.get("/api/lab/safe-error")
def lab_safe_error():
    return jsonify(error="Something went wrong. Please try again later."), 500

if __name__ == "__main__":
    # Localhost binding keeps this deliberately vulnerable training app on this computer.
    app.run(host="127.0.0.1", port=5000, debug=False)
