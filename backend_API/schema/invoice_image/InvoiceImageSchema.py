from bson import ObjectId


def image_invoice_schema(image_invoice) -> dict:
    if isinstance(image_invoice, ObjectId):
        # Si recibimos un ObjectId, solo devolvemos un string
        return str(image_invoice)
    
    """
    Convierte un documento de imagen de factura en un diccionario con claves estandarizadas.
    """
    return {
        "id": str(image_invoice["_id"]),
        "image_url": image_invoice.get("image_url"),
        "created_at": image_invoice.get("created_at"),
        "updated_at": image_invoice.get("updated_at")
    }

def image_invoices_schema(image_invoices) -> list:

    if not image_invoices:
        return []
    
    """
    Convierte una lista de documentos de imágenes de facturas en una lista de diccionarios.
    """
    # Si es una lusta de ObjectId, convertirlas directamente
    if isinstance(image_invoices, ObjectId):
        return [str(image_invoice) for image_invoice in image_invoices]

    return [image_invoice_schema(image_invoice) for image_invoice in image_invoices]
    
