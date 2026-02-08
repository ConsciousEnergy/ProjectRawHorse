"""
Advanced Search API routes for global search across all data types
"""
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import Entity, MoneyFlow, Award, FOIATarget, SearchLog
from dependencies import get_db

router = APIRouter()


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
    
    return 0.0


def search_entities(db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search entities by name and type"""
    results = []
    
    # Search display_name and entity_type
    entities = db.query(Entity).filter(
        or_(
            Entity.display_name.ilike(f"%{query}%"),
            Entity.entity_type.ilike(f"%{query}%"),
            Entity.normalized_name.ilike(f"%{query}%")
        )
    ).limit(limit * 2).all()
    
    for entity in entities:
        # Calculate relevance based on display_name
        relevance = calculate_relevance(entity.display_name, query)
        
        # Boost relevance if type matches
        if entity.entity_type and query.lower() in entity.entity_type.lower():
            relevance = min(1.0, relevance + 0.2)
        
        if relevance > 0:
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
    """Search awards by recipient, agency, and description"""
    results = []
    
    # Search recipient_name, awarding_agency, funding_agency, description
    awards = db.query(Award).filter(
        or_(
            Award.recipient_name.ilike(f"%{query}%"),
            Award.awarding_agency.ilike(f"%{query}%"),
            Award.funding_agency.ilike(f"%{query}%"),
            Award.description.ilike(f"%{query}%")
        )
    ).limit(limit * 2).all()
    
    for award in awards:
        # Determine which field matched
        matched_field = "recipient_name"
        matched_text = award.recipient_name or ""
        
        if award.awarding_agency and query.lower() in award.awarding_agency.lower():
            matched_field = "awarding_agency"
            matched_text = award.awarding_agency
        elif award.funding_agency and query.lower() in award.funding_agency.lower():
            matched_field = "funding_agency"
            matched_text = award.funding_agency
        elif award.description and query.lower() in award.description.lower():
            matched_field = "description"
            matched_text = award.description[:100] + "..." if len(award.description or "") > 100 else award.description
        
        relevance = calculate_relevance(matched_text, query)
        
        if relevance > 0:
            amount_str = f"${award.award_amount:,.0f}" if award.award_amount else "Amount N/A"
            date_str = str(award.action_date) if award.action_date else "Date N/A"
            
            results.append({
                "type": "award",
                "id": award.id,
                "title": f"{award.recipient_name or 'Unknown'}: {amount_str}",
                "description": f"{award.awarding_agency or 'Unknown Agency'} • {date_str}",
                "matched_field": matched_field,
                "matched_text": matched_text,
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
    """Search money flows by source, target, and relationship"""
    results = []
    
    # Search source, target, relationship
    flows = db.query(MoneyFlow).filter(
        or_(
            MoneyFlow.source.ilike(f"%{query}%"),
            MoneyFlow.target.ilike(f"%{query}%"),
            MoneyFlow.relationship.ilike(f"%{query}%")
        )
    ).limit(limit * 2).all()
    
    for flow in flows:
        # Determine which field matched
        matched_field = "source"
        matched_text = flow.source
        
        if flow.target and query.lower() in flow.target.lower():
            matched_field = "target"
            matched_text = flow.target
        elif flow.relationship and query.lower() in (flow.relationship or "").lower():
            matched_field = "relationship"
            matched_text = flow.relationship
        
        relevance = calculate_relevance(matched_text, query)
        
        if relevance > 0:
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
    """Search FOIA targets by agency and record request"""
    results = []
    
    # Search agency and record_request
    foia_targets = db.query(FOIATarget).filter(
        or_(
            FOIATarget.agency.ilike(f"%{query}%"),
            FOIATarget.record_request.ilike(f"%{query}%")
        )
    ).limit(limit * 2).all()
    
    for foia in foia_targets:
        matched_field = "agency"
        matched_text = foia.agency
        
        if foia.record_request and query.lower() in foia.record_request.lower():
            matched_field = "record_request"
            matched_text = foia.record_request[:100] + "..." if len(foia.record_request) > 100 else foia.record_request
        
        relevance = calculate_relevance(matched_text, query)
        
        if relevance > 0:
            results.append({
                "type": "foia_target",
                "id": foia.id,
                "title": f"FOIA: {foia.agency}",
                "description": foia.record_request[:100] + "..." if len(foia.record_request) > 100 else foia.record_request,
                "matched_field": matched_field,
                "matched_text": matched_text,
                "relevance": relevance,
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
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results,
        "response_time_ms": response_time_ms
    }


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

