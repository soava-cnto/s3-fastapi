from sqlmodel import SQLModel
from datetime import datetime

class ActivityRead(SQLModel):
    id: int
    numero_activite: str
    date_creation: datetime
    createur: str
    groupe_createur: str
    statut: str
    groupe_assigne: str | None
    utilisateur_assigne: str | None
    date_cloture: datetime | None
    groupe_traiteur: str | None
    utilisateur_traiteur: str | None
    type_activite: str
    activite: str
    raison: str
    sous_raison: str
    details: str | None
    date_debut_activite: datetime | None
    date_fin_activite: datetime | None
    modifie_par: str | None
    canal: str
    priorite: str
    num_compte_client: str
    nb_relance: int
    numero_service: str
    msisdn: str
