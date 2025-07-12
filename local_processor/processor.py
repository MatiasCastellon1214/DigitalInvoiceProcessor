import datetime
import logging
import re
from typing import Dict, List, Optional
import google.generativeai as genai
from PIL import Image
import pandas as pd
import os
import json
from pathlib import Path

class ProcesadorFacturasGemini:
    """
    Procesador de facturas usando Google Gemini AI para extraer datos estructurados
    """
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash'):
        """
        Inicializa el procesador de facturas
        
        Args:
            api_key: Clave API de Google Gemini
            model_name: Nombre del modelo a utilizar
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.logger = self._setup_logger()

        self.formatos_soportados = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif"]

    def _setup_logger(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger('ProcesadorFacturas')
        logger.setLevel(logging.INFO)
        
        # Crear handler para archivo
        file_handler = logging.FileHandler('procesador_facturas.log')
        file_handler.setLevel(logging.INFO)
        
        # Crear handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def validar_imagen(self, ruta_imagen: str) -> bool:
        """
        Valida si el archivo es una imagen válida
        
        Args:
            ruta_imagen: Ruta al archivo de imagen
            
        Returns:
            True si es válida, False en caso contrario
        """
        try:
            extension = Path(ruta_imagen).suffix.lower()
            if extension not in self.formatos_soportados:
                return False
                
            # Intentar abrir la imagen
            with Image.open(ruta_imagen) as img:
                img.verify()
            return True
        except Exception as e:
            self.logger.error(f"Error validando imagen {ruta_imagen}: {e}")
            return False
    
    def extraer_datos_factura(self, ruta_imagen):
        """
        Extrae datos de una factura usando Gemini AI
        
        Args:
            ruta_imagen: Ruta a la imagen de la factura
            
        Returns:
            Diccionario con los datos extraídos
        """
        if not self.validar_imagen(ruta_imagen):
            raise ValueError(f"Imagen no válida: {ruta_imagen}")
        imagen = Image.open(ruta_imagen)
        
        prompt = """
        Analiza esta factura y extrae los siguientes datos en formato JSON válido.
        Si algún campo no está presente, usa "No encontrado" como valor.
        
        Formato requerido:
        {
            "empresa": "nombre completo de la empresa emisora",
            "fecha": "fecha de emisión (formato YYYY-MM-DD si es posible)",
            "numero_factura": "número o código de factura",
            "precio_total": "monto total (solo números, sin símbolos de moneda)",
            "moneda": "tipo de moneda (USD, EUR, ARS, etc.)",
            "cantidad_items": "número total de items/productos",
            "descripcion_principal": "descripción del producto/servicio principal",
            "cuit_ruc": "CUIT, RUC o identificación fiscal",
            "direccion": "dirección de la empresa",
            "telefono": "teléfono de contacto",
            "email": "correo electrónico si está disponible"
        }
        
        IMPORTANTE: Responde SOLO con el JSON válido, sin texto adicional antes o después.
        """
        
        try:
            response = self.model.generate_content([prompt, imagen])
            return {
                'success': True,
                'data': response.text,
                'error': None
            }
        except Exception as e:
            self.logger.error(f"Error procesando {ruta_imagen}: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def limpiar_json_response(self, response_text: str) -> str:
        """
        Limpia la respuesta para extraer solo el JSON válido
        
        Args:
            response_text: Texto de respuesta del modelo
            
        Returns:
            JSON limpio como string
        """
        # Buscar JSON entre ```json y ``` o entre { y }
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{.*?\})'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                return match.group(1)
        
        return response_text

        
    def procesar_carpeta_facturas(self, carpeta_facturas: str, 
                                 max_archivos: Optional[int] = None) -> List[Dict]:
        """
        Procesa todas las facturas en una carpeta
        
        Args:
            carpeta_facturas: Ruta a la carpeta con facturas
            max_archivos: Número máximo de archivos a procesar (None para todos)
            
        Returns:
            Lista de diccionarios con los datos extraídos
        """

        if not os.path.exists(carpeta_facturas):
            raise FileNotFoundError(f"La carpeta {carpeta_facturas} no existe")
        
        datos_extraidos = []
        archivos_procesados = 0

        # Obtener lista de archivos de imagen
        archivos_imagen = []
        
        for archivo in os.listdir(carpeta_facturas):
            if Path(archivo).suffix.lower() in self.formatos_soportados:
                archivos_imagen.append(archivo)
        
        self.logger.info(f"Encontrados {len(archivos_imagen)} archivos de imagen")
        
        for archivo in archivos_imagen:
            if max_archivos and archivos_procesados >= max_archivos:
                break
                
            ruta_completa = os.path.join(carpeta_facturas, archivo)
            self.logger.info(f"Procesando: {archivo}")
            
            resultado = self.extraer_datos_factura(ruta_completa)
            
            datos_extraidos.append({
                'archivo': archivo,
                'ruta_completa': ruta_completa,
                'timestamp': datetime.datetime.now().isoformat(),
                'resultado': resultado
            })
            
            archivos_procesados += 1
        
        self.logger.info(f"Procesados {archivos_procesados} archivos")
        return datos_extraidos
    
    def exportar_a_excel(self, datos_extraidos: List[Dict], nombre_archivo: str ="facturas_procesadas.xlsx") -> str:
        """
        Exporta los datos extraídos a un archivo Excel
        
        Args:
            datos_extraidos: Lista de datos extraídos
            nombre_archivo: Nombre del archivo Excel
            
        Returns:
            Ruta del archivo creado
        """
        filas = []
        errores = []
        
        for item in datos_extraidos:
            fila_base = {
                'Archivo': item['archivo'],
                'Fecha_Procesamiento': item['timestamp'],
                'Estado': 'Éxito' if item['resultado']['success'] else 'Error'
            }
            
            if item['resultado']['success']:
                # Limpiar y parsear JSON
                json_limpio = self.limpiar_json_response(item['resultado']['data'])
                #datos_json = json.loads(json_limpio)

                try:
                    # Intentar parsear JSON
                    #datos_json = json.loads(item['datos_json'])
                    datos_json = json.loads(json_limpio)
                    fila = {
                        **fila_base,
                        'Empresa': datos_json.get('empresa', 'No encontrado'),
                        'Fecha_Factura': datos_json.get('fecha', 'No encontrado'),
                        'Número_Factura': datos_json.get('numero_factura', 'No encontrado'),
                        'Precio_Total': datos_json.get('precio_total', 'No encontrado'),
                        'Moneda': datos_json.get('moneda', 'No encontrado'),
                        'Cantidad_Items': datos_json.get('cantidad_items', 'No encontrado'),
                        'Descripción': datos_json.get('descripcion_principal', 'No encontrado'),
                        'CUIT_RUC': datos_json.get('cuit_ruc', 'No encontrado'),
                        'Dirección': datos_json.get('direccion', 'No encontrado'),
                        'Teléfono': datos_json.get('telefono', 'No encontrado'),
                        'Email': datos_json.get('email', 'No encontrado')
                    }
                    filas.append(fila)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parseando JSON para {item['archivo']}: {e}")
                    errores.append({
                        **fila_base,
                        'Error': f"Error JSON: {e}",
                        'Respuesta_Cruda': item['resultado']['data']
                    })
            else:
                errores.append({
                    **fila_base,
                    'Error': item['resultado']['error'],
                    'Respuesta_Cruda': 'N/A'
                })
        
    # Crear archivo Excel con múltiples hojas
        with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
            if filas:
                df_exitosos = pd.DataFrame(filas)
                df_exitosos.to_excel(writer, sheet_name='Facturas_Procesadas', index=False)
            
            if errores:
                df_errores = pd.DataFrame(errores)
                df_errores.to_excel(writer, sheet_name='Errores', index=False)
            
            # Resumen
            resumen = pd.DataFrame([{
                'Total_Archivos': len(datos_extraidos),
                'Exitosos': len(filas),
                'Errores': len(errores),
                'Fecha_Proceso': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }])
            resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        self.logger.info(f"Datos exportados a: {nombre_archivo}")
        self.logger.info(f"Procesados: {len(filas)} exitosos, {len(errores)} errores")
        
        return os.path.abspath(nombre_archivo)
    
    def generar_reporte_estadisticas(self, datos_extraidos: List[Dict]) -> Dict:
        """
        Genera estadísticas del procesamiento
        
        Args:
            datos_extraidos: Lista de datos extraídos
            
        Returns:
            Diccionario con estadísticas
        """
        total = len(datos_extraidos)
        exitosos = sum(1 for item in datos_extraidos if item['outputs']['success'])
        errores = total - exitosos
        
        estadisticas = {
            'total_archivos': total,
            'exitosos': exitosos,
            'errores': errores,
            'tasa_exito': (exitosos / total * 100) if total > 0 else 0,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return estadisticas

# Uso
API_KEY = "AIzaSyCQTKsf60v3u31rqm4yq5syxJcu__ZtvtQ"  # Obtener en https://makersuite.google.com/
procesador = ProcesadorFacturasGemini(API_KEY)
#resultados = procesador.procesar_carpeta_facturas("./facturas")
resultados = procesador.procesar_carpeta_facturas("./facturas")
procesador.exportar_a_excel(resultados)