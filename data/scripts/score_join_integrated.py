
import argparse, pandas as pd, re, os

def norm(s):
    if not isinstance(s, str): return None
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+"," ", s).strip()
    return re.sub(r"\s+"," ", s)

def load_kw(path):
    if not os.path.exists(path): return set()
    return set([line.strip().lower() for line in open(path) if line.strip()])

def load_w(path):
    if not os.path.exists(path): return {}
    import pandas as pd
    df = pd.read_csv(path)
    m = {}
    for _, r in df.iterrows():
        k = str(r.get("keyword") or "").strip().lower()
        try: m[k] = float(r.get("weight"))
        except: m[k] = 1.0
    return m

def kw_bonus(txt, kwset, wmap, cap):
    if not isinstance(txt, str): return 0.0, []
    base = " " + re.sub(r"[^a-z0-9]+"," ", txt.lower()) + " "
    hits, bonus = [], 0.0
    for k in kwset:
        token = " " + k + " "
        if token in base:
            hits.append(k); bonus += 0.05 * wmap.get(k, 1.0)
    return min(bonus, cap), hits[:3]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entities", required=True)
    ap.add_argument("--sbir", required=True)
    ap.add_argument("--research_outputs", required=True)
    ap.add_argument("--arpae_projects", required=False)
    ap.add_argument("--forecast", required=False)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--keywords_file", default="lookups/keywords_deduped.txt")
    ap.add_argument("--weights_file", default="lookups/keyword_weights.csv")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    ents = pd.read_csv(args.entities) if os.path.exists(args.entities) else pd.DataFrame()
    sbir = pd.read_csv(args.sbir) if os.path.exists(args.sbir) else pd.DataFrame()
    research = pd.read_csv(args.research_outputs) if os.path.exists(args.research_outputs) else pd.DataFrame()
    arpae = pd.read_csv(args.arpae_projects) if args.arpae_projects and os.path.exists(args.arpae_projects) else pd.DataFrame()
    forecast = pd.read_csv(args.forecast) if args.forecast and os.path.exists(args.forecast) else pd.DataFrame()

    kwset = load_kw(args.keywords_file)
    wmap = load_w(args.weights_file)

    # Entities map
    ent_map = {}
    if not ents.empty and "name" in ents.columns and "entity_id" in ents.columns:
        for _, r in ents.dropna(subset=["name"]).iterrows():
            ent_map[norm(r["name"])] = r["entity_id"]

    # Score SBIR
    if not sbir.empty:
        sbir["match_entity_id"] = None
        if "company" in sbir.columns:
            for i, r in sbir.iterrows():
                key = norm(str(r.get("company") or ""))
                if key in ent_map:
                    sbir.at[i, "match_entity_id"] = ent_map[key]
        bonus, hits = zip(*sbir.apply(lambda r: kw_bonus(str(r.get("title") or "") + " " + str(r.get("abstract") or ""), kwset, wmap, cap=0.3), axis=1)) if len(sbir)>0 else ([],[])
        sbir["credibility_score"] = 0.35 + sbir.get("solicitation_number").notna().astype(int)*0.15 + sbir.get("award_amount").notna().astype(int)*0.1 + sbir.get("award_start_date").notna().astype(int)*0.05 + sbir.get("program").notna().astype(int)*0.05 + sbir.get("phase").notna().astype(int)*0.05 + pd.Series(bonus)
        sbir["kw_top3"] = list(hits) if len(sbir)>0 else []
        sbir["credibility_score"] = sbir["credibility_score"].clip(upper=1.0)
        sbir.to_csv(os.path.join(args.out_dir, "sbir_scored.csv"), index=False)

    # Score research (OSTI)
    if not research.empty:
        # simple entity match via research_org / sponsor_org
        research["match_entity_id"] = None
        for i, r in research.iterrows():
            cand = norm(str(r.get("research_org") or "")) or norm(str(r.get("sponsor_org") or ""))
            if cand and cand in ent_map:
                research.at[i, "match_entity_id"] = ent_map[cand]
        bonus, hits = zip(*research.apply(lambda r: kw_bonus(str(r.get("title") or "") + " " + str(r.get("subject") or ""), kwset, wmap, cap=0.25), axis=1)) if len(research)>0 else ([],[])
        research["credibility_score"] = 0.4 + research.get("osti_id").notna().astype(int)*0.1 + research.get("award_dois").notna().astype(int)*0.05 + research.get("contract_numbers").notna().astype(int)*0.15 + research.get("sponsor_org").notna().astype(int)*0.1 + research.get("research_org").notna().astype(int)*0.05 + pd.Series(bonus)
        research["kw_top3"] = list(hits) if len(research)>0 else []
        research["credibility_score"] = research["credibility_score"].clip(upper=1.0)
        research.to_csv(os.path.join(args.out_dir, "research_outputs_scored.csv"), index=False)

    # Score ARPA-E (if present) and link by name overlap
    if not arpae.empty:
        bonus, hits = zip(*arpae.apply(lambda r: kw_bonus(str(r.get("project_title") or ""), kwset, wmap, cap=0.4), axis=1)) if len(arpae)>0 else ([],[])
        arpae["credibility_score"] = 0.3 + (arpae.get("program_hint").notna().astype(int)*0.05) + (arpae.get("url").notna().astype(int)*0.05) + pd.Series(bonus)
        arpae["kw_top3"] = list(hits) if len(arpae)>0 else []
        # naive entity join: look for exact normalized name tokens in title
        arpae["match_entity_id"] = None
        if not ents.empty and "name" in ents.columns:
            names = [(norm(n), eid) for n, eid in zip(ents["name"], ents["entity_id"]) if isinstance(n, str)]
            for i, r in arpae.iterrows():
                title = norm(str(r.get("project_title") or "")) or ""
                found = None
                for nm, eid in names:
                    if nm and nm in title and len(nm) > 4:
                        found = eid; break
                if found:
                    arpae.at[i, "match_entity_id"] = found
        arpae["credibility_score"] = arpae["credibility_score"].clip(upper=1.0)
        arpae.to_csv(os.path.join(args.out_dir, "arpae_projects_scored.csv"), index=False)

    # Build integrated pipeline candidates if forecast present
    if not forecast.empty and not sbir.empty:
        # text overlap between forecast title and SBIR title/abstract
        def overlap(a, b):
            a2 = set((norm(a) or "").split()); b2 = set((norm(b) or "").split())
            if not a2: return 0.0
            return len(a2 & b2) / max(1, len(a2))
        rows = []
        for _, fr in forecast.iterrows():
            f_title = str(fr.get("title") or "")
            f_naics = str(fr.get("naics") or "")
            sb = sbir.copy()
            sb["overlap"] = sb.apply(lambda r: overlap(f_title, str(r.get("title") or "") + " " + str(r.get("abstract") or "")), axis=1)
            top = sb.sort_values("overlap", ascending=False).head(5)
            for _, r in top.iterrows():
                rows.append({
                    "forecast_title": fr.get("title"),
                    "forecast_naics": f_naics,
                    "sbir_company": r.get("company"),
                    "sbir_title": r.get("title"),
                    "sbir_year": r.get("year"),
                    "sbir_phase": r.get("phase"),
                    "sbir_award_amount": r.get("award_amount"),
                    "sbir_match_entity_id": r.get("match_entity_id"),
                    "text_overlap": r.get("overlap"),
                })
        pd.DataFrame(rows).to_csv(os.path.join(args.out_dir, "pipeline_candidates.csv"), index=False)

if __name__ == "__main__":
    main()
