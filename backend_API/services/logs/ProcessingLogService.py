import logging
from fastapi import HTTPException
from backend_API.db.config import db
from backend_API.models.logs.ProcessingLogModel import ProcessingLogModel
from backend_API.schema.logs.ProcessingLogSchema import processing_log_schema, processing_logs_schema

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Search Log

def search_processing_log(field: str, key):
    
    try:
        log = db.processing_logs.find_one({field:key})

        if not log:
            return {"error": "Log not found"}
        
        print(log)
        return ProcessingLogModel(**processing_log_schema(log))
    except:
        raise{"error": "Log not found"}

