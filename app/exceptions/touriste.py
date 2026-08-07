from fastapi import status
from app.exceptions.base import AppException

class TouristNotFoundException(AppException):
    def __init__(self, tourist_id: int):
        super().__init__(
            message=f"Le touriste avec l'ID {tourist_id} n'a pas été trouvé.",
            status_code=status.HTTP_404_NOT_FOUND
        )

class TouristAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Un touriste avec l'email '{email}' existe déjà.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
