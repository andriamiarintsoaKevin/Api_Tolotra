from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.controllers import touriste as touriste_controller

router = APIRouter(prefix="/touristes", tags=["Touristes"])

@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_tourist(tourist: schemas.ItemCreate, db: Session = Depends(get_db)):
    return touriste_controller.create_tourist(db, tourist)

@router.get("/", response_model=List[schemas.ItemResponse])
def get_tourists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return touriste_controller.get_tourists(db, skip=skip, limit=limit)

@router.get("/{tourist_id}", response_model=schemas.ItemResponse)
def get_tourist(tourist_id: int, db: Session = Depends(get_db)):
    return touriste_controller.get_tourist_by_id(db, tourist_id)

@router.put("/{tourist_id}", response_model=schemas.ItemResponse)
def update_tourist(tourist_id: int, tourist_data: schemas.ItemUpdate, db: Session = Depends(get_db)):
    return touriste_controller.update_tourist(db, tourist_id, tourist_data)

@router.delete("/{tourist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tourist(tourist_id: int, db: Session = Depends(get_db)):
    touriste_controller.delete_tourist(db, tourist_id)
    return None
