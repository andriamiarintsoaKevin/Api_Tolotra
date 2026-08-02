from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass  # Utilisé pour la création (POST)

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True  # Permet la lecture depuis SQLAlchemy
