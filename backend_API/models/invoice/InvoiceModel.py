from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class InvoiceModel(BaseModel):
    id: Optional[str] = None
    invoice_file: str
    complete_path: str
    image_url: Optional[str] = None  # ✅ Ruta o URL accesible de la imagen
    timestamp: datetime
    company: Optional[str] = None
    date: datetime  # ✅ Ideal convertir a datetime si es posible
    invoice_number: str
    total_price: float
    currency: str
    number_of_items: int
    main_description: str
    cuit_ruc: str
    address: str
    phone: str
    email: Optional[EmailStr] = None
    status: str
    error: Optional[str] = None
    raw_answer: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
