from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from src.core.logging_config import setup_logging
from src.api.endpoints import router as pricing_router

# Initialize logging
setup_logging()

app = FastAPI(
    title="Back to the Future Pricing API",
    description="API to calculate the price of Back to the Future DVDs with special discounts.",
    version="0.1.0",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Remove 422 responses
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            if "responses" in method:
                method["responses"].pop("422", None)

    # Remove the schemas as well
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        openapi_schema["components"]["schemas"].pop("HTTPValidationError", None)
        openapi_schema["components"]["schemas"].pop("ValidationError", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(pricing_router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="static", html=True), name="static")
