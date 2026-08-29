from fastapi import HTTPException

from app.database import Base, engine
from app.models import Category, Product, StockMovement, MovementType


def test_stock_movement_updates_product_quantity():
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session

    db = Session(bind=engine)
    try:
        category = Category(name="Électronique", description="")
        product = Product(name="Laptop", description="Ordinateur portable", price=1000.0, quantity=10, category=category)
        db.add_all([category, product])
        db.commit()

        movement = StockMovement(product_id=product.id, quantity=5, movement_type=MovementType.IN, reason="Achat fournisseur")
        db.add(movement)
        product.quantity += movement.quantity
        db.commit()

        assert product.quantity == 15

        out = StockMovement(product_id=product.id, quantity=20, movement_type=MovementType.OUT, reason="Vente client")
        db.add(out)
        if product.quantity < out.quantity:
            raise HTTPException(status_code=400, detail="Stock insuffisant")
        product.quantity -= out.quantity
        db.commit()

        assert product.quantity == -5
    finally:
        db.close()
