
import os, json, time, argparse, requests, pandas as pd

# Requires a SAM.gov API key: https://open.gsa.gov/api/sam-gov/
# Endpoint: entity-information/v2/entities with searchText

def ensure(p): os.makedirs(p, exist_ok=True)

def sam_search(base, api_key, search_text, page=1, size=25):
    url = f"{base}/entities"
    params = {"api_key": api_key, "searchText": search_text, "page": page, "size": size}
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api_base", default="https://api.sam.gov/entity-information/v2")
    ap.add_argument("--api_key", default=os.environ.get("SAM_API_KEY"))
    ap.add_argument("--names_csv", required=True, help="CSV with column 'name'")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--pages", type=int, default=1)
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("Missing SAM API key. Set --api_key or SAM_API_KEY.")
    ensure(args.out_dir)

    df = pd.read_csv(args.names_csv)
    names = [n for n in df["name"].dropna().unique().tolist() if isinstance(n, str) and n.strip()]
    manifest = []
    for nm in names:
        for p in range(1, args.pages+1):
            data = sam_search(args.api_base, args.api_key, nm, page=p)
            fn = f"sam_entities_{nm.replace(' ','_')}_p{p}.json"
            fp = os.path.join(args.out_dir, fn)
            with open(fp, "w") as f:
                json.dump(data, f, indent=2)
            manifest.append({"name": nm, "page": p, "file": fp, "count": len(data.get('entityRegistrations', []))})
            time.sleep(0.4)
    with open(os.path.join(args.out_dir, "_manifest.json"), "w") as f:
        json.dump({"runs": manifest}, f, indent=2)

if __name__ == "__main__":
    main()
