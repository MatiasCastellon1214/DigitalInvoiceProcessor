from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend_API.db.config.db import db
from bson import ObjectId
import os

router = APIRouter(prefix="/processing/download", 
                   tags=["Processing"])

@router.get("/{run_id}", 
            summary="Download Excel report of the processing")
async def download_excel_report(run_id: str):
    try:
        run = db.runs.find_one({"_id": ObjectId(run_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if not run:
        raise HTTPException(status_code=404, detail="Run ID not found")

    excel_path = run.get("excel_report_path")
    if not excel_path or not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="Excel file not found")

    return FileResponse(
        path=excel_path,
        filename=os.path.basename(excel_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
