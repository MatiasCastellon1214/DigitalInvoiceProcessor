# Facturas-Gemini: Procesador Automático de Facturas

`facturas-gemini` es un proyecto personal que utiliza la API de Google Gemini para procesar imágenes de facturas, extraer datos clave en formato JSON (como empresa, fecha, monto total, etc.) y exportarlos a un archivo Excel organizado. Este proyecto es ideal para automatizar la extracción de información de facturas de manera rápida y eficiente.

## Características

- **Procesamiento de imágenes**: Extrae datos de facturas en formatos de imagen como `.jpg`, `.jpeg`, `.png`, entre otros.
- **Salida en Excel**: Genera un archivo Excel con tres hojas:
  - **Facturas_Procesadas**: Datos extraídos de las facturas.
  - **Errores**: Detalles de facturas que no se procesaron correctamente.
  - **Resumen**: Estadísticas del procesamiento (total de archivos, exitosos, errores).
- **Logging**: Registra el proceso en un archivo `procesador_facturas.log` para facilitar la depuración.
- **Configuración flexible**: Permite limitar el número de facturas procesadas para respetar la cuota de la API.

## Cómo Funciona

El proyecto sigue este flujo:

1. **Carga de la clave de API**: Lee la clave de Google Gemini desde un archivo `.env`.
2. **Validación de conexión**: Realiza una prueba para asegurar que la API esté accesible.
3. **Procesamiento de facturas**:
   - Escanea la carpeta `facturas/` en busca de imágenes válidas.
   - Usa la API de Gemini (`gemini-1.5-flash`) para analizar cada imagen y extraer datos en formato JSON.
   - Valida y limpia las respuestas JSON para asegurar consistencia.
4. **Exportación**: Guarda los datos extraídos en un archivo Excel (`outputs/facturas_procesadas.xlsx`).
5. **Logging**: Registra cada paso (archivos procesados, errores, estadísticas) en `procesador_facturas.log` y muestra mensajes amigables en la consola.

## Requisitos Previos

- **Python 3.8 o superior**: Verifica con:
  ```bash
  python --version
  ```
- **Dependencias**: `python-dotenv`, `google-generativeai`, `pandas`, `openpyxl`, `Pillow`.
- **Clave de API de Google Gemini**:
  - Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/).
  - Habilita la API de **Generative Language** (`generativelanguage.googleapis.com`).
  - Genera una clave de API en **APIs & Services > Credentials > Create Credentials > API Key**.
- **Imágenes de facturas**: Coloca las facturas (`.jpg`, `.jpeg`, `.png`, etc.) en la carpeta `facturas/`.

## Instalación

1. **Clonar o descargar el repositorio**:

   - Clona el proyecto:
     ```bash
     git clone <URL_DEL_REPOSITORIO>
     cd facturas-gemini
     ```
   - O descarga el ZIP desde el repositorio y descomprímelo.
2. **Instalar dependencias**:

   - Crea un entorno virtual (opcional pero recomendado):

     ```bash
     python -m venv venv
     source venv/bin/activate  # En Windows: venv\Scripts\activate
     ```
   - Instala las dependencias:

     ```bash
     pip install -r requirements.txt
     ```
3. **Configurar el archivo `.env`**:

   - Crea un archivo `.env` en el directorio raíz del proyecto:
     ```plaintext
     GEMINI_API_KEY=AIXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
     ```
   - Asegúrate de:
     - Usar la clave de API generada.
     - Evitar espacios, comillas o líneas vacías.
     - Guardar el archivo en codificación UTF-8.
     - Nombrarlo exactamente `.env` (sin `.txt`).
   - Verifica su presencia:
     ```bash
     ls -a
     ```
4. **Preparar la carpeta de facturas**:

   - Crea una carpeta `facturas/` en el directorio raíz.
   - Coloca las imágenes de facturas (`.jpg`, `.jpeg`, `.png`, etc.) en esta carpeta.
   - Verifica:
     ```bash
     ls facturas/
     ```

