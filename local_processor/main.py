import os
import sys
import logging
from dotenv import load_dotenv
from scripts.extractor import ProcesadorFacturasGemini
import google.generativeai as genai

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesador_facturas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('Main')

def main(max_archivos: int = None):
    """Procesa facturas desde la carpeta 'facturas/' y exporta los datos a un archivo Excel."""
    print("🚀 Iniciando el procesamiento de facturas...")

    # Cargar la clave de API desde el archivo .env
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        logger.error("No se pudo cargar la API key. Verifica el archivo .env.")
        print("❌ Error: No se encontró la API key. Crea un archivo .env con GEMINI_API_KEY.")
        sys.exit(1)
    
    logger.info(f"API_KEY cargada correctamente.")
    print(f"✅ Clave de API cargada.")

    # Verificar la conexión a la API de Gemini
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hola, esto es una prueba.")
        logger.info("Prueba de conexión a la API exitosa.")
        print("✅ Conexión con la API de Gemini verificada.")
    except Exception as e:
        logger.error(f"Error al conectar con la API: {e}")
        print(f"❌ Error al conectar con la API: {e}")
        sys.exit(1)

    # Procesar las facturas
    try:
        procesador = ProcesadorFacturasGemini(api_key=API_KEY)
        logger.info(f"Iniciando procesamiento de facturas en la carpeta 'facturas/'.")
        print(f"📂 Procesando facturas de la carpeta 'facturas/'...")
        resultados = procesador.procesar_carpeta_facturas("facturas", max_archivos=max_archivos)
        logger.info(f"Procesamiento completado. Exportando a Excel...")
        print(f"📄 Exportando datos a 'outputs/facturas_procesadas.xlsx'...")
        output_path = procesador.exportar_a_excel(resultados, "outputs/facturas_procesadas.xlsx")
        logger.info(f"Datos exportados correctamente a: {output_path}")
        print(f"🎉 ¡Listo! Los datos se exportaron a: {output_path}")
        
        # Mostrar estadísticas
        stats = procesador.generar_reporte_estadisticas(resultados)
        logger.info(f"Estadísticas: {stats['exitosos']} exitosos, {stats['errores']} errores de {stats['total_archivos']} archivos.")
        print(f"📊 Resumen: {stats['exitosos']} facturas procesadas con éxito, {stats['errores']} errores de {stats['total_archivos']} archivos.")
    except FileNotFoundError as e:
        logger.error(f"Error: La carpeta 'facturas/' no existe.")
        print(f"❌ Error: No se encontró la carpeta 'facturas/'. Asegúrate de que exista y contenga imágenes.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Permitir configurar max_archivos desde la línea de comandos
    import argparse
    parser = argparse.ArgumentParser(description="Procesa facturas y exporta los datos a Excel.")
    parser.add_argument("--max-archivos", type=int, default=None, help="Número máximo de facturas a procesar (opcional).")
    args = parser.parse_args()
    
    main(max_archivos=args.max_archivos)