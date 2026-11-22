import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

from probes.authentication import check_unauthenticated
from probes.authorization import check_cross_account
from probes.rate_limit import check_rate_limit
from probes.error_check import check_error_leak

def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def run_scan(endpoints, tokens):
    results = []
    with requests.Session() as session:
        for endpoint in endpoints:
            item = {
                "endpoint": endpoint["name"],
                "url": endpoint["url"],
                "authentication": check_unauthenticated(session, endpoint),
                "authorization": check_cross_account(session, endpoint, tokens["user_b"]),
                "rate_limit": check_rate_limit(session, endpoint, tokens["user_a"]),
                "error_leak": check_error_leak(session, endpoint),
            }
            results.append(item)
    return results

def write_text_report(results, output_path):
    lines = [
        "APIGuard Security Assessment Report",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Scope: local training API at 127.0.0.1 only",
        "=" * 72,
    ]
    for item in results:
        lines.extend([
            "",
            f"Endpoint: {item['endpoint']}",
            f"URL: {item['url']}",
        ])
        for check_name in ("authentication", "authorization", "rate_limit", "error_leak"):
            result = item[check_name]
            lines.append(f"  {check_name}: {result['verdict']} (HTTP {result['status']})")
            lines.append(f"    Evidence: {result['evidence']}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="APIGuard: local REST API security tester")
    parser.add_argument("--endpoints", default="config/endpoints.json", help="Path to endpoint JSON")
    parser.add_argument("--tokens", default="config/tokens.json", help="Path to lab token JSON")
    parser.add_argument("--report", default="reports/report.txt", help="Text report output path")
    parser.add_argument("--json-report", default="reports/report.json", help="JSON report output path")
    args = parser.parse_args()

    endpoints = load_json(args.endpoints)
    tokens = load_json(args.tokens)
    if not isinstance(endpoints, list) or not all(k in tokens for k in ("user_a", "user_b")):
        raise SystemExit("Invalid configuration: endpoints must be a list and tokens must contain user_a/user_b.")

    results = run_scan(endpoints, tokens)
    write_text_report(results, args.report)
    Path(args.json_report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_report).write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\nAPIGuard scan finished.")
    print(f"Text report: {args.report}")
    print(f"JSON report: {args.json_report}")
    print("\nEndpoint summary:")
    for item in results:
        print(f"- {item['endpoint']}")
        for name in ("authentication", "authorization", "rate_limit", "error_leak"):
            result = item[name]
            if result["verdict"] != "N/A":
                print(f"    {name}: {result['verdict']}")

if __name__ == "__main__":
    main()
