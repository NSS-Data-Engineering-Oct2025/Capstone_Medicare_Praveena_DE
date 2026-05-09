"""
main.py — FastAPI application entry point.

Usage:
    uv run uvicorn fastapi_app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi_app.routers.inpatient_router import router as inpatient_router
from fastapi_app.routers.physician_router import router as physician_router

app = FastAPI(
    title="Medicare Analytics API",
    version="1.0.0",
    description="""
    REST API serving Medicare analytics data from CMS datasets.

    ## Datasets
    - **Inpatient Hospital Data** — hospital payments, DRG procedures, discharge volumes
    - **Physician Data** — provider billing, specialty spending, drug vs non-drug services

    ## Data Source
    Centers for Medicare & Medicaid Services (CMS)
    https://data.cms.gov
    """,
    contact={
        "name": "Medicare Analytics Capstone Project"
    }
)

#  Include routers 
# Each router handles its own domain
# Adding a new domain = create new router + include it here

app.include_router(inpatient_router)
app.include_router(physician_router)


# Health check

@app.get("/api/v1/health", tags=["Health"])
def health():
    """
    Health check endpoint.
    Returns OK if the API is running.
    Used by monitoring tools to verify the service is up.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "description": "Medicare Analytics API is running"
    }