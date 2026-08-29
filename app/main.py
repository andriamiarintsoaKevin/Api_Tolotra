import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.exceptions import AppException
from app.routers import auth as auth_router
from app.routers import category as category_router
from app.routers import movement as movement_router
from app.routers import product as product_router
from app.routers import touriste as touriste_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gestion de Stock",
    description="API REST pour la gestion de stock, catégories et mouvements de stock",
    version="1.0.0",
)

# 3. Configuration du CORS (pour autoriser le Front-End / React / Vue / Flutter à communiquer)
# 3.1. Récupération de la variable d'environnement
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")

# 3.2. Traitement selon la valeur de ALLOWED_ORIGINS
if raw_origins.strip() == "*":
    origins = ["*"]
    # En dev avec "*", il faut désactiver allow_credentials pour éviter le rejet du navigateur
    allow_credentials = False
else:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    allow_credentials = True

# 3.3. Application du middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Enregistrement des Handlers d'exceptions personnalisées
# Gestionnaire d'exception global
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )

# 5. Inclusion des différents Routeurs d'entités
app.include_router(touriste_router.router)
app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(product_router.router)
app.include_router(movement_router.router)

# Si vous ajoutez d'autres entités plus tard :
# app.include_router(hotel_router.router)

# 6. Route de vérification / Health check (optionnel mais très utile)
@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Bienvenue sur l'API de gestion"}
