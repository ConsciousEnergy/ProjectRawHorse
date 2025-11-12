"""
Export API routes for CSV, JSON, and PDF generation
"""
import io
import csv
import json
from typing import List
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from database import Entity, MoneyFlow, Award, FOIATarget
from models.schemas import ExportRequest

# Import database dependency
from dependencies import get_db

router = APIRouter()


@router.get("/csv/entities")
async def export_entities_csv(
    db: Session = Depends(get_db)
):
    """Export entities to CSV"""
    entities = db.query(Entity).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['entity_id', 'display_name', 'normalized_name', 'entity_type'])
    
    # Write data
    for e in entities:
        writer.writerow([e.entity_id, e.display_name, e.normalized_name, e.entity_type])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=entities.csv"}
    )


@router.get("/csv/money-flows")
async def export_money_flows_csv(
    db: Session = Depends(get_db)
):
    """Export money flows to CSV"""
    flows = db.query(MoneyFlow).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['source', 'target', 'relationship', 'amount_usd', 'start_date', 'source_citation'])
    
    # Write data
    for f in flows:
        writer.writerow([
            f.source, f.target, f.relationship, f.amount_usd,
            f.start_date.isoformat() if f.start_date else '',
            f.source_citation
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=money_flows.csv"}
    )


@router.get("/csv/awards")
async def export_awards_csv(
    db: Session = Depends(get_db)
):
    """Export awards to CSV"""
    awards = db.query(Award).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'piid', 'recipient_name', 'recipient_uei', 'awarding_agency',
        'award_amount', 'action_date', 'description', 'naics_code'
    ])
    
    # Write data
    for a in awards:
        writer.writerow([
            a.piid, a.recipient_name, a.recipient_uei, a.awarding_agency,
            a.award_amount,
            a.action_date.isoformat() if a.action_date else '',
            a.description, a.naics_code
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=awards.csv"}
    )


@router.get("/json/entities")
async def export_entities_json(
    db: Session = Depends(get_db)
):
    """Export entities to JSON"""
    entities = db.query(Entity).all()
    
    data = [
        {
            "entity_id": e.entity_id,
            "display_name": e.display_name,
            "normalized_name": e.normalized_name,
            "entity_type": e.entity_type
        }
        for e in entities
    ]
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=entities.json"}
    )


@router.get("/json/money-flows")
async def export_money_flows_json(
    db: Session = Depends(get_db)
):
    """Export money flows to JSON"""
    flows = db.query(MoneyFlow).all()
    
    data = [
        {
            "source": f.source,
            "target": f.target,
            "relationship": f.relationship,
            "amount_usd": f.amount_usd,
            "start_date": f.start_date.isoformat() if f.start_date else None,
            "source_citation": f.source_citation
        }
        for f in flows
    ]
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=money_flows.json"}
    )


@router.get("/pdf/summary")
async def export_summary_pdf(
    db: Session = Depends(get_db)
):
    """Export summary report to PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Project RawHorse - Summary Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Get statistics
    total_entities = db.query(Entity).count()
    total_flows = db.query(MoneyFlow).count()
    total_awards = db.query(Award).count()
    
    # Add statistics
    stats_text = f"""
    <b>Database Statistics:</b><br/>
    Total Entities: {total_entities}<br/>
    Total Money Flows: {total_flows}<br/>
    Total Awards: {total_awards}<br/>
    """
    stats = Paragraph(stats_text, styles['Normal'])
    story.append(stats)
    story.append(Spacer(1, 12))
    
    # Top entities by money flow
    story.append(Paragraph("<b>Top Entities by Money Flow:</b>", styles['Heading2']))
    story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=uap_summary.pdf"}
    )
