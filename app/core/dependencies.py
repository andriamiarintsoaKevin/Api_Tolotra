from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.users import User
from app.database import redis_client


# Indique la route où Swagger UI peut récupérer un token si besoin
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Décode le token JWT et retourne l'utilisateur actuellement connecté"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton d'authentification invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    
    if redis_client.get(f"blacklist:{token}"):
        raise credentials_exception

    
    try:
        # Décodage du token JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        # Vérification du sujet (sub) : doit exister et être une chaîne de caractères
        if not email or not isinstance(email, str):
            raise credentials_exception

    except (jwt.InvalidTokenError, jwt.PyJWTError):
        # Intercepte l'expiration, la mauvaise signature ou la malformation du token
        raise credentials_exception

    # Récupération de l'utilisateur dans la base de données
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        """On passe la liste des rôles autorisés ex: ["admin"] ou ["user", "admin"]"""
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        """S'exécute automatiquement lors de la requête"""
        
        # On vérifie si la colonne 'role' de l'utilisateur fait partie des rôles autorisés
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, # 403 = Interdit !
                detail="Accès refusé : vous n'avez pas les droits nécessaires pour effectuer cette action."
            )
        return current_user

