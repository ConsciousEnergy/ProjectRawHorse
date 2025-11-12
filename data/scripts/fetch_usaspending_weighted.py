
import os, json, time, math, argparse, requests, datetime, csv

def load_keywords(path):
    return [line.strip() for line in open(path) if line.strip()] if os.path.exists(path) else []

def load_weights(path):
    if not os.path.exists(path): return {}
    w = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            k = (row.get("keyword") or "").strip().lower()
            try:
                w[k] = float(row.get("weight"))
            except Exception:
                w[k] = 1.0
    return w

def ensure(p): os.makedirs(p, exist_ok=True)

def search_awards(base, keyword, start=None, end=None, page=1, limit=100):
    url = f"{base}/api/v2/search/spending_by_award/"
    payload = {
        "filters": {
            "keywords": [keyword],
        },
        "fields": ["Award ID","Recipient Name","Recipient UEI","Recipient DUNS","Description","Action Date","Awarding Agency","Funding Agency","PIID"],
        "page": page,
        "limit": limit,
        "sort": "Action Date",
        "order": "desc"
    }
    if start or end:
        payload["filters"]["time_period"] = [{
            "start_date": start or "2000-01-01",
            "end_date": end or datetime.date.today().isoformat()
        }]
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint_base", default="https://api.usaspending.gov")
    ap.add_argument("--keywords_file", default="lookups/keywords_deduped.txt")
    ap.add_argument("--weights_file", default="lookups/keyword_weights.csv")
    ap.add_argument("--out_dir", default="external/usaspending_weighted")
    ap.add_argument("--min_action_date", default="2019-01-01")
    ap.add_argument("--max_action_date", default=None)
    ap.add_argument("--base_pages", type=int, default=2)
    ap.add_argument("--max_pages", type=int, default=8)
    args = ap.parse_args()

    ensure(args.out_dir)
    kws = load_keywords(args.keywords_file)
    wmap = load_weights(args.weights_file)

    meta = []
    for kw in kws:
        w = wmap.get(kw.lower(), 1.0)
        pages = min(args.max_pages, max(1, math.ceil(args.base_pages * w)))
        for p in range(1, pages+1):
            data = search_awards(args.endpoint_base, kw, args.min_action_date, args.max_action_date, page=p)
            fn = f"usaspending_{kw.replace(' ','_')}_p{p}.json"
            fp = os.path.join(args.out_dir, fn)
            with open(fp, "w") as f:
                json.dump(data, f, indent=2)
            meta.append({"keyword": kw, "weight": w, "page": p, "file": fp, "count": len(data.get("results", []))})
            time.sleep(0.6)
    with open(os.path.join(args.out_dir, "_manifest.json"), "w") as f:
        json.dump({"generated": datetime.datetime.utcnow().isoformat(), "meta": meta}, f, indent=2)

if __name__ == "__main__":
    main()
