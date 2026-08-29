from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import create_stock_movement, list_stock_movements
from app.database import get_db
from app.schemas.stock_movement import MovementType, StockMovementCreate, StockMovementResponse

router = APIRouter(
    prefix="/v1/movements",
    tags=["Stock - Mouvements"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
):
    return create_stock_movement(db, movement)


@router.get("/", response_model=List[StockMovementResponse])
def get_movements(
    product_id: int | None = Query(default=None),
    movement_type: MovementType | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_stock_movements(db, product_id=product_id, movement_type=movement_type)
