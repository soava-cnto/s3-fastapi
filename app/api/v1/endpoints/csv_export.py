# ... autres imports
import os
from fastapi import APIRouter, File, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.repositories.activity_repo import ActivityRepository
from app.services.export_service import ExportService
from fastapi.responses import FileResponse
from datetime import datetime

router = APIRouter()

@router.get("/export-csv/")
def export_csv(session: Session = Depends(get_session)):
    """
    Exporte tous les enregistrements d'activités en CSV.
    Retourne le fichier CSV au client.
    """

    repo = ActivityRepository(session)
    activities = repo.get_all()
    
    if not activities:
        raise HTTPException(status_code=404, detail="Aucune activité à exporter")
    
    file_path = ExportService.export_file_to_csv(activities)
    
    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=os.path.basename(file_path)
    )


@router.get("/export-csv/by-date/")
def export_csv_by_date(date: str, session: Session = Depends(get_session)):
    """
    Exporte les enregistrements d'activités correspondant à la date fournie
    sur la colonne `date_fin_activite` (format attendu: YYYY-MM-DD).
    """
    
    # Valide et parse la date fournie
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utiliser YYYY-MM-DD")

    repo = ActivityRepository(session)
    activities = repo.get_by_date(date_obj)

    if not activities:
        raise HTTPException(status_code=404, detail="Aucune activité trouvée pour cette date")

    file_path = ExportService.export_file_to_csv(activities)

    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=os.path.basename(file_path)
    )


@router.get("/export-csv/by-date-range/")
def export_csv_by_date_range(start_date: str, end_date: str, session: Session = Depends(get_session)):
    """
    Exporte les enregistrements d'activités dans une fourchette de dates
    sur la colonne `date_fin_activite` (format attendu: YYYY-MM-DD).
    """
    
    # Valide et parse les dates fournies
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utiliser YYYY-MM-DD")
    
    if start_date_obj > end_date_obj:
        raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")

    repo = ActivityRepository(session)
    activities = repo.get_by_date_range(start_date_obj, end_date_obj)

    if not activities:
        raise HTTPException(status_code=404, detail="Aucune activité trouvée dans cette période")

    file_path = ExportService.export_file_to_csv(activities)

    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=os.path.basename(file_path)
    )
