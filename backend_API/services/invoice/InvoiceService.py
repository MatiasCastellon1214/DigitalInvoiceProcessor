import os
import logging
import pandas as pd
from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime
from typing import List
from backend_API.db.config import db
from backend_API.models.invoice.InvoiceModel import InvoiceModel
from backend_API.schema.Invoice.InvoiceSchema import invoice_schema
from backend_API.utils.config import UPLOADS_DIR, REPORTS_DIR
from backend_API.utils.gemini_utils import extract_invoice_data
from backend_API.models.invoice.InvoiceCreate import InvoiceCreate
from backend_API.models.processing.ProcessingRunCreate import ProcessingRunCreate
from backend_API.models.statistics.StatisticsProcessCreate import StatisticsProcessCreate
from bson.errors import InvalidId
from pydantic import ValidationError

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

UPLOADS_DIR = "uploads"
REPORTS_DIR = "reports"

# Instance of the extractor
#extractor = ProcesadorFacturasGemini(api_key=os.getenv("GEMINI_API_KEY"))

# Mapeo de nombres de columnas para el Excel (más legibles)
column_labels = {
    "invoice_file": "Invoice File",
    "complete_path": "Path",
    "image_url": "Image URL",
    "timestamp": "Processing Timestamp",
    "company": "Company",
    "date": "Invoice Date",
    "invoice_number": "Invoice Number",
    "total_price": "Total Price",
    "currency": "Currency",
    "number_of_items": "Items",
    "main_description": "Main Description",
    "cuit_ruc": "Tax ID",
    "address": "Address",
    "phone": "Phone",
    "email": "Email",
    "status": "Status",
    "error": "Error",
    "raw_answer": "Raw Gemini Output",
    "created_at": "Created At",
    "updated_at": "Updated At",
}


