from sqlmodel import Session
from app.db.models import Activity
from typing import List

class ActivityRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_multiple(self, activities: List[Activity]):
        self.session.add_all(activities)
        self.session.commit()
