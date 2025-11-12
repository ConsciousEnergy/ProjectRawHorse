
import os, json, time, argparse, requests, datetime

def ensure(p): os.makedirs(p, exist_ok=True)

def get_toptier_map(base):
    url = f"{base}/api/v2/references/toptier_agencies/"
    r = requests.get(url, timeout=60); r.raise_for_status()
    mp = {}
    for it in r.json().get("results", []):
        nm = it.get("toptier_agency", {}).get("name") or it.get("name")
        code = it.get("toptier_agency", {}).get("toptier_code") or it.get("toptier_code")
        if nm and code:
            mp[nm.lower()] = code
    return mp

def search_awards(base, keyword, toptier_code=None, start=None, end=None, page=1, limit=100):
    url = f"{base}/api/v2/search/spending_by_award/"
    filters = {"keywords":[keyword]}
    if start or end:
        filters["time_period"] = [{
            "start_date": start or "2000-01-01",
            "end_date": end or datetime.date.today().isoformat()
        }]
    if toptier_code:
        filters["agencies"] = [{
            "type": "funding",
            "tier": "toptier",
            "name": None,
            "toptier_codes": [toptier_code]
        }]
    payload = {
        "filters": filters,
        "page": page, "limit": limit,
        "sort":"Action Date", "order":"desc",
        "fields": ["Award ID","Recipient Name","Recipient UEI","Recipient DUNS","Description","Action Date","Awarding Agency","Funding Agency","PIID"]
    }
    r = requests.post(url, json=payload, timeout=60); r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint_base", default="https://api.usaspending.gov")
    ap.add_argument("--keywords_file", required=True)
    ap.add_argument("--agencies_json", required=True)
    ap.add_argument("--out_dir", default="external/usaspending_multiagency")
    ap.add_argument("--min_action_date", default="2019-01-01")
    ap.add_argument("--pages", type=int, default=2)
    args = ap.parse_args()

    ensure(args.out_dir)
    kws = [line.strip() for line in open(args.keywords_file) if line.strip()]
    agencies = json.load(open(args.agencies_json)).get("toptier_agencies", [])
    tmap = get_toptier_map(args.endpoint_base)

    manifest = {"generated": datetime.datetime.utcnow().isoformat(), "runs":[]}
    for ag in agencies:
        code = tmap.get(ag.lower())
        for kw in kws:
            for p in range(1, args.pages+1):
                data = search_awards(args.endpoint_base, kw, toptier_code=code, start=args.min_action_date, page=p)
                fn = f"{ag.replace(' ','_')}_{kw.replace(' ','_')}_p{p}.json"
                fp = os.path.join(args.out_dir, fn)
                with open(fp, "w") as f:
                    json.dump(data, f, indent=2)
                manifest["runs"].append({"agency": ag, "toptier_code": code, "keyword": kw, "page": p, "file": fp, "count": len(data.get('results', []))})
                time.sleep(0.4)
    with open(os.path.join(args.out_dir, "_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
