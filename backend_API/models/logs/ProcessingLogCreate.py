from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProcessingLogCreate(BaseModel):
    
    invoice_filename: str
    image_url: str
    status: str  # "success" | "error"
    error_message: Optional[str] = None
    processing_run_id: Optional[str] = None
    created_at: datetime
