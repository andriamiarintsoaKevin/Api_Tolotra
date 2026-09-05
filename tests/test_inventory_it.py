import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Category
from app.models.users import User


client = TestClient(app)

mock_user = User(
    id=1,
    email="it_manager@omnistock.com",
    full_name="Marc Tech",
)


@pytest.fixture(autouse=True)
def setup_db_and_auth():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    db = SessionLocal()
    category = Category(name="Informatique", description="Matériel informatique et réseau")
    db.add(category)
    db.commit()
    db.close()

    yield

    app.dependency_overrides.clear()


def test_create_and_update_it_product():
    """Vérifie la création et mise à jour d'un actif IT avec numéro de série et assignation."""
    payload = {
        "name": "ThinkPad T14 Gen 4",
        "description": "Laptop développeur 32GB RAM",
        "price": 1450.00,
        "quantity": 1,
        "category_id": 1,
        "sku": "IT-TP-T14-04",
        "sector": "it",
        "serial_number": "20W0-001XFR",
        "hardware_condition": "Neuf",
        "assigned_to": "Dr. Dupont",
        "warehouse_location": "Baie IT-02",
    }

    response = client.post("/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["serial_number"] == "20W0-001XFR"
    assert data["hardware_condition"] == "Neuf"
    assert data["assigned_to"] == "Dr. Dupont"
    assert data["sector"] == "it"

    # Mise à jour de l'assignation et de l'état
    product_id = data["id"]
    update_payload = {
        "hardware_condition": "En service",
        "assigned_to": "Sarah Chen",
    }
    update_resp = client.put(f"/v1/products/{product_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["hardware_condition"] == "En service"
    assert updated["assigned_to"] == "Sarah Chen"


def test_scan_it_asset_by_serial():
    """Vérifie la recherche d'un actif IT par son numéro de série (simulation scan code-barre)."""
    client.post("/v1/products/", json={
        "name": "MacBook Pro M3 16\"",
        "price": 2800.00,
        "quantity": 15,
        "category_id": 1,
        "sector": "it",
        "serial_number": "IT-8842-DK",
        "warehouse_location": "Stock IT Rack B",
    })

    scan_resp = client.get("/v1/products/scan/IT-8842-DK")
    assert scan_resp.status_code == 200
    data = scan_resp.json()
    assert data["name"] == "MacBook Pro M3 16\""
    assert data["serial_number"] == "IT-8842-DK"
