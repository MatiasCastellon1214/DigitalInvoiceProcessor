
# 🧾 Digital Invoice Processor: Procesamiento Automático de Facturas con Google Gemini

`Digital Invoice Processor` es un proyecto personal que permite procesar facturas digitales mediante inteligencia artificial. Extrae información estructurada desde imágenes, genera reportes estadísticos y permite operar tanto de forma **local** como a través de una **API RESTful con FastAPI**. Utiliza tecnologías como **Google Gemini**, **MongoDB** y **AWS S3** para lograr un procesamiento robusto, escalable y trazable.

---

## 🚀 Funcionalidades

- 📸 **Procesamiento de imágenes de facturas** (`.jpg`, `.jpeg`, `.png`).
- 🧠 **Extracción automática** de campos clave: empresa, fecha, monto total, etc.
- 📊 **Exportación a Excel** con 3 hojas:
  - `Facturas_Procesadas`
  - `Errores`
  - `Resumen`
- 📈 **Estadísticas de procesamiento**.
- 📝 **Logging completo** del flujo de ejecución.
- 🌐 **Interfaz API** con endpoints REST para integración de sistemas externos.
- ☁️ **Carga en AWS S3** y almacenamiento en **MongoDB** de los datos procesados.

---

## 🧰 Tecnologías Utilizadas

- **Python 3.8+ / 3.11+**
- **Google Gemini API**
- **FastAPI** – para la versión backend
- **Pandas, Pillow, openpyxl** – para manipulación de datos y archivos
- **python-dotenv** – gestión de variables de entorno
- **MongoDB** – almacenamiento de datos estructurados
- **AWS S3** – almacenamiento de archivos de entrada y logs

---

## 📦 Estructura del Proyecto

```
DigitalInvoiceProcessor/
├── backend_API/           ← API con FastAPI
├── local_processor/       ← Procesamiento local
├── outputs/               ← Archivos Excel generados
├── facturas/              ← Carpeta de imágenes para el modo local
├── .env                   ← Clave de API
├── requirements.txt
└── README.md
```

---

## 🔧 Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/MatiasCastellon1214/DigitalInvoiceProcessor.git
cd DigitalInvoiceProcessor
```

2. **Crear entorno virtual (opcional pero recomendado)**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Crear archivo `.env`**

```env
GEMINI_API_KEY=TU_API_KEY
```

> Asegúrate de que no haya espacios extra ni comillas. No lo subas a GitHub.

---

## 🖥️ Modo Local

### 📂 Preparar las facturas

- Crea una carpeta `facturas/` (o `local_processor/facturas/` si estás dentro del submódulo).
- Coloca allí las imágenes `.jpg`, `.jpeg`, `.png`.

### ▶️ Ejecutar

```bash
python -m main
# o con límite
python -m main --max-archivos 5
```

> Los resultados se guardan en `outputs/facturas_procesadas.xlsx`.

---

## 🌐 Modo API con FastAPI

### ▶️ Iniciar servidor

```bash
uvicorn backend_API.main:app --reload
```

- Visita `http://127.0.0.1:8000/docs` para la documentación interactiva.

### 📡 Endpoints disponibles

| Método | Endpoint                    | Descripción                                      |
|--------|-----------------------------|--------------------------------------------------|
| GET    | `/`                         | Mensaje de bienvenida                            |
| POST   | `/processing/`              | Procesa nuevas facturas                          |
| GET    | `/invoices/`                | Lista todas las facturas procesadas              |
| GET    | `/invoices/{invoice_id}`    | Detalles de una factura específica               |
| GET    | `/logs/`                    | Descarga logs del sistema                        |
| GET    | `/statistics/`              | Métricas y estadísticas del procesamiento        |

---

## 📊 Gestión de Cuotas de Google Gemini

- El modelo `gemini-1.5-flash` tiene **50 solicitudes diarias gratuitas**.
- Para evitar errores:
  - Usa `--max-archivos` si procesas localmente.
  - Configura alertas o upgradea a un plan de pago: [Precios](https://ai.google.dev/pricing)

---

## 🛠️ Solución de Problemas

| Problema | Solución |
|---------|----------|
| ❌ `No se pudo cargar la API key` | Verifica `.env` y que `python-dotenv` esté instalado |
| 🔒 `429 - Quota Exceeded` | Espera 24h o configura un plan de pago |
| 📂 `La carpeta facturas no existe` | Crea `facturas/` y añade imágenes válidas |
| 🛑 Errores en extracción | Verifica calidad de las imágenes y revisa el log |

---

## 📌 Notas

- Agrega `.env` al `.gitignore`.
- Usa imágenes claras y sin distorsión para mejores resultados.
- Logs detallados en `procesador_facturas.log`.

---

## 🤝 Contribuciones

Este es un proyecto personal en evolución. Si tienes sugerencias, errores o ideas, ¡no dudes en abrir un issue o PR!
