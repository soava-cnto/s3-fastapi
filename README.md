# s3-fastapi

Application FastAPI pour l'importation et l'exportation de données CSV depuis/vers une base de données.

## Fonctionnalités

### 1. Import CSV
- **Endpoint** : `POST /api/v1/import-csv/`
- Upload d'un fichier CSV et importation automatique dans la table `nouvelle_table`
- Traitement des données et validation
- Log des erreurs d'importation dans `import_errors.log`

### 2. Export CSV

#### 2.1 Export complet
- **Endpoint** : `GET /api/v1/export-csv/`
- Exporte tous les enregistrements de la table `nouvelle_table` en CSV
- Retourne un fichier téléchargeable avec timestamp : `export_activities_YYYYMMDD_HHMMSS.csv`

#### 2.2 Export par date spécifique
- **Endpoint** : `GET /api/v1/export-csv/by-date/?date=YYYY-MM-DD`
- Exporte les enregistrements dont la `date_fin_activite` correspond à la date fournie
- **Paramètre** : `date` (format: YYYY-MM-DD)

#### 2.3 Export par fourchette de dates
- **Endpoint** : `GET /api/v1/export-csv/by-date-range/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- Exporte les enregistrements dont la `date_fin_activite` est comprise entre deux dates (inclusive)
- **Paramètres** : 
  - `start_date` (format: YYYY-MM-DD)
  - `end_date` (format: YYYY-MM-DD)

## Structure du projet

```
app/
├── api/v1/
│   ├── endpoints/
│   │   ├── csv_import.py      # Routes d'importation CSV
│   │   └── csv_export.py      # Routes d'exportation CSV
│   └── routers.py             # Agrégation des routeurs
├── core/
│   ├── config.py              # Configuration
│   └── database.py            # Connexion BD
├── db/
│   └── models.py              # Modèle Activity (table: nouvelle_table)
├── repositories/
│   └── activity_repo.py        # Accès aux données
├── schemas/
│   ├── activity.py
│   └── csv_import.py
├── services/
│   ├── csv_processor.py        # Traitement import CSV
│   └── export_service.py       # Service d'export CSV
└── main.py                     # Point d'entrée FastAPI
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn app.main:app --reload
```

L'API sera disponible sur `http://localhost:8000`
Documentation interactive : `http://localhost:8000/docs`

## Table : nouvelle_table

Colonnes principales :
- `id` : Identifiant unique
- `numero_activite` : Numéro de l'activité
- `date_creation` : Date de création
- `date_fin_activite` : Date de fin (utilisée pour les filtres d'export)
- `statut` : Statut de l'activité
- Et de nombreux autres champs...

## Notes

- Les fichiers exportés sont sauvegardés dans le dossier `./directory`
- Format de date toujours : `YYYY-MM-DD`
- Les timestamps dans les noms de fichier : `YYYYMMDD_HHMMSS`