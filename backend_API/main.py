from fastapi import FastAPI
from backend_API.routers.processing import ProcessingDownloadRouter
from backend_API.routers.processing.ProcessingRouter import router as processing_router
from backend_API.routers.invoince_image import InvoiceImageRouter
from backend_API.routers.invoice import InvoiceRouter
from backend_API.routers.logs import ProcessingLogRouter
from backend_API.routers.logs.ProcessingLogRouter import router as logs_router
from backend_API.routers.statistics.StatisticProcessRouter import router as statistics_router

from dotenv import load_dotenv

load_dotenv() 


print("Starting DIP App...")

app = FastAPI(
    title="Digital Invoices Processor App",
)

@app.get("/")
def read_root():
    return {"Message": "Digital Invoices Processor in Running now"}

app.include_router(processing_router)
app.include_router(InvoiceImageRouter.router)
app.include_router(InvoiceRouter.router)
app.include_router(ProcessingDownloadRouter.router)
app.include_router(logs_router)
app.include_router(statistics_router)

