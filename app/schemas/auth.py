from pydantic import BaseModel, EmailStr


# 1. Inscription classique (Email + Mot de passe)
class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str


# 2. Validation du code OTP Email
class VerifyOTPSchema(BaseModel):
    email: EmailStr
    code: str


# 3. Connexion classique (Rempli avec email + password)
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


# 4. Connexion Google OAuth
class GoogleAuthSchema(BaseModel):
    id_token: str


# 5. Réponse générée avec le Token JWT
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 6. Réponse après déconnexion
class LogoutResponse(BaseModel):
    message: str = "Déconnexion réussie avec succès."
