import csv
from io import StringIO
from slugify import slugify
from app.repositories.activity_repo import ActivityRepository
from app.db.models import Activity
from typing import List
from datetime import datetime
import re
import os

class CSVProcessor:
    def __init__(self, repo: ActivityRepository, log_file_path: str = "import_errors.log"):
        self.repo = repo
        self.log_file_path = log_file_path

    def process_and_store(self, file_content: bytes):
        content_string = file_content.decode('utf-8')
        
        # Pré-traitement pour corriger les motifs problématiques
        # Remplacer les motifs identifiés par des barres obliques pour ne pas les confondre avec des virgules
        content_string = re.sub(r'("compte",")', r'"compte /', content_string)
        content_string = re.sub(r'(bloqué, code)', r'bloqué / code', content_string)
        content_string = re.sub(r'(emploi, non)', r'emploi / non', content_string)
        content_string = re.sub(r'(Transaction P2P, CASH IN, CASH OUT,)', r'Transaction P2P / CASH IN / CASH OUT,', content_string)
        
        file_like_object = StringIO(content_string)
        csv_reader = csv.DictReader(file_like_object)
        
        activities_to_create: List[Activity] = []

        # Créer un dictionnaire de mapping pour assurer la correspondance correcte
        # entre les en-têtes du CSV et les noms des colonnes de la base de données.
        header_mapping = {
            'Numeroactivite': 'numero_activite',
            'Datecreation': 'date_creation',
            'Createur': 'createur',
            'Groupecreateur': 'groupe_createur',
            'Statut': 'statut',
            'Groupeassigne': 'groupe_assigne',
            'Utilisateurassigne': 'utilisateur_assigne',
            'Datecloture': 'date_cloture',
            'Groupetraiteur': 'groupe_traiteur',
            'Utilisateurtraiteur': 'utilisateur_traiteur',
            'Typeactivite': 'type_activite',
            'Activite': 'activite',
            'Raison': 'raison',
            'SousRaison': 'sous_raison', 
            # 'Sous Raison': 'sous_raison',
            'Details': 'details',
            'Datedebutactivite': 'date_debut_activite',
            'Datefinactivite': 'date_fin_activite',
            'Modifiepar': 'modifie_par',
            'Canal': 'canal',
            'Priorite': 'priorite',
            'Numcompteclient': 'num_compte_client',
            'NbRelance': 'nb_relance',
            'Numeroservice': 'numero_service',
            'Msisdn': 'msisdn',
        }

        with open(self.log_file_path, 'a') as log_file: # Ouvre le fichier en mode ajout
            for row in csv_reader:
                row_columns = len(row)
                expected_columns = len(Activity.__table__.columns) - 1
                
                if row_columns != expected_columns:
                    log_message = f"Skipping row due to inconsistent number of columns. Expected {expected_columns}, got {row_columns}: {row}\n"
                    log_file.write(log_message)
                    continue # Passer à la ligne suivante

                processed_row = {}
                
                # Utiliser le mapping pour construire le dictionnaire processed_row
                for key, value in row.items():
                    if key in header_mapping:
                        db_column_name = header_mapping[key]
                        processed_row[db_column_name] = None if value == '' else value
                    else:
                        # Gérer les en-têtes inconnus si nécessaire
                        print(f"Warning: Unknown CSV header '{key}'")
                
                # Conversion des chaînes de caractères en types Python appropriés
                for key in ["date_creation", "date_cloture", "date_debut_activite", "date_fin_activite"]:
                    if processed_row.get(key):
                        try:
                            processed_row[key] = datetime.strptime(processed_row[key], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            processed_row[key] = None
                
                # Conversion de nb_relance en int
                if processed_row.get('nb_relance'):
                    try:
                        processed_row['nb_relance'] = int(processed_row['nb_relance'])
                    except (ValueError, TypeError):
                        processed_row['nb_relance'] = None
                
                # Créer l'objet Activity et l'ajouter à la liste
                activity = Activity(**processed_row)
                activities_to_create.append(activity)

        if activities_to_create:
            self.repo.create_multiple(activities_to_create)

