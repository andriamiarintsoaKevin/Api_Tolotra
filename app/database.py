import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# ==========================================
# 1. BASE DE DONNÉES SQL (Votre code existant)
# ==========================================
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dépendance FastAPI pour obtenir une session SQL"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 2. CACHE REDIS (Ajout pour la gestion des OTP)
# ==========================================

# Initialisation du client Redis
# decode_responses=True permet de recevoir directement des chaînes 'str' (ex: "123456") au lieu de 'bytes' (ex: b"123456")
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def get_redis():
    """Dépendance FastAPI pour injecter le client Redis dans les controllers/routers"""
    return redis_client
