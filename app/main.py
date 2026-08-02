import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import touriste as touriste_router
from app.exceptions import TouristNotFoundException

# 1. Génération des tables dans la base de données (si elles n'existent pas ou on a pas encore alembic)
# Base.metadata.create_all(bind=engine)

# 2. Instanciation de l'application FastAPI
app = FastAPI(
    title="API de Gestion des Touristes",
    description="API REST avec FastAPI, SQLAlchemy et PostgreSQL",
    version="1.0.0"
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
@app.exception_handler(TouristNotFoundException)
def tourist_not_found_exception_handler(request: Request, exc: TouristNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Le touriste avec l'ID {exc.tourist_id} n'existe pas."}
    )

# 5. Inclusion des différents Routeurs d'entités
app.include_router(touriste_router.router)
# Si vous ajoutez d'autres entités plus tard :
# app.include_router(user_router.router)
# app.include_router(hotel_router.router)

# 6. Route de vérification / Health check (optionnel mais très utile)
@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Bienvenue sur l'API de gestion des touristes"}
