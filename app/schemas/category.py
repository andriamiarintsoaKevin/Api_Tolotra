from pydantic import BaseModel, ConfigDict


# ─── Schémas de base ────────────────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    description: str | None = None


# ─── Schéma de création ─────────────────────────────────────────────────────

class CategoryCreate(CategoryBase):
    """Champs requis pour créer une catégorie."""
    pass


# ─── Schéma de mise à jour (PATCH) ──────────────────────────────────────────

class CategoryUpdate(BaseModel):
    """Tous les champs sont optionnels pour permettre les mises à jour partielles."""
    name: str | None = None
    description: str | None = None


# ─── Schéma de réponse API ──────────────────────────────────────────────────

class CategoryResponse(CategoryBase):
    """Réponse renvoyée par l'API (inclut l'ID généré par la DB)."""
    id: int

    model_config = ConfigDict(from_attributes=True)
