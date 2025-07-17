from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProcessingRunCreate(BaseModel):
    name: Optional[str] = None
    folder_path: str
    total_files: int
    successful: int
    errors: int
    success_rate: float
    invoices: Optional[List[str]] = []
    excel_report_path: Optional[str] = None
    started_at: datetime
    ended_at: datetime
