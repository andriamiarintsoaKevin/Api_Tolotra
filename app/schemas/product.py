from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.category import CategoryResponse


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int = 0
    category_id: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Le prix doit être positif ou nul.")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative.")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None
    category_id: int | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Le prix doit être positif ou nul.")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("La quantité ne peut pas être négative.")
        return v


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    category: CategoryResponse

    model_config = ConfigDict(from_attributes=True)
