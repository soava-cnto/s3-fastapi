from sqlmodel import Session, select
from sqlalchemy import cast, Date
from datetime import date
from app.db.models import Activity
from typing import List

class ActivityRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_multiple(self, activities: List[Activity]):
        self.session.add_all(activities)
        self.session.commit()
    
    def get_all(self) -> List[Activity]:
        """
        Récupère tous les enregistrements d'activités.
        """
        statement = select(Activity)
        return self.session.exec(statement).all()

    def get_by_date(self, target_date: date) -> List[Activity]:
        """
        Récupère les activités dont la colonne `date_fin_activite` correspond
        à la date fournie (en ignorant l'heure).
        """
        statement = select(Activity).where(cast(Activity.date_fin_activite, Date) == target_date)
        return self.session.exec(statement).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Activity]:
        """
        Récupère les activités dont la `date_fin_activite` est comprise
        entre start_date et end_date (fourchette inclusive).
        """
        statement = select(Activity).where(
            (cast(Activity.date_fin_activite, Date) >= start_date) &
            (cast(Activity.date_fin_activite, Date) <= end_date)
        )
        return self.session.exec(statement).all()
    
    def get_all_for_export(self, start_date: date = None, end_date: date = None) -> List[Activity]:
        """
        Récupère les activités pour l'export.
        Si start_date et end_date sont fournis, filtre par fourchette de date.
        Sinon, retourne tous les enregistrements.
        """
        if start_date and end_date:
            return self.get_by_date_range(start_date, end_date)
        elif start_date:
            return self.get_by_date(start_date)
        else:
            return self.get_all()
