from fastapi import FastAPI
from src.core.logging_config import setup_logging

# Initialize logging
setup_logging()

from src.api.endpoints import router as pricing_router

app = FastAPI(
    title="Back to the Future Pricing API",
    description="API to calculate the price of Back to the Future DVDs with special discounts.",
    version="0.1.0",
)

from fastapi.staticfiles import StaticFiles

app.include_router(pricing_router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="static", html=True), name="static")
