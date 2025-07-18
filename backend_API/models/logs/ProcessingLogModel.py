from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProcessingLogModel(BaseModel):
    id: Optional[str]
    invoice_filename: str
    image_url: str
    status: str  # "success" | "error"
    error_message: Optional[str] = None
    processing_run_id: Optional[str] = None
    created_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
