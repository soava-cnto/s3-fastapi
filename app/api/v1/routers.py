from fastapi import APIRouter
from app.api.v1.endpoints import csv_import

api_router = APIRouter()
api_router.include_router(csv_import.router, tags=["csv-import"])
