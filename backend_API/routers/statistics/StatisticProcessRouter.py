from typing import List
from bson import ObjectId
from fastapi import APIRouter, status
from backend_API.db.config import db
from backend_API.models.statistics.StatisticsProcessModel import StatisticsProcessModel
from backend_API.schema.statistics.StatisticsProcessSchema import statistics_process_schema
from backend_API.services.statistics.StatisticProcessService import search_statistic_process

router = APIRouter(prefix="/statistics",
                   tags=["Statistics"],
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}})


# GET - All Statistics Process
@router.get("/",
            response_model=List[StatisticsProcessModel])
async def get_statistics():
    return statistics_process_schema(db.statistics.find())


# GET - Calling a Statistic Procress by id
@router.get("/{id}",
            response_model=StatisticsProcessModel)
async def get_statistic(id:str):
    return search_statistic_process('_id', ObjectId(id))