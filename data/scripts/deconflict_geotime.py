
import argparse, pandas as pd, math
from datetime import datetime, timedelta

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def to_dt(x):
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d","%m/%d/%Y %H:%M","%m/%d/%Y"):
        try: return datetime.strptime(str(x), fmt)
        except: pass
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sightings_csv", required=True, help="CSV with columns: id, date_time, lat, lon")
    ap.add_argument("--faa_csv", required=True, help="FAA UAS/other confounds with: date_time, lat, lon, location, description")
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--meters", type=int, default=5000)
    ap.add_argument("--minutes", type=int, default=60)
    args = ap.parse_args()

    s = pd.read_csv(args.sightings_csv)
    f = pd.read_csv(args.faa_csv)
    s["__dt"] = s["date_time"].apply(to_dt)
    f["__dt"] = f["date_time"].apply(to_dt)

    out = []
    for i, sr in s.iterrows():
        cand = f[(f["__dt"] >= sr["__dt"] - timedelta(minutes=args.minutes)) &
                 (f["__dt"] <= sr["__dt"] + timedelta(minutes=args.minutes))].copy()
        if cand.empty:
            continue
        cand["dist_m"] = cand.apply(lambda r: haversine(sr["lat"], sr["lon"], r["lat"], r["lon"]), axis=1)
        cand = cand[cand["dist_m"] <= args.meters]
        for _, r in cand.iterrows():
            out.append({
                "sighting_id": sr.get("id"),
                "sighting_time": sr.get("date_time"),
                "sighting_lat": sr.get("lat"),
                "sighting_lon": sr.get("lon"),
                "confound_time": r.get("date_time"),
                "confound_lat": r.get("lat"),
                "confound_lon": r.get("lon"),
                "confound_desc": r.get("description"),
                "confound_location": r.get("location"),
                "dist_m": r.get("dist_m")
            })
    pd.DataFrame(out).to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()