async def process_batch(files: List, folder_path: str) -> dict:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    processed = []
    start_time = datetime.now()

    for file in files:
        save_path = os.path.join(UPLOADS_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        success, data, error = extract_invoice_data(save_path)
        timestamp = datetime.now()

        entry = {
            "invoice_file": file.filename,
            "complete_path": save_path,
            "timestamp": timestamp,
            "status": "Success" if success else "Error",
            "error": error,
            "raw_answer": data if success else None,
        }

        if success:
            entry.update(data)

        processed.append(entry)


    # Procesar resultados
    invoice_ids = []
    success_rows, error_rows = [], []
    success_count, error_count = 0, 0

    for item in processed:
        if item["status"] == "Success":
            success_count += 1
            inv = InvoiceCreate(
                invoice_file=item["invoice_file"],
                complete_path=item["complete_path"],
                image_url=None,
                timestamp=item["timestamp"],
                company=item.get("company", "Not found"),
                date=datetime.fromisoformat(item.get("date")) if item.get("date") else item["timestamp"],
                invoice_number=item.get("invoice_number", "Not found"),
                total_price=float(item.get("total_price", 0)),
                currency=item.get("currency", "Not found"),
                number_of_items=int(item.get("number_of_items", 0)),
                main_description=item.get("main_description", "Not found"),
                cuit_ruc=item.get("cuit_ruc", "Not found"),
                address=item.get("address", "Not found"),
                phone=item.get("phone", "Not found"),
                email=item.get("email"),
                status="Success",
                raw_answer=str(item["raw_answer"]),
            )
            res = await db.invoices.insert_one(inv.dict())
            invoice_ids.append(str(res.inserted_id))
            success_rows.append(inv.dict())
        else:
            error_count += 1
            error_rows.append(item)

    # Exportar Excel
    timestamp_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    excel_path = REPORTS_DIR / f"invoice_report_{timestamp_str}.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        if success_rows:
            df_success = pd.DataFrame(success_rows)
            df_success.rename(columns=column_labels, inplace=True)
            df_success.to_excel(writer, sheet_name="Invoices", index=False)

    if error_rows:
        df_errors = pd.DataFrame(error_rows)
        df_errors.rename(columns=column_labels, inplace=True)
        df_errors.to_excel(writer, sheet_name="Errors", index=False)


    # Guardar estadísticas
    stats = StatisticsProcessCreate(
        process_date=start_time,
        total_files=len(files),
        successful=success_count,
        errors=error_count,
        success_rate=(success_count / len(files)) * 100 if files else 0
    )
    await db.statistics.insert_one(stats.dict())

    # Guardar corrida
    run = ProcessingRunCreate(
        name=f"Run_{timestamp_str}",
        folder_path=folder_path,
        total_files=len(files),
        successful=success_count,
        errors=error_count,
        success_rate=(success_count / len(files)) * 100,
        invoices=invoice_ids,
        excel_report_path=str(excel_path),
        started_at=start_time,
        ended_at=datetime.now()
    )
    await db.runs.insert_one(run.dict())

    return {
        "summary": {
            "total": len(files),
            "success": success_count,
            "errors": error_count,
            "excel_report_path": str(excel_path)
        }
    }


# Search Invoice
def search_invoice(field: str, key: str):
    try:
        logger.info(f"Searching invoice with {field} = {key}")

        if field == "_id":
            try:
                key = ObjectId(key)
            except InvalidId:
                logger.warning(f"Invalid ObjectId format: {key}")
                raise HTTPException(status_code=400, detail="Invalid invoice ID format")

        invoice = db.invoices.find_one({field: key})

        if not invoice:
            logger.warning(f"Invoice not found: {field} = {key}")
            #raise HTTPException(status_code=404, detail="Invoice not found")
            return None
        logger.info(f"Invoice found: {invoice}")

        parsed_invoice = invoice_schema(invoice)
        logger.info(f"Parsed invoice: {parsed_invoice}")

        return InvoiceModel(**parsed_invoice)

    except ValidationError as ve:
        logger.error(f"Validation error: {ve}", exc_info=True)
        raise HTTPException(status_code=422, detail="Invalid invoice data format")
    except Exception as e:
        logger.error(f"Error searching invoice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


# Create Invoice
def create_invoice(invoice: InvoiceCreate):
    try:
        logger.info(f"Creating Invoice: {invoice.invoice_file}")

        existing_invoice = search_invoice('invoice_file', invoice.invoice_file)
        if existing_invoice:
            logger.warning(f"Invoice already exists: {invoice.invoice_file}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Invoice already exists'
            )

        invoice_dict = invoice.dict()
        invoice_dict["created_at"] = datetime.now()

        id = db.invoices.insert_one(invoice_dict).inserted_id

        logger.info(f"Invoice created with ID: {id}")

        new_invoice = invoice_schema(db.invoices.find_one({'_id': id}))

        return InvoiceModel(**new_invoice)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error creating invoice'
        )
    

# Update Invoice
async def update_invoice(id: str, invoice: InvoiceModel):
    try:
        logger.info(f"Updating Invoice with ID: {id}")

        if not ObjectId.is_valid(id):
            logger.error(f"Invalid invoice ID format: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ivoice ID"
            )

        existing_invoice = db.invoices.find_one({"_id": ObjectId(id)})
        if not existing_invoice:
            logger.warning(f"Invoice not found with ID: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Invoice not found'
            )

        invoice_dict = invoice.model_dump(exclude='id')
        invoice_dict["updated_at"] = datetime.now()

        result = db.invoices.find_one_and_update(
            {'_id': ObjectId(id)},
            {'$set': invoice_dict},
            return_document=True
        )

        if result is None:
            logger.warning(f"Invoice not updated, not found: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Invoice not found'
            )

        logger.info(f"Invoice updated: {result}")
        return InvoiceModel(**invoice_schema(result))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred: {e}'
        )


# Delete Invoice
def delete_existing_invoice(id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid invoice Id'
        )
    
    invoice_found = db.invoices.find_one({'_id': ObjectId(id)})

    if not invoice_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    db.invoices.delete_one({'_id': ObjectId(id)})

    
    return InvoiceModel(**invoice_schema(invoice_found))