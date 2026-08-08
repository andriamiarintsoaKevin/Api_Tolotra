from fastapi import status
from app.exceptions.base import AppException

# 1. Utilisateur existe déjà (Inscription classique)
class UserAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Un utilisateur avec l'email '{email}' existe déjà.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

# 2. Utilisateur non trouvé
class UserNotFoundException(AppException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Aucun utilisateur trouvé avec l'email '{email}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )

# 3. Identifiants incorrects (Connexion classique)
class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Adresse email ou mot de passe incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# 4. Compte non vérifié (Tentative de login avant validation OTP)
class AccountNotVerifiedException(AppException):
    def __init__(self):
        super().__init__(
            message="Votre compte n'est pas encore vérifié. Veuillez valider le code OTP envoyé par email.",
            status_code=status.HTTP_403_FORBIDDEN
        )

# 5. OTP Invalide ou Expiré (Vérification Redis)
class InvalidOTPException(AppException):
    def __init__(self):
        super().__init__(
            message="Le code de vérification OTP est invalide ou a expiré.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

# 6. Jeton Google OAuth Invalide
class InvalidGoogleTokenException(AppException):
    def __init__(self, detail: str = "Le jeton Google est invalide ou expiré."):
        super().__init__(
            message=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
