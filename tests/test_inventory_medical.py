from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Category, Product
from app.models.users import User


client = TestClient(app)

mock_user = User(
    id=1,
    email="inventory_manager@omnistock.com",
    full_name="Dr. Dupont",
)


@pytest.fixture(autouse=True)
def setup_db_and_auth():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Setup default category
    db = SessionLocal()
    category = Category(name="Pharmacie", description="Produits pharmaceutiques et vaccins")
    db.add(category)
    db.commit()
    db.close()

    yield

    app.dependency_overrides.clear()


def test_create_and_read_medical_product():
    """Vérifie la création et lecture d'un produit médical avec lot et température."""
    payload = {
        "name": "Insuline Glargine 10ml",
        "description": "Flacons d'insuline rapide 100UI/ml",
        "price": 42.50,
        "quantity": 45,
        "category_id": 1,
        "sku": "PH-INS-10ML-R",
        "sector": "medical",
        "reorder_threshold": 50,
        "warehouse_location": "Allée 4B - Frigo #02",
        "batch_number": "MED-99201",
        "expiry_date": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
        "storage_temperature": 4.1,
    }

    response = client.post("/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["batch_number"] == "MED-99201"
    assert data["storage_temperature"] == 4.1
    assert data["sector"] == "medical"
    assert data["is_expired"] is False
    assert data["sku"] == "PH-INS-10ML-R"

    # Vérification par scan du batch_number
    scan_resp = client.get(f"/v1/products/scan/{data['batch_number']}")
    assert scan_resp.status_code == 200
    assert scan_resp.json()["id"] == data["id"]


def test_medical_product_is_expired_detection():
    """Vérifie que la propriété is_expired passe à True pour une date passée."""
    payload = {
        "name": "Vaccin ROR pédiatrique",
        "description": "Lot périmé pour mise au rebut",
        "price": 25.00,
        "quantity": 10,
        "category_id": 1,
        "sku": "VAC-ROR-01",
        "sector": "medical",
        "batch_number": "LOT-EXPIRED-99",
        "expiry_date": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
        "storage_temperature": 5.0,
    }

    response = client.post("/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["is_expired"] is True


def test_medical_temperature_validation_422():
    """Vérifie le rejet HTTP 422 si la température est hors de la plage autorisée (-60°C à +60°C)."""
    payload = {
        "name": "Sérum test",
        "price": 10.0,
        "quantity": 5,
        "category_id": 1,
        "sector": "medical",
        "storage_temperature": 150.0,  # Température irréaliste
    }
    response = client.post("/v1/products/", json=payload)
    assert response.status_code == 422


def test_medical_sector_filter():
    """Vérifie le filtrage par secteur médical."""
    # Création d'un produit médical
    client.post("/v1/products/", json={
        "name": "Insuline",
        "price": 10.0,
        "quantity": 10,
        "category_id": 1,
        "sector": "medical",
        "batch_number": "MED-1",
    })
    # Création d'un produit général
    client.post("/v1/products/", json={
        "name": "Carton emballage",
        "price": 2.0,
        "quantity": 100,
        "category_id": 1,
        "sector": "general",
    })

    resp = client.get("/v1/products/?sector=medical")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["sector"] == "medical"
