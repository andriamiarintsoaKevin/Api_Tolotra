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
    email="warehouse@omnistock.com",
    full_name="Jean Logistique",
)


@pytest.fixture(autouse=True)
def setup_db_and_auth():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    db = SessionLocal()
    category = Category(name="Consommables", description="Matériel général et consommables")
    db.add(category)
    db.commit()
    db.close()

    yield

    app.dependency_overrides.clear()


def test_general_stock_threshold_and_metrics():
    """Vérifie la gestion des seuils critiques et le calcul des métriques du dashboard."""
    # Produit 1 : Stock critique (quantité 5 <= seuil 10)
    client.post("/v1/products/", json={
        "name": "Gants Stériles Latex",
        "price": 8.50,
        "quantity": 5,
        "category_id": 1,
        "sku": "GEN-GLV-01",
        "sector": "general",
        "reorder_threshold": 10,
        "warehouse_location": "Allée 1A",
    })

    # Produit 2 : Stock suffisant (quantité 50 > seuil 10)
    client.post("/v1/products/", json={
        "name": "Blouses Jetables",
        "price": 12.00,
        "quantity": 50,
        "category_id": 1,
        "sku": "GEN-BLS-02",
        "sector": "general",
        "reorder_threshold": 10,
        "warehouse_location": "Allée 1B",
    })

    # Test filtre low_stock
    low_stock_resp = client.get("/v1/products/?low_stock=true")
    assert low_stock_resp.status_code == 200
    low_stock_items = low_stock_resp.json()
    assert len(low_stock_items) == 1
    assert low_stock_items[0]["name"] == "Gants Stériles Latex"

    # Test endpoint dashboard stats
    stats_resp = client.get("/v1/products/dashboard/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_units"] == 55
    assert stats["active_references"] == 2
    assert stats["critical_stock_count"] == 1


def test_business_errors_400_and_404():
    """Vérifie les erreurs métier HTTP 400 (stock insuffisant) et 404 (article introuvable)."""
    # 404 pour un produit ou code inexistant
    resp_404 = client.get("/v1/products/scan/INEXISTANT-999")
    assert resp_404.status_code == 404

    # Création d'un article avec 10 unités
    create_resp = client.post("/v1/products/", json={
        "name": "Seringues 5ml",
        "price": 1.50,
        "quantity": 10,
        "category_id": 1,
        "sku": "SRG-5ML",
    })
    product_id = create_resp.json()["id"]

    # Tentative de sortie de stock de 25 unités (stock insuffisant -> 400)
    movement_payload = {
        "product_id": product_id,
        "quantity": 25,
        "movement_type": "OUT",
        "reason": "Distribution service A",
    }
    mov_resp = client.post("/v1/movements/", json=movement_payload)
    assert mov_resp.status_code == 400
    assert mov_resp.json()["detail"] == "Stock insuffisant"
