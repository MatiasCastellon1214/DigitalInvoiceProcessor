from fastapi import APIRouter, status
from backend_API.db.config import db
from bson import ObjectId
from backend_API.models.logs.ProcessingLogModel import ProcessingLogModel
from backend_API.services.logs.ProcessingLogService import search_processing_log
from backend_API.schema.logs.ProcessingLogSchema import processing_logs_schema

router = APIRouter(prefix="/logs", 
                   tags=["Logs"],
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}})


# GET - All Logs
@router.get("/", 
            response_model=list[ProcessingLogModel])
async def list_logs():
    return processing_logs_schema(db.processing_logs.find())


# GET - Calling a Log by id
@router.get("/{id}", 
            response_model=ProcessingLogModel)
async def log(id: str):
    return search_processing_log('_id', ObjectId(id))
