"""
Advanced Search API routes for global search across all data types
"""
import csv
import os
import re
import time
from typing import List, Optional, Dict, Any, Tuple
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from rapidfuzz import fuzz, process

from database import Entity, MoneyFlow, Award, FOIATarget, SearchLog
from dependencies import get_db
from data_loader import AGENCY_ACRONYMS

router = APIRouter()

_NAME_CACHE: Dict[str, Tuple[List[str], float]] = {}
_NAME_CACHE_TTL = 300.0  # 5 minutes


def _get_cached_names(db: Session, column: Any, cache_key: str) -> List[str]:
    """Get distinct names from DB with 5-minute TTL cache."""
    now = time.time()
    if cache_key in _NAME_CACHE:
        cached, ts = _NAME_CACHE[cache_key]
        if now - ts < _NAME_CACHE_TTL:
            return cached
    names = [r[0] for r in db.query(column).distinct().all() if r[0]]
    _NAME_CACHE[cache_key] = (names, now)
    return names


def _build_suggestions(db: Session, query: str, limit: int = 3) -> List[str]:
    """Build 'Did you mean?' suggestions when search returns zero results."""
    q = query.strip()
    if len(q) < 2:
        return []
    names = _get_cached_names(db, Entity.display_name, "entity_names")
    if not names:
        return []
    fuzzy_matches = process.extract(
        q, names, scorer=fuzz.WRatio, score_cutoff=45, limit=limit
    )
    return [m[0] for m in fuzzy_matches if m[0] and m[0] != q]


