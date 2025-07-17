from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvoiceImageCreate(BaseModel):
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
