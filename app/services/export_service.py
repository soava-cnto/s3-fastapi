import os
import csv
from datetime import datetime
from io import StringIO
from sqlmodel import Session
from app.db.models import Activity


class ExportService:
    @staticmethod
    def export_activities_to_csv(activities: list[Activity]) -> str:
        """
        Exporte la liste des activités en format CSV.
        Retourne le contenu CSV en tant que string.
        """
        if not activities:
            return ""
        
        output = StringIO()
        
        # Récupère les noms des colonnes du modèle
        fieldnames = list(activities[0].__fields__.keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for activity in activities:
            writer.writerow(activity.dict())
        
        return output.getvalue()
    
    @staticmethod
    def export_file_to_csv(activities: list[Activity], output_dir="./directory") -> str:
        """
        Exporte les activités en CSV et les sauvegarde dans un fichier.
        Retourne le chemin absolu du fichier créé.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_S3_Activity_Historique_{timestamp}.csv"
        output_path = os.path.join(output_dir, filename)
        
        csv_content = ExportService.export_activities_to_csv(activities)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)
        
        return os.path.abspath(output_path)