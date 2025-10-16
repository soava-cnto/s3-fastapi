import sys
import os

# Optionnel, mais sécurise l'importation par rapport à la racine du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import create_db_and_tables
from app.db.models import Activity # <<-- Ajoutez cette ligne d'import

if __name__ == "__main__":
    print("Création de la base de données et des tables...")
    create_db_and_tables()
    print("Base de données et tables créées avec succès.")
