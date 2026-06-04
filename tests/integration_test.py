#!/usr/bin/env python3
"""
Integration test runner for demo-azure-5xx-app.

Run locally:
  python3 tests/integration_test.py <web_app_url>

Also callable by the Aziron agent via execute_local_command:
  python3 /path/to/integration_test.py https://<app>.azurewebsites.net
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error


def run_test(name, url, method="GET", body=None, expected_status=200):
    start = time.time()
    try:
        data = json.dumps(body).encode() if body else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            latency_ms = int((time.time() - start) * 1000)
            resp_body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        latency_ms = int((time.time() - start) * 1000)
        status = e.code
        resp_body = e.read().decode("utf-8")
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            "name": name,
            "url": url,
            "status": "error",
            "error": str(e),
            "latency_ms": latency_ms,
        }

    passed = status == expected_status
    return {
        "name": name,
        "url": url,
        "http_code": status,
        "expected_code": expected_status,
        "latency_ms": latency_ms,
        "status": "pass" if passed else "fail",
        "response_preview": resp_body[:200],
    }


def run_all(base_url):
    base_url = base_url.rstrip("/")
    results = [
        run_test("health_check",    f"{base_url}/health",        expected_status=200),
        run_test("products_list",   f"{base_url}/api/products",  expected_status=200),
        run_test(
            "checkout_order",
            f"{base_url}/api/checkout",
            method="POST",
            body={"item_id": 1, "qty": 1},
            expected_status=200,
        ),
    ]
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = len(results) - passed
    return {
        "total":   len(results),
        "passed":  passed,
        "failed":  failed,
        "overall": "pass" if failed == 0 else "fail",
        "tests":   results,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        base = os.environ.get("WEB_APP_URL", "")
        if not base:
            print(json.dumps({"error": "Usage: integration_test.py <web_app_url>"}))
            sys.exit(1)
    else:
        base = sys.argv[1]

    results = run_all(base)
    print(json.dumps(results, indent=2))
    sys.exit(0 if results["overall"] == "pass" else 1)
