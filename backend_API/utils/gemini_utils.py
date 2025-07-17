import os
import json
import re
import google.generativeai as genai
from pathlib import Path
from PIL import Image
from backend_API.utils.config import SUPPORTED_FORMATS
from backend_API.utils.logger import setup_logger
from pydantic import EmailStr, ValidationError

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

logger = setup_logger("GeminiUtils")


def limpiar_json_response(response_text: str) -> str:
    patrones = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
        r'(\{.*?\})'
    ]
    for pattern in patrones:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            return match.group(1)
    return response_text


def get_prompt() -> str:
    return """
Analiza esta factura y extrae los siguientes datos en formato JSON válido.
Si algún campo no está presente, usa "No encontrado" como valor.

Formato requerido:
{
    "empresa": "nombre completo de la empresa emisora",
    "fecha": "YYYY-MM-DD",
    "numero_factura": "...",
    "precio_total": "solo números",
    "moneda": "ARS, USD, etc.",
    "cantidad_items": "...",
    "descripcion_principal": "...",
    "cuit_ruc": "...",
    "direccion": "...",
    "telefono": "...",
    "email": "..."
}
IMPORTANTE: RESPONDE SOLO con el JSON. No agregues texto antes ni después.
"""




def is_valid_image(path: str) -> bool:
    try:
        ext = Path(path).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            return False
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.error(f"Invalid image {path}: {e}")
        return False


def extract_invoice_data(path: str) -> tuple[bool, dict, str]:
    logger.info(f"📥 Procesando imagen: {path}")
    if not is_valid_image(path):
        logger.error(f"❌ Imagen inválida: {path}")
        return False, {}, f"Invalid or unsupported file: {path}"

    try:
        image = Image.open(path)
        prompt = get_prompt()
        response = model.generate_content([prompt, image])
        logger.info(f"📤 Respuesta cruda Gemini:\n{response.text}")
        clean_json = limpiar_json_response(response.text)
        
        try:
            data = json.loads(clean_json)
            logger.info(f"✅ JSON extraído correctamente para {path}")
            return True, data, None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            return False, {}, f"JSON decode error: {str(e)}"
        
        #return True, json.loads(clean_json), None
    except Exception as e:
        logger.error(f"❌ Error general Gemini: {e}")
        return False, {}, str(e)

def parse_safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def parse_safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
    

def parse_safe_email(value: str) -> str | None:
    try:
        return EmailStr(value)
    except (ValidationError, TypeError):
        return None

