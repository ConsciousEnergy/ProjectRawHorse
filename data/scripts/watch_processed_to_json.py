
import os, time, json, argparse, pandas as pd

def serialize_csv(path, limit=None):
    try:
        df = pd.read_csv(path)
        if limit:
            df = df.head(limit)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed_dir", default="processed")
    ap.add_argument("--out_dir", default="apps/viz/public/data")
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--limit", type=int, default=None, help="optional row cap per file")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    def snapshot():
        for fn in os.listdir(args.processed_dir):
            if not fn.lower().endswith(".csv"): continue
            src = os.path.join(args.processed_dir, fn)
            dst = os.path.join(args.out_dir, os.path.splitext(fn)[0] + ".json")
            data = serialize_csv(src, args.limit)
            with open(dst, "w") as f:
                json.dump(data, f)
        # also write a manifest
        man = {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files": [f for f in os.listdir(args.out_dir) if f.endswith(".json")]
        }
        with open(os.path.join(args.out_dir, "_manifest.json"), "w") as f:
            json.dump(man, f, indent=2)

    last = 0
    while True:
        try:
            mtime = max([os.path.getmtime(os.path.join(args.processed_dir, f)) for f in os.listdir(args.processed_dir) if f.endswith(".csv")] + [0])
        except Exception:
            mtime = 0
        if mtime > last:
            snapshot()
            last = mtime
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
