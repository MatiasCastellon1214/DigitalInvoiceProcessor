import os
import logging

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")  # ruta relativa desde utils
LOG_FILE = os.path.join(LOG_DIR, "procesador_facturas.log")

os.makedirs(LOG_DIR, exist_ok=True)  # ✅ crear el directorio justo al cargar el módulo

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 🔧 Agregamos codificación UTF-8 explícita al handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
