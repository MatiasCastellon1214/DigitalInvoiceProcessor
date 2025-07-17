from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StatisticsProcessModel(BaseModel):
    id: Optional[str] = None
    process_date: datetime
    total_files: int
    successful: int
    errors: int
    success_rate: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
