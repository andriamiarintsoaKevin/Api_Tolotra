import secrets
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.database import redis_client
from app.models.users import User
from app.exceptions.auth import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    AccountNotVerifiedException,
    InvalidOTPException,
    InvalidGoogleTokenException,
)


class AuthController:

    @staticmethod
    def hash_password(password: str) -> str:
        """Hache un mot de passe en UTF-8 via la librairie native bcrypt"""
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie la correspondance d'un mot de passe brut avec son hash bcrypt"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except ValueError:
            return False

    @staticmethod
    def create_jwt_token(email: str) -> str:
        """Génère un token de session JWT pour l'utilisateur"""
        expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        payload = {"sub": email, "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # ------------------------------------------------------------------------
    # 1. AUTHENTIFICATION GOOGLE OAUTH
    # ------------------------------------------------------------------------
    @staticmethod
    def handle_google_login(token: str, db: Session):
        """Valide le token Google, puis authentifie ou crée l'utilisateur en BDD"""
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request())

            if id_info.get("aud") not in settings.google_client_ids_list:
                raise InvalidGoogleTokenException("Client ID Google non autorisé.")

        except ValueError:
            raise InvalidGoogleTokenException("Le jeton Google est invalide ou expiré.")

        email = id_info.get("email")
        if not email:
            raise InvalidGoogleTokenException("Impossible de récupérer l'e-mail depuis Google.")

        full_name = id_info.get("name")
        picture_url = id_info.get("picture")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                email=email,
                full_name=full_name,
                picture_url=picture_url,
                is_verified=True,  # L'email est déjà vérifié par Google
                provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if not user.is_verified: 
                user.is_verified = True
                db.commit()

        access_token = AuthController.create_jwt_token(user.email)
        return {"access_token": access_token, "token_type": "bearer"}

    # ------------------------------------------------------------------------
    # 2. AUTHENTIFICATION CLASSIQUE (EMAIL / MOT DE PASSE)
    # ------------------------------------------------------------------------
    @staticmethod
    def register_user(email: str, password: str, db: Session):
        """Crée ou réinitialise un utilisateur non vérifié et déclenche l'envoi de l'OTP"""
        existing_user = db.query(User).filter(User.email == email).first()
        hashed_password = AuthController.hash_password(password)

        if existing_user:
            if existing_user.is_verified:
                raise UserAlreadyExistsException(email)
            
            # Mise à jour du mot de passe si le compte existait mais n'était pas vérifié
            existing_user.hashed_password = hashed_password
            db.commit()
        else:
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                is_verified=False,
                provider="local"
            )
            db.add(new_user)
            db.commit()

        return AuthController.send_otp_code(email)

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        """Vérifie les identifiants et l'état de vérification du compte"""
        user = db.query(User).filter(User.email == email).first()

        # Vérification avec la nouvelle méthode natif-bcrypt
        if not user or not user.hashed_password or not AuthController.verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_verified:
            raise AccountNotVerifiedException()

        access_token = AuthController.create_jwt_token(user.email)
        return {"access_token": access_token, "token_type": "bearer"}

    # ------------------------------------------------------------------------
    # 3. GESTION DES OTP (REDIS)
    # ------------------------------------------------------------------------
    @staticmethod
    def send_otp_code(email: str):
        """Génère un OTP sécurisé à 6 chiffres et le stocke dans Redis pour 5 minutes (300s)"""
        otp = str(secrets.randbelow(900000) + 100000)

        redis_client.set(f"otp:{email}", otp, ex=300)

        print(f"📧 [EMAIL SIMULÉ] Code OTP pour {email} : {otp}")
        return {"message": "Un code de vérification à 6 chiffres a été envoyé par e-mail."}

    @staticmethod
    def verify_otp_code(email: str, code: str, db: Session):
        """Valide l'OTP stocké dans Redis et active le compte en BDD"""
        stored_otp = redis_client.get(f"otp:{email}")

        if isinstance(stored_otp, bytes):
            stored_otp = stored_otp.decode("utf-8")

        if not stored_otp or stored_otp != code:
            raise InvalidOTPException()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundException(email)

        user.is_verified = True
        db.commit()

        redis_client.delete(f"otp:{email}")

        access_token = AuthController.create_jwt_token(user.email)
        return {"access_token": access_token, "token_type": "bearer"}


    @staticmethod
    def logout_user(token: str):
        """Invalide un token JWT en l'ajoutant à la liste noire dans Redis"""
        try:
            # 1. Décode le token pour lire sa date d'expiration
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp_timestamp = payload.get("exp")

            if exp_timestamp:
                # 2. Calcule le temps restant avant que le token n'expire de lui-même
                now = datetime.now(timezone.utc).timestamp()
                time_to_live = int(exp_timestamp - now)

                # 3. Stocke le token dans Redis pour la durée restante exacte
                if time_to_live > 0:
                    redis_client.set(f"blacklist:{token}", "true", ex=time_to_live)

            return {"message": "Déconnexion réussie avec succès."}

        except jwt.PyJWTError:
            # Même si le token est invalide, on confirme la déconnexion
            return {"message": "Déconnexion réussie."}

