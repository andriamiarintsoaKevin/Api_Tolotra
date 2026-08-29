from sqlalchemy.orm import Session
from app import models
from app.schemas.product import ProductCreate, ProductUpdate
from app.exceptions.stock import ProductNotFoundException
from app.controllers.category import get_category_by_id  # vérifie que la catégorie existe


# ─── CRUD ───────────────────────────────────────────────────────────────────

def create_product(db: Session, product_data: ProductCreate) -> models.Product:
    """Crée un produit. Vérifie que la catégorie cible existe avant insertion."""
    # S'assure que category_id pointe vers une catégorie réelle (lève 404 sinon)
    get_category_by_id(db, product_data.category_id)

    db_product = models.Product(**product_data.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[models.Product]:
    """Retourne la liste paginée des produits (avec leur catégorie via jointure lazy)."""
    return db.query(models.Product).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> models.Product:
    """Récupère un produit par son ID. Lève 404 si introuvable."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id=product_id)
    return product


def update_product(
    db: Session, product_id: int, product_data: ProductUpdate
) -> models.Product:
    """Met à jour partiellement un produit (uniquement les champs fournis)."""
    db_product = get_product_by_id(db, product_id)

    # Si le client change la catégorie, on vérifie que la nouvelle existe
    if product_data.category_id is not None:
        get_category_by_id(db, product_data.category_id)

    # exclude_unset=True : applique uniquement les champs envoyés par le client
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """Supprime un produit par son ID."""
    db_product = get_product_by_id(db, product_id)
    db.delete(db_product)
    db.commit()
    return True
