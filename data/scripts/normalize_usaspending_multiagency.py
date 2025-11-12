
import os, json, argparse, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()

    rows = []
    for fn in os.listdir(args.in_dir):
        if not fn.endswith(".json"): continue
        data = json.load(open(os.path.join(args.in_dir, fn)))
        for r in data.get("results", []):
            rows.append({
                "award_uid": r.get("Award ID"),
                "description": r.get("Description"),
                "action_date": r.get("Action Date"),
                "recipient_name": r.get("Recipient Name"),
                "recipient_uei": r.get("Recipient UEI"),
                "recipient_duns": r.get("Recipient DUNS"),
                "awarding_agency": r.get("Awarding Agency"),
                "funding_agency": r.get("Funding Agency"),
                "source_file": fn,
            })
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()
