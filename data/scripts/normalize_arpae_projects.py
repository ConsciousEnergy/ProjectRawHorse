
import os, json, argparse, pandas as pd, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_json", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()

    data = json.load(open(args.in_json))
    items = data.get("items", [])
    rows = []
    for r in items:
        title = r.get("title")
        url = r.get("url")
        # Lightweight parsing hints (program name sometimes in title or URL path)
        program = None
        if url and "/programs-and-initiatives/" in url:
            m = re.search(r"/programs-and-initiatives/([^/]+)/", url)
            if m: program = m.group(1).replace("-", " ").upper()
        rows.append({
            "project_title": title,
            "program_hint": program,
            "url": url,
            "source_file": os.path.basename(args.in_json)
        })
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()
