
import os
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")


# ✅ Subir imagen a AWS S3
def upload_image_to_aws(file, key: str, content_type: str):
    s3 = boto3.client("s3")
    try:
        s3.upload_fileobj(
            file,
            AWS_S3_BUCKET,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{key}"
        return url
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


# ✅ Eliminar imagen de AWS S3
def delete_image_from_aws(s3_url: str):
    s3 = boto3.client("s3")

    if not s3_url.startswith(f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    bucket_key = s3_url.replace(f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/", "")

    try:
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=bucket_key)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")


# ✅ Función auxiliar semántica (opcional)
def delete_image_book_invoice_aws(s3_url: str):
    return delete_image_from_aws(s3_url)