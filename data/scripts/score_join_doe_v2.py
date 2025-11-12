
import argparse, pandas as pd, re, os

def norm_name(s):
    if not isinstance(s, str): return None
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+"," ", s).strip()
    return re.sub(r"\s+"," ", s)

def load_weights(path):
    if not path or not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    w = {}
    for _, r in df.iterrows():
        k = str(r.get("keyword") or "").strip().lower()
        try:
            w[k] = float(r.get("weight"))
        except Exception:
            w[k] = 1.0
    return w

def score_research(row, kwset, wmap):
    score = 0.0
    score += 0.4  # provenance
    if row.get("osti_id"): score += 0.1
    if row.get("award_dois"): score += 0.05
    if row.get("contract_numbers"): score += 0.15
    if row.get("sponsor_org"): score += 0.1
    if row.get("research_org"): score += 0.05
    txt = " ".join([str(row.get("title") or ""), str(row.get("subject") or "")]).lower()
    txt = " " + re.sub(r"[^a-z0-9]+"," ", txt) + " "
    hits = []
    bonus = 0.0
    for k in kwset:
        token = " " + k + " "
        if token in txt:
            hits.append(k)
            bonus += 0.05 * wmap.get(k, 1.0)
    score += min(bonus, 0.25)
    return round(min(score, 1.0), 2), ";".join(hits[:3])

def score_sbir(row, kwset, wmap):
    score = 0.0
    score += 0.35  # provenance
    if row.get("solicitation_number"): score += 0.15
    if row.get("award_amount"): score += 0.1
    if row.get("award_start_date"): score += 0.05
    if row.get("program"): score += 0.05
    if row.get("phase"): score += 0.05
    txt = " ".join([str(row.get("title") or ""), str(row.get("abstract") or "")]).lower()
    txt = " " + re.sub(r"[^a-z0-9]+"," ", txt) + " "
    hits = []
    bonus = 0.0
    for k in kwset:
        token = " " + k + " "
        if token in txt:
            hits.append(k)
            bonus += 0.05 * wmap.get(k, 1.0)
    score += min(bonus, 0.3)
    return round(min(score, 1.0), 2), ";".join(hits[:3])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entities", required=True)
    ap.add_argument("--research_outputs", required=True)
    ap.add_argument("--sbir_awards", required=True)
    ap.add_argument("--out_research_scored", required=True)
    ap.add_argument("--out_sbir_scored", required=True)
    ap.add_argument("--keywords_file", default="lookups/keywords_deduped.txt")
    ap.add_argument("--weights_file", default="lookups/keyword_weights.csv")
    args = ap.parse_args()

    ents = pd.read_csv(args.entities) if os.path.exists(args.entities) else pd.DataFrame()
    ro = pd.read_csv(args.research_outputs) if os.path.exists(args.research_outputs) else pd.DataFrame()
    sb = pd.read_csv(args.sbir_awards) if os.path.exists(args.sbir_awards) else pd.DataFrame()

    kw = []
    if os.path.exists(args.keywords_file):
        kw = [line.strip().lower() for line in open(args.keywords_file) if line.strip()]
    wmap = load_weights(args.weights_file)
    kwset = set(kw)

    ent_name_map = {}
    if not ents.empty and "name" in ents.columns and "entity_id" in ents.columns:
        for _, r in ents.dropna(subset=["name"]).iterrows():
            ent_name_map[norm_name(r["name"])] = r["entity_id"]

    if not ro.empty:
        ro["match_entity_id"] = None
        for i, r in ro.iterrows():
            cand = norm_name(str(r.get("research_org") or "")) or norm_name(str(r.get("sponsor_org") or ""))
            if cand and cand in ent_name_map:
                ro.at[i, "match_entity_id"] = ent_name_map[cand]
        ro["credibility_score"], ro["kw_top3"] = zip(*ro.apply(lambda r: score_research(r, kwset, wmap), axis=1))
        ro.to_csv(args.out_research_scored, index=False)

    if not sb.empty:
        sb["match_entity_id"] = None
        if "company" in sb.columns:
            for i, r in sb.iterrows():
                cand = norm_name(str(r.get("company") or ""))
                if cand and cand in ent_name_map:
                    sb.at[i, "match_entity_id"] = ent_name_map[cand]
        sb["credibility_score"], sb["kw_top3"] = zip(*sb.apply(lambda r: score_sbir(r, kwset, wmap), axis=1))
        sb.to_csv(args.out_sbir_scored, index=False)

if __name__ == "__main__":
    main()
