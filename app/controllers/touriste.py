from sqlalchemy.orm import Session
from app import models, schemas
from app.exceptions import TouristNotFoundException


# 1. Créer un touriste
def create_tourist(db: Session, tourist_data: schemas.ItemCreate):
    db_tourist = models.Touriste(name=tourist_data.name)
    db.add(db_tourist)
    db.commit()
    db.refresh(db_tourist)
    return db_tourist


# 2. Récupérer tous les touristes
def get_tourists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Touriste).offset(skip).limit(limit).all()


# 3. Récupérer un touriste par son ID (Lève une exception si non trouvé)
def get_tourist_by_id(db: Session, tourist_id: int):
    tourist = db.query(models.Touriste).filter(models.Touriste.id == tourist_id).first()
    if not tourist:
        raise TouristNotFoundException(tourist_id=tourist_id)
    return tourist


# 4. Mettre à jour un touriste
def update_tourist(db: Session, tourist_id: int, tourist_data: schemas.ItemCreate):
    # Reutilise get_tourist_by_id qui lève automatiquement l'exception si l'ID n'existe pas
    db_tourist = get_tourist_by_id(db, tourist_id)
    
    db_tourist.name = tourist_data.name # type: ignore
    db.commit()
    db.refresh(db_tourist)
    return db_tourist


# 5. Supprimer un touriste
def delete_tourist(db: Session, tourist_id: int):
    # Reutilise get_tourist_by_id qui lève automatiquement l'exception si l'ID n'existe pas
    db_tourist = get_tourist_by_id(db, tourist_id)
    
    db.delete(db_tourist)
    db.commit()
    return True