## Ejecución

1. **Ejecutar el script principal**:

   - Para procesar todas las facturas:
     ```bash
     python -m main
     ```
   - Para limitar el número de facturas (por ejemplo, 5):
     ```bash
     python -m main --max-archivos 5
     ```
2. **Salida esperada**:

   ```
   🚀 Iniciando el procesamiento de facturas...
   ✅ Clave de API cargada.
   ✅ Conexión con la API de Gemini verificada.
   📂 Procesando facturas de la carpeta 'facturas/'...
   📄 Exportando datos a 'outputs/facturas_procesadas.xlsx'...
   🎉 ¡Listo! Los datos se exportaron a: outputs/facturas_procesadas.xlsx
   📊 Resumen: X facturas procesadas con éxito, Y errores de Z archivos.
   ```
3. **Verificar resultados**:

   - **Archivo Excel**: Abre `outputs/facturas_procesadas.xlsx` para revisar:
     - **Facturas_Procesadas**: Datos extraídos (empresa, fecha, monto, etc.).
     - **Errores**: Archivos con problemas.
     - **Resumen**: Estadísticas del procesamiento.
   - **Logs**: Consulta `procesador_facturas.log` para detalles técnicos.

## Gestión de la Cuota de la API

- El nivel gratuito de `gemini-1.5-flash` permite **50 solicitudes por día**. Cada factura procesada consume 1 solicitud.
- Para evitar el error `429 You exceeded your current quota`:
  - Usa `--max-archivos` para limitar el número de facturas.
  - Verifica la cuota en [Google Cloud Console](https://console.cloud.google.com/) > **APIs & Services > Metrics** o **Quotas**.
  - Configura un plan de pago para aumentar la cuota ([https://ai.google.dev/pricing](https://ai.google.dev/pricing)).
  - Espera 24 horas para que se reinicie la cuota si la excedes.

## Solución de Problemas

1. **Error: `No se pudo cargar la API key`**:

   - Verifica que `.env` contenga `GEMINI_API_KEY=AIXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`.
   - Asegúrate de que `python-dotenv` esté instalado:
     ```bash
     pip install python-dotenv
     ```
2. **Error: `Variable de entorno 'tu_api_key'`**:

   - Verifica si hay una variable de entorno conflictiva:
     ```bash
     echo $GEMINI_API_KEY
     ```
   - Elimina la variable:
     ```bash
     unset GEMINI_API_KEY
     setx GEMINI_API_KEY "" /M  # En Windows
     ```
3. **Error: `429 You exceeded your current quota`**:

   - Limita las facturas con `--max-archivos`.
   - Espera 24 horas o configura un plan de pago.
4. **Error: `FileNotFoundError: La carpeta facturas no existe`**:

   - Crea la carpeta `facturas/` y añade imágenes válidas.
5. **Errores en la extracción de datos**:

   - Asegúrate de que las imágenes sean claras y contengan la información requerida.
   - Revisa la hoja **Errores** en el Excel y `procesador_facturas.log` para detalles.

## Notas

- Mantén la clave de API en `.env` y añádelo a `.gitignore` para evitar compartirla.
- Usa imágenes de alta calidad para mejores resultados.
- Los logs en `procesador_facturas.log` son útiles para depurar problemas.

## Estructura del Proyecto

```
facturas-gemini/
├── facturas/                    # Carpeta con imágenes de facturas
├── outputs/                     # Carpeta para el archivo Excel generado
├── scripts/
│   ├── extractor.py             # Lógica para procesar facturas
│   ├── logger.py                # Configuración del logging
│   ├── config.py                # Configuraciones generales
│   ├── utils.py                 # Utilidades para limpiar respuestas JSON
├── main.py                      # Script principal
├── .env                         # Archivo con la clave de API
├── procesador_facturas.log      # Archivo de logs
├── README.md                    # Este archivo
```

## Contribuciones

Este es un proyecto personal, pero si tienes sugerencias o mejoras, ¡siéntete libre de compartirlas!
