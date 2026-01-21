# Résumé du projet — API d'import/export CSV

## Objectif
- Fournir une API FastAPI pour importer et exporter des enregistrements d'activités au format CSV.
- Permettre des opérations CRUD basiques sur la table `nouvelle_table` via des endpoints REST.

## Structure principale
- `app/main.py` : point d'entrée de l'application et inclusion des routes.
- `app/api/v1/routers.py` : regroupe les routes `csv-import` et `csv-export`.
- `app/api/v1/endpoints/csv_import.py` : endpoints d'import CSV.
- `app/api/v1/endpoints/csv_export.py` : endpoints d'export CSV (dont un filtre par date `date_fin_activite`).
- `app/db/models.py` : modèle `Activity` (mapping SQLModel/SQLAlchemy vers `nouvelle_table`).
- `app/repositories/activity_repo.py` : couche d'accès aux données (ex. `get_all()`, `get_by_date()`).
- `app/services/export_service.py` : génération du contenu CSV et écriture sur disque.

## Pourquoi on n'écrit plus systématiquement du SQL brut
- **Sécurité :** l'ORM gère le paramétrage des requêtes et réduit les risques d'injection SQL.
- **Maintenabilité :** le code est typé/structuré en objets Python, plus facile à lire et refactorer.
- **Portabilité :** l'ORM abstrait certaines différences entre SGBD (types, casting, etc.).
- **Productivité :** moins de boilerplate pour les opérations CRUD courantes.

> Remarque : le SQL brut reste utile et parfois nécessaire (requêtes très complexes ou optimisations spécifiques).

## Performance — ORM vs SQL brut
- Pour des opérations CRUD simples, la différence de performance est souvent négligeable.
- Le SQL brut peut être plus rapide pour des requêtes complexes ou quand on veut exploiter des optimisations propres au SGBD.
- Les vrais leviers de performance sont :
  - index adaptés (ex. sur `date_fin_activite` si vous filtrez souvent dessus),
  - éviter `SELECT *` si seules quelques colonnes suffisent,
  - pagination / `LIMIT` pour réduire le transfert de données,
  - utiliser `EXPLAIN ANALYZE` pour profiler et optimiser les requêtes.

## Recommandations pratiques
- Utiliser l'ORM (`sqlmodel`/`sqlalchemy`) pour la majorité du code (sécurité & maintenance).
- Ajouter un index sur `date_fin_activite` si ce champ est souvent utilisé comme filtre.
- Pour les endpoints critiques, mesurer (profiling) puis comparer ORM vs SQL brut avant d'opter pour du SQL direct.
- Documenter les endroits où du SQL brut est utilisé et pourquoi.

## Exemple d'appel (export filtré par date)

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/export-csv/by-date/?date=2026-01-08" -o export_2026-01-08.csv
```

## Équivalent SQL

```sql
SELECT * FROM public.nouvelle_table
WHERE date_fin_activite::date = '2026-01-08';
```

---

Fichier créé : `PROJECT_SUMMARY.md`
