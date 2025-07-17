from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProcessingRunModel(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None  # nombre opcional (podés usar la fecha o un nombre único)
    folder_path: str
    total_files: int
    successful: int
    errors: int
    success_rate: float
    invoices: List[str] = []
    excel_report_path: Optional[str] = None
    started_at: datetime
    ended_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
