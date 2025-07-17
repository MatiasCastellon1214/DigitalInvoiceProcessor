import io
import os
import json
import uuid
import pandas as pd
from datetime import datetime
from typing import List
from fastapi import UploadFile
from backend_API.utils.s3_utils import upload_image_to_aws
from backend_API.utils.gemini_utils import extract_invoice_data, parse_safe_email, parse_safe_float, parse_safe_int
from backend_API.db.config.db import db
from backend_API.models.invoice.InvoiceCreate import InvoiceCreate
from backend_API.models.logs.ProcessingLogCreate import ProcessingLogCreate
from backend_API.models.statistics.StatisticsProcessCreate import StatisticsProcessCreate
from backend_API.models.processing.ProcessingRunCreate import ProcessingRunCreate

# Configuración
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ProcessingService:
    @staticmethod
    async def process_batch(files: List[UploadFile]) -> dict:
        processed = []
        extracted_data = []
        start_time = datetime.utcnow()
        today_path = start_time.strftime("%Y/%m/%d")
        invoice_ids = []
        logs = []

        for file in files:
            try:
                
                # Leer archivo una sola vez
                content = await file.read()
                unique_name = f"{uuid.uuid4()}_{file.filename}"
                s3_path = f"{today_path}/{unique_name}"

                image_url = upload_image_to_aws(io.BytesIO(content), s3_path, file.content_type)


                # Guardado temporal para Gemini (si lo necesita localmente)
                temp_path = f"temp/{unique_name}"
                os.makedirs("temp", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(content)

                # Procesamiento con Gemini
                success, data, error = extract_invoice_data(temp_path)

                os.remove(temp_path)

                timestamp = datetime.utcnow()
                raw_data = json.dumps(data) if success else None

                if success:
                    try:
                        
                        datos = data

                        inv = InvoiceCreate(
                            invoice_file=file.filename,
                            complete_path=s3_path,
                            image_url=image_url,
                            timestamp=timestamp,
                            company=datos.get("empresa", "No encontrado"),
                            date=datetime.fromisoformat(datos.get("fecha")) if datos.get("fecha") else timestamp,
                            invoice_number=datos.get("numero_factura", "No encontrado"),
                            total_price=parse_safe_float(datos.get("precio_total")),
                            currency=datos.get("moneda", "No encontrado"),
                            number_of_items=parse_safe_int(datos.get("cantidad_items")),
                            main_description=datos.get("descripcion_principal", "No encontrado"),
                            cuit_ruc=datos.get("cuit_ruc", "No encontrado"),
                            address=datos.get("direccion", "No encontrado"),
                            phone=datos.get("telefono", "No encontrado"),
                            email=parse_safe_email(datos.get("email")),
                            status="Success",
                            raw_answer=raw_data,
                        )


                        res = db.invoices.insert_one(inv.dict())
                        invoice_ids.append(str(res.inserted_id))

                        logs.append(ProcessingLogCreate(
                            invoice_filename=file.filename,
                            image_url=image_url,
                            status="Success",
                            processing_run_id=None,  # se agregará después
                            created_at=timestamp
                        ).dict())

                        extracted_data.append({
                            "invoice_filename": file.filename,
                            "image_url": image_url,
                            "company": inv.company,
                            "date": inv.date,
                            "invoice_number": inv.invoice_number,
                            "total_price": inv.total_price,
                            "currency": inv.currency,
                            "number_of_items": inv.number_of_items,
                            "main_description": inv.main_description,
                            "cuit_ruc": inv.cuit_ruc,
                            "address": inv.address,
                            "phone": inv.phone,
                            "email": inv.email,
                        })


                    except Exception as json_error:
                        logs.append(ProcessingLogCreate(
                            invoice_filename=file.filename,
                            image_url=image_url,
                            status="Error",
                            error_message=f"Error parseando JSON: {json_error}",
                            created_at=timestamp
                        ).dict())
                else:
                    logs.append(ProcessingLogCreate(
                        invoice_filename=file.filename,
                        image_url=image_url,
                        status="Error",
                        error_message=error,
                        created_at=timestamp
                    ).dict())

            except Exception as e:
                logs.append(ProcessingLogCreate(
                    invoice_filename=file.filename,
                    image_url="N/A",
                    status="Error",
                    error_message=str(e),
                    created_at=datetime.utcnow()
                ).dict())

        # Resumen
        total_files = len(files)
        successful = len([l for l in logs if l["status"] == "Success"])
        errors = total_files - successful
        success_rate = (successful / total_files * 100) if total_files > 0 else 0

        # Guardar estadísticas
        stats = StatisticsProcessCreate(
            process_date=start_time,
            total_files=total_files,
            successful=successful,
            errors=errors,
            success_rate=success_rate
        )
        db.statistics.insert_one(stats.dict())

        # Exportar Excel
        filename_base = start_time.strftime("invoice_report_%Y-%m-%dT%H-%M-%S")
        excel_name = f"{filename_base}.xlsx"
        excel_path = f"reports/{excel_name}"
        os.makedirs("reports", exist_ok=True)

        df_success = pd.DataFrame([l for l in logs if l["status"] == "Success"])
        df_error = pd.DataFrame([l for l in logs if l["status"] == "Error"])
        df_extracted = pd.DataFrame(extracted_data)

        with pd.ExcelWriter(excel_path) as writer:
            if not df_extracted.empty:
                df_extracted.to_excel(writer, sheet_name="ExtractedData", index=False)
            if not df_success.empty:
                df_success.to_excel(writer, sheet_name="Logs_Success", index=False)
            if not df_error.empty:
                df_error.to_excel(writer, sheet_name="Logs_Errors", index=False)


        # Crear ProcessingRun
        run = ProcessingRunCreate(
            name=filename_base,
            folder_path=today_path,
            total_files=total_files,
            successful=successful,
            errors=errors,
            success_rate=success_rate,
            invoices=invoice_ids,
            excel_report_path=excel_path,
            started_at=start_time,
            ended_at=datetime.utcnow()
        )
        res = db.runs.insert_one(run.dict())
        run_id = str(res.inserted_id)

        # Actualizar logs con processing_run_id
        for log in logs:
            log["processing_run_id"] = run_id
            db.processing_logs.insert_one(log)

        return {
            "run_id": run_id,
            "summary": {
                "total": total_files,
                "success": successful,
                "errors": errors,
                "success_rate": success_rate,
                "excel_report": excel_path,
                "invoices": invoice_ids
            }
        }
