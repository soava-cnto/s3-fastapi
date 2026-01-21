# ... autres imports
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.repositories.activity_repo import ActivityRepository
from app.services.csv_processor import CSVProcessor

router = APIRouter()

@router.post("/import-csv/")
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Importe un fichier CSV pour le traitement et le stockage dans la base de données.
    """
    # ... (vérification du format du fichier)

    content = await file.read()

    repo = ActivityRepository(session)
    log_file_path = os.path.join(os.getcwd(), "import_errors.log")
    processor = CSVProcessor(repo, log_file_path) # Passe le chemin du fichier de journal
    
    try:
        processor.process_and_store(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du fichier : {str(e)}")

    return {"message": f"Fichier {file.filename} importé et traité avec succès. Les erreurs ont été enregistrées dans {log_file_path}."}


