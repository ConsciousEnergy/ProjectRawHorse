"""
Temporal pattern detection and anomaly detection for financial flows
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import statistics
import logging

from database import MoneyFlow, Award

logger = logging.getLogger(__name__)


def detect_spending_spikes(
    db: Session,
    entity_name: str = None,
    threshold_std_devs: float = 2.0
) -> List[Dict]:
    """
    Detect anomalous spending spikes using statistical analysis
    
    Args:
        db: Database session
        entity_name: Optional entity to filter by (source or target)
        threshold_std_devs: Number of standard deviations for anomaly threshold
    
    Returns:
        List of detected anomalies with details
    """
    # Get all money flows
    query = db.query(MoneyFlow).filter(MoneyFlow.amount_usd.isnot(None))
    
    if entity_name:
        query = query.filter(
            (MoneyFlow.source == entity_name) | (MoneyFlow.target == entity_name)
        )
    
    flows = query.all()
    
    if len(flows) < 10:  # Need sufficient data for statistical analysis
        return []
    
    # Extract amounts
    amounts = [f.amount_usd for f in flows if f.amount_usd]
    
    if not amounts:
        return []
    
    # Calculate statistics
    mean_amount = statistics.mean(amounts)
    stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
    
    if stdev_amount == 0:  # All values are the same
        return []
    
    # Detect anomalies (values beyond threshold)
    threshold = mean_amount + (threshold_std_devs * stdev_amount)
    
    anomalies = []
    for flow in flows:
        if flow.amount_usd and flow.amount_usd > threshold:
            z_score = (flow.amount_usd - mean_amount) / stdev_amount
            
            anomalies.append({
                'type': 'spending_spike',
                'source': flow.source,
                'target': flow.target,
                'amount': flow.amount_usd,
                'date': flow.start_date.isoformat() if flow.start_date else None,
                'z_score': round(z_score, 2),
                'mean': mean_amount,
                'stdev': stdev_amount,
                'relationship': flow.relationship
            })
    
    # Sort by z-score (most anomalous first)
    anomalies.sort(key=lambda x: x['z_score'], reverse=True)
    
    return anomalies


def detect_award_clustering(
    db: Session,
    recipient: str = None,
    time_window_days: int = 30
) -> List[Dict]:
    """
    Detect temporal clustering of awards (multiple awards in short time period)
    
    Args:
        db: Database session
        recipient: Optional recipient to filter by
        time_window_days: Time window for clustering detection
    
    Returns:
        List of detected clusters
    """
    query = db.query(Award).filter(Award.action_date.isnot(None))
    
    if recipient:
        query = query.filter(Award.recipient_name == recipient)
    
    # Order by date
    awards = query.order_by(Award.action_date).all()
    
    if len(awards) < 3:
        return []
    
    clusters = []
    window = timedelta(days=time_window_days)
    
    i = 0
    while i < len(awards):
        cluster_start = awards[i].action_date
        cluster_awards = [awards[i]]
        cluster_amount = awards[i].award_amount or 0
        
        # Look ahead for awards within window
        j = i + 1
        while j < len(awards):
            if awards[j].action_date - cluster_start <= window:
                cluster_awards.append(awards[j])
                cluster_amount += awards[j].award_amount or 0
                j += 1
            else:
                break
        
        # Cluster detected if 3+ awards in window
        if len(cluster_awards) >= 3:
            agencies = set()
            for award in cluster_awards:
                if award.awarding_agency:
                    agencies.add(award.awarding_agency)
            
            clusters.append({
                'type': 'award_clustering',
                'recipient': cluster_awards[0].recipient_name,
                'start_date': cluster_start.isoformat(),
                'end_date': cluster_awards[-1].action_date.isoformat() if cluster_awards[-1].action_date else None,
                'award_count': len(cluster_awards),
                'total_amount': cluster_amount,
                'agencies': list(agencies),
                'window_days': (cluster_awards[-1].action_date - cluster_start).days if cluster_awards[-1].action_date else 0
            })
            
            i = j  # Skip past this cluster
        else:
            i += 1
    
    # Sort by award count (most clustered first)
    clusters.sort(key=lambda x: x['award_count'], reverse=True)
    
    return clusters


def detect_funding_gaps(
    db: Session,
    entity_name: str,
    min_gap_days: int = 180
) -> List[Dict]:
    """
    Detect significant gaps in funding activity
    
    Args:
        db: Database session
        entity_name: Entity to analyze
        min_gap_days: Minimum gap in days to report
    
    Returns:
        List of detected funding gaps
    """
    # Get all flows involving entity, ordered by date
    flows = db.query(MoneyFlow).filter(
        MoneyFlow.start_date.isnot(None),
        (MoneyFlow.source == entity_name) | (MoneyFlow.target == entity_name)
    ).order_by(MoneyFlow.start_date).all()
    
    if len(flows) < 2:
        return []
    
    gaps = []
    min_gap = timedelta(days=min_gap_days)
    
    for i in range(len(flows) - 1):
        current_date = flows[i].start_date
        next_date = flows[i + 1].start_date
        
        if current_date and next_date:
            gap = next_date - current_date
            
            if gap >= min_gap:
                gaps.append({
                    'type': 'funding_gap',
                    'entity': entity_name,
                    'gap_start': current_date.isoformat(),
                    'gap_end': next_date.isoformat(),
                    'gap_days': gap.days,
                    'last_flow_before': {
                        'source': flows[i].source,
                        'target': flows[i].target,
                        'amount': flows[i].amount_usd
                    },
                    'first_flow_after': {
                        'source': flows[i + 1].source,
                        'target': flows[i + 1].target,
                        'amount': flows[i + 1].amount_usd
                    }
                })
    
    # Sort by gap length (longest first)
    gaps.sort(key=lambda x: x['gap_days'], reverse=True)
    
    return gaps


def detect_periodic_patterns(
    db: Session,
    entity_name: str = None,
    min_occurrences: int = 3
) -> List[Dict]:
    """
    Detect periodic/recurring patterns in awards or flows
    
    Args:
        db: Database session
        entity_name: Optional entity to filter by
        min_occurrences: Minimum occurrences to consider a pattern
    
    Returns:
        List of detected periodic patterns
    """
    # Get awards with dates
    query = db.query(Award).filter(Award.action_date.isnot(None))
    
    if entity_name:
        query = query.filter(Award.recipient_name == entity_name)
    
    awards = query.order_by(Award.action_date).all()
    
    if len(awards) < min_occurrences:
        return []
    
    patterns = []
    
    # Group by recipient and agency
    recipient_agency_awards = {}
    for award in awards:
        key = (award.recipient_name, award.awarding_agency)
        if key not in recipient_agency_awards:
            recipient_agency_awards[key] = []
        recipient_agency_awards[key].append(award)
    
    # Analyze each recipient-agency pair
    for (recipient, agency), award_list in recipient_agency_awards.items():
        if len(award_list) < min_occurrences:
            continue
        
        # Calculate intervals between awards
        intervals = []
        for i in range(len(award_list) - 1):
            date1 = award_list[i].action_date
            date2 = award_list[i + 1].action_date
            if date1 and date2:
                interval = (date2 - date1).days
                intervals.append(interval)
        
        if not intervals:
            continue
        
        # Check for periodicity (similar intervals)
        mean_interval = statistics.mean(intervals)
        stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Pattern detected if intervals are consistent (low standard deviation)
        coefficient_of_variation = stdev_interval / mean_interval if mean_interval > 0 else float('inf')
        
        if coefficient_of_variation < 0.3:  # Less than 30% variation
            patterns.append({
                'type': 'periodic_awards',
                'recipient': recipient,
                'agency': agency,
                'occurrence_count': len(award_list),
                'avg_interval_days': round(mean_interval, 1),
                'stdev_interval_days': round(stdev_interval, 1),
                'periodicity_score': round(1 - coefficient_of_variation, 2),  # Higher = more periodic
                'first_award': award_list[0].action_date.isoformat() if award_list[0].action_date else None,
                'last_award': award_list[-1].action_date.isoformat() if award_list[-1].action_date else None
            })
    
    # Sort by periodicity score (most periodic first)
    patterns.sort(key=lambda x: x['periodicity_score'], reverse=True)
    
    return patterns


def get_comprehensive_pattern_analysis(
    db: Session,
    entity_name: str = None,
    threshold_std_devs: float = 2.0,
    time_window_days: int = 30,
    min_gap_days: int = 180
) -> Dict:
    """
    Run comprehensive pattern detection analysis
    
    Returns:
        Dictionary with all detected patterns and anomalies
    """
    spikes = detect_spending_spikes(db, entity_name, threshold_std_devs)
    clusters = detect_award_clustering(db, entity_name, time_window_days)
    
    gaps = []
    periodic = []
    
    if entity_name:  # Entity-specific analysis
        gaps = detect_funding_gaps(db, entity_name, min_gap_days)
        periodic = detect_periodic_patterns(db, entity_name)
    
    return {
        'entity': entity_name,
        'spending_spikes': spikes[:10],  # Top 10
        'award_clusters': clusters[:10],  # Top 10
        'funding_gaps': gaps[:10],  # Top 10
        'periodic_patterns': periodic[:10],  # Top 10
        'summary': {
            'spikes_detected': len(spikes),
            'clusters_detected': len(clusters),
            'gaps_detected': len(gaps),
            'patterns_detected': len(periodic)
        }
    }

