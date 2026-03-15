"""
Simulation API contract smoke test.

Usage:
  python tests/simulation_contract_check.py --base-url http://127.0.0.1:8000
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def require_keys(payload: dict, required: list[str], label: str):
    missing = [k for k in required if k not in payload]
    if missing:
        raise RuntimeError(f"{label} missing keys: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    timeline_url = f"{base}/api/simulation/timeline?{urllib.parse.urlencode({'page': 1, 'page_size': 50, 'confidence_min': 0.5, 'group_by': 'year'})}"
    entities_url = f"{base}/api/simulation/entities?{urllib.parse.urlencode({'page': 1, 'page_size': 25})}"
    flows_url = f"{base}/api/simulation/flows?{urllib.parse.urlencode({'page': 1, 'page_size': 25})}"

    timeline = get_json(timeline_url)
    entities = get_json(entities_url)
    flows = get_json(flows_url)

    require_keys(
        timeline,
        ["time_range", "events", "money_flows", "entities", "connections", "meta"],
        "simulation/timeline",
    )
    require_keys(timeline["meta"], ["total_events", "total_flows", "page", "page_size", "truncated"], "simulation/timeline.meta")
    require_keys(entities, ["total", "page", "page_size", "items"], "simulation/entities")
    require_keys(flows, ["total", "page", "page_size", "items"], "simulation/flows")

    print("Simulation contract check passed.")
    print(f"- timeline events: {len(timeline['events'])}")
    print(f"- timeline flows: {len(timeline['money_flows'])}")
    print(f"- entities items: {len(entities['items'])}")
    print(f"- flows items: {len(flows['items'])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Simulation contract check failed: {exc}")
        raise SystemExit(1)
