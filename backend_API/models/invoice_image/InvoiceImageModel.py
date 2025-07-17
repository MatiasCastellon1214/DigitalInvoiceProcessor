from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvoiceImageModel(BaseModel):
    id: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
