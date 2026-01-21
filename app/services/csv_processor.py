import csv
from io import StringIO
from slugify import slugify
from app.repositories.activity_repo import ActivityRepository
from app.db.models import Activity
from typing import List
from datetime import datetime
import re
import os
from sqlalchemy import delete

class CSVProcessor:
    def __init__(self, repo: ActivityRepository, log_file_path: str = "import_errors.log"):
        self.repo = repo
        self.log_file_path = log_file_path

    def process_and_store(self, file_content: bytes):
        # Truncate de la table avant l'insertion des nouvelles données
        self.repo.session.exec(delete(Activity))
        self.repo.session.commit()

        content_string = file_content.decode('ISO-8859-1')

        # Pré-traitement pour corriger les motifs problématiques avant de lire le CSV
        content_string = re.sub(r'("compte",")', r'"compte /', content_string)
        content_string = re.sub(r'(bloqué, code)', r'bloqué / code', content_string)
        content_string = re.sub(r'(emploi, non)', r'emploi / non', content_string)
        content_string = re.sub(r'(Transaction P2P, CASH IN, CASH OUT,)', r'Transaction P2P / CASH IN / CASH OUT,', content_string)
        content_string = re.sub(r'(Simple-Code oublié, compte non bloqué,)', r' Simple-Code oublié/ compte non bloqué,', content_string)
        content_string = re.sub(r'(Déblocage Simple-Compte bloqué, code connu,)', r' Déblocage Simple-Compte bloqué/ code connu,', content_string)
        content_string = re.sub(r'(Réinitialisation Déblocage-Code oublié, compte bloqué,)', r'Réinitialisation Déblocage-Code oublié/ compte bloqué,', content_string)

        # Créer un objet StringIO pour traiter le CSV après remplacement des motifs
        file_like_object = StringIO(content_string)
        csv_reader = csv.DictReader(file_like_object)

        activities_to_create: List[Activity] = []
        log_batch = []  # Pour les erreurs de log, à écrire en lot
        BATCH_SIZE = 50000  # Taille du lot pour les insertions
        MAX_LOG_SIZE = 100  # Taille du lot pour les logs

        # Dictionnaire de correspondance entre les entêtes CSV et les colonnes de la base de données
        header_mapping = {
            'NumeroActivite': 'numero_activite',
            'DateCreation': 'date_creation',
            'Createur': 'createur',
            'GroupeCreateur': 'groupe_createur',
            'Statut': 'statut',
            'GroupeAssigne': 'groupe_assigne',
            'UtilisateurAssigne': 'utilisateur_assigne',
            'DateCloture': 'date_cloture',
            'GroupeTraiteur': 'groupe_traiteur',
            'UtilisateurTraiteur': 'utilisateur_traiteur',
            'TypeActivite': 'type_activite',
            'Activite': 'activite',
            'Raison': 'raison',
            'SousRaison': 'sous_raison',
            'Sous Raison': 'sous_raison',
            'Details': 'details',
            'DateDebutActivite': 'date_debut_activite',
            'DateFinActivite': 'date_fin_activite',
            'ModifiePar': 'modifie_par',
            'Canal': 'canal',
            'Priorite': 'priorite',
            'NumCompteClient': 'num_compte_client',
            'NbRelance': 'nb_relance',
            'NumeroService': 'numero_service',
            'MSISDN': 'msisdn',
        }
        # header_mapping = {
        #     'Numeroactivite': 'numero_activite',
        #     'Datecreation': 'date_creation',
        #     'Createur': 'createur',
        #     'Groupecreateur': 'groupe_createur',
        #     'Statut': 'statut',
        #     'Groupeassigne': 'groupe_assigne',
        #     'Utilisateurassigne': 'utilisateur_assigne',
        #     'Datecloture': 'date_cloture',
        #     'Groupetraiteur': 'groupe_traiteur',
        #     'Utilisateurtraiteur': 'utilisateur_traiteur',
        #     'Typeactivite': 'type_activite',
        #     'Activite': 'activite',
        #     'Raison': 'raison',
        #     'SousRaison': 'sous_raison',
        #     'Sous Raison': 'sous_raison',
        #     'Details': 'details',
        #     'Datedebutactivite': 'date_debut_activite',
        #     'Datefinactivite': 'date_fin_activite',
        #     'Modifiepar': 'modifie_par',
        #     'Canal': 'canal',
        #     'Priorite': 'priorite',
        #     'Numcompteclient': 'num_compte_client',
        #     'NbRelance': 'nb_relance',
        #     'Numeroservice': 'numero_service',
        #     'Msisdn': 'msisdn',
        # }

        with open(self.log_file_path, 'a') as log_file:
            for row in csv_reader:
                row_columns = len(row)
                expected_columns = len(Activity.__table__.columns) - 1  # Nombre de colonnes attendues

                # Vérification du nombre de colonnes
                if row_columns != expected_columns:
                    log_message = f"Skipping row due to inconsistent number of columns. Expected {expected_columns}, got {row_columns}: {row}\n"
                    log_batch.append(log_message)

                    # Enregistrer le log en paquet si la taille maximale est atteinte
                    if len(log_batch) >= MAX_LOG_SIZE:
                        log_file.writelines(log_batch)
                        log_batch.clear()
                    continue  # Passer à la ligne suivante si le nombre de colonnes est incorrect

                processed_row = {}
                for key, value in row.items():
                    if key in header_mapping:
                        db_column_name = header_mapping[key]
                        processed_row[db_column_name] = None if value == '' else value
                    else:
                        print(f"Warning: Unknown CSV header '{key}'")  # Avertir si une colonne inconnue est trouvée

                # Conversion des dates
                for date_key in ["date_creation", "date_cloture", "date_debut_activite", "date_fin_activite"]:
                    if processed_row.get(date_key):
                        processed_row[date_key] = self.convert_date(processed_row[date_key])

                # Conversion de 'nb_relance' en int
                if processed_row.get('nb_relance'):
                    processed_row['nb_relance'] = self.convert_int(processed_row['nb_relance'])

                # Créer l'objet Activity et ajouter à la liste des activités
                activity = Activity(**processed_row)
                activities_to_create.append(activity)

                # Si le batch atteint la taille maximale, insérer les données
                if len(activities_to_create) >= BATCH_SIZE:
                    self.repo.create_multiple(activities_to_create)
                    activities_to_create.clear()  # Vider la liste après l'insertion

            # Insérer les activités restantes après la boucle
            if activities_to_create:
                self.repo.create_multiple(activities_to_create)

            # Enregistrer les logs restants si nécessaire
            if log_batch:
                log_file.writelines(log_batch)

    def convert_date(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    def convert_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
