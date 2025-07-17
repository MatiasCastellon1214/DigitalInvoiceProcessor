from bson import ObjectId
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import List
from fastapi.responses import JSONResponse
from backend_API.db.config import db
from backend_API.models.invoice.InvoiceCreate import InvoiceCreate
from backend_API.schema.Invoice.InvoiceSchema import invoices_schema
from backend_API.models.invoice.InvoiceModel import InvoiceModel
from backend_API.services.invoice.InvoiceService import create_invoice, delete_existing_invoice, process_batch, search_invoice, update_invoice

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)


# GET - All Invoices
@router.get("/",
            response_model=List[InvoiceModel])
async def get_invoice():
    return invoices_schema(db.invoices.find())


# GET - Calling an invoice by id - Path
@router.get("/{id}", response_model=InvoiceModel)
async def get_invoice(id: str):
    invoice = search_invoice('_id', ObjectId(id))
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice



# POST
@router.post("/",
             response_model=InvoiceModel,
             status_code=status.HTTP_201_CREATED)
async def create_new_invoice(invoice: InvoiceCreate):
    return create_invoice(invoice)


# PUT
@router.put("/{id}",
            response_model=InvoiceModel)
async def update_existing_invoice(id:str, invoice:InvoiceCreate):
    return await update_invoice(id, invoice)


# DELETE
@router.delete("/{id}",
               response_model=InvoiceModel)
async def delete_invoice(id:str):
    return delete_existing_invoice(id)