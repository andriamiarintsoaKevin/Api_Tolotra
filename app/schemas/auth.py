from pydantic import BaseModel, EmailStr, Field


# 1. Inscription classique (Email + Mot de passe sécurisé)
class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mot de passe d'au moins 8 caractères")


# 2. Validation du code OTP Email
class VerifyOTPSchema(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=6, description="Code OTP reçu par email")


# 3. Connexion classique
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


# 4. Connexion Google OAuth
class GoogleAuthSchema(BaseModel):
    id_token: str


# 5. Réponse générée avec le Token JWT (+ Refresh Token facultatif)
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


# 6. Réponse après déconnexion
class LogoutResponse(BaseModel):
    message: str = "Déconnexion réussie avec succès."
