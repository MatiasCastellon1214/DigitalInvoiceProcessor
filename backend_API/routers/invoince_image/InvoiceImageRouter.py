from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from backend_API.services.processing.ProcessingService import ProcessingService
from backend_API.utils.s3_utils import delete_image_from_aws, upload_image_to_aws
from backend_API.models.invoice_image.InvoiceImageModel import InvoiceImageModel
from backend_API.schema.invoice_image.InvoiceImageSchema import image_invoice_schema, image_invoices_schema
from backend_API.db.config import db
import logging



router = APIRouter(prefix="/image_invoice",
                   tags=["image_invoice"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})


def image_search_invoice(field: str, key):
    try:
        image_invoice = db.image_invoices.find_one({field: key})
        if not image_invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Invoice image not found")
        return InvoiceImageModel(**image_invoice_schema(image_invoice))
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching for the image: {str(e)}"
        )
    

# GET
@router.get("/", 
            response_model= List[InvoiceImageModel])
async def image_invoices():
    return image_invoices_schema(db.image_invoices.find())

# GET by ID
@router.get("/{id}", 
            response_model=InvoiceImageModel)
async def image_invoice(id: str):
    return image_search_invoice("_id", ObjectId(id))

#POST - Multiple files
@router.post("/", 
             response_model= List[InvoiceImageModel], 
             status_code= status.HTTP_201_CREATED)
async def create_image_invoice(files: List[UploadFile] = File(...)):#,
                                #invoice_id: str = Form(...)
    #if not invoice_id:
     #   raise HTTPException(
      #      status.HTTP_400_BAD_REQUEST, 
       #     detail="Invoice ID is required")
    try:    
        uploaded_images = []

        for file in files:
            # Verificar si ya existe una imagen con el mismo nombre
            existing_image = db.image_invoices.find_one({"image_url": {"$regex": f"{file.filename}$"}})
            if existing_image:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"An image with the name  {file.filename} already exists"
                )

            # Subir la imagen a AWS S3
            s3_url = upload_image_to_aws(file.file, file.filename, file.content_type)

            # Crear los metadatos de la imagen
            image_invoice_dict = {
                "image_url": s3_url,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insertar en MongoDB
            inserted_id = db.image_invoices.insert_one(image_invoice_dict).inserted_id

            # Recuperar el documento insertado
            new_image_invoice = image_invoice_schema(db.image_invoices.find_one({"_id": inserted_id}))
            uploaded_images.append(InvoiceImageModel(**new_image_invoice))

        return uploaded_images

        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing the request: {str(e)}"
        )


# PUT
@router.put("/{id}",
            response_model=InvoiceImageModel)
async def update_image_invoice(id: str, file: UploadFile = File(...)):
    
    image_invoice = image_search_invoice("_id", ObjectId(id))
    
    if type(image_invoice) != InvoiceImageModel:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, 
            detail="Image of invoice not found")
    
    # Eliminar la imagen del bucket S3
    current_s3_url = image_invoice.image_url
    if current_s3_url:
        try:
            delete_image_from_aws(current_s3_url)
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error deleting image of Invoice from AWS: {str(e)}")
    
    # Subir la nueva imagen a AWS S3
    try:
        s3_url = upload_image_to_aws(file.file, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error uploading image of Invoice to AWS: {str(e)}"
        )

    image_invoice_dict = {"image_url": s3_url, "updated_at": datetime.utcnow()}

    if not isinstance(s3_url, str) and 'error' in s3_url:
        raise HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR, 
        detail=s3_url["error"])
    
    # Actualizar la imagen de la factura en la base de datos
    db.image_invoices.update_one({"_id": ObjectId(id)}, {"$set": image_invoice_dict})

    return InvoiceImageModel(**image_invoice_schema(
        db.image_invoices.find_one({"_id": ObjectId(id)})))



  
# DELETE
@router.delete("/{id}", 
               status_code=status.HTTP_200_OK)
async def delete_image_invoice(id: str):

    try:
        # Buscar la imagen de la factura en la base de datos
        image = db.image_invoices.find_one({"_id": ObjectId(id)})
        if not image:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, 
                detail="Image of Invoice not found"
            )


        # Eliminar la referencia de la imagen en la factura
        #if "invoice_id" in image:
         #   db.invoices.update_one(
          #      #{"_id": ObjectId(image["invoice_id"])}, 
           #     {"$pull": {"image": ObjectId(id)}}
            #)

        # Eliminar la imagen
        if "image_url" in image:
            try:
                delete_image_from_aws(image["image_url"])
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error eliminando la imagen de AWS: {str(e)}"
                )

        # Eliminar la imagen de la factura de la base de datos
        db.image_invoices.delete_one({"_id": ObjectId(id)})    

        return {"message": "Image of Invoice deleted successfully"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="ID inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando la solicitud: {str(e)}"
        )
    
