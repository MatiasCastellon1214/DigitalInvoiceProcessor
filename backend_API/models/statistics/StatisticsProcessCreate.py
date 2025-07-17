from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StatisticsProcessCreate(BaseModel):
    process_date: datetime
    total_files: int
    successful: int
    errors: int
    success_rate: float
    
