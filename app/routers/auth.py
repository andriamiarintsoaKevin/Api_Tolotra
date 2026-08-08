from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import oauth2_scheme
from app.controllers.auth import AuthController
from app.schemas.auth import (
    GoogleAuthSchema,
    LogoutResponse, 
    UserRegisterSchema, 
    VerifyOTPSchema, 
    TokenResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# 1. Endpoint Google Auth (1 Clic)
@router.post("/google", response_model=TokenResponse)
def google_auth(payload: GoogleAuthSchema, db: Session = Depends(get_db)):
    return AuthController.handle_google_login(payload.id_token, db=db)


# 2. Endpoint Inscription Classique (Génère OTP dans Redis)
@router.post("/register")
def register(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    return AuthController.register_user(email=payload.email, password=payload.password, db=db)


# 3. Endpoint Connexion Classique (Vérifie Email + Password) 
@router.post("/login", response_model=TokenResponse)
def login(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    return AuthController.login_user(email=payload.email, password=payload.password, db=db)


# 4. Endpoint Vérification OTP (Valide Redis + Retourne JWT)
@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOTPSchema, db: Session = Depends(get_db)):
    return AuthController.verify_otp_code(payload.email, payload.code, db=db)

@router.post("/logout", response_model=LogoutResponse)
def logout(token: str = Depends(oauth2_scheme)): 
    return AuthController.logout_user(token)
