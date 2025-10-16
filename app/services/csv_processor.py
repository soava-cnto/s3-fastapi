import csv
from io import StringIO
from slugify import slugify
from app.repositories.activity_repo import ActivityRepository
from app.db.models import Activity
from typing import List, Dict
from datetime import datetime

class CSVProcessor:
    def __init__(self, repo: ActivityRepository):
        self.repo = repo

    def process_and_store(self, file_content: bytes):
        file_like_object = StringIO(file_content.decode('utf-8'))
        csv_reader = csv.DictReader(file_like_object)

        activities_to_create: List[Activity] = []
        for row in csv_reader:
            processed_row = {slugify(key.lower(), separator='_'): value for key, value in row.items()}
            
            # Conversion des chaînes de caractères en types Python appropriés
            for key in ["date_creation", "date_cloture", "date_debut_activite", "date_fin_activite"]:
                if processed_row.get(key) and processed_row.get(key) != '':
                    try:
                        processed_row[key] = datetime.strptime(processed_row[key], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        processed_row[key] = None
            
            if processed_row.get('nb_relance') and processed_row.get('nb_relance') != '':
                try:
                    processed_row['nb_relance'] = int(processed_row['nb_relance'])
                except ValueError:
                    processed_row['nb_relance'] = None
            
            # Gérer les champs vides pour les colonnes non obligatoires
            for key in processed_row:
                if processed_row[key] == '':
                    processed_row[key] = None

            activity = Activity(**processed_row)
            activities_to_create.append(activity)

        if activities_to_create:
            self.repo.create_multiple(activities_to_create)
