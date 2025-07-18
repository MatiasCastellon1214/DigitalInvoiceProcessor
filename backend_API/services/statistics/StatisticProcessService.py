import logging

from backend_API.db.config import db
from backend_API.models.statistics.StatisticsProcessModel import StatisticsProcessModel
from backend_API.schema.statistics.StatisticsProcessSchema import statistic_process_schema

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_statistic_process(field:str, key):
    try:
        statistic = db.statistics.find_one({field:key})

        if not statistic:
            return {"error":"Statistic Processing not found"}
        
        print(statistic)
        return StatisticsProcessModel(**statistic_process_schema(statistic))
    
    except:
        raise{"error": "Statistic Process not found"}