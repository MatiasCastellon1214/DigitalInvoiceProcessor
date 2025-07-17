from fastapi import APIRouter, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from backend_API.db.config import db
from backend_API.db.config.db import processing_run
from backend_API.services.processing.ProcessingService import ProcessingService


router = APIRouter(
    prefix="/process",
    tags=["processing"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

# GET - Health
@router.get("/health", status_code=200)
async def health_check():
    """
    Verifica si el router de procesamiento está disponible.
    """
    return {"message": "Processing service is running ✅"}



# POST
@router.post("/", status_code=status.HTTP_201_CREATED)
async def process_invoices(files: List[UploadFile] = File(...)):
    """
    Procesa una o varias imágenes de facturas:
    - Sube imágenes a S3
    - Procesa con Gemini
    - Guarda facturas, logs, estadísticas y el resumen
    """
    try:
        result = await ProcessingService.process_batch(files)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error durante el procesamiento: {str(e)}"}
        )


# GET - Run Process
@router.get("/runs")
async def list_processing_runs():
    runs_cursor = processing_run.find().sort("started_at", -1).limit(20)
    runs = []
    for run in runs_cursor:
        runs.append({
            "run_id": str(run["_id"]),
            "name": run.get("name"),
            "started_at": run.get("started_at"),
            "excel_report_path": run.get("excel_report_path")
        })
    return runs