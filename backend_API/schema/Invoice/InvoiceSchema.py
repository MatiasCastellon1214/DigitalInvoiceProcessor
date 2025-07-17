def invoice_schema(invoice) -> dict:
    # Obtener imágenes si existen
    images = []
    if invoice.get("image"):
        if isinstance(invoice["image"], list):
            image_ids = invoice["image"]
            images = [str(img_id) for img_id in image_ids]

    return {
        "id": str(invoice["_id"]),
        "invoice_file": invoice["invoice_file"],
        "complete_path": invoice["complete_path"],
        "image_url": invoice.get("image_url"),
        "timestamp": invoice["timestamp"],
        "company": invoice.get("company"),
        "date": invoice["date"],
        "invoice_number": invoice["invoice_number"],
        "total_price": invoice["total_price"],
        "currency": invoice["currency"],
        "number_of_items": invoice["number_of_items"],
        "main_description": invoice["main_description"],
        "cuit_ruc": invoice["cuit_ruc"],
        "address": invoice["address"],
        "phone": invoice["phone"],
        "email": invoice["email"],
        "status": invoice["status"],
        "error": invoice.get("error"),
        "raw_answer": invoice.get("raw_answer"),
        "created_at": invoice.get("created_at"),
        "updated_at": invoice.get("updated_at")
    }

def invoices_schema(invoices):
    return [invoice_schema(inv) for inv in invoices]
