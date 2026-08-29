from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"


class StockMovementBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    movement_type: MovementType
    reason: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La quantité doit être supérieure à 0.")
        return v


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementUpdate(BaseModel):
    product_id: int | None = None
    quantity: int | None = Field(default=None, gt=0)
    movement_type: MovementType | None = None
    reason: str | None = None


class StockMovementResponse(StockMovementBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
