import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    # Identifiant unique de l'utilisateur
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Adresse e-mail (Clé unique qui sert de rapprochement entre Google et Email classique)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Mot de passe hashé avec Bcrypt
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Indique si l'adresse e-mail a été vérifiée
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Provenance de la création du compte : "local" (Email/Password) ou "google"
    provider: Mapped[str] = mapped_column(String, default="local", nullable=False)

    # Informations optionnelles sur le profil
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    picture_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Rôle de l'utilisateur géré proprement par l'Enum UserRole
    # role: Mapped[UserRole] = mapped_column(
    #     Enum(UserRole), 
    #     default=UserRole.USER, 
    #     nullable=False
    # )

    # Horodatage automatique de la création et de la mise à jour du compte
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', provider='{self.provider}')>"
