from sqlalchemy.orm import Session
from app import models, schemas
from app.exceptions import TouristAlreadyExistsException, TouristNotFoundException



def check_email_unique(db: Session, email: str, exclude_id: int | None = None) -> None:
    """
    Vérifie l'unicité de l'email.
    - Si 'exclude_id' est fourni, ignore le touriste en cours de modification.
    """
    query = db.query(models.Touriste).filter(models.Touriste.email == email)
    
    # Si c'est un UPDATE, on ignore le touriste actuel !
    if exclude_id is not None:
        query = query.filter(models.Touriste.id != exclude_id)
        
    if query.first():
        raise TouristAlreadyExistsException(email=email)

# 1. Créer un touriste# crud.py
def create_tourist(db: Session, tourist_data: schemas.ItemCreate):

    # Verification du unicité de l'email avant
    check_email_unique(db, email=tourist_data.email)

    # **tourist_data.model_dump() évite d'écrire chaque champ à la main
    db_tourist = models.Touriste(**tourist_data.model_dump())
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
def update_tourist(db: Session, tourist_id: int, tourist_data: schemas.ItemUpdate): 
    # 1. Récupération de l'enregistrement
    db_tourist = get_tourist_by_id(db, tourist_id)

    
    if tourist_data.email is not None:
        # On vérifie l'unicité EN EXCLUANT l'ID du touriste actuel
        check_email_unique(db, email=tourist_data.email, exclude_id=tourist_id)
    
    # 2. Conversion du schéma Pydantic en dictionnaire
    # exclude_unset=True isole uniquement les champs que le client a choisi d'envoyer
    update_data = tourist_data.model_dump(exclude_unset=True)

    # 3. Mise à jour dynamique de chaque attribut
    for field, value in update_data.items():
        setattr(db_tourist, field, value)

    # 4. Sauvegarde
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

