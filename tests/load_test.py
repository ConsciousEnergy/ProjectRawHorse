"""
Lightweight load test for Project RawHorse API.
Uses concurrent.futures for parallel requests — no extra dependencies.

Usage:
    python load_test.py [--base-url http://localhost:8000] [--concurrency 10] [--duration 60]
"""
import argparse
import time
import statistics
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINTS = [
    "/api/health",
    "/api/data/stats",
    "/api/data/entities?limit=20",
    "/api/data/money-flows?limit=20",
    "/api/analysis/financial/flows",
    "/api/analysis/timeline",
    "/api/timeline/events?page_size=10",
    "/api/timeline/buckets?bucket_size=decade",
]


def make_request(base_url: str, path: str) -> dict:
    url = f"{base_url}{path}"
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception:
        status = 0
    duration_ms = round((time.time() - start) * 1000, 1)
    return {"path": path, "status": status, "duration_ms": duration_ms}


def run_load_test(base_url: str, concurrency: int, duration_sec: int):
    print(f"Load test: {base_url} | concurrency={concurrency} | duration={duration_sec}s")
    print("-" * 60)

    results = []
    start_time = time.time()
    endpoint_idx = 0

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {}
        while time.time() - start_time < duration_sec:
            path = ENDPOINTS[endpoint_idx % len(ENDPOINTS)]
            endpoint_idx += 1
            future = pool.submit(make_request, base_url, path)
            futures[future] = path

            if len(futures) >= concurrency * 2:
                done = []
                for f in as_completed(futures, timeout=15):
                    results.append(f.result())
                    done.append(f)
                for f in done:
                    del futures[f]

        for f in as_completed(futures, timeout=15):
            results.append(f.result())

    elapsed = round(time.time() - start_time, 1)
    durations = [r["duration_ms"] for r in results]
    errors = [r for r in results if r["status"] != 200]
    error_rate = len(errors) / max(len(results), 1) * 100

    print(f"\nResults ({len(results)} requests in {elapsed}s):")
    print(f"  Throughput: {len(results) / elapsed:.1f} req/s")
    print(f"  p50 latency: {statistics.median(durations):.0f}ms")
    print(f"  p95 latency: {sorted(durations)[int(len(durations) * 0.95)]:.0f}ms")
    print(f"  p99 latency: {sorted(durations)[int(len(durations) * 0.99)]:.0f}ms")
    print(f"  Max latency: {max(durations):.0f}ms")
    print(f"  Error rate: {error_rate:.1f}%")

    if error_rate > 2:
        print("\n  FAIL: Error rate exceeds 2% SLO")
    p95 = sorted(durations)[int(len(durations) * 0.95)]
    if p95 > 500:
        print(f"\n  WARN: p95 latency {p95:.0f}ms exceeds 500ms target")
    else:
        print("\n  PASS: All SLOs met")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test Project RawHorse API")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--duration", type=int, default=60)
    args = parser.parse_args()
    run_load_test(args.base_url, args.concurrency, args.duration)
