from fastapi import APIRouter
from app.api.v1.endpoints import csv_import
from app.api.v1.endpoints import csv_export

api_router = APIRouter()
api_router.include_router(csv_import.router, tags=["csv-import"])
api_router.include_router(csv_export.router, tags=["csv-export"])
