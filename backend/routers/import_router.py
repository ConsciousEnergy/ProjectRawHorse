from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from dependencies import get_db
from services.import_service import (
    SUPPORTED_TYPES,
    get_template_columns,
    parse_uploaded_rows,
    validate_and_import_rows,
)

router = APIRouter()


@router.get("/templates/{data_type}")
async def get_import_template(data_type: str):
    if data_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported data_type: {data_type}")
    return {"data_type": data_type, "columns": get_template_columns(data_type)}


@router.post("/offline")
async def import_offline_data(
    data_type: str = Form(...),
    dry_run: bool = Form(True),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if data_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported data_type: {data_type}")
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")

    try:
        payload = await file.read()
        rows = parse_uploaded_rows(payload, file.filename, data_type)
        result = validate_and_import_rows(db, data_type, rows, dry_run=dry_run)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Import failed: {exc}")
