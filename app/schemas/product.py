from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.category import CategoryResponse


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int = 0
    category_id: int

    # Champs généraux & sectoriels
    sku: str | None = None
    sector: str = "general"
    reorder_threshold: int = 10
    warehouse_location: str | None = None

    # Spécificités Médicales
    batch_number: str | None = None
    expiry_date: datetime | None = None
    storage_temperature: float | None = None

    # Spécificités IT
    serial_number: str | None = None
    hardware_condition: str | None = None
    assigned_to: str | None = None

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

    @field_validator("reorder_threshold")
    @classmethod
    def threshold_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Le seuil de réapprovisionnement doit être positif ou nul.")
        return v

    @field_validator("sector")
    @classmethod
    def sector_must_be_valid(cls, v: str) -> str:
        valid_sectors = {"general", "medical", "it"}
        if v.lower() not in valid_sectors:
            raise ValueError(f"Secteur invalide. Valeurs autorisées: {', '.join(valid_sectors)}")
        return v.lower()

    @field_validator("storage_temperature")
    @classmethod
    def temperature_must_be_realistic(cls, v: float | None) -> float | None:
        if v is not None and (v < -60.0 or v > 60.0):
            raise ValueError("La température de stockage doit être comprise entre -60°C et +60°C.")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None
    category_id: int | None = None

    sku: str | None = None
    sector: str | None = None
    reorder_threshold: int | None = None
    warehouse_location: str | None = None

    batch_number: str | None = None
    expiry_date: datetime | None = None
    storage_temperature: float | None = None

    serial_number: str | None = None
    hardware_condition: str | None = None
    assigned_to: str | None = None

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

    @field_validator("reorder_threshold")
    @classmethod
    def threshold_must_be_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Le seuil de réapprovisionnement doit être positif ou nul.")
        return v

    @field_validator("sector")
    @classmethod
    def sector_must_be_valid(cls, v: str | None) -> str | None:
        if v is not None:
            valid_sectors = {"general", "medical", "it"}
            if v.lower() not in valid_sectors:
                raise ValueError(f"Secteur invalide. Valeurs autorisées: {', '.join(valid_sectors)}")
            return v.lower()
        return v

    @field_validator("storage_temperature")
    @classmethod
    def temperature_must_be_realistic(cls, v: float | None) -> float | None:
        if v is not None and (v < -60.0 or v > 60.0):
            raise ValueError("La température de stockage doit être comprise entre -60°C et +60°C.")
        return v


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    category: CategoryResponse
    is_expired: bool = False

    model_config = ConfigDict(from_attributes=True)

