from pydantic import BaseModel,  ConfigDict, EmailStr

class ItemBase(BaseModel):
    name: str
    email : EmailStr

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name : str | None = None
    email : EmailStr | None = None

class ItemResponse(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
