from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.category import CategoryResponse


# ─── Schéma de base ────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    unit_price: float
    stock_quantity: int = 0
    category_id: int

    @field_validator("unit_price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Le prix unitaire doit être positif ou nul.")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("La quantité en stock ne peut pas être négative.")
        return v


# ─── Schéma de création ─────────────────────────────────────────────────────

class ProductCreate(ProductBase):
    """Champs requis pour créer un produit."""
    pass


# ─── Schéma de mise à jour (PATCH) ──────────────────────────────────────────

class ProductUpdate(BaseModel):
    """Tous les champs sont optionnels pour permettre les mises à jour partielles."""
    name: str | None = None
    description: str | None = None
    unit_price: float | None = None
    stock_quantity: int | None = None
    category_id: int | None = None

    @field_validator("unit_price")
    @classmethod
    def price_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Le prix unitaire doit être positif ou nul.")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("La quantité en stock ne peut pas être négative.")
        return v


# ─── Schéma de réponse API ──────────────────────────────────────────────────

class ProductResponse(ProductBase):
    """Réponse renvoyée par l'API (inclut l'ID et la date de création)."""
    id: int
    created_at: datetime
    # Inclusion de la catégorie imbriquée dans la réponse
    category: CategoryResponse

    model_config = ConfigDict(from_attributes=True)
