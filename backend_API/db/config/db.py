# config/db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Cargar archivo .env

try:
    MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017/dip")
    client = MongoClient(MONGO_DB_URL)
    db = client.get_database()  # Usa la base de datos especificada en MONGO_DB_URL (ej., 'dip')
    print(f"✅ Conectado a la base de datos: {db.name}")

    # Definir colecciones
    invoices = db["invoices"]
    statistics_process = db["statistics_process"]
    processing_run = db["processing_run"]
    image_invoices = db["image_invoices"]  # Agregar la nueva colección
    processing_run = db["runs"]
    processing_logs = db["processing_logs"]

except Exception as e:
    print(f"❌ Error de conexión: {e}")
    raise