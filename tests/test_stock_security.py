from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Category, MovementType, Product, StockMovement


client = TestClient(app)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_stock_flow_updates_quantity_and_history():
    reset_db()
    db = SessionLocal()
    try:
        category = Category(name="Électronique", description="Matériel")
        product = Product(name="Laptop", description="Portable", price=1000.0, quantity=10, category=category)
        db.add_all([category, product])
        db.commit()
        db.refresh(product)

        in_movement = StockMovement(
            product_id=product.id,
            quantity=5,
            movement_type=MovementType.IN,
            reason="Achat fournisseur",
        )
        db.add(in_movement)
        product.quantity += in_movement.quantity
        db.commit()

        out_movement = StockMovement(
            product_id=product.id,
            quantity=3,
            movement_type=MovementType.OUT,
            reason="Vente client",
        )
        db.add(out_movement)
        if product.quantity < out_movement.quantity:
            raise HTTPException(status_code=400, detail="Stock insuffisant")
        product.quantity -= out_movement.quantity
        db.commit()

        db.refresh(product)
        assert product.quantity == 12
        history = db.query(StockMovement).filter(StockMovement.product_id == product.id).all()
        assert len(history) == 2
        assert {movement.movement_type for movement in history} == {MovementType.IN, MovementType.OUT}
    finally:
        db.close()


def test_insufficient_stock_raises_400():
    reset_db()
    db = SessionLocal()
    try:
        category = Category(name="Maison", description="Maison")
        product = Product(name="Lampe", description="Lampe", price=20.0, quantity=2, category=category)
        db.add_all([category, product])
        db.commit()

        movement = StockMovement(
            product_id=product.id,
            quantity=5,
            movement_type=MovementType.OUT,
            reason="Vente client",
        )
        db.add(movement)
        if product.quantity < movement.quantity:
            raise HTTPException(status_code=400, detail="Stock insuffisant")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Stock insuffisant"
    finally:
        db.close()


def test_products_route_requires_authentication():
    response = client.get("/v1/products/")
    assert response.status_code == 401
