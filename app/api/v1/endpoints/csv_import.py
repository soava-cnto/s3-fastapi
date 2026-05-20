# ... autres imports
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.repositories.activity_repo import ActivityRepository
from app.services.csv_processor import CSVProcessor
from app.services.sftp_service import SFTPService

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


@router.post("/import-csv/sftp/history")
async def import_csv_from_sftp_history(session: Session = Depends(get_session)):
    """
    Importe le dernier fichier CSV depuis le serveur SFTP pour le traitement et le stockage dans la base de données.
    
    Le fichier doit correspondre au pattern: YYYY-MM-DD_S3_Activity_Historique_M(0)_to_J-1.csv
    La connexion SFTP doit être configurée dans le fichier .env
    """
    sftp_service = SFTPService()
    
    try:
        # Récupère le dernier fichier d'activité
        filename, content = sftp_service.read_latest_activity_file()
        
        if not filename or not content:
            raise HTTPException(
                status_code=404, 
                detail="Aucun fichier d'activité correspondant au pattern trouvé sur le serveur SFTP"
            )
        
        # Traite le fichier avec le processeur CSV
        repo = ActivityRepository(session)
        log_file_path = os.path.join(os.getcwd(), "import_errors.log")
        processor = CSVProcessor(repo, log_file_path, file_type="history")
        
        processor.process_and_store(content)
        
        return {
            "message": f"Fichier {filename} importé depuis SFTP et traité avec succès.",
            "filename": filename,
            "log_file": log_file_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de l'import SFTP : {str(e)}"
        )

@router.post("/import-csv/sftp/monthly/")
async def import_csv_from_sftp_monthly(session: Session = Depends(get_session)):
    """
    Importe le dernier fichier CSV depuis le serveur SFTP pour le traitement et le stockage dans la base de données.
    
    Le fichier doit correspondre au pattern: S3_Activity_Historique_Monthly_YYYY-MM-DD.csv
    La connexion SFTP doit être configurée dans le fichier .env (SFTP_REMOTE_PATH_MONTHLY)
    """
    sftp_service = SFTPService()
    
    try:
        # Récupère le dernier fichier d'activité monthly
        filename, content = sftp_service.read_latest_activity_file_monthly()
        
        if not filename or not content:
            raise HTTPException(
                status_code=404, 
                detail="Aucun fichier d'activité monthly correspondant au pattern trouvé sur le serveur SFTP"
            )
        
        # Traite le fichier avec le processeur CSV (format monthly)
        repo = ActivityRepository(session)
        log_file_path = os.path.join(os.getcwd(), "import_errors.log")
        processor = CSVProcessor(repo, log_file_path, file_type="monthly")
        
        processor.process_and_store(content)
        
        return {
            "message": f"Fichier {filename} importé depuis SFTP et traité avec succès.",
            "filename": filename,
            "log_file": log_file_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de l'import SFTP : {str(e)}"
        )