def _load_alias_map() -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Load alias map from entity_aliases.csv and AGENCY_ACRONYMS. Cached at module level."""
    if hasattr(_load_alias_map, "_cache"):
        return _load_alias_map._cache
    alias_to_canonical: Dict[str, str] = {}
    canonical_to_aliases: Dict[str, List[str]] = {}
    # Seed from AGENCY_ACRONYMS
    for acro, full in AGENCY_ACRONYMS.items():
        al, fu = acro.strip().lower(), full.strip().lower()
        if al and fu:
            alias_to_canonical[fu] = al
            alias_to_canonical[al] = fu
            canonical_to_aliases.setdefault(al, []).append(fu)
            canonical_to_aliases.setdefault(fu, []).append(al)
    # Load CSV
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "entities", "entity_aliases.csv")
    path = os.path.abspath(path)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                canonical = (row.get("canonical") or "").strip()
                alias = (row.get("alias") or "").strip()
                if not canonical or not alias or canonical.startswith("#"):
                    continue
                cl, al = canonical.lower(), alias.lower()
                alias_to_canonical[al] = cl
                alias_to_canonical[cl] = al
                canonical_to_aliases.setdefault(cl, []).append(al)
                canonical_to_aliases.setdefault(al, []).append(cl)
    _load_alias_map._cache = (alias_to_canonical, canonical_to_aliases)
    return _load_alias_map._cache


def expand_query(query: str) -> List[str]:
    """Expand query with aliases so e.g. 'National Geospatial' also searches 'NGA'."""
    q = query.strip()
    if not q:
        return [q]
    q_lower = q.lower()
    seen = {q_lower}
    alias_to_canonical, canonical_to_aliases = _load_alias_map()
    # Direct hit: query is an alias or canonical
    if q_lower in alias_to_canonical:
        linked = alias_to_canonical[q_lower]
        seen.add(linked)
        for a in canonical_to_aliases.get(linked, []):
            seen.add(a)
    # Substring: query appears inside any alias or canonical
    for canon, aliases in canonical_to_aliases.items():
        if q_lower in canon:
            seen.add(canon)
            seen.update(aliases)
        for a in aliases:
            if q_lower in a:
                seen.add(canon)
                seen.update(aliases)
                break
    return [q] + [t for t in sorted(seen) if t != q_lower]


def parse_amount_query(query: str) -> Optional[List[Tuple[float, float]]]:
    """
    If query looks like a dollar amount, return a list of (lo, hi) ranges for DB filtering.
    E.g. '223' -> [(222, 224), (222e3, 224e3), (222e6, 224e6)] (exact, K, M).
    '223M' -> [(222e6, 224e6)].
    """
    q = query.strip().replace("$", "").replace(",", "").upper()
    if not q:
        return None
    mult = 1.0
    if q.endswith("K"):
        mult, q = 1e3, q[:-1]
    elif q.endswith("M"):
        mult, q = 1e6, q[:-1]
    elif q.endswith("B"):
        mult, q = 1e9, q[:-1]
    m = re.match(r"^(\d+(?:\.\d+)?)$", q.strip())
    if not m:
        return None
    try:
        val = float(m.group(1)) * mult
    except ValueError:
        return None
    if val <= 0:
        return None
    ranges: List[Tuple[float, float]] = []
    if mult > 1:
        # Explicit suffix: single range
        delta = max(val * 0.01, 1)
        ranges.append((val - delta, val + delta))
    else:
        # No suffix: try multiple scales (exact, thousands, millions)
        if val < 100000:
            delta = max(val * 0.01, 0.5)
            ranges.append((val - delta, val + delta))
        if val < 10000:
            v_k = val * 1e3
            delta_k = max(v_k * 0.01, 500)
            ranges.append((v_k - delta_k, v_k + delta_k))
            v_m = val * 1e6
            delta_m = max(v_m * 0.01, 0.5e6)
            ranges.append((v_m - delta_m, v_m + delta_m))
        else:
            delta = max(val * 0.01, 1)
            ranges.append((val - delta, val + delta))
    return ranges


def calculate_relevance(text: str, query: str) -> float:
    """Calculate relevance score based on match quality"""
    if not text or not query:
        return 0.0
    
    text_lower = text.lower()
    query_lower = query.lower()
    
    # Exact match gets highest score
    if text_lower == query_lower:
        return 1.0
    
    # Starts with query gets high score
    if text_lower.startswith(query_lower):
        return 0.9
    
    # Contains query as whole word gets good score
    if f" {query_lower} " in f" {text_lower} ":
        return 0.8
    
    # Contains query anywhere gets medium score
    if query_lower in text_lower:
        return 0.7
    
    # Fuzzy matching - check if query words are in text
    query_words = query_lower.split()
    text_words = text_lower.split()
    matches = sum(1 for qw in query_words if any(qw in tw for tw in text_words))
    if matches > 0:
        return 0.5 + (0.2 * matches / len(query_words))

    # Rapidfuzz fallback for typos (e.g. Pereton -> Peraton)
    ratio = fuzz.token_sort_ratio(text_lower, query_lower)
    if ratio >= 70:
        return ratio / 100 * 0.65
    return 0.0


def search_entities(db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search entities by name and type (with alias expansion)."""
    results = []
    terms = expand_query(query)
    query_lower = query.strip().lower()
    conditions = []
    for t in terms:
        conditions.extend([
            Entity.display_name.ilike(f"%{t}%"),
            Entity.entity_type.ilike(f"%{t}%"),
            Entity.normalized_name.ilike(f"%{t}%"),
            Entity.entity_id.ilike(f"%{t}%"),
        ])
    # Multi-word: add tokenized AND conditions (e.g. "National Geospatial" -> display_name contains both)
    words = [w for w in query.strip().split() if w]
    if len(words) > 1:
        for col in [Entity.display_name, Entity.normalized_name, Entity.entity_type, Entity.entity_id]:
            conditions.append(and_(*[col.ilike(f"%{w}%") for w in words]))
    entities = db.query(Entity).filter(or_(*conditions)).limit(limit * 2).all()

    for entity in entities:
        best_relevance = 0.0
        matched_on_original = False
        for t in terms:
            r = calculate_relevance(entity.display_name, t)
            if entity.entity_type and t.lower() in entity.entity_type.lower():
                r = min(1.0, r + 0.2)
            if r > best_relevance:
                best_relevance = r
                matched_on_original = t.lower() == query_lower
        if best_relevance > 0 and not matched_on_original:
            best_relevance *= 0.95
        if best_relevance > 0:
            results.append({
                "type": "entity",
                "id": entity.entity_id,
                "title": entity.display_name,
                "description": entity.entity_type or "Unknown Type",
                "matched_field": "display_name",
                "matched_text": entity.display_name,
                "relevance": best_relevance,
                "metadata": {
                    "entity_type": entity.entity_type,
                    "normalized_name": entity.normalized_name
                }
            })
    # Always run fuzzy matching (not just fallback); use WRatio, lower cutoff for short queries
    score_cutoff = 55 if len(query.strip()) < 8 else 70
    names = _get_cached_names(db, Entity.display_name, "entity_names")
    if names:
        fuzzy_matches = process.extract(
            query.strip(), names, scorer=fuzz.WRatio, score_cutoff=score_cutoff, limit=limit * 2
        )
        seen_ids = {r["id"] for r in results}
        for name, score, _ in fuzzy_matches:
            entity = db.query(Entity).filter(Entity.display_name == name).first()
            if entity and entity.entity_id not in seen_ids:
                seen_ids.add(entity.entity_id)
                relevance = score / 100 * 0.7
                results.append({
                    "type": "entity",
                    "id": entity.entity_id,
                    "title": entity.display_name,
                    "description": entity.entity_type or "Unknown Type",
                    "matched_field": "display_name",
                    "matched_text": entity.display_name,
                    "relevance": relevance,
                    "metadata": {
                        "entity_type": entity.entity_type,
                        "normalized_name": entity.normalized_name
                    }
                })
    return results


