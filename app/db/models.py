from sqlmodel import SQLModel, Field
from datetime import datetime

class Activity(SQLModel, table=True):
    __tablename__ = "activities"

    id: int | None = Field(default=None, primary_key=True)
    numero_activite: str | None = Field(default=None, index=True)
    date_creation: datetime | None = None
    createur: str | None = None
    groupe_createur: str | None = None
    statut: str | None = None
    groupe_assigne: str | None = None
    utilisateur_assigne: str | None = None
    date_cloture: datetime | None = None
    groupe_traiteur: str | None = None
    utilisateur_traiteur: str | None = None
    type_activite: str | None = None
    activite: str | None = None
    raison: str | None = None
    sous_raison: str | None = None
    details: str | None = None
    date_debut_activite: datetime | None = None
    date_fin_activite: datetime | None = None
    modifie_par: str | None = None
    canal: str | None = None
    priorite: str | None = None
    num_compte_client: str | None = None
    nb_relance: int | None = None
    numero_service: str | None = None
    msisdn: str | None = None