def search_awards(db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search awards by recipient, agency, description, and amount (with alias expansion)."""
    results = []
    terms = expand_query(query)
    query_lower = query.strip().lower()
    conditions = []
    for t in terms:
        conditions.extend([
            Award.recipient_name.ilike(f"%{t}%"),
            Award.awarding_agency.ilike(f"%{t}%"),
            Award.funding_agency.ilike(f"%{t}%"),
            Award.description.ilike(f"%{t}%"),
        ])
    words = [w for w in query.strip().split() if w]
    if len(words) > 1:
        for col in [Award.recipient_name, Award.awarding_agency, Award.funding_agency, Award.description]:
            conditions.append(and_(*[col.ilike(f"%{w}%") for w in words]))
    amount_ranges = parse_amount_query(query)
    if amount_ranges:
        range_conditions = []
        for lo, hi in amount_ranges:
            range_conditions.append(and_(Award.award_amount.isnot(None), Award.award_amount.between(lo, hi)))
        conditions.append(or_(*range_conditions))
        # Text fallback: search raw query in description (e.g. "223" in "Contract #223-...")
        q_clean = query.strip().replace("$", "").replace(",", "")
        if q_clean and q_clean.replace(".", "").isdigit():
            conditions.append(Award.description.ilike(f"%{q_clean}%"))
    awards = db.query(Award).filter(or_(*conditions)).limit(limit * 2).all()

    for award in awards:
        matched_field = "recipient_name"
        matched_text = award.recipient_name or ""
        best_relevance = 0.0
        matched_on_original = False
        if amount_ranges and award.award_amount is not None:
            for lo, hi in amount_ranges:
                if lo <= award.award_amount <= hi:
                    best_relevance = 0.85
                    matched_field = "award_amount"
                    matched_text = f"${award.award_amount:,.0f}"
                    matched_on_original = True
                    break
        for t in terms:
            for field_name, text in [
                ("recipient_name", award.recipient_name or ""),
                ("awarding_agency", award.awarding_agency or ""),
                ("funding_agency", award.funding_agency or ""),
                ("description", (award.description or "")[:200]),
            ]:
                if t.lower() in text.lower():
                    r = calculate_relevance(text, t)
                    if r > best_relevance:
                        best_relevance = r
                        matched_field = field_name
                        matched_text = text[:100] + "..." if len(text) > 100 else text
                        matched_on_original = t.lower() == query_lower
        if best_relevance > 0 and not matched_on_original:
            best_relevance *= 0.95
        if best_relevance > 0:
            amount_str = f"${award.award_amount:,.0f}" if award.award_amount else "Amount N/A"
            date_str = str(award.action_date) if award.action_date else "Date N/A"
            results.append({
                "type": "award",
                "id": award.id,
                "title": f"{award.recipient_name or 'Unknown'}: {amount_str}",
                "description": f"{award.awarding_agency or 'Unknown Agency'} • {date_str}",
                "matched_field": matched_field,
                "matched_text": matched_text,
                "relevance": best_relevance,
                "metadata": {
                    "recipient_name": award.recipient_name,
                    "amount": award.award_amount,
                    "agency": award.awarding_agency,
                    "date": str(award.action_date) if award.action_date else None
                }
            })
    score_cutoff = 55 if len(query.strip()) < 8 else 70
    names = _get_cached_names(db, Award.recipient_name, "award_recipients")
    names = [n for n in names if n]
    if names:
        fuzzy_matches = process.extract(
            query.strip(), names, scorer=fuzz.WRatio, score_cutoff=score_cutoff, limit=limit * 2
        )
        seen_award_ids = {r["id"] for r in results}
        for name, score, _ in fuzzy_matches:
            for award in db.query(Award).filter(Award.recipient_name == name).limit(limit).all():
                    if award.id not in seen_award_ids:
                        seen_award_ids.add(award.id)
                        relevance = score / 100 * 0.7
                        amount_str = f"${award.award_amount:,.0f}" if award.award_amount else "Amount N/A"
                        date_str = str(award.action_date) if award.action_date else "Date N/A"
                        results.append({
                            "type": "award",
                            "id": award.id,
                            "title": f"{award.recipient_name or 'Unknown'}: {amount_str}",
                            "description": f"{award.awarding_agency or 'Unknown Agency'} • {date_str}",
                            "matched_field": "recipient_name",
                            "matched_text": award.recipient_name or "",
                            "relevance": relevance,
                            "metadata": {
                                "recipient_name": award.recipient_name,
                                "amount": award.award_amount,
                                "agency": award.awarding_agency,
                                "date": str(award.action_date) if award.action_date else None
                            }
                        })
    return results


def search_money_flows(db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search money flows by source, target, relationship, and amount (with alias expansion)."""
    results = []
    terms = expand_query(query)
    query_lower = query.strip().lower()
    conditions = []
    for t in terms:
        conditions.extend([
            MoneyFlow.source.ilike(f"%{t}%"),
            MoneyFlow.target.ilike(f"%{t}%"),
            MoneyFlow.relationship.ilike(f"%{t}%"),
        ])
    words = [w for w in query.strip().split() if w]
    if len(words) > 1:
        for col in [MoneyFlow.source, MoneyFlow.target, MoneyFlow.relationship]:
            conditions.append(and_(*[col.ilike(f"%{w}%") for w in words]))
    amount_ranges = parse_amount_query(query)
    if amount_ranges:
        range_conditions = []
        for lo, hi in amount_ranges:
            range_conditions.append(and_(MoneyFlow.amount_usd.isnot(None), MoneyFlow.amount_usd.between(lo, hi)))
        conditions.append(or_(*range_conditions))
        q_clean = query.strip().replace("$", "").replace(",", "")
        if q_clean and q_clean.replace(".", "").isdigit():
            conditions.append(MoneyFlow.relationship.ilike(f"%{q_clean}%"))
    flows = db.query(MoneyFlow).filter(or_(*conditions)).limit(limit * 2).all()

    for flow in flows:
        matched_field = "source"
        matched_text = flow.source
        best_relevance = 0.0
        matched_on_original = False
        if amount_ranges and flow.amount_usd is not None:
            for lo, hi in amount_ranges:
                if lo <= flow.amount_usd <= hi:
                    best_relevance = 0.85
                    matched_field = "amount_usd"
                    matched_text = f"${flow.amount_usd:,.0f}"
                    matched_on_original = True
                    break
        for t in terms:
            for fn, text in [
                ("source", flow.source),
                ("target", flow.target or ""),
                ("relationship", flow.relationship or ""),
            ]:
                if t.lower() in text.lower():
                    r = calculate_relevance(text, t)
                    if r > best_relevance:
                        best_relevance = r
                        matched_field = fn
                        matched_text = text
                        matched_on_original = t.lower() == query_lower
        if best_relevance > 0 and not matched_on_original:
            best_relevance *= 0.95
        if best_relevance > 0:
            amount_str = f"${flow.amount_usd:,.0f}" if flow.amount_usd else "Amount N/A"
            title = f"{flow.source} → {flow.target}: {amount_str}"
            description = flow.relationship or "Transaction"
            if flow.start_date:
                description += f" • {flow.start_date}"
            results.append({
                "type": "money_flow",
                "id": flow.id,
                "title": title,
                "description": description,
                "matched_field": matched_field,
                "matched_text": matched_text,
                "relevance": best_relevance,
                "metadata": {
                    "source": flow.source,
                    "target": flow.target,
                    "amount": flow.amount_usd,
                    "date": str(flow.start_date) if flow.start_date else None,
                    "relationship": flow.relationship
                }
            })
    score_cutoff = 55 if len(query.strip()) < 8 else 70
    sources = _get_cached_names(db, MoneyFlow.source, "flow_sources")
    targets = _get_cached_names(db, MoneyFlow.target, "flow_targets")
    names = list(dict.fromkeys([n for n in sources + targets if n]))
    if names:
        fuzzy_matches = process.extract(
            query.strip(), names, scorer=fuzz.WRatio, score_cutoff=score_cutoff, limit=limit * 2
        )
        seen_flow_ids = {r["id"] for r in results}
        for name, score, _ in fuzzy_matches:
            for flow in db.query(MoneyFlow).filter(
                or_(MoneyFlow.source == name, MoneyFlow.target == name)
            ).limit(limit).all():
                if flow.id not in seen_flow_ids:
                    seen_flow_ids.add(flow.id)
                    relevance = score / 100 * 0.7
                    amount_str = f"${flow.amount_usd:,.0f}" if flow.amount_usd else "Amount N/A"
                    title = f"{flow.source} → {flow.target}: {amount_str}"
                    description = flow.relationship or "Transaction"
                    if flow.start_date:
                        description += f" • {flow.start_date}"
                    results.append({
                        "type": "money_flow",
                        "id": flow.id,
                        "title": title,
                        "description": description,
                        "matched_field": "source" if flow.source == name else "target",
                        "matched_text": name,
                        "relevance": relevance,
                        "metadata": {
                            "source": flow.source,
                            "target": flow.target,
                            "amount": flow.amount_usd,
                            "date": str(flow.start_date) if flow.start_date else None,
                            "relationship": flow.relationship
                        }
                    })
    return results


def search_foia_targets(db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search FOIA targets by agency and record request (with alias expansion)."""
    results = []
    terms = expand_query(query)
    query_lower = query.strip().lower()
    conditions = []
    for t in terms:
        conditions.extend([
            FOIATarget.agency.ilike(f"%{t}%"),
            FOIATarget.record_request.ilike(f"%{t}%"),
        ])
    words = [w for w in query.strip().split() if w]
    if len(words) > 1:
        for col in [FOIATarget.agency, FOIATarget.record_request]:
            conditions.append(and_(*[col.ilike(f"%{w}%") for w in words]))
    foia_targets = db.query(FOIATarget).filter(or_(*conditions)).limit(limit * 2).all()

    for foia in foia_targets:
        matched_field = "agency"
        matched_text = foia.agency
        best_relevance = 0.0
        matched_on_original = False
        for t in terms:
            for fn, text in [
                ("agency", foia.agency or ""),
                ("record_request", (foia.record_request or "")[:200]),
            ]:
                if t.lower() in text.lower():
                    r = calculate_relevance(text, t)
                    if r > best_relevance:
                        best_relevance = r
                        matched_field = fn
                        matched_text = text[:100] + "..." if len(text) > 100 else text
                        matched_on_original = t.lower() == query_lower
        if best_relevance > 0 and not matched_on_original:
            best_relevance *= 0.95
        if best_relevance > 0:
            results.append({
                "type": "foia_target",
                "id": foia.id,
                "title": f"FOIA: {foia.agency}",
                "description": foia.record_request[:100] + "..." if len(foia.record_request or "") > 100 else (foia.record_request or ""),
                "matched_field": matched_field,
                "matched_text": matched_text,
                "relevance": best_relevance,
                "metadata": {
                    "agency": foia.agency,
                    "timeframe": foia.timeframe,
                    "relevance": foia.relevance
                }
            })
    return results


@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=2, max_length=200, description="Search query (2-200 characters)"),
    types: Optional[List[str]] = Query(None, description="Filter by data types: entities, awards, money_flows, foia_targets"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Global search across all data types
    
    Searches through entities, awards, money flows, and FOIA targets.
    Returns unified results sorted by relevance score.
    
    **Query Parameters:**
    - q: Search term (required, min 2 characters)
    - types: Filter by specific data types (optional)
    - limit: Max results to return (default: 20, max: 100)
    
    **Returns:**
    - query: Original search term
    - total_results: Total number of results found
    - results: Array of search results with relevance scores
    """
    # Track start time for analytics
    start_time = time.time()
    
    results = []
    
    # Search entities
    if not types or "entities" in types:
        entity_results = search_entities(db, q, limit)
        results.extend(entity_results)
    
    # Search awards
    if not types or "awards" in types:
        award_results = search_awards(db, q, limit)
        results.extend(award_results)
    
    # Search money flows
    if not types or "money_flows" in types:
        flow_results = search_money_flows(db, q, limit)
        results.extend(flow_results)
    
    # Search FOIA targets
    if not types or "foia_targets" in types:
        foia_results = search_foia_targets(db, q, limit)
        results.extend(foia_results)
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Limit to requested number
    results = results[:limit]
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Log search for analytics
    try:
        search_log = SearchLog(
            query=q,
            results_count=len(results),
            response_time_ms=response_time_ms,
            types_searched=",".join(types) if types else "all"
        )
        db.add(search_log)
        db.commit()
    except Exception as e:
        # Don't fail the search if logging fails
        print(f"Failed to log search: {e}")
        db.rollback()
    
    response = {
        "query": q,
        "total_results": len(results),
        "results": results,
        "response_time_ms": response_time_ms
    }
    if len(results) == 0:
        response["suggestions"] = _build_suggestions(db, q, limit=3)
    return response


@router.get("/search/analytics")
async def get_search_analytics(
    limit: int = Query(20, le=100, description="Number of top searches to return"),
    db: Session = Depends(get_db)
):
    """
    Get search analytics and statistics
    
    Returns insights about what users are searching for, including:
    - Most popular searches
    - Searches with no results (areas to improve)
    - Average response time
    - Search activity statistics
    
    **Query Parameters:**
    - limit: Number of top searches to return (default: 20, max: 100)
    
    **Returns:**
    - total_searches: Total number of searches logged
    - popular_searches: Most frequently searched terms
    - no_result_searches: Searches that returned no results
    - performance: Response time statistics
    - activity: Search activity over time
    """
    # Total searches
    total_searches = db.query(func.count(SearchLog.id)).scalar() or 0
    
    # Popular searches (top queries)
    popular_searches = db.query(
        SearchLog.query,
        func.count(SearchLog.id).label('count'),
        func.avg(SearchLog.results_count).label('avg_results')
    ).filter(
        SearchLog.query != ''
    ).group_by(
        SearchLog.query
    ).order_by(
        func.count(SearchLog.id).desc()
    ).limit(limit).all()
    
    # Searches with no results (opportunities to add data)
    no_result_searches = db.query(
        SearchLog.query,
        func.count(SearchLog.id).label('attempt_count')
    ).filter(
        SearchLog.results_count == 0
    ).group_by(
        SearchLog.query
    ).order_by(
        func.count(SearchLog.id).desc()
    ).limit(limit).all()
    
    # Performance statistics
    performance_stats = db.query(
        func.avg(SearchLog.response_time_ms).label('avg_ms'),
        func.min(SearchLog.response_time_ms).label('min_ms'),
        func.max(SearchLog.response_time_ms).label('max_ms')
    ).first()
    
    # Recent searches (last 24 hours activity)
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = db.query(func.count(SearchLog.id)).filter(
        SearchLog.search_timestamp >= yesterday
    ).scalar() or 0
    
    return {
        "total_searches": total_searches,
        "searches_last_24h": recent_count,
        "popular_searches": [
            {
                "query": s[0],
                "search_count": s[1],
                "avg_results": round(float(s[2]) if s[2] else 0, 1)
            }
            for s in popular_searches
        ],
        "no_result_searches": [
            {
                "query": s[0],
                "attempt_count": s[1]
            }
            for s in no_result_searches
        ],
        "performance": {
            "avg_response_ms": round(float(performance_stats[0]) if performance_stats[0] else 0, 1),
            "min_response_ms": performance_stats[1] or 0,
            "max_response_ms": performance_stats[2] or 0
        }
    }

